from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.child_profile import ChildProfile
from app.models.user import User
from app.schemas.child_profile import ChildProfileCreate, ChildProfileResponse, ChildProfileUpdate

router = APIRouter(prefix="/children", tags=["children"])

@router.post("/", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
def create_child_profile(child: ChildProfileCreate, db: Session = Depends(get_db)):
    """创建儿童档案"""
    # 验证用户是否存在
    user = db.query(User).filter(User.id == child.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # 创建儿童档案
    db_child = ChildProfile(**child.dict())
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child

@router.get("/{child_id}", response_model=ChildProfileResponse)
def get_child_profile(child_id: UUID, db: Session = Depends(get_db)):
    """获取儿童档案"""
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=404,
            detail="Child profile not found"
        )
    return child

@router.put("/{child_id}", response_model=ChildProfileResponse)
def update_child_profile(child_id: UUID, child_update: ChildProfileUpdate, db: Session = Depends(get_db)):
    """更新儿童档案"""
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=404,
            detail="Child profile not found"
        )
    
    update_data = child_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(child, field, value)
    
    db.commit()
    db.refresh(child)
    return child

@router.get("/user/{user_id}", response_model=List[ChildProfileResponse])
def list_children_by_user(user_id: UUID, db: Session = Depends(get_db)):
    """获取用户的所有儿童档案"""
    children = db.query(ChildProfile).filter(ChildProfile.user_id == user_id).all()
    return children

@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child_profile(child_id: UUID, db: Session = Depends(get_db)):
    """删除儿童档案"""
    child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=404,
            detail="Child profile not found"
        )
    
    db.delete(child)
    db.commit()
    return None
