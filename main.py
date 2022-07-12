from flask import Flask, render_template, request
from post import Post
import requests

app = Flask(__name__)
all_posts = None

@app.route('/')
def home():
    global all_posts
    response = requests.get("https://api.npoint.io/c790b4d5cab58020d391")
    posts = response.json()
    all_posts = []
    for post in posts:
        new_post = Post(post)
        all_posts.append(new_post)

    return render_template("base.html", content=all_posts)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contacts')
def contacts():
    return render_template("contact.html", message="Contact Me")


@app.route('/post/<int:id>')
def one_post(id):
    content = all_posts[id - 1]
    return render_template("post.html", content=content)

@app.route("/contacts", methods=["POST"])
def receive_data():
    data = request.form
    print(data["name"])
    print(data["email"])
    print(data["phone"])
    print(data["message"])
    return render_template("contact.html", message="Successfully sent your message")


if __name__ == "__main__":
    app.run(debug=True)
