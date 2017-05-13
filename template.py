from handlers.bloghandler import BlogHandler
from handlers.cookiesandhash import CookiesAndHash
from handlers.editpost import EditPost
from handlers.login import Login
from handlers.logout import Logout
from handlers.mainpage import MainPage
from handlers.newpost import NewPost
from handlers.postpage import PostPage
from handlers.register import Register
from handlers.signup import Signup
from handlers.welcome import Welcome
import webapp2

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
