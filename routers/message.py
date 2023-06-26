from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict, List
from database.models import User, Message
from database.hash import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from database.schemas import MessageCreateRequest, MessageResponse
import jwt
from utils.token import get_current_user, oauth2_scheme


router = APIRouter(prefix='/message',
                   tags=['Message'])






@router.post("/message", response_model=MessageResponse, description='Create a message to a user')
async def send_message(
    message: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        sender_username = payload.get("sub")
        sender = await User.get(username=sender_username)
        if not sender:
            raise HTTPException(status_code=401, detail="Invalid token.")

        if current_user.id != sender.id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        recipient = await User.get(username=message.recipient)
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found.")

        message_obj = await Message.create(
            user_id_id=sender.id,  
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


    

@router.get("/messages/{recipient}", response_model=List[MessageResponse], description='Retrieve all messages sent to a user')
async def get_messages(recipient: str, current_user: User = Depends(get_current_user)):
    recipient_user = await User.filter(username=recipient).first()
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient not found.")

    if current_user.username != recipient and current_user not in await recipient_user.following.all():
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

