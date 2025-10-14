"""API路由"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
import json
import io

from pdf_generator import PDFReportGenerator
from pdf_generator.config.validator import ConfigValidator
from api.models import (
    GenerateRequest,
    GenerateResponse,
    ConfigValidationRequest,
    ConfigValidationResponse,
    StatusResponse,
)

router = APIRouter()


@router.get("/", response_model=StatusResponse)
async def root():
    """API根路径"""
    return StatusResponse(
        status="running",
        version="0.1.0",
        message="PDF Report Generator API is running"
    )


@router.post("/api/generate")
async def generate_pdf_json(request: GenerateRequest):
    """
    从JSON配置生成PDF
    
    接受JSON格式的配置和数据，返回PDF文件流
    """
    try:
        # 创建生成器
        generator = PDFReportGenerator(config_dict=request.config)
        
        # 添加额外数据源（如果提供）
        if request.data:
            for name, data in request.data.items():
                generator.add_data_source(name, data)
        
        # 生成PDF
        pdf_bytes = generator.to_bytes()
        
        # 返回PDF文件流
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.output_filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF generation failed: {str(e)}")


@router.post("/api/generate/upload")
async def generate_pdf_upload(
    config: UploadFile = File(..., description="JSON配置文件"),
    data: UploadFile = File(None, description="可选的数据文件（CSV/JSON/Excel）"),
):
    """
    通过文件上传生成PDF
    
    上传配置文件和可选的数据文件，返回PDF
    """
    try:
        # 读取配置文件
        config_content = await config.read()
        config_dict = json.loads(config_content.decode('utf-8'))
        
        # 创建生成器
        generator = PDFReportGenerator(config_dict=config_dict)
        
        # 如果提供了数据文件，添加为数据源
        if data:
            data_content = await data.read()
            data_filename = data.filename
            
            # 根据文件类型处理
            if data_filename.endswith('.json'):
                data_dict = json.loads(data_content.decode('utf-8'))
                generator.add_data_source('uploaded_data', data_dict)
            elif data_filename.endswith('.csv'):
                import pandas as pd
                df = pd.read_csv(io.BytesIO(data_content))
                generator.add_data_source('uploaded_data', df)
            elif data_filename.endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(io.BytesIO(data_content))
                generator.add_data_source('uploaded_data', df)
        
        # 生成PDF
        pdf_bytes = generator.to_bytes()
        
        # 返回PDF
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=report.pdf"
            }
        )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON configuration file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF generation failed: {str(e)}")


@router.post("/api/validate", response_model=ConfigValidationResponse)
async def validate_config(request: ConfigValidationRequest):
    """
    验证PDF配置
    
    检查配置是否有效，返回错误和警告信息
    """
    try:
        validator = ConfigValidator()
        is_valid = validator.validate(request.config)
        
        return ConfigValidationResponse(
            valid=is_valid,
            errors=validator.get_errors(),
            warnings=validator.get_warnings()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


@router.get("/api/templates")
async def list_templates():
    """
    列出可用的模板
    
    返回预定义的配置模板列表
    """
    # 这里可以返回预定义的模板
    templates = {
        "simple_report": {
            "name": "Simple Report",
            "description": "A basic report template with text and tables",
        },
        "sales_report": {
            "name": "Sales Report",
            "description": "Sales analysis report with charts and tables",
        },
        "financial_report": {
            "name": "Financial Report",
            "description": "Financial report with complex layouts",
        },
    }
    
    return templates


@router.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

