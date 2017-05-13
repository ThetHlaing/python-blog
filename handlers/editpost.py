from handlers.bloghandler import BlogHandler
from models.user import User
from models.post import Post
from utilities import *

class EditPost(BlogHandler):
    @post_exists
    def get(self,post_id,post):
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.user_logged_in():
            if str(post.author.key().id()) != uid:
                self.render('editpost.html',error='You can only edit your own post')
            else:
                self.render('editpost.html',post=post)
    @post_exists
    def post(self,post_id,post):
        if self.user_logged_in():
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
            elif action == "Cancel":
                self.redirect('/post/%s'%post_id)