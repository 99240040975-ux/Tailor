import os
import sys
import unittest
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import db
from models.user import User
from models.tailor import Tailor
from models.measurement import Measurement
from models.order import Order
from models.review import Review
from models.message import Message
from models.location import State, District, Taluk, City, Town, Village


class ComprehensiveAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('default')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_01_homepage_and_static(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    def test_02_auth_login_and_logout(self):
        # Test login page
        res = self.client.get('/auth/login')
        self.assertEqual(res.status_code, 200)

        # Test login with invalid credentials
        res = self.client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Invalid email or password', res.data)

    def test_02b_registration_requires_terms(self):
        uid = str(uuid.uuid4())[:8]
        email = f"no_terms_{uid}@test.com"

        res = self.client.post('/auth/register', data={
            'name': f'Customer {uid}',
            'email': email,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'role': 'customer',
            'phone': '9876543210'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Please accept the platform terms', res.data)
        self.assertIsNone(User.query.filter_by(email=email).first())

    def test_03_tailor_discovery_and_filtering(self):
        res = self.client.get('/customer/tailors')
        self.assertEqual(res.status_code, 200)

        # Test with non-existent district
        res = self.client.get('/customer/tailors?district_id=999999')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'No registered tailors found in this location.', res.data)

    def test_04_locations_api(self):
        res = self.client.get('/api/locations/states')
        self.assertEqual(res.status_code, 200)
        states = res.get_json()
        self.assertTrue(len(states) > 0)
        state_id = states[0]['id']

        res = self.client.get(f'/api/locations/districts/{state_id}')
        self.assertEqual(res.status_code, 200)
        districts = res.get_json()
        self.assertTrue(len(districts) > 0)
        dist_id = districts[0]['id']

        res = self.client.get(f'/api/locations/taluks/{dist_id}')
        self.assertEqual(res.status_code, 200)

    def test_05_customer_workflow(self):
        uid = str(uuid.uuid4())[:8]
        email = f"cust_{uid}@test.com"
        res = self.client.post('/auth/register', data={
            'name': f'Customer {uid}',
            'email': email,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'role': 'customer',
            'terms': '1',
            'phone': '9876543210'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Customer dashboard
        res = self.client.get('/customer/dashboard')
        self.assertEqual(res.status_code, 200)

        # Create a measurement profile
        res = self.client.post('/measurements/add', data={
            'profile_name': 'My Formal Wear',
            'unit': 'inches',
            'chest': '40.0',
            'waist': '34.0',
            'hip': '40.0',
            'shoulder': '18.0',
            'sleeve': '25.0',
            'neck': '15.5',
            'inseam': '32.0',
            'height': '70.0',
            'notes': 'Fit comfortably'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        cust_user = User.query.filter_by(email=email).first()
        measurement = Measurement.query.filter_by(customer_id=cust_user.id).first()
        self.assertIsNotNone(measurement)
        self.assertEqual(measurement.profile_name, 'My Formal Wear')

    def test_06_order_and_review_workflow(self):
        # 1. Register a tailor
        t_uid = str(uuid.uuid4())[:8]
        t_email = f"tailor_{t_uid}@test.com"
        res = self.client.post('/auth/register', data={
            'name': f'Tailor Pro {t_uid}',
            'email': t_email,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'role': 'tailor',
            'terms': '1',
            'phone': '9876543211',
            'shop_name': f'Studio {t_uid}',
            'specialization': 'Bespoke Suits',
            'city': 'Chennai',
            'address': '100 Mount Road'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        tailor_user = User.query.filter_by(email=t_email).first()
        tailor = Tailor.query.filter_by(user_id=tailor_user.id).first()
        self.assertIsNotNone(tailor)

        # Logout tailor before registering customer
        self.client.get('/auth/logout')

        # 2. Register a customer
        c_uid = str(uuid.uuid4())[:8]
        c_email = f"cust_{c_uid}@test.com"
        res = self.client.post('/auth/register', data={
            'name': f'Customer {c_uid}',
            'email': c_email,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'role': 'customer',
            'terms': '1',
            'phone': '9876543212'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        cust_user = User.query.filter_by(email=c_email).first()
        self.assertIsNotNone(cust_user)

        # 3. Create an order with the tailor
        res = self.client.post('/orders/create', data={
            'tailor_id': tailor.id,
            'service_type': 'custom',
            'clothing_type': 'Two-piece Suit',
            'description': 'Charcoal grey wool suit with satin lapel',
            'delivery_method': 'pickup'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        order = Order.query.filter_by(customer_id=cust_user.id, tailor_id=tailor.id).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'pending')

        # 4. Tailor logs in and quotes order
        self.client.get('/auth/logout')
        self.client.post('/auth/login', data={
            'email': t_email,
            'password': 'Password@123'
        }, follow_redirects=True)

        res = self.client.post(f'/orders/{order.id}/quotation', data={
            'quotation': '4500.00',
            'quotation_notes': 'Includes premium Italian wool fabric'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Reload order
        db.session.expire_all()
        order = Order.query.get(order.id)
        self.assertEqual(order.status, 'quoted')
        self.assertEqual(float(order.quotation), 4500.00)

        # 5. Customer logs in and confirms order
        self.client.get('/auth/logout')
        self.client.post('/auth/login', data={
            'email': c_email,
            'password': 'Password@123'
        }, follow_redirects=True)

        res = self.client.post(f'/orders/{order.id}/accept_quote', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        db.session.expire_all()
        order = Order.query.get(order.id)
        self.assertEqual(order.status, 'confirmed')

        # 6. Tailor transitions order through all stages to delivered
        self.client.get('/auth/logout')
        self.client.post('/auth/login', data={
            'email': t_email,
            'password': 'Password@123'
        }, follow_redirects=True)

        # STATUS_FLOW after confirmed: cutting -> stitching -> alteration -> quality_check -> ready -> delivered
        flow = ['cutting', 'stitching', 'alteration', 'quality_check', 'ready', 'delivered']
        for next_status in flow:
            res = self.client.post(f'/orders/{order.id}/update_status', data={
                'status': next_status
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)

        db.session.expire_all()
        order = Order.query.get(order.id)
        self.assertEqual(order.status, 'delivered')

        # 7. Customer writes a review
        self.client.get('/auth/logout')
        self.client.post('/auth/login', data={
            'email': c_email,
            'password': 'Password@123'
        }, follow_redirects=True)

        res = self.client.post(f'/reviews/create/{order.id}', data={
            'rating': '5',
            'comment': 'Exceptional fit and finish! Highly recommended.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        db.session.expire_all()
        review = Review.query.filter_by(order_id=order.id).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)

        # Tailor rating should be updated
        tailor = Tailor.query.get(tailor.id)
        self.assertEqual(tailor.rating, 5.0)
        self.assertGreaterEqual(tailor.total_reviews, 1)


if __name__ == '__main__':
    unittest.main()
