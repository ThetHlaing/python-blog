import os
import re
import hmac
import random
import hashlib
from pprint import pprint
from string import letters
from google.appengine.ext import db


secret = 's(*&^@xld.)cretafdwoeupoasdas'

import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader= jinja2.FileSystemLoader(template_dir),autoescape= True)


def blog_key(name='default'):
    return db.Key.from_path('blogs',name)


def hash_str(s):
    s = str(s)
    return hmac.new(secret,s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(secure_val):
    s = secure_val.split("|")[0]
    if(make_secure_val(s) == secure_val):
        return s

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


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


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


##### blog stuff

class Post(db.Model):
    subject = db.StringProperty(required= True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    author_id = db.IntegerProperty(required = True)
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

class Comment(db.Model):
    content = db.TextProperty(required = True)
    author_id = db.IntegerProperty(required = True)
    post_id = db.IntegerProperty(required = True)

    @classmethod
    def by_post_id(cls,post_id):
        c = Comment.all().filter('post_id',post_id)
        return c


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
                key = db.Key.from_path('Post',int(post_id),parent=blog_key())
                post = db.get(key)
                if post.author_id == self.user.key().id():
                    if action == 'like' or action == 'dislike':
                        error_message = 'You cannot like your own post'
                    elif action == 'edit':
                        self.redirect('/editpost/%s'%str(post.key().id()))
                    elif action == 'delete':
                        #Delete Comments First
                        associate_comments = Comments.all().filter('post_id',post_id)
                        db.delete(associate_comments)
                        db.delete(post)

                else:
                    if action == 'edit' or action == 'delete':
                        error_message = 'You can only edit or delete your own post'
                    if(action == 'like'):
                        post = Post.likePost(post)
                    elif (action == 'dislike'):
                        post = Post.dislikePost(post)
                post.put()
        posts = Post.all().order('-created')
        self.render("front.html",posts=posts,current_userid = self.user.key().id(),error_message=error_message)


class PostPage(BlogHandler):
    def get(self, post_id):
        #post_id = int(post_id)
        #post = Post.get_by_id(post_id)
        self.renderPage(post_id)
    def post(self,post_id):
        action = self.request.get("action")
        error_message = "";
        if action:
            if post_id.isdigit():
                key = db.Key.from_path('Post',int(post_id),parent=blog_key())
                post = db.get(key)
                if post.author_id == self.user.key().id():
                    if action == 'like' or action == 'dislike':
                        error_message = 'You cannot like your own post'
                    elif action == 'edit':
                        self.redirect('/editpost/%s'%str(post.key().id()))
                    elif action == 'delete':
                        associate_comments = Comments.all().filter('post_id',post_id)
                        db.delete(associate_comments)
                        db.delete(post)
                        post.delete()
                        self.redirect('/')
                else:
                    if action == 'edit' or action == 'delete':
                        error_message = 'You can only edit or delete your own post'
                    if(action == 'like'):
                        post = Post.likePost(post)
                    elif (action == 'dislike'):
                        post = Post.dislikePost(post)
                post.put()
                # Adding Comment
                if(action == 'Add Comment'):
                    if(self.user):
                        content = self.request.get("comment_content")
                        author_id = self.user.key().id()
                        comment = Comment(parent = blog_key(),content = content, author_id = author_id, post_id= int(post_id))
                        comment.put()
                    else:
                        error_message = "Please login first to make comment"
                # Deleting Comments
                elif(action == 'Delete Comment'):
                    comment_id = self.request.get("comment_id")
                    key = db.Key.from_path('Comment',int(comment_id),parent=blog_key())
                    comment = db.get(key)
                    if(self.user):
                        if(comment.author_id == self.user.key().id()):
                            comment.delete()
                        else:
                            error_message = "You can only delete your own comments"
                    else:
                        error_message = "You need to login to delete comments"
                elif(action == "Edit Comment"):
                    comment_id = self.request.get("comment_id")
                    comment_content = self.request.get("comment_edit_content")
                    key = db.Key.from_path('Comment',int(comment_id),parent=blog_key())
                    comment = db.get(key)
                    if(self.user):
                        if(comment.author_id == self.user.key().id()):
                            comment.content = comment_content
                            comment.put()
                        else:
                            error_message = "You can only edit your own comments"
                    else:
                        error_message = "You can only edit your own comments"
                self.renderPage(post_id,error_message)

    def renderPage(self,post_id,error_message=None):
        key = db.Key.from_path('Post',int(post_id),parent=blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return

        comments = Comment.by_post_id(int(post_id))

        if(self.user):
            self.render("single.html",post=post,comments=comments,error_message=error_message,current_userid=self.user.key().id())
        else:
            self.render("single.html",post=post,comments=comments,error_message=error_message)

class NewPost(BlogHandler):
    def render_form(self,subject="",content="",error=""):
        self.render("newpost.html",subject=subject,content=content,error=error)
    def get(self):
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.user:
           self.render_form()
        else:
           self.redirect('/signup')

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            #uid = self.read_secure_cookie('user_id')
            #self.user = uid and User.by_id(int(uid))
            a = Post(parent = blog_key(),subject=subject,content=content,author_id= self.user.key().id())
            a.put()
            key = str(a.key().id())
            self.redirect("/post/%s"%key)
        else:
            error = "subject and content please!"
            self.render_form(subject,content,error)

class EditPost(BlogHandler):
    def get(self,post_id):
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        if self.user:
            if post_id.isdigit():
                key = db.Key.from_path('Post',int(post_id),parent=blog_key())
                post = db.get(key)
                if not post:
                    #self.error(404)
                    self.render('editpost.html',post=post,error='Post not found %s'%post_id)
                elif str(post.author_id) != uid:
                    self.redirect('/')
                else:
                    self.render('editpost.html',post=post)
            else:
                #self.error(404)
                self.render('editpost.html',post=post,error='Post id is not valid %s'%post_id)
        else:
           self.redirect('/login')
    def post(self,post_id):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            uid = self.read_secure_cookie('user_id')
            self.user = uid and User.by_id(int(uid))
            if self.user:
                if post_id.isdigit():
                    key = db.Key.from_path('Post',int(post_id),parent=blog_key())
                    post = db.get(key)
                    post.content = content
                    post.subject = subject
                    post.put()
                    self.redirect("/post/%s"%post_id)
        else:
            error = "subject and content please!"
            self.render('editpost.html',post=post,error="subject and content please!")



class CookiesAndHash(BlogHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get("visits")
        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)

        visits += 1

        new_cookie_val = make_secure_val(visits)
        self.response.headers.add_header('Set-Cookie','visits=%s' % new_cookie_val)

        if visits > 10:
            self.write("You are the best ever!")
        else:
            self.write("You already visited %s" % visits)

class Signup(BlogHandler):
    def get(self):
        self.render("signup.html")
    def post(self):
        #validate input here
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.verify = self.request.get("verify")
        self.email = self.request.get("email")

        #validate user name
        valid = True
        params = dict(username=self.username,email=self.email)
        if not self.username:
            params['username_error'] = "Please enter user name"
            valid = False
        if(self.validate_username(self.username) == None):
            params['username_error'] = "Your user name is not valid"
            valid = False
        if not self.password:
            params['password_error']  = "Please enter password"
            valid = False
        if(self.validate_password(self.password) == None):
            params['password_error']  = "Your password is not valid"
            valid = False
        if(self.email):
            if(self.validate_email(self.email) == None):
                params['email_error']  = "You email is not valid"
                valid = False
        if(self.password != self.verify):
            params['verify_error']  = "Your passwords didn't match"
            valid = False

        if valid:
            self.done()
        else:
            #username=username,email=email
            self.render("signup.html",**params)

    def validate_username(self,username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$");
        return USER_RE.match(username)
    def validate_password(self,password):
        PASSWORD_RE = re.compile(r"^.{3,20}$")
        return PASSWORD_RE.match(password)
    def validate_email(self,email):
        VALIDATOR_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        return VALIDATOR_RE.match(email)

    def done(self,*a,**kw):
        raise NotImplementedError


class Welcome(BlogHandler):
    def get(self):
        #self.render("welcome.html");
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.user:
           self.render("welcome.html",username = self.user.name)
        else:
           self.redirect('/signup')


class Register(Signup):
    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup.html',username_error=msg)
        else :
            u = User.register(self.username,self.password,self.email)
            u.put()
            self.login(u)
            self.redirect('/welcome')

class Login(BlogHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        u = User.login(username,password)
        if u:
            self.login(u)
            self.redirect('/welcome')
        else:
            self.write(password)
            #self.render("login.html",password_error="invalid login")

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    (r'/editpost/([0-9]+)',EditPost),
    (r'/post/([0-9]+)', PostPage),
    ('/cookietest',CookiesAndHash),
    ('/signup',Register),
    ('/login',Login),
    ('/logout',Logout),
    ('/welcome',Welcome)

], debug=True)
