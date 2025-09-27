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

def get_mock_story(story_id: str) -> StoryDetailResponse:
    """返回模拟故事数据"""
    from datetime import datetime
    from uuid import uuid4
    
    return StoryDetailResponse(
        id=str(uuid4()),  # 使用随机UUID代替story_id
        child_id=str(uuid4()),
        series_bible_id=None,
        title="小兔子的冒险",
        theme="友谊",
        age_group="6-8",
        content={
            "pages": [
                {
                    "page_number": 1,
                    "text": "从前，有一只小兔子叫小白，它住在一个美丽的森林里。小白非常善良，总是愿意帮助别人。",
                    "illustration_prompt": "一只可爱的小白兔在森林里，阳光透过树叶洒在它身上",
                    "crowd_prompt": {
                        "completion": "小白是一只...",
                        "recall": "小兔子住在哪里？",
                        "open_ended": "你觉得小白是什么样的兔子？",
                        "wh_question": "为什么小白总是愿意帮助别人？",
                        "distancing": "你有没有像小白一样帮助过朋友？"
                    },
                    "reading_time_seconds": 30,
                    "word_count": 45
                },
                {
                    "page_number": 2,
                    "text": "有一天，小白的朋友小熊生病了，不能出门玩耍。小白很担心，决定去看望小熊。",
                    "illustration_prompt": "小白担心地看着躺在床上的小熊，手里拿着一些水果",
                    "crowd_prompt": {
                        "completion": "小熊生病了，小白决定...",
                        "recall": "小熊怎么了？",
                        "open_ended": "如果你是小白，你会怎么做？",
                        "wh_question": "小白为什么要去看望小熊？",
                        "distancing": "当你的朋友生病时，你会怎么做？"
                    },
                    "reading_time_seconds": 35,
                    "word_count": 42
                },
                {
                    "page_number": 3,
                    "text": "小白带着新鲜的水果和温暖的拥抱去看小熊。小熊看到小白，脸上露出了笑容。",
                    "illustration_prompt": "小白和小熊拥抱在一起，周围有水果，画面温馨",
                    "crowd_prompt": {
                        "completion": "小白带着...去看小熊",
                        "recall": "小白带了什么去看小熊？",
                        "open_ended": "小熊为什么笑了？",
                        "wh_question": "为什么小白要带水果？",
                        "distancing": "你生病时，朋友是怎么关心你的？"
                    },
                    "reading_time_seconds": 30,
                    "word_count": 38
                },
                {
                    "page_number": 4,
                    "text": "从那天起，小白每天都去看望小熊，陪它聊天，给它讲故事。小熊很快就康复了。",
                    "illustration_prompt": "小白坐在小熊床边讲故事，小熊开心地听着",
                    "crowd_prompt": {
                        "completion": "小白每天都...",
                        "recall": "小白每天做什么？",
                        "open_ended": "你觉得友谊是什么？",
                        "wh_question": "为什么小白要每天去看小熊？",
                        "distancing": "真正的朋友应该怎么做？"
                    },
                    "reading_time_seconds": 35,
                    "word_count": 40
                },
                {
                    "page_number": 5,
                    "text": "小熊康复后，两个好朋友更加亲密了。他们明白了，真正的友谊就是在需要时互相帮助。",
                    "illustration_prompt": "小白和小熊手拉手在森林里玩耍，阳光明媚",
                    "crowd_prompt": {
                        "completion": "真正的友谊就是...",
                        "recall": "小熊康复后，他们明白了什么？",
                        "open_ended": "这个故事告诉我们什么道理？",
                        "wh_question": "什么是真正的友谊？",
                        "distancing": "你和朋友之间有什么感人的故事？"
                    },
                    "reading_time_seconds": 30,
                    "word_count": 42
                }
            ],
            "characters": [
                {
                    "name": "小白",
                    "description": "一只善良的小白兔",
                    "personality": "善良、乐于助人、关心朋友",
                    "visual_description": "毛茸茸的白色兔子，有着粉色的鼻子和长长的耳朵",
                    "role_in_story": "主角"
                },
                {
                    "name": "小熊",
                    "description": "小白的好朋友",
                    "personality": "友善、感恩、坚强",
                    "visual_description": "棕色的小熊，有着圆圆的眼睛和温暖的微笑",
                    "role_in_story": "配角"
                }
            ],
            "vocabulary_targets": ["友谊", "帮助", "关心", "康复", "互相"],
            "extension_activities": [
                "画出你心中的小白和小熊",
                "和爸爸妈妈讨论什么是真正的友谊",
                "想想你可以怎样帮助朋友"
            ],
            "cultural_elements": ["中华文化中的友谊观念", "助人为乐的传统美德"]
        },
        generation_type=GenerationType.PREPRODUCED,
        status=StoryStatus.READY,
        reading_time=160,
        word_count=207,
        page_count=5,
        illustrations=[],
        interaction_points=[],
        quality_score=8.5,
        safety_score=9.0,
        educational_value_score=8.8,
        story_metadata={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

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
    """获取单个故事（需要认证）"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.get("/public/{story_id}", response_model=StoryDetailResponse)
async def get_story_public(
    story_id: str,
    db: Session = Depends(get_db)
):
    """获取单个故事（公开端点，用于演示）"""
    # 如果是模拟故事ID，返回模拟数据
    if story_id.startswith('mock-') or story_id == 'test-story-id':
        return get_mock_story(story_id)
    
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