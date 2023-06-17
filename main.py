from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import  timedelta
from tortoise.contrib.fastapi import register_tortoise
from typing import Dict
from typing import List
from utils.token import get_user,get_current_user,create_access_token, password_context,oauth2_scheme, authenticate_token
from utils.models import User, Profile, Post, Comment, Share,Like, Message
from utils.secrets import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
import jwt
from utils.schema import PostCreateRequest,PostResponse,ProfileCreateRequest,ProfileResponse,LikeCreateRequest,LikeResponse,AddFollowersRequest,RemoveFollowersRequest,CommentCreateRequest,CommentResponse,MessageCreateRequest,MessageResponse


app = FastAPI()


register_tortoise(
    app,
    db_url='sqlite:///Users/neo/Documents/Codez/FASTApipractice/socialmediafastapi/database.db',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.post('/register')
async def register(username:str, password:str):
    existing_user = await get_user(username)
    if existing_user:
        raise HTTPException(status_code = 400, detail = 'Username already exists')
    hashed_password = password_context.hash(password)
    user = await User.create(username=username, password_hash = hashed_password)
    return {"message": "Registered successfuly"}


@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not await user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": user.username}, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

    
@app.get("/protected")
async def protected_route(user: User = Depends(authenticate_token)):
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token.")
        return {"message": "Protected route accessed successfully."}
    

@app.post("/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not await user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": user.username}, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/create_profile", response_model = ProfileResponse )
async def create_profile(new_profile:ProfileCreateRequest, user: User = Depends(authenticate_token)):
            create_profile = await Profile.create(user=user, first_name=new_profile.first_name, surname = new_profile.surname,
                                                  email_address = new_profile.email_address, gender = new_profile.gender
                                                    )

            response = ProfileResponse(user=user.username, first_name=new_profile.first_name, surname = new_profile.surname,
                                                  email_address = new_profile.email_address, gender = new_profile.gender  )
            return response

    
@app.get('/userprofile')
async def user_profile(user: User = Depends(authenticate_token)):
            
            userprofile =  await Profile.filter(user=user)
            if not userprofile:
                raise HTTPException(status_code=404, detail="Profile not found.")
            return userprofile  

@app.put('/updateprofile')   
async def update_profile(update_profile:ProfileCreateRequest, user: User = Depends(authenticate_token)):
            profile = await Profile.filter(user=user).first()
            if not profile:
                raise HTTPException(status_code=404, detail="Portfolio not found.")
            edit_profile = await Profile.filter(id=profile.id).update(user=user, first_name=update_profile.first_name, surname = update_profile.surname,
                                                  email_address = update_profile.email_address, gender = update_profile.gender
                                                    )

            response = ProfileResponse(user=user.username, first_name=update_profile.first_name, surname = update_profile.surname,
                                                  email_address = update_profile.email_address, gender = update_profile.gender  )
            return response
      
          
@app.post("/create_post", response_model = PostResponse)
async def create_post(new_post:PostCreateRequest,user: User = Depends(authenticate_token)):
    
            create_post = await Post.create(user=user, body=new_post.body)

            response = PostResponse(user=user.username, body=new_post.body)
            return response

    
@app.get('/user_posts')
async def user_posts(user: User = Depends(authenticate_token)):
        
        user_posts = await Post.filter(user=user)

        following = await user.following.all()

        following_user_ids = [follow.following_user.id for follow in following]
   
        following_posts = await Post.filter(user_id__in=following_user_ids)
         
        all_posts = user_posts + following_posts

        if not all_posts:
            raise HTTPException(status_code=404, detail="Posts not found.")
        
        return all_posts


@app.get('/single_post')
async def single_post(post_id: int, user: User = Depends(authenticate_token)):  
            post = await Post.get_or_none(id=post_id)
            if not post:
                raise HTTPException(status_code=404, detail="post not found.")   
            return post 
 

@app.delete('/delete_post/{post_id}')
async def delete_post(post_id: int, user: User = Depends(authenticate_token)):
            
                post = await Post.get_or_none(id=post_id, user=user)
                if post:
                      post.delete()
                      return {'message': 'post deleted'}
                else:
                    raise HTTPException(status_code=404, detail="post not found for the user.")
                                

@app.post("/create_comment", response_model = CommentResponse)
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


@app.get("/comments")
async def comments(user: User = Depends(authenticate_token)):
   
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token.")
            post = await Comment.all() 
            return post

@app.get('/user_comments')
async def user_comments(user: User = Depends(authenticate_token)):
      comments = await Comment.filter(user=user).prefetch_related('post')
      return comments


@app.delete('/delete_comment/{comment_id}')
async def delete_comment(comment_id: int, user: User = Depends(authenticate_token)):
    comment = await Comment.get_or_none(id=comment_id, user=user)
    if comment:
        await comment.delete()
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Comment not found")
      
    
@app.post("/like", response_model=LikeResponse)
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
    

@app.get("/like_count/{post_id}")
async def like_count(post_id: int, user: User = Depends(authenticate_token)):
        post = await Post.get_or_none(id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="post not found.")      
        likes = await Like.filter(post=post).count()
        return likes    
    

@app.post('/share/{post_id}')
async def share_post(post_id: int, user: User = Depends(authenticate_token)):
    
        post = await Post.get_or_none(id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")

        share = await Share.create(user=user, post=post)
        
        return post


@app.post('/follow_user')
async def follower_user(request: AddFollowersRequest, user: User = Depends(authenticate_token)):
    

        target_user = await get_user(request.follower_username)
        if not target_user:
            raise HTTPException(status_code=404, detail="user not found.")
       
        await user.followers.add(target_user)
        
        return {"message": "Followed user successfully."}

    
@app.post('/unfollow_user')
async def unfollow_user(request: RemoveFollowersRequest, user: User = Depends(authenticate_token)):
    

        target_user = await get_user(request.follower_username)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found.")

        await user.following.remove(target_user)

        return {"message": "Unfollowed user successfully."}

       
@app.get('/number_of_following')
async def number_of_followers(user: User = Depends(authenticate_token)):
    
        following_count = await user.following.all().count()

        return {"number of following": following_count}

    
@app.get('/list_of_following')
async def list_of_following(user: User = Depends(authenticate_token)):
    

        following_list = await user.following.all()  

        following_usernames = [following.username for following in following_list]
        return {"list of following": following_usernames}

    
@app.get("/followers/{username}")
async def get_followers(username: str, user: User = Depends(authenticate_token)):
        user = await get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        followers = await user.followers.all()

        follower_usernames = [follower.username for follower in followers]

        return {"followers": follower_usernames}


@app.get("/search/{query}")
async def search_user(query: str, user: User = Depends(authenticate_token)):
    results = User.filter(username__icontains=query)
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="User not found.")


@app.post("/message", response_model=MessageResponse)
async def send_message(message: MessageCreateRequest, current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        sender_username = payload.get("sub")
        sender = await User.get(username=sender_username)
        if not sender:
            raise HTTPException(status_code=401, detail="Invalid token.")
        user_id = sender.id

        recipient = await User.get(username=message.recipient)
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found.")
        
        if current_user.username != sender_username:
            raise HTTPException(status_code=403, detail="Unauthorized")

        message_obj = await Message.create(
            user_id_id=user_id,
            recipient=recipient,
            message=message.message,
        )
        response = MessageResponse(
            user=sender.username,
            recipient=recipient.username,
            message=message_obj.message,
        )
        return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    

@app.get("/messages/{recipient}", response_model=List[MessageResponse])
async def get_messages(recipient: str, current_user: User = Depends(get_current_user)):
    recipient_user = await User.get(username=recipient)
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient not found.")

    
    if current_user.username != recipient and current_user not in recipient_user.following:
        raise HTTPException(status_code=403, detail="Unauthorized")

    messages = await Message.filter(recipient=recipient_user).select_related("user_id")
    message_responses = []
    for message in messages:
        message_response = MessageResponse(
            user=message.user_id.username,
            recipient=recipient,
            message=message.message,
        )
        message_responses.append(message_response)

    return message_responses





    

          

