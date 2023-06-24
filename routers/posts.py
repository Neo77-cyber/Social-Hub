from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict
from database.models import User,Post, Share
from database.hash import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from database.schemas import PostCreateRequest, PostResponse


router = APIRouter(prefix='/posts',
                   tags=['Posts'])



@router.post("/create_post", response_model = PostResponse, 
                            description ='Create a Post for authenticated users')
async def create_post(new_post:PostCreateRequest,user: User = Depends(authenticate_token)):
    
            create_post = await Post.create(user=user, body=new_post.body)

            response = PostResponse(user=user.username, body=new_post.body)
            return response

    
@router.get('/user_posts',
                description = 'Retrieves users posts, following users posts and shared posts')
async def user_posts(user: User = Depends(authenticate_token)):
        
        user_posts = await Post.filter(user=user)

        following = await user.following.all()

        following_user_ids = [follow.following_user.id for follow in following]
   
        following_posts = await Post.filter(user_id__in=following_user_ids)

        shared_posts = await Share.filter(user=user)
        shared_post_ids = [share.post_id for share in shared_posts]
        shared_posts = await Post.filter(id__in=shared_post_ids)
         
        all_posts = user_posts + following_posts + shared_posts

        if not all_posts:
            raise HTTPException(status_code=404, detail="Posts not found.")
        
        return all_posts


@router.get('/single_post',
            description = 'Retrieves a single post of a user')
async def single_post(post_id: int, user: User = Depends(authenticate_token)):  
            post = await Post.get_or_none(id=post_id)
            if not post:
                raise HTTPException(status_code=404, detail="post not found.")   
            return post 
 

@router.delete('/delete_post/{post_id}',
               description ='Delete users post')
async def delete_post(post_id: int, user: User = Depends(authenticate_token)):
            
                post = await Post.get_or_none(id=post_id, user=user)
                if post:
                      await post.delete()
                      return {'message': 'post deleted'}
                else:
                    raise HTTPException(status_code=404, detail="post not found for the user.")
                
                
@router.post('/share/{post_id}',
                    description = 'Share a post with the post Id')
async def share_post(post_id: int, user: User = Depends(authenticate_token)):
    
        post = await Post.get_or_none(id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")

        share = await Share.create(user=user, post=post)
        
        return post
                                

