from handlers.bloghandler import BlogHandler
from models.user import User

class Welcome(BlogHandler):
    def get(self):
        #self.render("welcome.html");
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.user:
           self.render("welcome.html",username = self.user.name)
        else:
           self.redirect('/signup')