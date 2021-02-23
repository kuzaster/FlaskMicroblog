from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from blog import app, db
from blog.forms import (
    CreatePostCommentForm,
    EditPostCommentForm,
    EditProfileForm,
    LoginForm,
    RegistrationForm,
)
from blog.models import Comments, Posts, Users


@app.route("/")
@app.route("/index")
def index():
    posts = Posts.query.order_by(Posts.publication_datetime.desc()).all()
    return render_template("index.html", title="Home", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you`ve successfully registered!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("user", username=user.username)
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/user/<username>", methods=["GET", "POST"])
@login_required
def user(username):
    form = CreatePostCommentForm()
    user = Users.query.filter_by(username=username).first_or_404()
    posts = Posts.query.filter_by(author=user).all()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=user)
        db.session.add(post)
        db.session.commit()
        flash("Congratulations, you`ve successfully created new post!")
        return redirect(url_for("user", username=username))
    return render_template("user.html", user=user, posts=posts, form=form)


@app.route("/post/<post_id>", methods=["GET", "POST"])
def post(post_id):
    form = CreatePostCommentForm()
    post = Posts.query.filter_by(id=post_id).first()
    author = current_user
    comments = Comments.query.filter_by(post_id=post.id)
    if form.validate_on_submit():
        if current_user.is_anonymous:
            flash("Please log in or register for leaving comments")
            return redirect(url_for("login"))
        comment = Comments(
            title=form.title.data, content=form.content.data, author=author, post=post
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("post", post_id=post.id))
    return render_template("post.html", post=post, comments=comments, form=form)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("user", username=form.username.data))
    elif request.method == "GET":
        form.username.data = current_user.username
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/edit_post/<post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    form = EditPostCommentForm()
    post = Posts.query.filter_by(id=post_id).first()
    author = post.author
    if form.delete.data:
        db.session.delete(post)
        db.session.commit()
        flash("Your post is successfully deleted")
        return redirect(url_for("user", username=author.username))
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.publication_datetime = datetime.utcnow()
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "edit_post_comment.html", title="Edit Post", form=form, del_button=True
    )


@app.route("/edit_comment/<comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    form = EditPostCommentForm()
    comment = Comments.query.filter_by(id=comment_id).first()
    post = comment.post
    if form.delete.data:
        db.session.delete(comment)
        db.session.commit()
        flash("Your comment is successfully deleted")
        return redirect(url_for("post", post_id=post.id))
    if form.validate_on_submit():
        comment.title = form.title.data
        comment.content = form.content.data
        comment.publication_datetime = datetime.utcnow()
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = comment.title
        form.content.data = comment.content
    return render_template(
        "edit_post_comment.html", title="Edit comment", form=form, del_button=True
    )
