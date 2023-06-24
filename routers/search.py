from utils.token import get_user, authenticate_token
from fastapi import Depends, HTTPException, APIRouter
from typing import Dict
from database.models import User


router = APIRouter(prefix='/search',
                   tags=['Search'])




@router.get("/search/{query}",
            description='A search query that returns user details with a specific username')
async def search_user(query: str, user: User = Depends(authenticate_token)):
    results = await User.filter(username__icontains=query)
    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="User not found.")