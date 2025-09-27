from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.models.story import Story
from app.models.child_profile import ChildProfile
from app.schemas.story import StoryCreate, StoryResponse, StoryUpdate

router = APIRouter(prefix="/stories", tags=["stories"])

@router.post("/", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
def create_story(story: StoryCreate, db: Session = Depends(get_db)):
    """创建新故事"""
    # 验证儿童档案是否存在
    child = db.query(ChildProfile).filter(ChildProfile.id == story.child_id).first()
    if not child:
        raise HTTPException(
            status_code=404,
            detail="Child profile not found"
        )
    
    # 创建故事
    db_story = Story(**story.dict())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: UUID, db: Session = Depends(get_db)):
    """获取故事详情"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )
    return story

@router.put("/{story_id}", response_model=StoryResponse)
def update_story(story_id: UUID, story_update: StoryUpdate, db: Session = Depends(get_db)):
    """更新故事"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )
    
    update_data = story_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(story, field, value)
    
    db.commit()
    db.refresh(story)
    return story

@router.get("/child/{child_id}", response_model=List[StoryResponse])
def list_stories_by_child(child_id: UUID, db: Session = Depends(get_db)):
    """获取儿童的所有故事"""
    stories = db.query(Story).filter(Story.child_id == child_id).all()
    return stories

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(story_id: UUID, db: Session = Depends(get_db)):
    """删除故事"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )
    
    db.delete(story)
    db.commit()
    return None
