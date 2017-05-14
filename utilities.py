from google.appengine.ext import db
import hmac
import os
import jinja2
from functools import wraps

secret = 's(*&^@xld.)cretafdwoeupoasdas'
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

#Decorators
#Not sure if i should put this inside the utility file
#Need to ask the reviewer about where to put these
def post_exists(function):
    @wraps(function)
    def wrapper(self, post_id):
        if post_id.isdigit():
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)
            if post:
                return function(self, post_id, post)
            else:
                self.error(404)
                return
        else:
            self.error(404)
            return
    return wrapper

def login_required(function):
    @wraps(function)
    def wrapper(self):
        if self.user:
            return function(self)
        else:
            self.redirect('/login')
            return
    return wrapper

