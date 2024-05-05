from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class NewRestaurantForm(FlaskForm):
    rating_choices = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    name = StringField("Restaurant Name", validators=[DataRequired()])
    fav_item = StringField("Favorite Item Ordered", validators=[DataRequired()])
    ave_price = StringField("Average Price for One Person", validators=[DataRequired()])
    rate_food = SelectField("Rate the Food", validators=[DataRequired()], choices=rating_choices)
    rate_service = SelectField("Rate the Service", validators=[DataRequired()], choices=rating_choices)
    rate_vibe = SelectField("Rate the Vibe", validators=[DataRequired()], choices=rating_choices)
    location = StringField("Google Maps URL", validators=[DataRequired()])
    submit = SubmitField("Add")


class EditRestaurantForm(FlaskForm):
    rating_choices = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]
    name = StringField("Restaurant Name", validators=[DataRequired()])
    fav_item = StringField("Favorite Item Ordered", validators=[DataRequired()])
    ave_price = StringField("Average Price for One Person", validators=[DataRequired()])
    rate_food = SelectField("Rate the Food", validators=[DataRequired()], choices=rating_choices)
    rate_service = SelectField("Rate the Service", validators=[DataRequired()], choices=rating_choices)
    rate_vibe = SelectField("Rate the Vibe", validators=[DataRequired()], choices=rating_choices)
    location = StringField("Google Maps URL", validators=[DataRequired()])
    submit = SubmitField("Save")

    def __init__(self, method, data):
        super(EditRestaurantForm, self).__init__()
        self.name.default = data.name
        self.fav_item.default = data.fav_item
        self.ave_price.default = data.ave_price
        self.rate_food.default = "".join(["⭐" for _ in range(data.rate_food)])
        self.rate_service.default = "".join(["⭐" for _ in range(data.rate_service)])
        self.rate_vibe.default = "".join(["⭐" for _ in range(data.rate_vibe)])
        self.location.default = data.location
        if method == "GET":
            self.process()


class NewNoteForm(FlaskForm):
    note = TextAreaField("Add Bullet Notes", validators=[DataRequired()])
    submit = SubmitField("Add")


class EditNoteForm(FlaskForm):
    note = TextAreaField("Edit Note")
    submit = SubmitField("Save")

    def __init__(self, method, old_note="Type a note..."):
        super(EditNoteForm, self).__init__()
        self.note.default = old_note
        self.method = method
        if self.method == "GET":
            self.process()
