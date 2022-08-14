from functools import wraps
from flask import Flask, render_template, request, url_for, flash, abort
from flask_gravatar import Gravatar
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf import FlaskForm, RecaptchaField
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField, EmailField, DateTimeField
from wtforms.validators import DataRequired, InputRequired, Length, URL
from flask_bootstrap import Bootstrap
import datetime
from forms import RegisterForm, LoginForm, CommentForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_migrate import Migrate
import requests


# -------- using posts from Api --------
# from post import Post


app = Flask(__name__)
ckeditor = CKEditor(app)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "sadLAHSDK/.64646adA"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------- using posts from Api --------
# all_posts = None

# ----------- using posts from Database ---------
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")

    def __repr__(self):
        return '<Post %r>' % self.title


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def to_json(self):
        return {"name": self.name,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"), nullable=True)
    parent_post = relationship("BlogPost", back_populates="comments")


    def __repr__(self):
        return '<Comment %r>' % self.content


# db.create_all()
# db.session.commit()

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(message='Your post title')])
    img_url = StringField('Image Url',validators=[DataRequired(), URL()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    content = CKEditorField('Content')
    submit = SubmitField('Submit')

@app.route('/')
def home():


    # -------- using posts from Api --------
    # global all_posts
    # response = requests.get("https://api.npoint.io/c790b4d5cab58020d391")
    # posts = response.json()
    # all_posts = []
    # for post in posts:
    #     new_post = Post(post)
    #     all_posts.append(new_post)

        # ----------- using posts from Database ---------
    all_posts = reversed(BlogPost.query.all())
    return render_template("index.html", all_posts=all_posts)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contacts')
def contacts():
    return render_template("contact.html", message="Contact Me")


@app.route('/post/<int:id>', methods=["POST", "GET"])
def one_post(id):
    # -------- using posts from Api --------
    # content = all_posts[id - 1]

    # ----------- using posts from Database ---------
    content = BlogPost.query.get(id)
    form = CommentForm()
    if request.method == "POST" and form.validate_on_submit():
        if current_user.is_authenticated:
            data = request.form.get('comment')
            new_comment = Comment(
                content=data,
                author_id=current_user.id,
                post_id=id,
            )
            db.session.add(new_comment)
            db.session.commit()
        else:
            flash("You need to log in or register to add comments!")
            return redirect(url_for("login"))
        return redirect(request.referrer)
    else:
        return render_template("post.html", content=content, form=form)


@app.route("/contacts", methods=["POST"])
def receive_data():
    data = request.form
    print(data["name"])
    print(data["email"])
    print(data["phone"])
    print(data["message"])
    return render_template("contact.html", message="Successfully sent your message")


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)
    return wrapper


@app.route("/new-post", methods=["POST", "GET"])
@admin_only
def new_post():
    form = PostForm()
    if request.method == "POST" and form.validate_on_submit():
        time = datetime.datetime.now()
        month_num = time.month
        day = time.day
        year = time.year
        datetime_object = datetime.datetime.strptime(str(month_num), "%m")
        full_month_name = datetime_object.strftime("%B")
        date = f"{full_month_name} {day}, {year}"
        # date = datetime.date.today().strftime("%B %d, %Y")
        try:
            new_blog = BlogPost(
                title=request.form.get("title"),
                date=date,
                content=request.form.get("content"),
                img_url=request.form.get("img_url"),
                subtitle=request.form.get("subtitle"),
                author_id=current_user.id,
            )
            db.session.add(new_blog)
            db.session.commit()
            return redirect(url_for("home"))
        except Exception as error:
            print(error)
            msg = "Ops Error, Title must be unique!"
            return render_template('make-post.html', form=form, msg=msg)
    return render_template('make-post.html', form=form, msg="You're going to make a great blog post!")


@app.route('/edit-post/<int:post_id>', methods=["POST", "GET"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = PostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        content=post.content
    )

    if request.method == "POST" and edit_form.validate_on_submit():
        post.title = request.form.get("title")
        post.subtitle = request.form.get("subtitle")
        post.img_url = request.form.get("img_url")
        post.author = request.form.get("author")
        post.content = request.form.get("content")
        db.session.commit()
        return redirect(url_for("one_post", id=post_id))

    return render_template("make-post.html", form=edit_form, msg="Edit your post here...",
                           title="Editing Post")


@app.route('/delete/<post_id>')
@admin_only
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        email = request.form.get('email')
        if User.query.filter_by(email=email).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        new_user = User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=hash_and_salted_password,
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("home"))
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        # Find user by email entered.
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("The email doesn't exist in database, try again!")
            return redirect(url_for("login"))

        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Password incorrect, try again!")
            return render_template("login.html", form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
