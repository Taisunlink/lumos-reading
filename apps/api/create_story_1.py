#!/usr/bin/env python3
"""
Create story-1 in database for frontend testing
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models.user import User
from app.models.child_profile import ChildProfile
from app.models.story import Story, StoryStatus
from datetime import datetime
import uuid

def create_story_1():
    """Create story-1 for frontend testing"""

    with Session(engine) as db:
        try:
            # Use a valid UUID for story-1
            story_uuid = "11111111-1111-1111-1111-111111111111"

            # Check if story already exists
            existing_story = db.query(Story).filter(Story.id == story_uuid).first()
            if existing_story:
                print(f"Story {story_uuid} already exists: {existing_story.title}")
                return

            # Check if we have a user to associate with
            user = db.query(User).first()
            if not user:
                # Create a test user
                user = User(
                    id=uuid.uuid4(),
                    username="test_user",
                    email="test@example.com",
                    hashed_password="test_password_hash",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"Created test user: {user.id}")

            # Check if we have a child to associate with
            child = db.query(ChildProfile).filter(ChildProfile.user_id == user.id).first()
            if not child:
                # Create a test child
                child = ChildProfile(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    name="测试小朋友",
                    age=6,
                    created_at=datetime.utcnow()
                )
                db.add(child)
                db.commit()
                db.refresh(child)
                print(f"Created test child: {child.id}")

            # Create the story record
            story = Story(
                id=story_uuid,  # Use UUID format
                title="小兔子的冒险",
                theme="友谊",
                reading_time=600,  # 10 minutes
                child_id=child.id,
                content={
                    "pages": [
                        {
                            "page_number": 1,
                            "text": "从前有一只小兔子，它非常喜欢跳跳跳。小兔子每天都会在花园里蹦蹦跳跳，快乐极了。",
                            "illustration_prompt": "一只快乐的小兔子在花园里跳跃",
                            "reading_time_seconds": 30
                        },
                        {
                            "page_number": 2,
                            "text": "有一天，小兔子遇到了一只小松鼠。小松鼠看起来很伤心，因为它找不到回家的路了。",
                            "illustration_prompt": "小兔子遇到一只伤心的小松鼠",
                            "reading_time_seconds": 30
                        },
                        {
                            "page_number": 3,
                            "text": "善良的小兔子决定帮助小松鼠。它们一起走过了森林，越过了小溪，终于找到了小松鼠的家。",
                            "illustration_prompt": "小兔子和小松鼠一起在森林中前行",
                            "reading_time_seconds": 30
                        }
                    ]
                },
                status=StoryStatus.READY,
                created_at=datetime.utcnow()
            )

            db.add(story)
            db.commit()
            db.refresh(story)

            print(f"Successfully created story: {story.id} - {story.title}")
            print(f"Associated with user: {user.id} and child: {child.id}")

        except Exception as e:
            print(f"Error creating story: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    create_story_1()