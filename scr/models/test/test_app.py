import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from scr.app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_create_booking(client):
    rv = client.post('/book', json={
        'fullname': 'Test User',
        'checkin_date': '2024-06-01',
        'checkout_date': '2024-06-10',
        'price': 100.0,
        'document_number': '1234567899'
    })
    assert rv.status_code == 200  # Redirection

def test_get_bookings(client):
    rv = client.get('/bookings')
    assert rv.status_code == 200
    assert b'Test User' in rv.data

def test_get_booking_by_document_number(client):
    rv = client.get('/bookings/1234567899')
    assert rv.status_code == 200
    assert b'Test User' in rv.data

def test_update_booking(client):
    rv = client.put('/bookings/1234567899', json={
        'fullname': 'Updated User',
        'checkin_date': '2024-06-01',
        'checkout_date': '2024-06-10',
        'price': 150.0,
        'document_number': '1234567899'
    })
    assert rv.status_code == 200

    rv = client.get('/bookings/1234567899')
    json_data = rv.get_json()
    assert json_data[1] == 'Updated User'

def test_delete_booking(client):
    # Need to implement delete logic in the app
    rv = client.delete('/bookings/1234567899')
    assert rv.status_code == 200

    rv = client.get('/bookings/1234567899')
    assert b'Booking not found' in rv.datas
