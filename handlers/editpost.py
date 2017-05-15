from handlers.bloghandler import BlogHandler
from models.user import User
from models.post import Post
from utilities import *

class EditPost(BlogHandler):
    @post_exists
    def get(self,post_id,post):
        if self.user_logged_in():
            if self.user_owns_post(post):
                self.render('editpost.html',post=post)
            else:
                self.render('editpost.html',error='You can only edit your own post')
    @post_exists
    def post(self,post_id,post):
        if self.user_logged_in():
            if self.user_owns_post(post):
                action = self.request.get("action")
                subject = self.request.get("subject")
                content = self.request.get("content")
                if action == "Save":
                    if subject and content:
                        uid = self.read_secure_cookie('user_id')
                        self.user = uid and User.by_id(int(uid))
                        if self.user:
                            post.content = content
                            post.subject = subject
                            post.put()
                            self.redirect("/post/%s"%post_id)
                    else:
                        error = "subject and content please!"
                        self.render('editpost.html',post=post,error="subject and content please!")
            else:
                self.render('editpost.html',error='You can only edit your own post')