from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict
from database.models import User,Post, Like
from database.hash import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from database.schemas import LikeCreateRequest, LikeResponse


router = APIRouter(prefix='/like',
                   tags=['Like'])





@router.post("/like", response_model=LikeResponse,
                        description = 'Like a post')
async def create_like(new_like: LikeCreateRequest, user: User = Depends(authenticate_token)):

        post = await Post.get_or_none(id=new_like.post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")
        
        existing_like = await Like.get_or_none(user=user, post=post)
        if existing_like:
            raise HTTPException(status_code=400, detail="User has already liked the post.")

        like = await Like.create(user=user, post=post)

        response = LikeResponse(
            id=like.id,
            user=user.username,
            post_id=post.id,
        )
        return response

@router.post("/dislike", response_model=LikeResponse, description='Unlike a post')
async def dislike_post(like_request: LikeCreateRequest, user: User = Depends(authenticate_token)):
    post = await Post.get_or_none(id=like_request.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    existing_like = await Like.get_or_none(user=user, post=post)
    if not existing_like:
        raise HTTPException(status_code=400, detail="User has not liked the post.")

    await existing_like.delete()  

    response = LikeResponse(
        id=existing_like.id,
        user=user.username,
        post_id=post.id,
    )
    return response


    

@router.get("/like_count/{post_id}",
                    description = 'Count the number of likes of a post with the Post ID')
async def like_count(post_id: int, user: User = Depends(authenticate_token)):
        post = await Post.get_or_none(id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="post not found.")      
        likes = await Like.filter(post=post).count()
        return likes    


