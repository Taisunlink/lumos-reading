from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
import asyncio
import json
import logging

from app.core.database import get_db
from app.schemas.story import (
    StoryRequest, StoryResponse, StoryGenerationStatus,
    ProgressiveGenerationRequest, ProgressiveGenerationResponse,
    StoryCreate, StoryUpdate, StoryDetailResponse
)
from app.models.story import Story, GenerationType, StoryStatus
from app.models.child_profile import ChildProfile
from app.services.story_generation import StoryGenerationService
from app.services.ai_orchestrator import AIOrchestrator
from app.dependencies.auth import get_current_user, get_current_active_user
from app.dependencies.rate_limit import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=StoryResponse)
@rate_limit(requests=10, per_minutes=60)  # 每小时10个故事生成请求
async def generate_story(
    request: StoryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    生成个性化故事
    """
    try:
        # 验证儿童档案权限
        child_profile = db.query(ChildProfile).filter(
            ChildProfile.id == request.child_id,
            ChildProfile.user_id == current_user.id
        ).first()

        if not child_profile:
            raise HTTPException(status_code=404, detail="Child profile not found")

        # 初始化故事生成服务
        story_service = StoryGenerationService(db)

        # 创建故事记录
        story = Story(
            id=uuid.uuid4(),
            child_id=request.child_id,
            title="生成中...",
            theme=request.theme,
            age_group=child_profile.cognitive_stage,
            generation_type=GenerationType.REALTIME,
            status=StoryStatus.GENERATING,
            content={},
            story_metadata=request.dict()
        )

        db.add(story)
        db.commit()
        db.refresh(story)

        # 后台异步生成故事
        background_tasks.add_task(
            story_service.generate_story_async,
            story.id,
            child_profile,
            request
        )

        return StoryResponse(
            story_id=str(story.id),
            status=StoryStatus.GENERATING,
            estimated_time_minutes=2,
            message="故事生成已开始，请稍后查看进度"
        )

    except Exception as e:
        logger.error(f"Story generation request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Story generation failed")

@router.get("/{story_id}/status", response_model=StoryGenerationStatus)
async def get_story_status(
    story_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取故事生成状态"""
    try:
        story_service = StoryGenerationService(db)
        status = await story_service.get_story_generation_status(uuid.UUID(story_id))
        return status
    except Exception as e:
        logger.error(f"Failed to get story status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get story status")

@router.websocket("/{story_id}/stream")
async def story_generation_stream(
    websocket: WebSocket,
    story_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket端点 - 实时推送故事生成进度
    """
    await websocket.accept()

    try:
        story = db.query(Story).filter(Story.id == story_id).first()

        if not story:
            await websocket.send_json({"error": "Story not found"})
            await websocket.close()
            return

        # 获取框架和已有内容
        framework = story.story_metadata.get('framework', {})
        existing_pages = story.content.get('pages', [])
        target_pages = story.story_metadata.get('total_pages', 8)

        # 初始化AI服务
        ai_orchestrator = AIOrchestrator()
        await ai_orchestrator.initialize()

        # 逐页生成剩余页面
        for page_num in range(len(existing_pages) + 1, target_pages + 1):
            try:
                # 生成新页面
                new_page = await ai_orchestrator.story_creator.create_next_page(
                    framework=framework,
                    existing_pages=existing_pages,
                    page_number=page_num
                )

                # 更新故事内容
                existing_pages.append(new_page)
                story.content = {'pages': existing_pages}

                # 计算进度
                progress = (page_num / target_pages) * 100

                # 发送进度更新
                await websocket.send_json({
                    "type": "page_generated",
                    "page_number": page_num,
                    "page_content": new_page,
                    "progress_percentage": progress,
                    "total_pages": target_pages
                })

                # 更新数据库
                db.commit()

                # 添加延迟以避免过快推送
                await asyncio.sleep(2)

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Page {page_num} generation failed: {str(e)}"
                })

        # 故事生成完成
        story.status = StoryStatus.READY

        # 进行最终质量检查
        quality_score = await ai_orchestrator.quality_controller.final_quality_check(story.content)
        story.quality_score = quality_score

        db.commit()

        # 发送完成通知
        await websocket.send_json({
            "type": "generation_complete",
            "story_id": str(story.id),
            "quality_score": quality_score,
            "total_pages": len(existing_pages)
        })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for story {story_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Generation failed: {str(e)}"
        })
    finally:
        await websocket.close()

@router.post("/", response_model=StoryDetailResponse)
async def create_story(
    story: StoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建故事"""
    db_story = Story(**story.dict())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@router.get("/", response_model=List[StoryDetailResponse])
async def get_stories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取故事列表"""
    stories = db.query(Story).offset(skip).limit(limit).all()
    return stories

@router.get("/{story_id}", response_model=StoryDetailResponse)
async def get_story(
    story_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个故事"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.put("/{story_id}", response_model=StoryDetailResponse)
async def update_story(
    story_id: str,
    story_update: StoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新故事"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    for field, value in story_update.dict(exclude_unset=True).items():
        setattr(story, field, value)
    
    db.commit()
    db.refresh(story)
    return story

@router.delete("/{story_id}")
async def delete_story(
    story_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除故事"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    db.delete(story)
    db.commit()
    return {"message": "Story deleted successfully"}