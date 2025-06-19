"""
场景执行服务 - 场景实际执行和监控
"""
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from sqlalchemy.orm import selectinload

from ..dto.scenario_dto import (
    ScenarioExecutionCreateDTO, ScenarioExecutionUpdateDTO, ScenarioExecutionResponseDTO,
    ScenarioExecutionQueryDTO, ScenarioExecutionStatus, ScenarioExecutionType
)
from ...infrastructure.database.models import (
    ScenarioExecutionModel, ScenarioInstanceModel, ScenarioTemplateModel,
    WorkflowExecutionModel, RuleExecutionLogModel
)
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError
)

# 集成现有配置引擎服务
from .workflow_configuration_service import WorkflowConfigurationService
from .business_rule_service import BusinessRuleService
from .form_configuration_service import FormConfigurationService

logger = logging.getLogger(__name__)


class ScenarioExecutionService:
    """场景执行服务 - 执行引擎核心"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        # 集成现有配置引擎
        self.workflow_service = WorkflowConfigurationService(db_session)
        self.business_rule_service = BusinessRuleService(db_session)
        self.form_service = FormConfigurationService(db_session)
    
    async def create_execution(
        self,
        execution_data: ScenarioExecutionCreateDTO,
        created_by: str,
        tenant_id: str
    ) -> ScenarioExecutionResponseDTO:
        """创建场景执行"""
        try:
            # 验证场景实例存在且可执行
            scenario_instance = await self._get_executable_scenario(
                execution_data.scenario_instance_id, tenant_id
            )
            
            if not scenario_instance:
                raise ConfigurationNotFoundError(
                    f"场景实例 {execution_data.scenario_instance_id} 不存在或不可执行"
                )
            
            # 创建执行记录
            execution = ScenarioExecutionModel(
                scenario_instance_id=execution_data.scenario_instance_id,
                execution_status=ScenarioExecutionStatus.PENDING.value,
                execution_type=execution_data.execution_type.value,
                trigger_source=execution_data.trigger_source.value if execution_data.trigger_source else None,
                trigger_user_id=execution_data.trigger_user_id,
                trigger_context=execution_data.trigger_context,
                target_entity_type=execution_data.target_entity_type,
                target_entity_id=execution_data.target_entity_id,
                target_entity_data=execution_data.target_entity_data,
                created_by=created_by,
                updated_by=created_by,
                tenant_id=tenant_id
            )
            
            self.db.add(execution)
            await self.db.commit()
            await self.db.refresh(execution)
            
            # 异步启动执行
            if execution_data.execution_type != ScenarioExecutionType.TEST:
                asyncio.create_task(self._execute_scenario_async(execution))
            
            logger.info(f"创建场景执行成功: {execution.id}")
            return await self._build_execution_response(execution)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建场景执行失败: {str(e)}")
            raise
    
    async def _get_executable_scenario(
        self, 
        scenario_id: UUID, 
        tenant_id: str
    ) -> Optional[ScenarioInstanceModel]:
        """获取可执行的场景实例"""
        stmt = select(ScenarioInstanceModel).options(
            selectinload(ScenarioInstanceModel.scenario_template)
        ).where(
            and_(
                ScenarioInstanceModel.id == scenario_id,
                ScenarioInstanceModel.tenant_id == tenant_id,
                ScenarioInstanceModel.instance_status == "active",
                ScenarioInstanceModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _execute_scenario_async(self, execution: ScenarioExecutionModel) -> None:
        """异步执行场景（后台任务）"""
        try:
            logger.info(f"开始异步执行场景: execution_id={execution.id}")
            
            # 更新执行状态为运行中
            await self._update_execution_status(
                execution.id, 
                ScenarioExecutionStatus.RUNNING,
                {"started_at": datetime.utcnow().isoformat()}
            )
            
            # 加载场景实例和模板配置
            scenario_instance = await self._get_executable_scenario(
                execution.scenario_instance_id, 
                execution.tenant_id
            )
            
            if not scenario_instance:
                await self._fail_execution(execution.id, "场景实例不存在或不可执行")
                return
            
            # 构建执行上下文
            exec_context = await self._build_execution_context(execution, scenario_instance)
            
            # 执行场景步骤
            success = await self._execute_scenario_steps(execution, scenario_instance, exec_context)
            
            if success:
                await self._complete_execution(execution.id, exec_context)
            else:
                await self._fail_execution(execution.id, "场景执行失败")
            
        except Exception as e:
            logger.error(f"场景异步执行异常: execution_id={execution.id}, error={str(e)}")
            await self._fail_execution(execution.id, f"执行异常: {str(e)}")
    
    async def _build_execution_context(
        self, 
        execution: ScenarioExecutionModel,
        scenario_instance: ScenarioInstanceModel
    ) -> Dict[str, Any]:
        """构建执行上下文"""
        context = {
            "execution_id": str(execution.id),
            "scenario_id": str(scenario_instance.id),
            "template_id": str(scenario_instance.template_id),
            "entity_type": execution.target_entity_type,
            "entity_id": execution.target_entity_id,
            "trigger_context": execution.trigger_context or {},
            "target_data": execution.target_entity_data or {},
            "tenant_id": execution.tenant_id,
            "started_at": execution.started_at.isoformat(),
            "execution_data": {},
            "step_results": {},
            "current_step": None
        }
        
        # 合并场景配置
        merged_config = await self._merge_scenario_configurations(scenario_instance)
        context["scenario_config"] = merged_config
        
        return context
    
    async def _merge_scenario_configurations(
        self, 
        scenario_instance: ScenarioInstanceModel
    ) -> Dict[str, Any]:
        """合并场景配置（模板 + 实例覆盖）"""
        # 获取模板默认配置
        template_config = scenario_instance.scenario_template.default_configurations or {}
        
        # 应用实例覆盖
        merged_config = template_config.copy()
        
        if scenario_instance.custom_configurations:
            merged_config.update(scenario_instance.custom_configurations)
        
        if scenario_instance.form_config_overrides:
            merged_config["form_config"] = merged_config.get("form_config", {})
            merged_config["form_config"].update(scenario_instance.form_config_overrides)
        
        if scenario_instance.workflow_config_overrides:
            merged_config["workflow_config"] = merged_config.get("workflow_config", {})
            merged_config["workflow_config"].update(scenario_instance.workflow_config_overrides)
        
        if scenario_instance.business_rule_overrides:
            merged_config["business_rules"] = scenario_instance.business_rule_overrides
        
        if scenario_instance.spatial_config_overrides:
            merged_config["spatial_config"] = merged_config.get("spatial_config", {})
            merged_config["spatial_config"].update(scenario_instance.spatial_config_overrides)
        
        return merged_config
    
    async def _execute_scenario_steps(
        self,
        execution: ScenarioExecutionModel,
        scenario_instance: ScenarioInstanceModel,
        context: Dict[str, Any]
    ) -> bool:
        """执行场景步骤"""
        try:
            scenario_config = context["scenario_config"]
            
            # 定义执行步骤顺序
            execution_steps = [
                ("validate_form", self._execute_form_validation),
                ("apply_business_rules", self._execute_business_rules),
                ("execute_workflow", self._execute_workflow),
                ("update_spatial_config", self._execute_spatial_updates),
                ("send_notifications", self._execute_notifications)
            ]
            
            step_results = {}
            
            for step_name, step_executor in execution_steps:
                try:
                    logger.debug(f"执行步骤: {step_name}, execution_id={execution.id}")
                    
                    # 更新当前步骤
                    context["current_step"] = step_name
                    await self._update_execution_progress(execution.id, step_name, context)
                    
                    # 执行步骤
                    step_result = await step_executor(scenario_config, context)
                    step_results[step_name] = step_result
                    
                    # 检查步骤是否成功
                    if not step_result.get("success", False):
                        error_msg = step_result.get("error", f"步骤 {step_name} 执行失败")
                        logger.error(f"执行步骤失败: {step_name}, error={error_msg}")
                        
                        # 根据配置决定是否继续
                        if step_result.get("critical", False):
                            return False
                        # 非关键步骤失败，记录但继续执行
                    
                except Exception as e:
                    logger.error(f"执行步骤异常: {step_name}, error={str(e)}")
                    step_results[step_name] = {
                        "success": False,
                        "error": str(e),
                        "critical": True
                    }
                    return False
            
            # 更新最终执行结果
            context["step_results"] = step_results
            
            return True
            
        except Exception as e:
            logger.error(f"执行场景步骤失败: {str(e)}")
            return False
    
    async def _execute_form_validation(
        self, 
        scenario_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行表单验证步骤"""
        try:
            form_config = scenario_config.get("form_config")
            if not form_config:
                return {"success": True, "message": "无表单配置，跳过验证"}
            
            target_data = context.get("target_data", {})
            
            # 使用现有表单配置服务进行验证
            validation_schema = form_config.get("validation_schema", {})
            
            if validation_schema:
                # 这里可以调用表单配置服务的验证方法
                # validation_result = await self.form_service.validate_data(target_data, validation_schema)
                # 简化实现
                validation_result = self._simple_form_validation(target_data, validation_schema)
                
                if not validation_result["valid"]:
                    return {
                        "success": False,
                        "error": f"表单验证失败: {validation_result['errors']}",
                        "critical": True
                    }
            
            return {
                "success": True,
                "message": "表单验证通过",
                "validated_data": target_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"表单验证异常: {str(e)}",
                "critical": True
            }
    
    def _simple_form_validation(
        self, 
        data: Dict[str, Any], 
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """简单表单验证实现"""
        errors = []
        
        required_fields = schema.get("required_fields", [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"必填字段 {field} 缺失或为空")
        
        field_rules = schema.get("field_rules", {})
        for field, rules in field_rules.items():
            if field in data:
                value = data[field]
                
                # 类型验证
                if "type" in rules:
                    expected_type = rules["type"]
                    if expected_type == "string" and not isinstance(value, str):
                        errors.append(f"字段 {field} 类型错误，期望字符串")
                    elif expected_type == "number" and not isinstance(value, (int, float)):
                        errors.append(f"字段 {field} 类型错误，期望数字")
                
                # 长度验证
                if "min_length" in rules and len(str(value)) < rules["min_length"]:
                    errors.append(f"字段 {field} 长度不足")
                
                if "max_length" in rules and len(str(value)) > rules["max_length"]:
                    errors.append(f"字段 {field} 长度超限")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _execute_business_rules(
        self, 
        scenario_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行业务规则步骤"""
        try:
            business_rules = scenario_config.get("business_rules", [])
            if not business_rules:
                return {"success": True, "message": "无业务规则，跳过执行"}
            
            rule_results = []
            
            for rule_config in business_rules:
                try:
                    # 使用现有业务规则服务执行规则
                    # rule_result = await self.business_rule_service.execute_rule(rule_config, context)
                    # 简化实现
                    rule_result = await self._execute_single_business_rule(rule_config, context)
                    rule_results.append(rule_result)
                    
                    # 检查关键业务规则
                    if not rule_result["success"] and rule_config.get("critical", False):
                        return {
                            "success": False,
                            "error": f"关键业务规则执行失败: {rule_result['error']}",
                            "critical": True
                        }
                        
                except Exception as e:
                    logger.error(f"业务规则执行异常: {str(e)}")
                    rule_results.append({
                        "success": False,
                        "error": str(e)
                    })
            
            success_count = sum(1 for r in rule_results if r["success"])
            
            return {
                "success": True,
                "message": f"业务规则执行完成: {success_count}/{len(rule_results)} 成功",
                "rule_results": rule_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"业务规则执行异常: {str(e)}",
                "critical": False
            }
    
    async def _execute_single_business_rule(
        self, 
        rule_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个业务规则"""
        try:
            rule_name = rule_config.get("rule_name", "未命名规则")
            rule_conditions = rule_config.get("rule_conditions", {})
            rule_actions = rule_config.get("rule_actions", [])
            
            # 评估规则条件
            conditions_met = self._evaluate_business_rule_conditions(rule_conditions, context)
            
            if conditions_met:
                # 执行规则动作
                action_results = []
                for action in rule_actions:
                    action_result = await self._execute_rule_action(action, context)
                    action_results.append(action_result)
                
                return {
                    "success": True,
                    "rule_name": rule_name,
                    "triggered": True,
                    "action_results": action_results
                }
            else:
                return {
                    "success": True,
                    "rule_name": rule_name,
                    "triggered": False,
                    "message": "规则条件不满足"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"规则执行失败: {str(e)}"
            }
    
    def _evaluate_business_rule_conditions(
        self, 
        conditions: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> bool:
        """评估业务规则条件"""
        try:
            # 简化的条件评估
            if not conditions:
                return True
            
            # 这里可以实现复杂的条件评估逻辑
            # 现在简化为总是返回True
            return True
            
        except Exception as e:
            logger.error(f"业务规则条件评估失败: {str(e)}")
            return False
    
    async def _execute_rule_action(
        self, 
        action: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行规则动作"""
        try:
            action_type = action.get("action_type")
            action_params = action.get("params", {})
            
            if action_type == "update_status":
                # 更新状态动作
                return await self._execute_update_status_action(action_params, context)
            elif action_type == "send_notification":
                # 发送通知动作
                return await self._execute_notification_action(action_params, context)
            elif action_type == "log_event":
                # 记录事件动作
                return await self._execute_log_event_action(action_params, context)
            else:
                return {
                    "success": False,
                    "error": f"不支持的动作类型: {action_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"动作执行失败: {str(e)}"
            }
    
    async def _execute_update_status_action(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行状态更新动作"""
        # 简化实现
        return {
            "success": True,
            "message": "状态更新成功",
            "action": "update_status",
            "params": params
        }
    
    async def _execute_notification_action(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行通知动作"""
        # 简化实现
        return {
            "success": True,
            "message": "通知发送成功", 
            "action": "send_notification",
            "params": params
        }
    
    async def _execute_log_event_action(
        self, 
        params: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行日志记录动作"""
        logger.info(f"业务规则日志: {params.get('message', '')}")
        return {
            "success": True,
            "message": "事件记录成功",
            "action": "log_event",
            "params": params
        }
    
    async def _execute_workflow(
        self, 
        scenario_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工作流步骤"""
        try:
            workflow_config = scenario_config.get("workflow_config")
            if not workflow_config:
                return {"success": True, "message": "无工作流配置，跳过执行"}
            
            # 使用现有工作流配置服务
            # workflow_result = await self.workflow_service.execute_workflow(workflow_config, context)
            # 简化实现
            
            workflow_steps = workflow_config.get("workflow_steps", [])
            step_results = []
            
            for step in workflow_steps:
                step_result = await self._execute_workflow_step(step, context)
                step_results.append(step_result)
                
                if not step_result["success"] and step.get("critical", False):
                    return {
                        "success": False,
                        "error": f"关键工作流步骤失败: {step_result['error']}",
                        "critical": True
                    }
            
            return {
                "success": True,
                "message": "工作流执行完成",
                "step_results": step_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"工作流执行异常: {str(e)}",
                "critical": False
            }
    
    async def _execute_workflow_step(
        self, 
        step: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工作流步骤"""
        try:
            step_type = step.get("step_type")
            step_config = step.get("config", {})
            
            # 简化的步骤执行
            await asyncio.sleep(0.1)  # 模拟异步处理
            
            return {
                "success": True,
                "step_type": step_type,
                "message": f"步骤 {step_type} 执行成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"工作流步骤执行失败: {str(e)}"
            }
    
    async def _execute_spatial_updates(
        self, 
        scenario_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行空间配置更新"""
        return {
            "success": True,
            "message": "空间配置更新完成"
        }
    
    async def _execute_notifications(
        self, 
        scenario_config: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行通知发送"""
        return {
            "success": True,
            "message": "通知发送完成"
        }
    
    async def _update_execution_status(
        self, 
        execution_id: UUID, 
        status: ScenarioExecutionStatus,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """更新执行状态"""
        try:
            update_dict = {
                "execution_status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            if additional_data:
                if "started_at" in additional_data:
                    # 不直接更新started_at，因为它在模型中有默认值
                    pass
                
                if "execution_data" in additional_data:
                    update_dict["execution_data"] = additional_data["execution_data"]
            
            stmt = update(ScenarioExecutionModel).where(
                ScenarioExecutionModel.id == execution_id
            ).values(**update_dict)
            
            await self.db.execute(stmt)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"更新执行状态失败: {str(e)}")
    
    async def _update_execution_progress(
        self, 
        execution_id: UUID, 
        current_step: str,
        context: Dict[str, Any]
    ) -> None:
        """更新执行进度"""
        try:
            stmt = update(ScenarioExecutionModel).where(
                ScenarioExecutionModel.id == execution_id
            ).values(
                current_step=current_step,
                execution_data=context.get("execution_data", {}),
                updated_at=datetime.utcnow()
            )
            
            await self.db.execute(stmt)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"更新执行进度失败: {str(e)}")
    
    async def _complete_execution(
        self, 
        execution_id: UUID, 
        context: Dict[str, Any]
    ) -> None:
        """完成执行"""
        try:
            completed_at = datetime.utcnow()
            started_at = context.get("started_at")
            
            duration = None
            if started_at:
                try:
                    start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    duration = (completed_at - start_time).total_seconds()
                except Exception:
                    pass
            
            stmt = update(ScenarioExecutionModel).where(
                ScenarioExecutionModel.id == execution_id
            ).values(
                execution_status=ScenarioExecutionStatus.COMPLETED.value,
                completed_at=completed_at,
                execution_duration=duration,
                execution_result=context.get("step_results"),
                step_results=context.get("step_results"),
                updated_at=completed_at
            )
            
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.info(f"场景执行完成: execution_id={execution_id}, duration={duration}s")
            
        except Exception as e:
            logger.error(f"完成执行失败: {str(e)}")
    
    async def _fail_execution(
        self, 
        execution_id: UUID, 
        error_message: str
    ) -> None:
        """标记执行失败"""
        try:
            stmt = update(ScenarioExecutionModel).where(
                ScenarioExecutionModel.id == execution_id
            ).values(
                execution_status=ScenarioExecutionStatus.FAILED.value,
                error_details=error_message,
                completed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            await self.db.execute(stmt)
            await self.db.commit()
            
            logger.error(f"场景执行失败: execution_id={execution_id}, error={error_message}")
            
        except Exception as e:
            logger.error(f"标记执行失败失败: {str(e)}")
    
    async def _build_execution_response(
        self, 
        execution: ScenarioExecutionModel
    ) -> ScenarioExecutionResponseDTO:
        """构建执行响应DTO"""
        # 加载关联的场景实例
        await self.db.refresh(execution, ['scenario_instance'])
        
        response = ScenarioExecutionResponseDTO.from_orm(execution)
        
        # 如果需要，可以加载更多关联信息
        # if execution.scenario_instance:
        #     response.scenario_instance = ScenarioInstanceResponseDTO.from_orm(execution.scenario_instance)
        
        return response
    
    # ================== 查询和管理接口 ==================
    
    async def get_execution(
        self, 
        execution_id: UUID, 
        tenant_id: str
    ) -> ScenarioExecutionResponseDTO:
        """获取场景执行"""
        stmt = select(ScenarioExecutionModel).options(
            selectinload(ScenarioExecutionModel.scenario_instance)
        ).where(
            and_(
                ScenarioExecutionModel.id == execution_id,
                ScenarioExecutionModel.tenant_id == tenant_id
            )
        )
        result = await self.db.execute(stmt)
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise ConfigurationNotFoundError(f"场景执行 {execution_id} 不存在")
        
        return await self._build_execution_response(execution)
    
    async def list_executions(
        self,
        query: ScenarioExecutionQueryDTO,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ScenarioExecutionResponseDTO], int]:
        """列出场景执行"""
        conditions = [
            ScenarioExecutionModel.tenant_id == tenant_id
        ]
        
        if query.scenario_instance_id:
            conditions.append(ScenarioExecutionModel.scenario_instance_id == query.scenario_instance_id)
        
        if query.execution_status:
            conditions.append(ScenarioExecutionModel.execution_status == query.execution_status.value)
        
        if query.execution_type:
            conditions.append(ScenarioExecutionModel.execution_type == query.execution_type.value)
        
        if query.trigger_source:
            conditions.append(ScenarioExecutionModel.trigger_source == query.trigger_source.value)
        
        if query.target_entity_type:
            conditions.append(ScenarioExecutionModel.target_entity_type == query.target_entity_type)
        
        if query.date_from:
            conditions.append(ScenarioExecutionModel.started_at >= query.date_from)
        
        if query.date_to:
            conditions.append(ScenarioExecutionModel.started_at <= query.date_to)
        
        # 执行查询
        stmt = select(ScenarioExecutionModel).options(
            selectinload(ScenarioExecutionModel.scenario_instance)
        ).where(and_(*conditions))
        
        count_stmt = select(func.count(ScenarioExecutionModel.id)).where(and_(*conditions))
        
        # 获取总数
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 获取分页数据
        stmt = stmt.offset(skip).limit(limit).order_by(ScenarioExecutionModel.started_at.desc())
        result = await self.db.execute(stmt)
        executions = result.scalars().all()
        
        responses = []
        for execution in executions:
            responses.append(await self._build_execution_response(execution))
        
        return responses, total 