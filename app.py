from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for,
    send_file,
    abort,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import secrets
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import pytz
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from os import environ as env
from dotenv import find_dotenv, load_dotenv
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
import uuid


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

utc_now = datetime.utcnow()
ist_timezone = pytz.timezone("Asia/Kolkata")
ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = secrets.token_hex(64)
app.config["UPLOAD_FOLDER"] = "static/uploads"

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    redirect_uri=env.get("AUTH0_CALLBACK_URL"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)
    musics = db.relationship("Music", backref="author", lazy=True)
    profile_picture = db.Column(db.String(255))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    posted_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    music_link = db.Column(db.String(100), nullable=False)
    music_name = db.Column(db.String(100), nullable=False)
    posted_at = db.Column(db.DateTime(), default=ist_now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@app.route("/admin")
def admin_panel():

    if "user_id" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    current_user = User.query.get(session["user_id"])
    if current_user.id != 2 and current_user.id != 3:
        flash("You do not have permission to access the admin panel.", "danger")
        return redirect(url_for("dashboard"))

    posts = Post.query.all()
    users = User.query.all()
    musics = Music.query.all()

    return render_template(
        "/admin/admin_panel.html", posts=posts, musics=musics, users=users
    )


@app.route("/admin/deleteuser/<int:user_id>")
def admin_panel_delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
def admin_panel_edit_user(user_id):
    user = User.query.get(user_id)

    if request.method == "POST":
        user.file_name = request.form.get("file_name")
        user.file_description = request.form.get("file_description")
        db.session.commit()
        return redirect(url_for("admin_panel"))

    return render_template("/admin/edit_user.html", user=user)


@app.route("/admin/deletepost/<int:post_id>")
def admin_panel_delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/admin/editpost/<int:post_id>", methods=["GET", "POST"])
def admin_panel_edit_post(post_id):
    post = Post.query.get(post_id)

    if request.method == "POST":
        post.file_name = request.form.get("file_name")
        post.file_description = request.form.get("file_description")
        db.session.commit()
        return redirect(url_for("admin_panel"))

    return render_template("/admin/edit_post.html", post=post)


@app.route("/admin/deletemusic/<int:music_id>")
def admin_panel_delete_music(music_id):
    music = Music.query.get(music_id)
    db.session.delete(music)
    db.session.commit()
    return redirect(url_for("admin_panel"))


@app.route("/admin/editmusic/<int:music_id>", methods=["GET", "POST"])
def admin_panel_edit_music(music_id):
    music = Music.query.get(music_id)

    if request.method == "POST":
        music.music_link = request.form.get("music_link")
        music.music_name = request.form.get("music_name")
        db.session.commit()
        return redirect(url_for("admin_panel"))

    return render_template("/admin/edit_music.html", music=music)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash("Login successful!", "success")
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        else:
            flash("Login failed. Check your username and password.", "danger")

    return render_template("/auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash(
                "Username or email already exists. Please choose a different one.",
                "danger",
            )
        else:
            hashed_password = generate_password_hash(password)

            new_user = User(username=username, email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))

    return render_template("/auth/register.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        session.pop("user_id", None)
        flash("You have been logged out.", "info")
    else:
        flash("You are not currently logged in.", "warning")

    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    posts = Post.query.order_by(desc(Post.id)).all()
    musics = Music.query.order_by(desc(Music.id)).all()
    post_details = []
    music_details = []
    for post in posts:
        author = post.author
        profile_picture = author.profile_picture
        post_details.append({"post": post, "author_profile_picture": profile_picture})

    for music in musics:
        author = music.author
        profile_picture = author.profile_picture
        music_details.append(
            {"music": music, "author_profile_picture": profile_picture}
        )

    current_user = None
    if "user_id" in session:
        current_user = User.query.filter_by(id=session["user_id"]).first()

    return render_template(
        "dashboard.html",
        post_details=post_details,
        musiclist=music_details,
        curr_user=current_user,
    )


if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def upload_file(file_or_path):
    if isinstance(file_or_path, str):
        return file_or_path

    if file_or_path and hasattr(file_or_path, "filename"):
        unique_filename = (
            str(uuid.uuid4()) + "_" + secure_filename(file_or_path.filename)
        )
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file_or_path.save(file_path)
        return file_path

    return None


@app.route("/create_post", methods=["GET", "POST"])
def create_post():
    if "user_id" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files["file"]
        file_name = request.form["file_name"]
        file_description = request.form["file_description"]

        if file:
            user_id = session["user_id"]
            file_path = upload_file(file)

            new_post = Post(
                file_name=file_name,
                file_description=file_description,
                file_path=file_path,
                posted_at=ist_now,
                user_id=user_id,
            )

            db.session.add(new_post)
            db.session.commit()

            flash("Post created successfully!", "success")
            return redirect(url_for("dashboard"))

        else:
            flash("Please upload a file.", "danger")
    current_user = User.query.filter_by(id=session["user_id"]).first()
    return render_template("create_post.html", curr_user=current_user)


@app.route("/view_post/<int:post_id>")
def view_post(post_id):
    post = Post.query.get(post_id)
    file_path = post.file_path.replace("static/", "")
    # print(file_path)
    current_user = User.query.filter_by(id=session["user_id"]).first()
    if post:
        return render_template(
            "view_post.html", post=post, file_path=file_path, curr_user=current_user
        )
    else:
        abort(404)


@app.route("/download_file/<int:post_id>")
def download_file(post_id):
    post = Post.query.get(post_id)

    if post:
        return send_file(post.file_path, as_attachment=True)
    else:
        abort(404)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        file = request.files["profile_picture"]
        if file:
            filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            user.profile_picture = file_path

        user.username = request.form["username"]
        user.email = request.form["email"]
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


@app.route("/author/<int:user_id>")
def author_profile(user_id):
    user = User.query.get(user_id)
    if user:
        user_profile_picture = user.profile_picture.replace("static/", "")
        user_profile_picture = (
            f"{{{url_for('static', filename={user_profile_picture})}}}"
        )
        return render_template(
            "author_profile.html", user=user, user_profile_picture=user_profile_picture
        )
    else:
        abort(404)


@app.route("/study_music", methods=["GET", "POST"])
def share_music():
    if "user_id" not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        music_link = request.form["music_link"]
        music_name = request.form["music_name"]
        if music_link:
            user_id = session["user_id"]
            music_link = music_link.split("/")[-1]
            new_music = Music(
                music_link=music_link, music_name=music_name, user_id=user_id
            )

            db.session.add(new_music)
            db.session.commit()

            flash("Music Added successfully!", "success")
            return redirect(url_for("dashboard"))

        else:
            flash("Please upload a Music.", "danger")
    current_user = User.query.filter_by(id=session["user_id"]).first()
    return render_template("study_music.html", curr_user=current_user)


@app.route("/change_password", methods=["GET", "POST"])
def change_pass():
    if request.method == "POST":
        password = request.form["password"]
        new_password = request.form["confirm-password"]
        if password == new_password:
            user = User.query.get(session["user_id"])
            user.password = generate_password_hash(password)
            db.session.commit()
            flash("Password changed successfully!", "success")
            return redirect(url_for("dashboard"))
    return render_template("change_password.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6011)
