from models.user import User
from models.post import Post
from google.appengine.ext import db

class Like(db.Model):
    author = db.ReferenceProperty(User,collection_name='likes',required = True)
    post = db.ReferenceProperty(Post,collection_name='likes',required = True)


