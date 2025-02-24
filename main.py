from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random



app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)



    def to_dict(self):
        dictionary = {}  # Corrected to a dictionary

        for column in self.__table__.columns:  # Fixed typo
            dictionary[column.name] = getattr(self, column.name)  # Proper indentation
        return dictionary



with app.app_context():
    db.create_all()


@app.route("/")
def home():
    # all_cafes = Cafe.query.all()
    return render_template("index.html")


@app.route("/all")
def get_cafe():
     with app.app_context():
        # Get the 'page' query parameter (default to 1 if not provided)
        page = request.args.get('page', 1, type=int)
        per_page = 15  # Number of cafes to display per page

        # Get cafes with pagination
        paginated_cafes = Cafe.query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template("allcafes.html", cafes=paginated_cafes.items, pagination=paginated_cafes)
    


@app.route("/search")
def search():
    location = request.args.get("location")  # Retrieve location from query params

    if not location:
        return "Please enter a location to search for cafes."

    cafes_by_location = Cafe.query.filter_by(location=location).all()

    if not cafes_by_location:
        return "No cafes found for this location"

    return render_template("bylocation.html", cafes=cafes_by_location)



# - Create Record

@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price")
        )

        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('search', location=new_cafe.location))  # Redirect to the cafes list

    return render_template("add_cafe.html")  # Render a form for GET request



#  Delete Record


@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)

    if not cafe_to_delete:
        return "No such cafe found", 404

    db.session.delete(cafe_to_delete)
    db.session.commit()

    return redirect(url_for('search', location=cafe_to_delete.location))  # Redirect after deletion


# @app.route("/update-price/<cafe_id>", methods =["PATCH"])
# def update_price(cafe_id):
#     cafe_place_by_id = Cafe.query.filter_by(id=cafe_id).first()


#     if not cafe_place_by_id:
#         return jsonify({"error": "Cafe not found"}), 404
    
#     new_price = request.form.get("new_price")

#     if new_price:
#         cafe_place_by_id.coffee_price = new_price
#         db.session.commit()
#         return jsonify({"message": "The price was updated "})
#     else:
#         return jsonify({"error": "No price provided"})
    





if __name__ == '__main__':
    app.run(debug=True)
