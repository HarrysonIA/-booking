from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
import sqlite3
from flask_marshmallow import Marshmallow
from marshmallow import fields, validates, ValidationError, validate
import re

app = Flask(__name__)
ma = Marshmallow(app)

# Crear la base de datos y la tabla de bookings si no existe
def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            checkin_date TEXT NOT NULL,
            checkout_date TEXT NOT NULL,
            price REAL NOT NULL,
            document_number TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

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

    fullname = data['fullname']
    checkin_date = data['checkin_date']
    checkout_date = data['checkout_date']
    price = float(data['price'])
    document_number = data['document_number']
    
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO bookings (fullname, checkin_date, checkout_date, price, document_number)
            VALUES (?, ?, ?, ?, ?)
        ''', (fullname, checkin_date, checkout_date, price, document_number))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        abort(400, description="Document number already exists")
    conn.close()
    
    return jsonify({
        'fullname': fullname,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'price': price,
        'document_number': document_number
    })

# Ruta para obtener todos los datos de bookings
@app.route('/bookings', methods=['GET'])
def get_bookings():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    conn.close()
    return jsonify(bookings)

# Ruta para buscar un booking por document_number
@app.route('/bookings/<document_number>', methods=['GET'])
def get_booking_by_document_number(document_number):
    if not document_number.isdigit() or len(document_number) != 10:
        abort(400, description="Invalid document number format")
    
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE document_number = ?', (document_number,))
    booking = cursor.fetchone()
    conn.close()
    if booking is None:
        return jsonify({'message': 'Booking not found'}), 404
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

    fullname = data.get('fullname')
    checkin_date = data.get('checkin_date')
    checkout_date = data.get('checkout_date')
    price = data.get('price')

    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bookings
        SET fullname = ?, checkin_date = ?, checkout_date = ?, price = ?
        WHERE document_number = ?
    ''', (fullname, checkin_date, checkout_date, price, document_number))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Booking not found")
    conn.close()
    return jsonify({
        'fullname': fullname,
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'price': price,
        'document_number': document_number
    })

@app.route('/bookings/<document_number>', methods=['DELETE'])
def delete_booking(document_number):
    if not document_number.isdigit() or len(document_number) != 10:
        abort(400, description="Invalid document number format")

    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM bookings
        WHERE document_number = ?
    ''', (document_number,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        abort(404, description="Booking not found")
    conn.close()
    return jsonify({'message': 'Booking deleted successfully'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
