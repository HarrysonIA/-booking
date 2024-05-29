# app.py
from flask import Flask, render_template, request, jsonify, abort
from flask_pymongo import PyMongo
from flask_marshmallow import Marshmallow
from marshmallow import fields, validates, ValidationError, validate
from transformers import pipeline
from flask_cors import CORS
from models.txt2txtmodel import load_huggingface_model
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/bookings_db"
mongo = PyMongo(app)
ma = Marshmallow(app)
CORS(app)

# Cargar el modelo Hugging Face una vez al inicio
huggingface_model = load_huggingface_model()

# Esquema de validación
class BookingSchema(ma.Schema):
    fullname = fields.String(required=True, validate=[
        validate.Length(max=50), 
        validate.Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', error="Fullname must contain only letters and spaces")
    ])
    checkin_date = fields.String(required=True)
    checkout_date = fields.String(required=True)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    document_number = fields.String(required=True, validate=[
        validate.Length(equal=10), 
        validate.Regexp(r'^\d{10}$', error="Document number must be exactly 10 digits")
    ])

    @validates('checkin_date')
    def validate_checkin_date(self, value):
        if not self._validate_date_format(value):
            raise ValidationError('Invalid date format. Use YYYY-MM-DD.')

    @validates('checkout_date')
    def validate_checkout_date(self, value):
        if not self._validate_date_format(value):
            raise ValidationError('Invalid date format. Use YYYY-MM-DD.')

    def _validate_date_format(self, value):
        from datetime import datetime
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar el formulario de reserva
@app.route('/book', methods=['POST'])
def book():
    try:
        data = request.get_json()
        booking_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    booking = {
        'fullname': data['fullname'],
        'checkin_date': data['checkin_date'],
        'checkout_date': data['checkout_date'],
        'price': data['price'],
        'document_number': data['document_number']
    }
    
    try:
        result = mongo.db.bookings.insert_one(booking)
        booking['_id'] = str(result.inserted_id)  # Convertir ObjectId a string
    except Exception as e:
        abort(400, description="Document number already exists or another database error")

    return jsonify(booking)

# Ruta para obtener todos los datos de bookings
@app.route('/bookings', methods=['GET'])
def get_bookings():
    bookings = list(mongo.db.bookings.find())
    for booking in bookings:
        booking['_id'] = str(booking['_id'])
    return jsonify(bookings)

# Ruta para buscar un booking por document_number
@app.route('/bookings/<document_number>', methods=['GET'])
def get_booking_by_document_number(document_number):
    if not document_number.isdigit() or len(document_number) != 10:
        abort(400, description="Invalid document number format")
    
    booking = mongo.db.bookings.find_one({'document_number': document_number})
    if booking is None:
        return jsonify({'message': 'Booking not found'}), 404

    booking['_id'] = str(booking['_id'])
    return jsonify(booking)

@app.route('/bookings/<document_number>', methods=['PUT'])
def update_booking(document_number):
    if not document_number.isdigit() or len(document_number) != 10:
        abort(400, description="Invalid document number format")
    
    data = request.get_json()
    try:
        booking_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    update_fields = {key: data[key] for key in data if key in ['fullname', 'checkin_date', 'checkout_date', 'price']}

    result = mongo.db.bookings.update_one({'document_number': document_number}, {'$set': update_fields})
    if result.matched_count == 0:
        abort(404, description="Booking not found")

    booking = mongo.db.bookings.find_one({'document_number': document_number})
    booking['_id'] = str(booking['_id'])
    return jsonify(booking)

@app.route('/bookings/<document_number>', methods=['DELETE'])
def delete_booking(document_number):
    if not document_number.isdigit() or len(document_number) != 10:
        abort(400, description="Invalid document number format")

    result = mongo.db.bookings.delete_one({'document_number': document_number})
    if result.deleted_count == 0:
        abort(404, description="Booking not found")

    return jsonify({'message': 'Booking deleted successfully'})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    result = huggingface_model(message)
    return jsonify(result[0])

if __name__ == '__main__':
    app.run(debug=True)
