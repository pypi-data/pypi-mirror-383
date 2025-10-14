"""API数据模型"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """PDF生成请求模型"""
    config: Dict[str, Any] = Field(..., description="PDF配置（JSON格式）")
    data: Optional[Dict[str, Any]] = Field(None, description="可选的数据字典")
    output_filename: Optional[str] = Field("report.pdf", description="输出文件名")


class GenerateResponse(BaseModel):
    """PDF生成响应模型"""
    success: bool
    message: str
    filename: Optional[str] = None


class ConfigValidationRequest(BaseModel):
    """配置验证请求模型"""
    config: Dict[str, Any]


class ConfigValidationResponse(BaseModel):
    """配置验证响应模型"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class DataSourceSummary(BaseModel):
    """数据源摘要"""
    name: str
    rows: int
    columns: List[str]
    dtypes: Dict[str, str]


class StatusResponse(BaseModel):
    """服务状态响应"""
    status: str
    version: str
    message: str

