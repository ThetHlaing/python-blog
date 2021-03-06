from google.appengine.ext import db
from bloghandler import BlogHandler
from models.post import Post
from models.comment import Comment
from utilities import *



class PostPage(BlogHandler):
    @post_exists
    def get(self, post_id,post):
        self.renderPage(post_id,post)

    def already_liked(self,post):
        post_key = str(post.key())
        user_key = str(self.user.key())
        like = Like.gql("where post = :post and user = :user", post = post_key,user = user_key).get()
        if like:
            return True
        else:
            return False

    @post_exists
    def post(self,post_id,post):
        action = self.request.get("action")
        error_message = "";
        if action:
            if self.user_logged_in():
                if self.user_owns_post(post):
                    if action == 'like' or action == 'dislike':
                        error_message = 'You cannot like your own post'
                else:
                    if(action == 'like'):
                        if Post.likedPost(post,self.user.key()):
                            post.liked_user.append(self.user.key())
                            post.put()
                        else:
                            error_message = 'You can like only once'
                    elif (action == 'dislike'):
                        if Post.dislikedPost(post,self.user.key()):
                            post.disliked_user.append(self.user.key())
                            post.put()
                        else:
                            error_message = 'You cand dislike only once'

                # Adding Comment
                if(action == 'Add Comment'):
                    content = self.request.get("comment_content")
                    comment = Comment(parent = blog_key(),content = content, author = self.user, post = post)
                    comment.put()
                # Deleting Comments
                elif(action == 'Delete Comment'):
                    comment_id = self.request.get("comment_id")
                    key = db.Key.from_path('Comment',int(comment_id),parent=blog_key())
                    comment = db.get(key)
                    if comment:
                        if self.user_owns_comment(comment):
                            comment.delete()
                        else:
                            error_message = "You can only delete your own comments"
                elif(action == "Edit Comment"):
                    comment_id = self.request.get("comment_id")
                    comment_content = self.request.get("comment_edit_content")
                    key = db.Key.from_path('Comment',int(comment_id),parent=blog_key())
                    comment = db.get(key)
                    if comment:
                        if self.user_owns_comment(comment):
                            comment.content = comment_content
                            comment.put()
                        else:
                            error_message = "You can only edit your own comments"
                self.renderPage(post_id,post,error_message)

    def renderPage(self,post_id,post,error_message=None):
        comments = post.comments
        if self.user:
            self.render("single.html",post=post,comments=comments,error_message=error_message,current_userid=self.user.key().id())
        else:
            self.render("single.html",post=post,comments=comments,error_message=error_message)
