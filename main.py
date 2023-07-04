from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from routers import users,profile,posts, comments, like, follow, message, search






app = FastAPI(
    description = 'A social media API that provides features like creating an account, posting updates, following other users, staying connected and interacting with posts through likes and comments'
)
app.include_router(users.router)
app.include_router(profile.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(like.router)
app.include_router(follow.router)
app.include_router(message.router)
app.include_router(search.router)


register_tortoise(
    app,
    db_url='YOUR API KEY'
    modules={'models': ['database.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)






      
          




      
    

    















    

          

