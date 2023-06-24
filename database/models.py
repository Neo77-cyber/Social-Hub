from tortoise import fields
from tortoise.models import Model
from database.hash import password_context






class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length = 100)
    password_hash = fields.CharField(max_length = 100)
    following = fields.ManyToManyField("models.User", related_name="followers")

    async def verify_password(self, plain_password):
        return password_context.hash(plain_password)
    
    class PydanticMeta:
        exclude = ["password_hash"]

class Profile(Model):
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", on_delete=fields.CASCADE, related_name="profile")
    first_name = fields.CharField(max_length = 100)
    surname = fields.CharField(max_length = 100)
    email_address = fields.CharField(max_length= 100)
    gender = fields.CharField(max_length= 100)

class Post(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    body = fields.CharField(max_length = 500)
    
class Comment(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    post = fields.ForeignKeyField("models.Post", on_delete=fields.CASCADE)
    comment = fields.CharField(max_length=200)
    created_at = fields.DatetimeField(auto_now_add=True)

class Like(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    post = fields.ForeignKeyField("models.Post", on_delete=fields.CASCADE)
    like = fields.CharField(max_length=200, default = 'like')

class Share(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    post = fields.ForeignKeyField("models.Post", on_delete=fields.CASCADE)

class Message(Model):
    id = fields.IntField(pk=True)
    user_id = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE)
    message = fields.CharField(max_length=1000)
    recipient = fields.CharField(max_length=100) 