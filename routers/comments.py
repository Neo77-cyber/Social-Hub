from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict
from database.models import User,Post, Comment
from database.schemas import CommentCreateRequest, CommentResponse


router = APIRouter(prefix='/comments',
                   tags=['Comments'])



@router.post("/create_comment", response_model = CommentResponse,
                                description = 'Create a comment with post ID')
async def create_comment(new_comment:CommentCreateRequest, user: User = Depends(authenticate_token)):
    
            post = await Post.get_or_none(id=new_comment.post_id)
            if not post:
                raise HTTPException(status_code=404, detail="post not found.")

            comment = await Comment.create(user=user, post=post, comment=new_comment.comment,
                                       created_at=new_comment.created_at)
            
            response = CommentResponse(
                id=comment.id,
                user=user.username,
                post_id=post.id,
                comment=comment.comment,
                created_at=comment.created_at
            )
            return response


@router.get("/post_comments", 
            description = 'get all comments for a specific post')
async def comments(post_id: int, user: User = Depends(authenticate_token)):
   
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token.")
            
            post_comments = await Comment.filter(post_id=post_id)
            if not post_comments:
                raise HTTPException(status_code=404, detail="post not found.") 
            return post_comments 


@router.delete('/delete_comment/{comment_id}', 
                            description = 'delete comment with an ID')
async def delete_comment(comment_id: int, user: User = Depends(authenticate_token)):
    comment = await Comment.get_or_none(id=comment_id, user=user)
    if comment:
        await comment.delete()
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found")