from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
import sqlite3

app = Flask(__name__)

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
            document_number TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar el formulario de reserva
@app.route('/book', methods=['POST'])
def book():
    fullname = request.form['fullname']
    checkin_date = request.form['checkin_date']
    checkout_date = request.form['checkout_date']
    price = request.form['price']
    document_number = request.form['document_number']
    
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (fullname, checkin_date, checkout_date, price, document_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (fullname, checkin_date, checkout_date, price, document_number))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

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
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings WHERE document_number = ?', (document_number,))
    booking = cursor.fetchone()
    conn.close()
    return jsonify(booking)
@app.route('/bookings/<document_number>', methods=['PUT'])
def update_booking(document_number):
    data = request.get_json()
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
