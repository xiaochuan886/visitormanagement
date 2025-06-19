"""
API响应基础模型
"""
from typing import Generic, TypeVar, Optional, Any, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")


class DataResponse(BaseResponse, Generic[T]):
    """数据响应模型"""
    data: T = Field(..., description="响应数据")


class ListResponse(BaseResponse, Generic[T]):
    """列表响应模型"""
    data: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")


class PaginatedResponse(BaseResponse, Generic[T]):
    """分页响应模型"""
    data: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码", ge=1)
    page_size: int = Field(..., description="每页记录数", ge=1, le=1000)
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")

    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        page_size: int,
        message: str = "获取数据成功"
    ) -> "PaginatedResponse[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            message=message
        )


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = Field(False, description="操作失败")
    error_code: Optional[str] = Field(None, description="错误代码")
    error_details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    
    def __init__(self, message: str, error_code: str = None, error_details: Dict[str, Any] = None, **kwargs):
        super().__init__(
            success=False,
            message=message,
            error_code=error_code,
            error_details=error_details,
            **kwargs
        )


class ValidationErrorResponse(ErrorResponse):
    """验证错误响应模型"""
    validation_errors: List[Dict[str, Any]] = Field(..., description="验证错误详情")


class OperationResponse(BaseResponse):
    """操作响应模型（无数据返回）"""
    affected_count: Optional[int] = Field(None, description="影响的记录数")


class BatchOperationResponse(BaseResponse):
    """批量操作响应模型"""
    total_count: int = Field(..., description="总操作数")
    success_count: int = Field(..., description="成功数")
    failed_count: int = Field(..., description="失败数")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")


class AnalyticsResponse(BaseResponse):
    """分析数据响应模型"""
    data: Dict[str, Any] = Field(..., description="分析数据")
    period: str = Field(..., description="统计周期")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")


class ExportResponse(BaseResponse):
    """导出响应模型"""
    download_url: str = Field(..., description="下载链接")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    expires_at: datetime = Field(..., description="链接过期时间")


class ImportResponse(BaseResponse):
    """导入响应模型"""
    import_id: str = Field(..., description="导入任务ID")
    total_records: int = Field(..., description="总记录数")
    processed_records: int = Field(0, description="已处理记录数")
    success_records: int = Field(0, description="成功记录数")
    failed_records: int = Field(0, description="失败记录数")
    status: str = Field("processing", description="导入状态")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误详情")


# 状态码定义
class StatusCodes:
    """HTTP状态码定义"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


# 错误代码定义
class ErrorCodes:
    """业务错误代码定义"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # 场景管理相关错误
    SCENARIO_TEMPLATE_NOT_FOUND = "SCENARIO_TEMPLATE_NOT_FOUND"
    SCENARIO_INSTANCE_NOT_FOUND = "SCENARIO_INSTANCE_NOT_FOUND"
    SCENARIO_EXECUTION_FAILED = "SCENARIO_EXECUTION_FAILED"
    SCENARIO_ROUTING_FAILED = "SCENARIO_ROUTING_FAILED"
    SCENARIO_CONFIG_INVALID = "SCENARIO_CONFIG_INVALID" 