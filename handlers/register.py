from handlers.signup import Signup
from models.user import User
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