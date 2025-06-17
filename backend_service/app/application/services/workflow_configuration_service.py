"""
工作流配置服务
提供工作流配置管理和执行的业务逻辑
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.application.interfaces.repository import (
    IWorkflowConfigurationRepository,
    IWorkflowExecutionRepository
)
from app.domain.exceptions.config_exceptions import (
    WorkflowConfigurationException,
    ConfigurationNotFoundException,
    DuplicateConfigurationException
)
from app.infrastructure.database.models import WorkflowConfiguration
from app.core.logging import LoggerMixin


class WorkflowConfigurationService(LoggerMixin):
    """工作流配置服务"""
    
    def __init__(
        self,
        workflow_config_repository: IWorkflowConfigurationRepository,
        workflow_execution_repository: IWorkflowExecutionRepository
    ):
        self.workflow_config_repo = workflow_config_repository
        self.workflow_execution_repo = workflow_execution_repository
        self.logger.info("工作流配置服务初始化完成")
    
    async def get_workflow_configuration(
        self,
        config_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """获取工作流配置详情"""
        try:
            config = await self.workflow_config_repo.get_by_id(config_id)
            if not config or config.tenant_id != tenant_id:
                raise ConfigurationNotFoundException("工作流配置", str(config_id))
            
            return {
                "id": config.id,
                "workflow_name": config.workflow_name,
                "workflow_type": config.workflow_type,
                "workflow_version": config.workflow_version,
                "description": config.description,
                "is_active": config.is_active,
                "created_at": config.created_at,
                "updated_at": config.updated_at
            }
            
        except ConfigurationNotFoundException:
            raise
        except Exception as e:
            self.logger.error(f"获取工作流配置失败: {str(e)}")
            raise WorkflowConfigurationException(f"获取工作流配置失败: {str(e)}") 