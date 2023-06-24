from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict
from database.models import User
from database.schemas import AddFollowersRequest, RemoveFollowersRequest



router = APIRouter(prefix='/follow',
                   tags=['Follow'])




@router.post('/follow_user',
             description = 'Follow a user')
async def follower_user(request: AddFollowersRequest, user: User = Depends(authenticate_token)):
    

        target_user = await get_user(request.follower_username)
        if not target_user:
            raise HTTPException(status_code=404, detail="user not found.")
       
        await user.followers.add(target_user)
        
        return {"message": "Followed user successfully."}

    
@router.post('/unfollow_user',
                description = 'Unfollow a user')
async def unfollow_user(request: RemoveFollowersRequest, user: User = Depends(authenticate_token)):
    

        target_user = await get_user(request.follower_username)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found.")

        await user.following.remove(target_user)

        return {"message": "Unfollowed user successfully."}

       
@router.get('/number_of_following', 
                description = 'Retrieve the number of user a user follows')
async def number_of_followers(user: User = Depends(authenticate_token)):
    
        following_count = await user.following.all().count()

        return {"number of following": following_count}

    
@router.get('/list_of_following', 
            description = 'Retrieve a list of all the users a user follows')
async def list_of_following(user: User = Depends(authenticate_token)):
    

        following_list = await user.following.all()  

        following_usernames = [following.username for following in following_list]
        return {"list of following": following_usernames}

    
@router.get("/followers/{username}", 
                        description = 'Retrieve the users that follows a specific user')
async def get_followers(username: str, user: User = Depends(authenticate_token)):
        user = await get_user(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        followers = await user.followers.all()

        follower_usernames = [follower.username for follower in followers]

        return {"followers": follower_usernames}
