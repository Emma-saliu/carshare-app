from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.distance import geodesic

import ssl
import certifi
import math


# ---------------------------------------------------------
# APP SETUP
# ---------------------------------------------------------

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carshare.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------
# GEOCODER SETUP
# ---------------------------------------------------------

ssl_context = ssl.create_default_context(
    cafile=certifi.where()
)

geolocator = Nominatim(
    user_agent="carshare-final-year-project-emoshoke",
    ssl_context=ssl_context
)

geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    swallow_exceptions=False
)


# ---------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(
        db.String(50),
        nullable=False
    )

    last_name = db.Column(
        db.String(50),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


class Journey(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    driver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    origin = db.Column(
        db.String(120),
        nullable=False
    )

    origin_latitude = db.Column(
        db.Float,
        nullable=False
    )

    origin_longitude = db.Column(
        db.Float,
        nullable=False
    )

    destination = db.Column(
        db.String(120),
        nullable=False
    )

    destination_latitude = db.Column(
        db.Float,
        nullable=False
    )

    destination_longitude = db.Column(
        db.Float,
        nullable=False
    )

    departure_date = db.Column(
        db.String(20),
        nullable=False
    )

    departure_time = db.Column(
        db.String(20),
        nullable=False
    )

    available_seats = db.Column(
        db.Integer,
        nullable=False
    )


with app.app_context():
    db.create_all()


# ---------------------------------------------------------
# GEOGRAPHICAL FUNCTIONS
# ---------------------------------------------------------

def geocode_location(place):
    """
    Convert a place name such as 'Carlow'
    into latitude and longitude.
    """

    try:
        clean_place = place.strip()

        location = geocode(
            f"{clean_place}, Ireland",
            country_codes="ie",
            exactly_one=True,
            timeout=10
        )

        if not location:
            print("LOCATION NOT FOUND:", clean_place)
            return None

        print(
            f"FOUND {clean_place}:",
            location.latitude,
            location.longitude
        )

        return {
            "latitude": location.latitude,
            "longitude": location.longitude
        }

    except (GeocoderTimedOut, GeocoderServiceError) as error:
        print("GEOCODING ERROR:", error)
        return None


def route_projection(
    driver_start,
    driver_end,
    passenger_point
):
    """
    Work out:
    1. how far a passenger point is from the driver's route
    2. where along the driver's route the point occurs

    This uses a straight-line approximation for Iteration 1.
    """

    start_lat, start_lon = driver_start
    end_lat, end_lon = driver_end
    point_lat, point_lon = passenger_point

    average_latitude = math.radians(
        (start_lat + end_lat + point_lat) / 3
    )

    km_per_latitude = 111.32
    km_per_longitude = (
        111.32 * math.cos(average_latitude)
    )

    ax = start_lon * km_per_longitude
    ay = start_lat * km_per_latitude

    bx = end_lon * km_per_longitude
    by = end_lat * km_per_latitude

    px = point_lon * km_per_longitude
    py = point_lat * km_per_latitude

    ab_x = bx - ax
    ab_y = by - ay

    ap_x = px - ax
    ap_y = py - ay

    route_length_squared = (
        ab_x ** 2 + ab_y ** 2
    )

    if route_length_squared == 0:
        return {
            "distance": 999,
            "position": 0
        }

    position = (
        (ap_x * ab_x + ap_y * ab_y)
        / route_length_squared
    )

    closest_position = max(
        0,
        min(1, position)
    )

    closest_x = (
        ax + closest_position * ab_x
    )

    closest_y = (
        ay + closest_position * ab_y
    )

    distance = math.sqrt(
        (px - closest_x) ** 2
        + (py - closest_y) ** 2
    )

    return {
        "distance": distance,
        "position": position
    }


def calculate_match_score(
    journey,
    passenger_origin,
    passenger_destination
):
    """
    Determine whether the passenger journey is compatible
    with the driver's journey.
    """

    driver_start = (
        journey.origin_latitude,
        journey.origin_longitude
    )

    driver_end = (
        journey.destination_latitude,
        journey.destination_longitude
    )

    passenger_start = (
        passenger_origin["latitude"],
        passenger_origin["longitude"]
    )

    passenger_end = (
        passenger_destination["latitude"],
        passenger_destination["longitude"]
    )

    pickup = route_projection(
        driver_start,
        driver_end,
        passenger_start
    )

    dropoff = route_projection(
        driver_start,
        driver_end,
        passenger_end
    )

    print(
        "PICKUP DISTANCE FROM ROUTE:",
        pickup["distance"]
    )

    print(
        "DROPOFF DISTANCE FROM ROUTE:",
        dropoff["distance"]
    )

    print(
        "PICKUP ROUTE POSITION:",
        pickup["position"]
    )

    print(
        "DROPOFF ROUTE POSITION:",
        dropoff["position"]
    )

    # Passenger should not require a huge deviation.
    maximum_route_distance = 30

    if pickup["distance"] > maximum_route_distance:
        print("REJECTED: pickup too far from route")
        return None

    if dropoff["distance"] > maximum_route_distance:
        print("REJECTED: destination too far from route")
        return None

    # Passenger should travel in roughly the same direction.
    if pickup["position"] > dropoff["position"]:
        print("REJECTED: wrong direction")
        return None

    # Passenger journey should overlap the driver's journey.
    if pickup["position"] > 1.20:
        print("REJECTED: pickup after driver's destination")
        return None

    if dropoff["position"] < -0.20:
        print("REJECTED: destination before driver's start")
        return None

    # Estimate detour using geographical distances.
    normal_driver_distance = geodesic(
        driver_start,
        driver_end
    ).km

    route_with_passenger = (
        geodesic(
            driver_start,
            passenger_start
        ).km
        +
        geodesic(
            passenger_start,
            passenger_end
        ).km
        +
        geodesic(
            passenger_end,
            driver_end
        ).km
    )

    estimated_extra_distance = max(
        0,
        route_with_passenger
        - normal_driver_distance
    )

    average_route_distance = (
        pickup["distance"]
        + dropoff["distance"]
    ) / 2

    # 100 = strongest match.
    score = (
        100
        - average_route_distance * 2
        - estimated_extra_distance
    )

    score = max(
        0,
        min(100, score)
    )

    print(
        "MATCH SCORE:",
        round(score)
    )

    print(
        "ESTIMATED EXTRA DISTANCE:",
        estimated_extra_distance
    )

    return {
        "score": round(score),
        "extraDistance": round(
            estimated_extra_distance,
            2
        ),
        "pickupDistance": round(
            pickup["distance"],
            2
        ),
        "dropoffDistance": round(
            dropoff["distance"],
            2
        )
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "CarShare API is running"
    })


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    first_name = data.get(
        "firstName",
        ""
    ).strip()

    last_name = data.get(
        "lastName",
        ""
    ).strip()

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    )

    if (
        not first_name
        or not last_name
        or not email
        or not password
    ):
        return jsonify({
            "message": "All fields are required"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=generate_password_hash(
            password
        )
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "userId": new_user.id
    }), 201


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get(
        "email",
        ""
    ).strip().lower()

    password = data.get(
        "password",
        ""
    )

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        user.password_hash,
        password
    ):
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


# ---------------------------------------------------------
# CREATE JOURNEY
# ---------------------------------------------------------

@app.route("/api/journeys", methods=["POST"])
def create_journey():
    data = request.get_json()

    driver_id = data.get("driverId")

    origin = data.get(
        "origin",
        ""
    ).strip()

    destination = data.get(
        "destination",
        ""
    ).strip()

    departure_date = data.get(
        "departureDate",
        ""
    ).strip()

    departure_time = data.get(
        "departureTime",
        ""
    ).strip()

    available_seats = data.get(
        "availableSeats"
    )

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
        available_seats = int(
            available_seats
        )

    except (ValueError, TypeError):
        return jsonify({
            "message": "Seats must be a number"
        }), 400

    if available_seats < 1:
        return jsonify({
            "message": "At least one seat must be available"
        }), 400

    origin_coordinates = geocode_location(
        origin
    )

    if not origin_coordinates:
        return jsonify({
            "message": "Could not find the starting location"
        }), 400

    destination_coordinates = geocode_location(
        destination
    )

    if not destination_coordinates:
        return jsonify({
            "message": "Could not find the destination"
        }), 400

    print(
        "DRIVER ORIGIN:",
        origin_coordinates
    )

    print(
        "DRIVER DESTINATION:",
        destination_coordinates
    )

    journey = Journey(
        driver_id=driver_id,

        origin=origin,

        origin_latitude=(
            origin_coordinates["latitude"]
        ),

        origin_longitude=(
            origin_coordinates["longitude"]
        ),

        destination=destination,

        destination_latitude=(
            destination_coordinates["latitude"]
        ),

        destination_longitude=(
            destination_coordinates["longitude"]
        ),

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


# ---------------------------------------------------------
# SMART JOURNEY SEARCH
# ---------------------------------------------------------

@app.route("/api/journeys", methods=["GET"])
def search_journeys():
    origin = request.args.get(
        "origin",
        ""
    ).strip()

    destination = request.args.get(
        "destination",
        ""
    ).strip()

    departure_date = request.args.get(
        "date",
        ""
    ).strip()

    if (
        not origin
        or not destination
        or not departure_date
    ):
        return jsonify({
            "message":
            "Origin, destination and date are required"
        }), 400

    passenger_origin = geocode_location(
        origin
    )

    if not passenger_origin:
        return jsonify({
            "message":
            "Could not find passenger starting location"
        }), 400

    passenger_destination = geocode_location(
        destination
    )

    if not passenger_destination:
        return jsonify({
            "message":
            "Could not find passenger destination"
        }), 400

    print(
        "PASSENGER ORIGIN:",
        passenger_origin
    )

    print(
        "PASSENGER DESTINATION:",
        passenger_destination
    )

    journeys = Journey.query.filter_by(
        departure_date=departure_date
    ).all()

    print(
        "JOURNEYS FOUND FOR DATE:",
        len(journeys)
    )

    results = []

    for journey in journeys:

        print(
            "CHECKING JOURNEY:",
            journey.id,
            journey.origin,
            "->",
            journey.destination
        )

        if journey.available_seats < 1:
            continue

        match = calculate_match_score(
            journey,
            passenger_origin,
            passenger_destination
        )

        if match is None:
            continue

        results.append({
            "id": journey.id,

            "driverId":
            journey.driver_id,

            "origin":
            journey.origin,

            "destination":
            journey.destination,

            "departureDate":
            journey.departure_date,

            "departureTime":
            journey.departure_time,

            "availableSeats":
            journey.available_seats,

            "matchScore":
            match["score"],

            "extraDistance":
            match["extraDistance"],

            "pickupDistance":
            match["pickupDistance"],

            "dropoffDistance":
            match["dropoffDistance"]
        })

    results.sort(
        key=lambda result:
        result["matchScore"],
        reverse=True
    )

    print(
        "MATCHING JOURNEYS:",
        len(results)
    )

    return jsonify(results), 200


# ---------------------------------------------------------
# START SERVER
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )