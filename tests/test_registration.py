import unittest
from application.frontend.frontend import app
from application import db
from application.frontend.forms import RegistrationForm
import json



class RegistrationTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True,

        db.create_all()
        self.app = app
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_registration_returns_new_title_number(self):
        response = self.client.get('/registration')
        self.assertEqual(200, response.status_code)
        self.assertTrue('Create title' in response.data)

    def get_valid_create_form_without_charge(self):
        with self.app.test_request_context():
            form = RegistrationForm()

            form.title_number.data = "TEST1234"
            form.first_name1.data = "Kurt"
            form.surname1.data = "Cobain"
            form.first_name2.data = "Courtney"
            form.surname2.data = "Love"

            form.house_number.data = '101'
            form.road.data = "Lake Washington Bldv E"
            form.town.data = "Seattle"
            form.postcode.data = 'SW1A1AA'

            form.property_tenure.data = "Freehold"
            form.property_class.data = "Absolute"
            form.price_paid.data = "1000000"
            form.extent.data = '{   "type": "Feature",   "crs": {     "type": "name",     "properties": {       "name": "urn:ogc:def:crs:EPSG:27700"     }   },   "geometry": {      "type": "Polygon",     "coordinates": [       [ [530857.01, 181500.00], [530857.00, 181500.00], [530857.00, 181500.00], [530857.00, 181500.00], [530857.01, 181500.00] ]       ]   },   "properties" : {      } }'

            return form

    # def test_post_registration_returns_property_url_with_for_title(self):
    #     form = self.get_valid_create_form_without_charge()
    #     response = self.client.post('/registration', data=form)
    #     self.assertEquals(200, response.status_code)