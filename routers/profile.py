from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict
from database.models import User,Profile
from database.hash import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from database.schemas import ProfileResponse, ProfileCreateRequest


router = APIRouter(prefix='/profile',
                   tags=['Profile'])





@router.post("/create_profile", response_model = ProfileResponse,
                                description ='Creates a user profile' )
async def create_profile(new_profile:ProfileCreateRequest, user: User = Depends(authenticate_token)):
            create_profile = await Profile.create(user=user, first_name=new_profile.first_name, surname = new_profile.surname,
                                                  email_address = new_profile.email_address, gender = new_profile.gender
                                                    )

            response = ProfileResponse(user=user.username, first_name=new_profile.first_name, surname = new_profile.surname,
                                                  email_address = new_profile.email_address, gender = new_profile.gender  )
            return response

    
@router.get('/userprofile',
            description ='Retreive the current user profile')
async def user_profile(user: User = Depends(authenticate_token)):
            
            userprofile =  await Profile.filter(user=user)
            if not userprofile:
                raise HTTPException(status_code=404, detail="Profile not found.")
            return userprofile  

@router.put('/updateprofile',
            description ='Update current user profile')   
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

@router.delete('/delete/{user_id}',
               description ='Delete users profile')
async def delete_post(user_id: int, user: User = Depends(authenticate_token)):
            
                delete_user = await User.get_or_none(id=user_id)
                if delete_user and delete_user == user:
                      await delete_user.delete()
                      return {'message': 'user deleted'}
                else:
                    raise HTTPException(status_code=404, detail="user not found.")
