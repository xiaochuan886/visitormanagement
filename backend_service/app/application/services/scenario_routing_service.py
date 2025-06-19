"""
场景路由服务 - 智能场景路由和自动化场景匹配
"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, text
from sqlalchemy.orm import selectinload

from ..dto.scenario_dto import (
    ScenarioRoutingRuleCreateDTO, ScenarioRoutingRuleUpdateDTO, ScenarioRoutingRuleResponseDTO,
    ScenarioInstanceResponseDTO, ScenarioExecutionCreateDTO, ScenarioExecutionResponseDTO,
    ScenarioInstanceStatus, TriggerSource
)
from ...infrastructure.database.models import (
    ScenarioInstanceModel, ScenarioRoutingRuleModel, ScenarioExecutionModel,
    ScenarioTemplateModel, VisitorModel, EmployeeModel
)
from ...domain.exceptions.config_exceptions import (
    ConfigurationNotFoundError, ConfigurationValidationError
)
from .scenario_service import ScenarioInstanceService
from .scenario_execution_service import ScenarioExecutionService

logger = logging.getLogger(__name__)


class ScenarioRoutingService:
    """场景路由服务 - 智能路由核心引擎"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.instance_service = ScenarioInstanceService(db_session)
        self.execution_service = ScenarioExecutionService(db_session)
    
    async def route_scenario(
        self,
        context: Dict[str, Any],
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        tenant_id: str = "default"
    ) -> List[ScenarioInstanceResponseDTO]:
        """
        智能场景路由 - 根据上下文自动匹配合适的场景
        
        Args:
            context: 路由上下文数据
            entity_type: 实体类型 (visitor, employee, event, etc.)
            entity_id: 实体ID
            user_id: 触发用户ID
            tenant_id: 租户ID
            
        Returns:
            匹配的场景实例列表
        """
        try:
            logger.info(f"开始场景路由: entity_type={entity_type}, entity_id={entity_id}")
            
            # 1. 获取激活的路由规则（按优先级排序）
            routing_rules = await self._get_active_routing_rules(tenant_id)
            
            if not routing_rules:
                logger.warning("没有找到激活的路由规则")
                return []
            
            # 2. 增强上下文信息
            enhanced_context = await self._enhance_context(context, entity_type, entity_id, tenant_id)
            
            # 3. 执行规则匹配
            matched_scenarios = []
            for rule in routing_rules:
                try:
                    is_match = await self._evaluate_rule_conditions(rule, enhanced_context)
                    
                    if is_match:
                        # 更新规则匹配统计
                        await self._update_rule_statistics(rule.id, True)
                        
                        # 获取目标场景
                        target_scenarios = await self._get_target_scenarios(
                            rule.target_scenario_ids, tenant_id
                        )
                        
                        for scenario in target_scenarios:
                            if await self._is_scenario_applicable(scenario, enhanced_context):
                                matched_scenarios.append(scenario)
                        
                        # 根据匹配策略决定是否继续
                        if rule.match_strategy == "first_match" and matched_scenarios:
                            break
                        elif rule.match_strategy == "best_match":
                            # 继续评估其他规则，最后选择最佳匹配
                            continue
                
                except Exception as e:
                    logger.error(f"规则评估失败: rule_id={rule.id}, error={str(e)}")
                    await self._update_rule_statistics(rule.id, False)
                    continue
            
            # 4. 去重和优先级排序
            unique_scenarios = self._deduplicate_scenarios(matched_scenarios)
            sorted_scenarios = self._sort_scenarios_by_priority(unique_scenarios)
            
            logger.info(f"场景路由完成: 匹配到 {len(sorted_scenarios)} 个场景")
            
            return sorted_scenarios
            
        except Exception as e:
            logger.error(f"场景路由失败: {str(e)}")
            raise
    
    async def _get_active_routing_rules(self, tenant_id: str) -> List[ScenarioRoutingRuleModel]:
        """获取激活的路由规则（按优先级排序）"""
        now = datetime.utcnow()
        
        stmt = select(ScenarioRoutingRuleModel).where(
            and_(
                ScenarioRoutingRuleModel.tenant_id == tenant_id,
                ScenarioRoutingRuleModel.is_active == True,
                ScenarioRoutingRuleModel.is_deleted == False,
                or_(
                    ScenarioRoutingRuleModel.effective_from.is_(None),
                    ScenarioRoutingRuleModel.effective_from <= now
                ),
                or_(
                    ScenarioRoutingRuleModel.effective_until.is_(None),
                    ScenarioRoutingRuleModel.effective_until > now
                )
            )
        ).order_by(ScenarioRoutingRuleModel.rule_priority.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _enhance_context(
        self, 
        context: Dict[str, Any], 
        entity_type: str, 
        entity_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """增强上下文信息 - 加载相关实体数据"""
        enhanced = context.copy()
        enhanced.update({
            "entity_type": entity_type,
            "entity_id": entity_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "weekday": datetime.utcnow().weekday(),
            "hour": datetime.utcnow().hour
        })
        
        try:
            # 根据实体类型加载相关数据
            if entity_type == "visitor":
                visitor_data = await self._load_visitor_data(entity_id, tenant_id)
                if visitor_data:
                    enhanced["visitor"] = visitor_data
                    enhanced["company_name"] = visitor_data.get("company_name")
                    enhanced["purpose"] = visitor_data.get("purpose")
                    enhanced["employee_id"] = visitor_data.get("employee_id")
                    
                    # 加载被访员工信息
                    if visitor_data.get("employee_id"):
                        employee_data = await self._load_employee_data(
                            visitor_data["employee_id"], tenant_id
                        )
                        if employee_data:
                            enhanced["employee"] = employee_data
                            enhanced["department_id"] = employee_data.get("department_id")
            
            elif entity_type == "employee":
                employee_data = await self._load_employee_data(entity_id, tenant_id)
                if employee_data:
                    enhanced["employee"] = employee_data
                    enhanced["department_id"] = employee_data.get("department_id")
                    enhanced["designation_id"] = employee_data.get("designation_id")
            
            logger.debug(f"上下文增强完成: {len(enhanced)} 个字段")
            
        except Exception as e:
            logger.warning(f"上下文增强失败: {str(e)}")
            # 增强失败不影响主流程
        
        return enhanced
    
    async def _load_visitor_data(self, visitor_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """加载访客数据"""
        try:
            stmt = select(VisitorModel).where(
                and_(
                    VisitorModel.id == int(visitor_id),
                    VisitorModel.tenant_id == tenant_id,
                    VisitorModel.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            visitor = result.scalar_one_or_none()
            
            if visitor:
                return {
                    "id": visitor.id,
                    "name": visitor.name,
                    "email": visitor.email,
                    "phone_number": visitor.phone_number,
                    "company_name": visitor.company_name,
                    "purpose": visitor.purpose,
                    "status": visitor.status,
                    "employee_id": visitor.employee_id,
                    "expected_date": visitor.expected_date.isoformat() if visitor.expected_date else None
                }
            
        except Exception as e:
            logger.error(f"加载访客数据失败: {str(e)}")
        
        return None
    
    async def _load_employee_data(self, employee_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """加载员工数据"""
        try:
            stmt = select(EmployeeModel).where(
                and_(
                    EmployeeModel.id == int(employee_id),
                    EmployeeModel.tenant_id == tenant_id,
                    EmployeeModel.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            employee = result.scalar_one_or_none()
            
            if employee:
                return {
                    "id": employee.id,
                    "name": employee.name,
                    "employee_id": employee.employee_id,
                    "email": employee.email,
                    "department_id": employee.department_id,
                    "designation_id": employee.designation_id,
                    "position": employee.position,
                    "status": employee.status
                }
            
        except Exception as e:
            logger.error(f"加载员工数据失败: {str(e)}")
        
        return None
    
    async def _evaluate_rule_conditions(
        self, 
        rule: ScenarioRoutingRuleModel, 
        context: Dict[str, Any]
    ) -> bool:
        """评估规则条件"""
        try:
            conditions = rule.rule_conditions
            
            if not conditions or not isinstance(conditions, dict):
                logger.warning(f"规则条件格式错误: rule_id={rule.id}")
                return False
            
            # 支持的条件操作符
            operators = {
                "eq": lambda a, b: a == b,
                "ne": lambda a, b: a != b,
                "gt": lambda a, b: a > b,
                "gte": lambda a, b: a >= b,
                "lt": lambda a, b: a < b,
                "lte": lambda a, b: a <= b,
                "in": lambda a, b: a in b if isinstance(b, list) else False,
                "not_in": lambda a, b: a not in b if isinstance(b, list) else True,
                "contains": lambda a, b: b in str(a),
                "not_contains": lambda a, b: b not in str(a),
                "starts_with": lambda a, b: str(a).startswith(str(b)),
                "ends_with": lambda a, b: str(a).endswith(str(b)),
                "is_null": lambda a, b: a is None,
                "is_not_null": lambda a, b: a is not None,
                "match_regex": lambda a, b: self._match_regex(str(a), str(b))
            }
            
            # 评估条件组
            condition_results = []
            
            for condition_group in conditions.get("conditions", []):
                if not isinstance(condition_group, dict):
                    continue
                
                field = condition_group.get("field")
                operator = condition_group.get("operator")
                value = condition_group.get("value")
                
                if not field or not operator:
                    continue
                
                # 从上下文获取字段值（支持嵌套字段）
                field_value = self._get_nested_value(context, field)
                
                # 执行条件判断
                if operator in operators:
                    try:
                        result = operators[operator](field_value, value)
                        condition_results.append(result)
                    except Exception as e:
                        logger.warning(f"条件评估失败: field={field}, operator={operator}, error={str(e)}")
                        condition_results.append(False)
                else:
                    logger.warning(f"不支持的操作符: {operator}")
                    condition_results.append(False)
            
            # 根据逻辑操作符合并结果
            if rule.condition_logic == "OR":
                return any(condition_results) if condition_results else False
            else:  # AND
                return all(condition_results) if condition_results else False
            
        except Exception as e:
            logger.error(f"规则条件评估失败: rule_id={rule.id}, error={str(e)}")
            return False
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """获取嵌套字段值（支持点号分隔的路径）"""
        try:
            keys = field_path.split(".")
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _match_regex(self, text: str, pattern: str) -> bool:
        """正则表达式匹配"""
        try:
            import re
            return bool(re.search(pattern, text))
        except Exception:
            return False
    
    async def _update_rule_statistics(self, rule_id: UUID, success: bool) -> None:
        """更新规则统计信息"""
        try:
            if success:
                stmt = update(ScenarioRoutingRuleModel).where(
                    ScenarioRoutingRuleModel.id == rule_id
                ).values(
                    matched_count=ScenarioRoutingRuleModel.matched_count + 1,
                    success_count=ScenarioRoutingRuleModel.success_count + 1,
                    last_matched_at=datetime.utcnow()
                )
            else:
                stmt = update(ScenarioRoutingRuleModel).where(
                    ScenarioRoutingRuleModel.id == rule_id
                ).values(
                    matched_count=ScenarioRoutingRuleModel.matched_count + 1
                )
            
            await self.db.execute(stmt)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"更新规则统计失败: {str(e)}")
            # 统计更新失败不影响主流程
    
    async def _get_target_scenarios(
        self, 
        scenario_ids: List[str], 
        tenant_id: str
    ) -> List[ScenarioInstanceResponseDTO]:
        """获取目标场景实例"""
        try:
            # 转换字符串ID到UUID
            uuid_ids = []
            for sid in scenario_ids:
                try:
                    uuid_ids.append(UUID(sid))
                except ValueError:
                    logger.warning(f"无效的场景ID: {sid}")
                    continue
            
            if not uuid_ids:
                return []
            
            stmt = select(ScenarioInstanceModel).options(
                selectinload(ScenarioInstanceModel.scenario_template)
            ).where(
                and_(
                    ScenarioInstanceModel.id.in_(uuid_ids),
                    ScenarioInstanceModel.tenant_id == tenant_id,
                    ScenarioInstanceModel.instance_status == ScenarioInstanceStatus.ACTIVE.value,
                    ScenarioInstanceModel.is_deleted == False
                )
            )
            
            result = await self.db.execute(stmt)
            instances = result.scalars().all()
            
            scenarios = []
            for instance in instances:
                response = await self.instance_service._build_instance_response(instance)
                scenarios.append(response)
            
            return scenarios
            
        except Exception as e:
            logger.error(f"获取目标场景失败: {str(e)}")
            return []
    
    async def _is_scenario_applicable(
        self, 
        scenario: ScenarioInstanceResponseDTO, 
        context: Dict[str, Any]
    ) -> bool:
        """检查场景是否适用于当前上下文"""
        try:
            now = datetime.utcnow()
            
            # 检查时间有效性
            if scenario.effective_from and scenario.effective_from > now:
                return False
            
            if scenario.effective_until and scenario.effective_until < now:
                return False
            
            # 检查站点适用性
            if scenario.applicable_sites:
                site_id = context.get("site_id")
                if site_id and str(site_id) not in scenario.applicable_sites:
                    return False
            
            # 检查部门适用性
            if scenario.applicable_departments:
                dept_id = context.get("department_id")
                if dept_id and str(dept_id) not in scenario.applicable_departments:
                    return False
            
            # 检查角色适用性
            if scenario.applicable_roles:
                user_role = context.get("user_role")
                if user_role and user_role not in scenario.applicable_roles:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"场景适用性检查失败: {str(e)}")
            return False
    
    def _deduplicate_scenarios(
        self, 
        scenarios: List[ScenarioInstanceResponseDTO]
    ) -> List[ScenarioInstanceResponseDTO]:
        """去重场景实例"""
        seen = set()
        unique_scenarios = []
        
        for scenario in scenarios:
            if scenario.id not in seen:
                seen.add(scenario.id)
                unique_scenarios.append(scenario)
        
        return unique_scenarios
    
    def _sort_scenarios_by_priority(
        self, 
        scenarios: List[ScenarioInstanceResponseDTO]
    ) -> List[ScenarioInstanceResponseDTO]:
        """按优先级排序场景"""
        return sorted(scenarios, key=lambda s: s.priority_level, reverse=True)
    
    async def execute_matched_scenarios(
        self,
        scenarios: List[ScenarioInstanceResponseDTO],
        context: Dict[str, Any],
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        tenant_id: str = "default"
    ) -> List[ScenarioExecutionResponseDTO]:
        """执行匹配的场景"""
        executions = []
        
        for scenario in scenarios:
            try:
                # 创建场景执行
                execution_data = ScenarioExecutionCreateDTO(
                    scenario_instance_id=scenario.id,
                    execution_type="triggered",
                    trigger_source=TriggerSource.SYSTEM,
                    trigger_user_id=user_id,
                    trigger_context=context,
                    target_entity_type=entity_type,
                    target_entity_id=entity_id
                )
                
                execution = await self.execution_service.create_execution(
                    execution_data, user_id or "system", tenant_id
                )
                
                executions.append(execution)
                
                logger.info(f"启动场景执行: scenario_id={scenario.id}, execution_id={execution.id}")
                
            except Exception as e:
                logger.error(f"场景执行失败: scenario_id={scenario.id}, error={str(e)}")
                continue
        
        return executions
    
    # ================== 路由规则管理 ==================
    
    async def create_routing_rule(
        self,
        rule_data: ScenarioRoutingRuleCreateDTO,
        created_by: str,
        tenant_id: str
    ) -> ScenarioRoutingRuleResponseDTO:
        """创建路由规则"""
        try:
            # 验证目标场景存在
            await self._validate_target_scenarios(rule_data.target_scenario_ids, tenant_id)
            
            rule = ScenarioRoutingRuleModel(
                rule_name=rule_data.rule_name,
                rule_description=rule_data.rule_description,
                rule_priority=rule_data.rule_priority,
                rule_conditions=rule_data.rule_conditions,
                target_scenario_ids=[str(sid) for sid in rule_data.target_scenario_ids],
                condition_logic=rule_data.condition_logic,
                match_strategy=rule_data.match_strategy,
                effective_from=rule_data.effective_from,
                effective_until=rule_data.effective_until,
                created_by=created_by,
                updated_by=created_by,
                tenant_id=tenant_id
            )
            
            self.db.add(rule)
            await self.db.commit()
            await self.db.refresh(rule)
            
            logger.info(f"创建路由规则成功: {rule.rule_name} (ID: {rule.id})")
            return ScenarioRoutingRuleResponseDTO.from_orm(rule)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建路由规则失败: {str(e)}")
            raise
    
    async def _validate_target_scenarios(self, scenario_ids: List[UUID], tenant_id: str) -> None:
        """验证目标场景存在且有效"""
        stmt = select(func.count(ScenarioInstanceModel.id)).where(
            and_(
                ScenarioInstanceModel.id.in_(scenario_ids),
                ScenarioInstanceModel.tenant_id == tenant_id,
                ScenarioInstanceModel.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar()
        
        if count != len(scenario_ids):
            raise ConfigurationValidationError("存在无效的目标场景ID") 