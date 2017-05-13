from google.appengine.ext import db
from handlers.bloghandler import BlogHandler
from models.comment import Comment
from models.post import Post
from utilities import *


def blog_key(name='default'):
    return db.Key.from_path('blogs',name)

class MainPage(BlogHandler):

    def get(self):
        #posts = db.GqlQuery("Select * FROM Post ORDER BY created DESC limit 10")
        posts = Post.all().order('-created')
        if(self.user):
            self.render("front.html",posts=posts,current_userid = self.user.key().id())
        else:
            self.render("front.html",posts=posts)

    def post(self):
        action =  self.request.get("action");
        post_id =  self.request.get("post_id");
        error_message = ''
        if action:
            if post_id.isdigit():
                post = Post.get_by_id(int(post_id))
                if post:
                    if self.user_logged_in():
                        if self.user_owns_post(post):
                            if action == 'like' or action == 'dislike':
                                error_message = 'You cannot like your own post'
                        else:
                            if(action == 'like'):
                                post = Post.likePost(post)
                            elif (action == 'dislike'):
                                post = Post.dislikePost(post)
                            post.put()
        posts = Post.all().order('-created')
        if self.user:
            self.render("front.html",posts=posts,current_userid = self.user.key().id(),error_message=error_message)
        else:
            self.render("front.html",posts=posts,error_message=error_message)