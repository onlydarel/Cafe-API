from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/all")
def get_all():
    all_cafe = db.session.query(Cafe).all()
    
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafe = result.scalars().all()
    # return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    
    cafes_data = []
    for cafe in all_cafe:
        cafe_data = {
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price
        }
        cafes_data.append(cafe_data)

    return jsonify(cafes=cafes_data)

@app.route("/random")
def get_random():
    all_cafe = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafe)
    return jsonify(id=random_cafe.id,
                   name=random_cafe.name,
                   map_url=random_cafe.map_url,
                   img_url=random_cafe.img_url,
                   location=random_cafe.location,
                   seats=random_cafe.seats,
                   has_toilet=random_cafe.has_toilet,
                   has_wifi=random_cafe.has_wifi,
                   has_sockets=random_cafe.has_sockets,
                   can_take_calls=random_cafe.can_take_calls,
                   coffee_price=random_cafe.coffee_price)

@app.route("/search")
def search_cafe():
    location_query = request.args.get("loc")
    if location_query:
        cafes_w_matching_loc = db.session.query(Cafe).where(Cafe.location == location_query).all()
        cafes_data = []
        for cafe in cafes_w_matching_loc:
            cafe_data = {
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "seats": cafe.seats,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "has_sockets": cafe.has_sockets,
                "can_take_calls": cafe.can_take_calls,
                "coffee_price": cafe.coffee_price
            }
            cafes_data.append(cafe_data)
        
        if cafes_data == []:
            return jsonify(error={'Not Found': "Sorry, we dont have coffee at that location."})
        else:
            return jsonify(cafes=cafes_data)

@app.route('/add', methods=["POST"])
def add_cafe():
    data = request.form

    new_cafe = Cafe(
        name=data['name'],
        map_url=data['map_url'],
        img_url=data['img_url'],
        location=data['location'],
        seats=data['seats'],
        has_toilet=bool(data['has_toilet']),
        has_wifi=bool(data['has_wifi']),
        has_sockets=bool(data['has_sockets']),
        can_take_calls=bool(data['can_take_calls']),
        coffee_price=data['coffee_price']
    )

    db.session.add(new_cafe)
    db.session.commit()
    
    return jsonify(respsone={"success": "Succesfully added the new cafe"})

@app.route('/update-price/<cafe_id>', methods=["GET", "POST", "PATCH"])
def update_price(cafe_id):
    
    data = request.form
    new_price = data['new_price']
    price = db.session.query(Cafe).filter_by(id=cafe_id).first().coffee_price
    if price:
        price = new_price
        db.session.commit()
        return jsonify(success="Succesfully updated the price")
    else:
        return jsonify(error={'Not found': "Sorry a cafe with that id was not found in the database"})

@app.route('/delete-cafe/<int:cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "This-Is-An-API-Key":
        cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
        
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success="Succesfully deleted the Cafe from the database"), 200
        else:
            return jsonify(error={'Not found': "Sorry a cafe with that id was not found in the database"}), 404
    else:
        return jsonify(error={'Forbidden': 'You are not allowed to change the content of the database'}), 403
  
if __name__ == '__main__':
    app.run(debug=True)
