from handlers.bloghandler import BlogHandler
from models.user import User
from models.post import Post
from utilities import *

class NewPost(BlogHandler):
    def render_form(self,subject="",content="",error=""):
        self.render("newpost.html",subject=subject,content=content,error=error)

    @login_required
    def get(self):
        self.render_form()

    @login_required
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if subject and content:
            #uid = self.read_secure_cookie('user_id')
            #self.user = uid and User.by_id(int(uid))
            a = Post(subject=subject,content=content,author= self.user)
            a.put()
            key = str(a.key().id())
            self.redirect("/post/%s"%key)
        else:
            error = "subject and content please!"
            self.render_form(subject,content,error)
