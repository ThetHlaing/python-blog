import os
from google.appengine.ext import db
import jinja2
import webapp2
from models.user import User
from utilities import *


class Post(db.Model):
    subject = db.StringProperty(required= True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    author = db.ReferenceProperty(User,collection_name='posts',required = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    liked_user = db.ListProperty(db.Key, required=True)
    disliked_user = db.ListProperty(db.Key, required=True)

    def render(self,current_userid = None):
        self._render_text = self.content.replace('/n','<br>')
        return render_str("post.html",p=self,current_userid = current_userid)

    def likedPost(post,user_key):
        if user_key not in post.liked_user:
            return True
        else:
            return False

    def dislikedPost(post,user_key):
        if user_key not in post.disliked_user:
            return True
        else:
            return False

    @property
    def likes(self):
        return count(self.liked_user)

    @property
    def dislikes(self):
        return count(self.disliked_user)

