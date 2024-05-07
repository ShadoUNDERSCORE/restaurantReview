import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv, set_key

from forms import NewRestaurantForm, EditRestaurantForm, NewNoteForm, EditNoteForm, AdminLoginForm, AdminPasswdForm


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///restaurants.db")
app.config['SECRET_KEY'] = os.urandom(32)
admin_passwd = os.environ.get("ADMIN_PASSWD")
CSRFProtect(app)
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap5(app)


class Restaurant(db.Model):
    __tablename__ = "restaurants"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    fav_item: Mapped[str] = mapped_column(String, nullable=True)
    ave_price: Mapped[str] = mapped_column(String, nullable=True)
    rate_food: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_service: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_vibe: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=True)
    notes = relationship("Note", back_populates="restaurant")


class Note(db.Model):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note: Mapped[str] = mapped_column(String, nullable=False)
    restaurant_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("restaurants.id"))
    restaurant = relationship("Restaurant", back_populates="notes")


class Admin(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.passwd = password


admin_user = Admin("admin", admin_passwd)

with app.app_context():
    db.create_all()


def is_money(money: str,):
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    ave_price = [char for char in money.split(".")[0] if char in digits]

    if not ave_price:
        return False
    return f'${"".join(ave_price)}'


@login_manager.user_loader
def load_user(user_id):
    # Since we only have one user, return the admin user if the user_id matches
    if user_id == admin_user.id:
        return admin_user
    else:
        return None


def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not isinstance(current_user, Admin):
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@app.route("/", methods=["GET", "POST"])
def home():
    if admin_passwd:
        return render_template("index.html")
    else:
        form = AdminPasswdForm()
        if form.validate_on_submit():
            set_key(".env", "ADMIN_PASSWD", generate_password_hash(form.password.data))
            return "<h1>SUCCESS! RESTART SERVER NOW!</h1>"
        return render_template("create_admin.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.username.data == admin_user.id and check_password_hash(admin_user.passwd, form.password.data):
            login_user(admin_user)
            return redirect(url_for("home"))
    return render_template("admin_login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


# Restaurant Data CRUD Systems
# Create
@app.route("/add", methods=["GET", "POST"])
@admin_only
def add():
    form = NewRestaurantForm()
    if form.validate_on_submit():
        ave_price = is_money(form.ave_price.data)
        if ave_price:
            new_restaurant = Restaurant(
                name=form.name.data,
                fav_item=form.fav_item.data,
                ave_price=ave_price,
                rate_food=len(form.rate_food.data),
                rate_service=len(form.rate_service.data),
                rate_vibe=len(form.rate_vibe.data),
                location=form.location.data,
            )
            db.session.add(new_restaurant)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            flash(f"Invalid input '{form.ave_price.data}' for 'Average Price'")
            return redirect(url_for("add"))
    return render_template("add.html", form=form)


# Read
@app.route("/restaurants")
def restaurants():
    restaurant_data = db.session.execute(db.select(Restaurant)).scalars().all()
    return render_template("restaurants.html", data=restaurant_data)


@app.route("/restaurant/<restaurant_id>", methods=["GET", "POST"])
def restaurant_info(restaurant_id):
    form = NewNoteForm()
    restaurant = db.session.execute(db.select(Restaurant).where(Restaurant.id == restaurant_id)).scalar()
    notes = db.session.execute(db.select(Note).where(restaurant_id == restaurant_id)).scalars()
    if form.validate_on_submit():
        new_note = Note(note=form.note.data, restaurant_id=restaurant_id)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for("restaurant_info", restaurant_id=restaurant_id))
    return render_template("restaurant_info.html",
                           restaurant=restaurant, form=form, notes=notes)


# Update
@app.route("/edit/<restaurant_id>", methods=["GET", "POST"])
@admin_only
def edit(restaurant_id):
    form_data = db.session.execute(db.select(Restaurant).where(Restaurant.id == restaurant_id)).scalar()
    form = EditRestaurantForm(data=form_data, method=request.method)
    if form.validate_on_submit():
        ave_price = is_money(form.ave_price.data)
        if ave_price:
            db.session.query(Restaurant).filter(Restaurant.id == restaurant_id).update(
                {"name": form.name.data,
                    "fav_item": form.fav_item.data,
                    "ave_price": ave_price,
                    "rate_food": len(form.rate_food.data),
                    "rate_service": len(form.rate_service.data),
                    "rate_vibe": len(form.rate_vibe.data),
                    "location": form.location.data}
            )
            db.session.commit()
            return redirect(url_for("restaurant_info", restaurant_id=restaurant_id))
        else:
            flash(f"Invalid input '{form.ave_price.data}' for 'Average Price'")
            return redirect(url_for("edit", restaurant_id=restaurant_id))
    return render_template("edit.html", restaurant=form_data, form=form)


# Delete
@app.route("/confirm-delete/<restaurant_id>")
@admin_only
def delete_conf(restaurant_id):
    restaurant_data = db.session.execute(db.select(Restaurant).where(Restaurant.id == restaurant_id)).scalar()
    return render_template("delete_confirm.html", data=restaurant_data)


@app.route("/delete/<restaurant_id>")
@admin_only
def delete(restaurant_id):
    restaurant_to_delete = db.session.execute(db.select(Restaurant).where(Restaurant.id == restaurant_id)).scalar()
    notes_to_delete = db.session.execute(db.select(Note).where(restaurant_id == restaurant_id)).scalars()
    db.session.delete(restaurant_to_delete)
    for note in notes_to_delete:
        db.session.delete(note)
    db.session.commit()
    return redirect(url_for("restaurants"))


# Notes
@app.route("/edit_notes/<restaurant_id>/<note_id>", methods=["GET", "POST"])
@admin_only
def edit_notes(restaurant_id, note_id):
    old_note = db.session.execute(db.select(Note).where(Note.id == note_id)).scalar()
    restaurant = db.session.execute(db.select(Restaurant).where(Restaurant.id == restaurant_id)).scalar()
    form = EditNoteForm(method=request.method, old_note=old_note.note)
    if form.validate_on_submit():
        db.session.query(Note).filter(Note.id == note_id).update({"note": form.note.data})
        db.session.commit()
        return redirect(url_for("restaurant_info", restaurant_id=restaurant_id))
    return render_template("edit_notes.html", form=form, restaurant=restaurant, note_id=note_id)


@app.route("/delete_note/<restaurant_id>/<note_id>")
@admin_only
def delete_note(restaurant_id, note_id):
    note_to_del = db.session.execute(db.select(Note).where(Note.id == note_id)).scalar()
    db.session.delete(note_to_del)
    db.session.commit()
    return redirect(url_for("restaurant_info", restaurant_id=restaurant_id))


if __name__ == "__main__":
    app.run(debug=False)
