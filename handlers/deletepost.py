from handlers.bloghandler import BlogHandler
from models.user import User
from models.post import Post
from utilities import *

class DeletePost(BlogHandler):
    @post_exists
    def get(self,post_id,post):
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.user_logged_in():
            if self.user_owns_post(post):
                db.delete(post.comments)
                db.delete(post)
                #post.delete()
                self.redirect('/')
            else:
                self.render('editpost.html',error='You can only delete your own post')

