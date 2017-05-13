import os
from google.appengine.ext import db
import jinja2
import webapp2
from models.user import User

template_dir = os.path.join(os.path.dirname(__file__),'../templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),autoescape= True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Post(db.Model):
    subject = db.StringProperty(required= True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    author = db.ReferenceProperty(User,collection_name='posts',required = True)
    like_count = db.IntegerProperty()
    dislike_count = db.IntegerProperty()
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self,current_userid = None):
        self._render_text = self.content.replace('/n','<br>')
        return render_str("post.html",p=self,current_userid = current_userid)
    def likePost(post):
        if post.like_count != None:
            post.like_count += 1
        else:
            post.like_count = 1
        return post
    def dislikePost(post):
        if post.dislike_count != None:
            post.dislike_count += 1
        else:
            post.dislike_count = 1
        return post