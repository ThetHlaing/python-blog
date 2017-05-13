from models.user import User
from models.post import Post
from google.appengine.ext import db

class Comment(db.Model):
    content = db.TextProperty(required = True)
    author = db.ReferenceProperty(User,collection_name='comments',required = True)
    post = db.ReferenceProperty(Post,collection_name='comments',required = True)

    @classmethod
    def by_post_id(cls,post_id):
        c = Comment.all().filter('post_id',post_id)
        return c