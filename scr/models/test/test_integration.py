import sys
import os
import pytest
import json
from flask import Flask
import sqlite3

# Añade el directorio `scr` al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from scr.app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client

def test_integration(client):
    # Crear una nueva reserva
    response = client.post('/book', json={
        'fullname': 'Test User',
        'checkin_date': '2024-06-01',
        'checkout_date': '2024-06-10',
        'price': 100.0,
        'document_number': '8888888888'
    })
    assert response.status_code == 200

    # Leer la reserva creada
    response = client.get('/bookings/8888888888')
    assert response.status_code == 200
    assert b'Test User' in response.data

    # Actualizar la reserva
    response = client.put('/bookings/8888888888', json={
        'fullname': 'Updated User',
        'checkin_date': '2024-06-01',
        'checkout_date': '2024-06-10',
        'price': 150.0,
        'document_number': '8888888888'
    })
    assert response.status_code == 200

    # Leer la reserva actualizada
    response = client.get('/bookings/8888888888')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data[1] == 'Updated User'

    # Eliminar la reserva
    response = client.delete('/bookings/8888888888')
    assert response.status_code == 200
    assert response.json['message'] == 'Booking deleted successfully'

    # Verificar que la reserva ha sido eliminada
    rv = client.get('/bookings/8888888888')
    assert b'Booking not found' in rv.data
