import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import db
from models.user import User
from models.tailor import Tailor
from models.location import State, District, Taluk, City, Town, Village


class TamilNaduLocationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('default')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_01_database_counts_and_all_districts(self):
        """Verify complete official Tamil Nadu dataset hierarchy."""
        tn_state = State.query.filter(State.name.ilike('%Tamil Nadu%')).first()
        self.assertIsNotNone(tn_state, "Tamil Nadu state must exist")
        self.assertEqual(tn_state.code, "33", "Tamil Nadu LGD state code is 33")

        # Districts
        districts = District.query.filter_by(state_id=tn_state.id).all()
        self.assertGreaterEqual(len(districts), 38, "Must contain all 38 Tamil Nadu districts")

        # Check key districts exist
        dist_names = [d.name.upper() for d in districts]
        for expected in ["CHENNAI", "COIMBATORE", "MADURAI", "TIRUCHIRAPPALLI", "SALEM"]:
            self.assertTrue(any(expected in name for name in dist_names), f"Expected district {expected} in TN")

        # Taluks
        taluk_count = Taluk.query.join(District).filter(District.state_id == tn_state.id).count()
        self.assertGreaterEqual(taluk_count, 300, "Must contain > 300 taluks in TN")

        # Villages
        village_count = Village.query.count()
        self.assertGreaterEqual(village_count, 18000, "Must contain complete revenue villages (18,000+)")
        print(f"\n[Test 1 OK] TN State ID: {tn_state.id}, Districts: {len(districts)}, Taluks: {taluk_count}, Villages: {village_count}")

    def test_02_location_api_endpoints(self):
        """Verify all 6 location REST API endpoints."""
        # 1. States
        res = self.client.get('/api/locations/states')
        self.assertEqual(res.status_code, 200)
        states_data = res.get_json()
        self.assertGreater(len(states_data), 0)
        self.assertEqual(states_data[0]['name'], 'Tamil Nadu')

        tn_id = states_data[0]['id']

        # 2. Districts
        res = self.client.get(f'/api/locations/districts/{tn_id}')
        self.assertEqual(res.status_code, 200)
        dist_data = res.get_json()
        self.assertGreaterEqual(len(dist_data), 38)
        d0_id = dist_data[0]['id']

        # 3. Taluks
        res = self.client.get(f'/api/locations/taluks/{d0_id}')
        self.assertEqual(res.status_code, 200)
        taluk_data = res.get_json()
        self.assertGreater(len(taluk_data), 0)
        t0_id = taluk_data[0]['id']

        # 4. Cities
        res = self.client.get(f'/api/locations/cities/{t0_id}?district_id={d0_id}')
        self.assertEqual(res.status_code, 200)

        # 5. Towns
        res = self.client.get(f'/api/locations/towns/0?taluk_id={t0_id}')
        self.assertEqual(res.status_code, 200)

        # 6. Villages
        res = self.client.get(f'/api/locations/villages/0?taluk_id={t0_id}')
        self.assertEqual(res.status_code, 200)
        print("\n[Test 2 OK] All 6 API endpoints verified with HTTP 200.")

    def test_03_tailor_registration_with_location_hierarchy(self):
        """Verify tailor registration stores full location hierarchy and coordinates."""
        tn_state = State.query.filter(State.name.ilike('%Tamil Nadu%')).first()
        test_dist = District.query.filter_by(state_id=tn_state.id).first()
        test_taluk = Taluk.query.filter_by(district_id=test_dist.id).first()
        test_village = Village.query.filter_by(taluk_id=test_taluk.id).first()

        import uuid
        uid = str(uuid.uuid4())[:8]
        email = f"test_tailor_{uid}@tailorconnect.test"

        form_data = {
            'role': 'tailor',
            'name': f'Master Artisan {uid}',
            'email': email,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'terms': '1',
            'phone': '+91 98401 23456',
            'shop_name': f'Chennai Silk Couture {uid}',
            'specialization': 'Kanchipuram Silk Blouses, Wedding Suits',
            'state_id': tn_state.id,
            'district_id': test_dist.id,
            'taluk_id': test_taluk.id,
            'village_id': test_village.id if test_village else '',
            'address': '12 Anna Salai, Opposite Metro',
            'latitude': '13.082700',
            'longitude': '80.270700'
        }

        res = self.client.post('/auth/register', data=form_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify tailor record in db
        registered_user = User.query.filter_by(email=email).first()
        self.assertIsNotNone(registered_user)
        self.assertTrue(registered_user.is_tailor)

        tailor = Tailor.query.filter_by(user_id=registered_user.id).first()
        self.assertIsNotNone(tailor)
        self.assertEqual(tailor.district_id, test_dist.id)
        self.assertEqual(tailor.taluk_id, test_taluk.id)
        self.assertEqual(tailor.latitude, 13.082700)
        self.assertEqual(tailor.longitude, 80.270700)
        self.assertTrue(tailor.is_active)
        self.assertTrue(tailor.is_verified)
        print(f"\n[Test 3 OK] Registered tailor ID {tailor.id}: {tailor.location_display}")

    def test_04_customer_search_and_empty_state_message(self):
        """Verify discovery search by district and empty location display message."""
        # Query an empty location district (e.g. non-existent or fresh district without tailors)
        empty_dist = District.query.filter(District.name.ilike('%Nilgiris%')).first()
        if not empty_dist:
            empty_dist = District.query.first()

        res = self.client.get(f'/customer/tailors?district_id=999999')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"No registered tailors found in this location.", res.data)
    def test_05_live_location_typeahead_search(self):
        """Verify live location typeahead search by typed place name in Tamil Nadu."""
        # 1. Search with matching location
        res = self.client.get('/customer/tailors?location_q=Madurai')
        self.assertEqual(res.status_code, 200)

        # 2. Search with empty location returns required message
        res = self.client.get('/customer/tailors?location_q=NonExistentTownInTamilNadu999')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"No registered tailors found in this location.", res.data)
        print("\n[Test 5 OK] Live location search verified with matching and empty results.")


if __name__ == '__main__':
    unittest.main()

