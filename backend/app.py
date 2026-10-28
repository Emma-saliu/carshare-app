from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carshare.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    origin = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)

    departure_date = db.Column(db.String(20), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)

    available_seats = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "CarShare API is running"
    })


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not first_name or not last_name or not email or not password:
        return jsonify({
            "message": "All fields are required"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=generate_password_hash(password)
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "userId": new_user.id
    }), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email
        }
    }), 200

@app.route("/api/journeys", methods=["POST"])
def create_journey():
    data = request.get_json()

    driver_id = data.get("driverId")
    origin = data.get("origin", "").strip()
    destination = data.get("destination", "").strip()
    departure_date = data.get("departureDate", "").strip()
    departure_time = data.get("departureTime", "").strip()
    available_seats = data.get("availableSeats")

    if (
        not driver_id
        or not origin
        or not destination
        or not departure_date
        or not departure_time
        or not available_seats
    ):
        return jsonify({
            "message": "All journey details are required"
        }), 400

    try:
        available_seats = int(available_seats)
    except ValueError:
        return jsonify({
            "message": "Seats must be a number"
        }), 400

    if available_seats < 1:
        return jsonify({
            "message": "At least one seat must be available"
        }), 400

    journey = Journey(
        driver_id=driver_id,
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        departure_time=departure_time,
        available_seats=available_seats
    )

    db.session.add(journey)
    db.session.commit()

    return jsonify({
        "message": "Journey created successfully",
        "journeyId": journey.id
    }), 201

@app.route("/api/journeys", methods=["GET"])
def get_journeys():
    origin = request.args.get("origin", "").strip().lower()
    destination = request.args.get("destination", "").strip().lower()
    departure_date = request.args.get("date", "").strip()

    query = Journey.query

    if origin:
        query = query.filter(
            db.func.lower(Journey.origin) == origin
        )

    if destination:
        query = query.filter(
            db.func.lower(Journey.destination) == destination
        )

    if departure_date:
        query = query.filter(
            Journey.departure_date == departure_date
        )

    journeys = query.all()

    results = []

    for journey in journeys:
        driver = db.session.get(User, journey.driver_id)

        results.append({
            "id": journey.id,
            "origin": journey.origin,
            "destination": journey.destination,
            "departureDate": journey.departure_date,
            "departureTime": journey.departure_time,
            "availableSeats": journey.available_seats,
            "driver": {
                "id": driver.id,
                "firstName": driver.first_name,
                "lastName": driver.last_name
            }
        })

    return jsonify(results), 200

@app.route("/api/journeys", methods=["GET"])
def search_journeys():
    origin = request.args.get("origin", "").strip().lower()
    destination = request.args.get("destination", "").strip().lower()
    departure_date = request.args.get("date", "").strip()

    query = Journey.query

    if origin:
        query = query.filter(
            db.func.lower(Journey.origin) == origin
        )

    if destination:
        query = query.filter(
            db.func.lower(Journey.destination) == destination
        )

    if departure_date:
        query = query.filter(
            Journey.departure_date == departure_date
        )

    journeys = query.all()

    results = []

    for journey in journeys:
        results.append({
            "id": journey.id,
            "driverId": journey.driver_id,
            "origin": journey.origin,
            "destination": journey.destination,
            "departureDate": journey.departure_date,
            "departureTime": journey.departure_time,
            "availableSeats": journey.available_seats
        })

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )