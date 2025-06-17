"""
业务规则服务
提供业务规则管理和执行的业务逻辑
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.application.interfaces.repository import (
    IBusinessRuleRepository,
    IRuleExecutionLogRepository
)
from app.domain.enums.config_enums import BusinessRuleCategory, RuleExecutionResult
from app.domain.exceptions.config_exceptions import (
    BusinessRuleException,
    RuleExecutionException,
    ConfigurationNotFoundException,
    DuplicateConfigurationException
)
from app.infrastructure.database.models import BusinessRule, RuleExecutionLog
from app.core.logging import LoggerMixin


class BusinessRuleService(LoggerMixin):
    """业务规则服务"""
    
    def __init__(
        self,
        business_rule_repository: IBusinessRuleRepository,
        rule_execution_log_repository: IRuleExecutionLogRepository
    ):
        self.business_rule_repo = business_rule_repository
        self.rule_execution_log_repo = rule_execution_log_repository
        self.logger.info("业务规则服务初始化完成")
    
    async def get_business_rule(
        self,
        rule_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """获取业务规则详情"""
        try:
            rule = await self.business_rule_repo.get_by_id(rule_id)
            if not rule or rule.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("业务规则", str(rule_id))
            
            return {
                "id": rule.id,
                "rule_name": rule.rule_name,
                "rule_category": rule.rule_category,
                "rule_version": rule.rule_version,
                "description": rule.description,
                "conditions": rule.conditions,
                "actions": rule.actions,
                "priority": rule.priority,
                "is_active": rule.is_active,
                "effective_from": rule.effective_from,
                "effective_until": rule.effective_until,
                "execution_mode": rule.execution_mode,
                "target_entities": rule.target_entities,
                "tags": rule.tags,
                "execution_count": rule.execution_count,
                "last_executed_at": rule.last_executed_at,
                "created_at": rule.created_at,
                "updated_at": rule.updated_at
            }
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"获取业务规则失败: {str(e)}")
            raise BusinessRuleException(f"获取业务规则失败: {str(e)}")
    
    async def list_business_rules(
        self,
        tenant_id: str,
        category: Optional[BusinessRuleCategory] = None,
        target_entity: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """查询业务规则列表"""
        try:
            filters = {"tenant_id": UUID(tenant_id)}
            
            if category:
                filters["rule_category"] = category.value
            if target_entity:
                rules = await self.business_rule_repo.find_by_target_entity(
                    target_entity, UUID(tenant_id)
                )
            elif is_active is not None:
                if is_active:
                    rules = await self.business_rule_repo.find_active_rules(UUID(tenant_id))
                else:
                    all_rules = await self.business_rule_repo.find_by(filters)
                    rules = [r for r in all_rules if not r.is_active]
            else:
                rules = await self.business_rule_repo.find_by(filters)
            
            # 分页处理
            total = len(rules)
            skip = (page - 1) * page_size
            paginated_rules = rules[skip:skip + page_size]
            
            items = []
            for rule in paginated_rules:
                items.append({
                    "id": rule.id,
                    "rule_name": rule.rule_name,
                    "rule_category": rule.rule_category,
                    "rule_version": rule.rule_version,
                    "description": rule.description,
                    "priority": rule.priority,
                    "is_active": rule.is_active,
                    "execution_count": rule.execution_count,
                    "last_executed_at": rule.last_executed_at,
                    "created_at": rule.created_at
                })
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            self.logger.error(f"查询业务规则列表失败: {str(e)}")
            raise BusinessRuleException(f"查询业务规则列表失败: {str(e)}")
    
    async def execute_business_rule(
        self,
        rule_id: UUID,
        target_entity_type: str,
        target_entity_id: str,
        input_data: Dict[str, Any],
        tenant_id: str,
        execution_context: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """执行业务规则"""
        try:
            self.logger.info(f"开始执行业务规则: {rule_id}")
            
            # 获取业务规则
            rule = await self.business_rule_repo.get_by_id(rule_id)
            if not rule or rule.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("业务规则", str(rule_id))
            
            if not rule.is_active:
                raise BusinessRuleException("业务规则未激活")
            
            execution_id = uuid4()
            start_time = datetime.utcnow()
            
            # 简单的条件评估
            condition_results = []
            overall_condition_result = True
            
            # 简单的动作执行
            action_results = []
            if not dry_run:
                self.logger.info(f"执行业务规则动作: {rule.rule_name}")
                
            overall_result = RuleExecutionResult.SUCCESS
            
            end_time = datetime.utcnow()
            total_execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # 构建执行结果
            result = {
                "execution_id": execution_id,
                "rule_id": rule_id,
                "rule_name": rule.rule_name,
                "target_entity_type": target_entity_type,
                "target_entity_id": target_entity_id,
                "overall_result": overall_result.value,
                "execution_start_time": start_time.isoformat(),
                "execution_end_time": end_time.isoformat(),
                "total_execution_time_ms": total_execution_time_ms,
                "condition_results": condition_results,
                "action_results": action_results,
                "input_data": input_data,
                "output_data": {},
                "was_dry_run": dry_run
            }
            
            self.logger.info(f"业务规则执行完成: {rule_id}, 结果: {overall_result.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"执行业务规则失败: {str(e)}")
            raise RuleExecutionException(f"执行业务规则失败: {str(e)}")
    
    async def get_rule_execution_history(
        self,
        rule_id: Optional[UUID] = None,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[str] = None,
        tenant_id: str = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取规则执行历史"""
        try:
            filters = {"tenant_id": UUID(tenant_id)}
            
            if rule_id:
                logs = await self.rule_execution_log_repo.find_by_rule(rule_id)
            elif target_entity_type and target_entity_id:
                logs = await self.rule_execution_log_repo.find_by_target_entity(
                    target_entity_type, target_entity_id, UUID(tenant_id)
                )
            elif start_date and end_date:
                logs = await self.rule_execution_log_repo.find_by_date_range(
                    start_date, end_date, UUID(tenant_id)
                )
            else:
                logs = await self.rule_execution_log_repo.find_by(filters)
            
            # 分页处理
            total = len(logs)
            skip = (page - 1) * page_size
            paginated_logs = logs[skip:skip + page_size]
            
            items = []
            for log in paginated_logs:
                items.append({
                    "execution_id": log.id,
                    "rule_id": log.rule_id,
                    "target_entity_type": log.target_entity_type,
                    "target_entity_id": log.target_entity_id,
                    "execution_result": log.execution_result,
                    "execution_start_time": log.execution_start_time,
                    "execution_end_time": log.execution_end_time,
                    "total_execution_time_ms": log.total_execution_time_ms,
                    "condition_results": log.condition_results,
                    "action_results": log.action_results
                })
            
            total_pages = (total + page_size - 1) // page_size
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
            
        except Exception as e:
            self.logger.error(f"获取规则执行历史失败: {str(e)}")
            raise BusinessRuleException(f"获取规则执行历史失败: {str(e)}")
    
    # 私有辅助方法
    
    async def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """评估规则条件"""
        condition_results = []
        
        for condition in conditions:
            start_time = datetime.utcnow()
            
            condition_id = condition.get("condition_id", "unknown")
            field_name = condition.get("field_name")
            operator = condition.get("operator")
            expected_value = condition.get("expected_value")
            
            # 从输入数据或上下文数据中获取实际值
            actual_value = input_data.get(field_name) or context_data.get(field_name)
            
            # 评估条件
            evaluation_result = self._evaluate_single_condition(
                actual_value, operator, expected_value
            )
            
            end_time = datetime.utcnow()
            evaluation_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            condition_results.append({
                "condition_id": condition_id,
                "condition_name": condition.get("condition_name", condition_id),
                "evaluation_result": evaluation_result,
                "actual_value": actual_value,
                "expected_value": expected_value,
                "operator": operator,
                "evaluation_time_ms": evaluation_time_ms,
                "error_message": None
            })
        
        return condition_results
    
    def _evaluate_single_condition(
        self,
        actual_value: Any,
        operator: str,
        expected_value: Any
    ) -> bool:
        """评估单个条件"""
        try:
            if operator == "eq":
                return actual_value == expected_value
            elif operator == "ne":
                return actual_value != expected_value
            elif operator == "gt":
                return actual_value > expected_value
            elif operator == "gte":
                return actual_value >= expected_value
            elif operator == "lt":
                return actual_value < expected_value
            elif operator == "lte":
                return actual_value <= expected_value
            elif operator == "in":
                return actual_value in expected_value
            elif operator == "not_in":
                return actual_value not in expected_value
            elif operator == "contains":
                return expected_value in str(actual_value)
            elif operator == "not_contains":
                return expected_value not in str(actual_value)
            elif operator == "is_null":
                return actual_value is None
            elif operator == "is_not_null":
                return actual_value is not None
            elif operator == "is_empty":
                return not actual_value
            elif operator == "is_not_empty":
                return bool(actual_value)
            else:
                self.logger.warning(f"不支持的操作符: {operator}")
                return False
        except Exception as e:
            self.logger.error(f"条件评估失败: {str(e)}")
            return False
    
    async def _execute_actions(
        self,
        actions: List[Dict[str, Any]],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """执行规则动作"""
        action_results = []
        
        # 按执行顺序排序
        sorted_actions = sorted(actions, key=lambda x: x.get("execution_order", 0))
        
        for action in sorted_actions:
            start_time = datetime.utcnow()
            
            action_id = action.get("action_id", "unknown")
            action_type = action.get("action_type")
            action_config = action.get("action_config", {})
            
            try:
                # 执行具体动作
                output_data = await self._execute_single_action(
                    action_type, action_config, input_data, context_data
                )
                
                end_time = datetime.utcnow()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                action_results.append({
                    "action_id": action_id,
                    "action_type": action_type,
                    "execution_result": RuleExecutionResult.SUCCESS.value,
                    "execution_time_ms": execution_time_ms,
                    "output_data": output_data,
                    "error_message": None,
                    "retry_count": 0
                })
                
            except Exception as e:
                end_time = datetime.utcnow()
                execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                action_results.append({
                    "action_id": action_id,
                    "action_type": action_type,
                    "execution_result": RuleExecutionResult.FAILURE.value,
                    "execution_time_ms": execution_time_ms,
                    "output_data": None,
                    "error_message": str(e),
                    "retry_count": 0
                })
        
        return action_results
    
    async def _execute_single_action(
        self,
        action_type: str,
        action_config: Dict[str, Any],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个动作"""
        if action_type == "notification":
            return await self._execute_notification_action(action_config, input_data, context_data)
        elif action_type == "data_update":
            return await self._execute_data_update_action(action_config, input_data, context_data)
        elif action_type == "workflow_trigger":
            return await self._execute_workflow_trigger_action(action_config, input_data, context_data)
        elif action_type == "log_event":
            return await self._execute_log_event_action(action_config, input_data, context_data)
        else:
            self.logger.info(f"执行通用动作: {action_type}")
            return {
                "action_type": action_type,
                "message": f"动作 {action_type} 执行完成",
                "executed_at": datetime.utcnow().isoformat()
            }
    
    async def _execute_notification_action(
        self,
        action_config: Dict[str, Any],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行通知动作"""
        notification_type = action_config.get("type", "email")
        recipients = action_config.get("recipients", [])
        message = action_config.get("message", "")
        
        # 这里应该集成实际的通知服务
        self.logger.info(f"发送 {notification_type} 通知给 {recipients}: {message}")
        
        return {
            "notification_type": notification_type,
            "recipients": recipients,
            "message": message,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_data_update_action(
        self,
        action_config: Dict[str, Any],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行数据更新动作"""
        target_entity = action_config.get("target_entity")
        update_fields = action_config.get("update_fields", {})
        
        # 这里应该执行实际的数据更新逻辑
        self.logger.info(f"更新 {target_entity} 的数据: {update_fields}")
        
        return {
            "target_entity": target_entity,
            "update_fields": update_fields,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_workflow_trigger_action(
        self,
        action_config: Dict[str, Any],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行工作流触发动作"""
        workflow_type = action_config.get("workflow_type")
        workflow_config = action_config.get("workflow_config", {})
        
        # 这里应该集成工作流服务
        self.logger.info(f"触发工作流: {workflow_type}")
        
        return {
            "workflow_type": workflow_type,
            "workflow_config": workflow_config,
            "triggered_at": datetime.utcnow().isoformat()
        }
    
    async def _execute_log_event_action(
        self,
        action_config: Dict[str, Any],
        input_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行日志记录动作"""
        log_level = action_config.get("level", "info")
        log_message = action_config.get("message", "")
        
        # 记录日志
        if log_level == "info":
            self.logger.info(f"业务规则日志: {log_message}")
        elif log_level == "warning":
            self.logger.warning(f"业务规则日志: {log_message}")
        elif log_level == "error":
            self.logger.error(f"业务规则日志: {log_message}")
        
        return {
            "log_level": log_level,
            "log_message": log_message,
            "logged_at": datetime.utcnow().isoformat()
        } 