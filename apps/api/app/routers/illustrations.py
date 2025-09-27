from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.services.illustration_service import IllustrationService, BatchIllustrationService
from app.models.illustration import Illustration, IllustrationStatus, IllustrationStyle
from app.models.story import Story
from app.schemas.illustration import (
    IllustrationCreate, IllustrationResponse, IllustrationUpdate,
    BatchIllustrationRequest, BatchIllustrationResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=IllustrationResponse)
async def create_illustration(
    illustration_data: IllustrationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建单张插图"""
    try:
        service = IllustrationService(db)

        # 检查故事是否存在 (暂时禁用用于测试)
        # story = db.query(Story).filter(Story.id == illustration_data.story_id).first()
        # if not story:
        #     raise HTTPException(status_code=404, detail="Story not found")

        # 生成插图
        logger.info(f"Starting illustration generation for story {illustration_data.story_id}, page {illustration_data.page_number}")
        illustration = await service.generate_illustration(
            story_id=str(illustration_data.story_id),
            page_number=illustration_data.page_number,
            prompt=illustration_data.prompt,
            style=illustration_data.style,
            character_bible=illustration_data.character_bible,
            negative_prompt=illustration_data.negative_prompt
        )

        logger.info(f"Illustration generated successfully: {illustration.id}")
        return illustration

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to create illustration: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create illustration: {str(e)}")

@router.get("/{illustration_id}", response_model=IllustrationResponse)
async def get_illustration(
    illustration_id: str,
    db: Session = Depends(get_db)
):
    """获取单张插图"""
    service = IllustrationService(db)
    illustration = service.get_illustration(illustration_id)
    
    if not illustration:
        raise HTTPException(status_code=404, detail="Illustration not found")
    
    return illustration

@router.get("/story/{story_id}", response_model=List[IllustrationResponse])
async def get_story_illustrations(
    story_id: str,
    db: Session = Depends(get_db)
):
    """获取故事的所有插图"""
    service = IllustrationService(db)
    illustrations = service.get_story_illustrations(story_id)
    return illustrations

@router.post("/batch", response_model=BatchIllustrationResponse)
async def create_batch_illustrations(
    request: BatchIllustrationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """批量创建插图"""
    try:
        service = BatchIllustrationService(db)
        
        # 检查故事是否存在
        story = db.query(Story).filter(Story.id == request.story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # 批量生成插图
        illustrations = await service.generate_illustrations_with_fallback(
            story_id=request.story_id,
            pages=request.pages,
            character_bible=request.character_bible,
            style=request.style
        )
        
        return BatchIllustrationResponse(
            story_id=request.story_id,
            illustrations=illustrations,
            total_pages=len(request.pages),
            successful_generations=len([i for i in illustrations if i.status == IllustrationStatus.COMPLETED]),
            failed_generations=len([i for i in illustrations if i.status == IllustrationStatus.FAILED])
        )
        
    except Exception as e:
        logger.error(f"Failed to create batch illustrations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create batch illustrations: {str(e)}")

@router.put("/{illustration_id}", response_model=IllustrationResponse)
async def update_illustration(
    illustration_id: str,
    illustration_data: IllustrationUpdate,
    db: Session = Depends(get_db)
):
    """更新插图"""
    service = IllustrationService(db)
    illustration = service.get_illustration(illustration_id)
    
    if not illustration:
        raise HTTPException(status_code=404, detail="Illustration not found")
    
    # 更新字段
    for field, value in illustration_data.dict(exclude_unset=True).items():
        setattr(illustration, field, value)
    
    db.commit()
    db.refresh(illustration)
    
    return illustration

@router.delete("/{illustration_id}")
async def delete_illustration(
    illustration_id: str,
    db: Session = Depends(get_db)
):
    """删除插图"""
    service = IllustrationService(db)
    success = service.delete_illustration(illustration_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Illustration not found")
    
    return {"message": "Illustration deleted successfully"}

@router.get("/{illustration_id}/status")
async def get_illustration_status(
    illustration_id: str,
    db: Session = Depends(get_db)
):
    """获取插图生成状态"""
    service = IllustrationService(db)
    illustration = service.get_illustration(illustration_id)
    
    if not illustration:
        raise HTTPException(status_code=404, detail="Illustration not found")
    
    return {
        "id": str(illustration.id),
        "status": illustration.status,
        "progress": self._get_progress_percentage(illustration.status),
        "image_url": illustration.image_url,
        "created_at": illustration.created_at,
        "generated_at": illustration.generated_at
    }

def _get_progress_percentage(status: IllustrationStatus) -> int:
    """根据状态返回进度百分比"""
    progress_map = {
        IllustrationStatus.PENDING: 0,
        IllustrationStatus.GENERATING: 50,
        IllustrationStatus.COMPLETED: 100,
        IllustrationStatus.FAILED: 0,
        IllustrationStatus.CACHED: 100
    }
    return progress_map.get(status, 0)
