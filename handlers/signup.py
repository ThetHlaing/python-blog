from handlers.bloghandler import BlogHandler

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