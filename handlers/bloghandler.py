import webapp2
from models.user import User
from utilities import *


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def user_logged_in(self):
        if self.user:
            return True
        else:
            self.redirect('/login')

    def user_owns_post(self,post):
        return self.user.key().id() == post.author.key().id()

    def user_owns_comment(self,comment):
        return self.user.key().id() == comment.author.key().id()

    def post_exists(self,post_id):
        if post_id.isdigit():
                post = Post.get_by_id(int(post_id))
                if post:
                    return post
        return False




