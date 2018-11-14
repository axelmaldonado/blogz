from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    deleted = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.deleted = False
        self.owner = owner



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


# This is not a request handler. We want this to run for every request
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blogs', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_error = ''
        email_error = ''
        
        # TODO - validate user's data
        if password == verify:
            pass
        else:
            verify_error = "Passwords don't match"


        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response message
            return "<h1> Duplicate user</h1>"

    return render_template('register.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['POST', 'GET'])
def blogs():

    id_check = request.args.get("id")
    if id_check is not None:
        post_id = int(request.args.get("id"))
        post = Blog.query.filter_by(id=post_id).first()
        return render_template("single-blog.html", post=post)
    else:
        posts = Blog.query.filter_by(deleted=False).all()

    return render_template("index.html", posts=posts)

@app.route('/blog/newpost', methods=['GET', 'POST'])
def new_post():
    
    if request.method == "POST":
        blog_title = request.form['blog-title']
        blog_post = request.form['blog-post']
        title_error = ""
        post_error = ""

        if blog_title == "":
            title_error = "Enter a Blog title for your post"
        if len(blog_title) > 50:
            title_error = "Blog title limit is 120 characters"
        if blog_post == "":
            post_error = "Please enter a Blog post before submitting"
        if len(blog_post) > 300:
            post_error = "Please limit your Blog post to 400 characters"

        if not title_error and not post_error:
            new_post = Blog(blog_title, blog_post)
            db.session.add(new_post)
            db.session.commit()
            post_id = (new_post.id)
            return redirect(url_for("blogs", id=post_id))
        else:
            return render_template("add-blog.html",title_error=title_error, post_error=post_error)

    return render_template('add-blog.html')

if __name__ == '__main__':
    app.run()