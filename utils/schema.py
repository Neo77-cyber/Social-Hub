from pydantic import BaseModel, Field
from datetime import datetime
from utils.models import User






class ProfileCreateRequest(BaseModel):
    first_name: str
    surname: str
    email_address: str
    gender: str
    
class ProfileResponse(BaseModel):
    user: str
    first_name: str
    surname: str
    email_address: str
    gender: str

class PostCreateRequest(BaseModel):
    body: str
    
class PostResponse(BaseModel):
    user: str
    body: str
    
class CommentCreateRequest(BaseModel):
    post_id: int
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentResponse(BaseModel):
    id: int
    user: str
    post_id: int
    comment: str
    created_at: datetime

class LikeCreateRequest(BaseModel):
    post_id: int
    like: str = "like"
    
class LikeResponse(BaseModel):
    user: str
    post_id: int

class AddFollowersRequest(BaseModel):
    follower_username: str

class RemoveFollowersRequest(BaseModel):
    follower_username: str

class MessageCreateRequest(BaseModel):
    user_id_id: int
    message: str
    recipient: str

class MessageResponse(BaseModel):
     user: str
     message: str