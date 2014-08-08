import unittest
import mock
import flask
import datetime
from casework.server import app, _format_postcode
from casework import utils
from casework.forms import RegistrationForm, validate_price_paid, ChargeForm
from wtforms import FormField, FieldList
from wtforms.validators import ValidationError

class MockMintResponse():
    status_code = 200
    url = 'http://localhost:8000'

mock_mint_response = MockMintResponse()

class CaseworkTestCase(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True,
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'testing-not-a-secret'
        self.app = app
        self.client = app.test_client()

    def check_server(self):

        rv = self.client.get('/registration')
        assert rv.status == '200 OK'

        rv = self.client.get('/pagedoesnotexist')
        assert rv.status == '404 NOT FOUND'

        rv = self.client.get('/')
        assert rv.status == '200 OK'

    def test_geojson(self):
        with self.app.test_request_context():

            form = RegistrationForm()


            form.extent.data = ''
            form.validate()
            assert form.extent.errors[0] == 'This field is required.'

            #valid data is valid
            form.extent.data = '{   "type": "Feature",   "crs": {     "type": "name",     "properties": {       "name": "urn:ogc:def:crs:EPSG:27700"     }   },   "geometry": {      "type": "Polygon",     "coordinates": [       [ [530857.01, 181500.00], [530857.00, 181500.00], [530857.00, 181500.00], [530857.00, 181500.00], [530857.01, 181500.00] ]       ]   },   "properties" : {      } }'
            form.validate()
            assert len(form.extent.errors) == 0

            #test cannot validate a point
            form.extent.data = '{"type": "Feature","geometry": {"type": "Point","coordinates": [125.6, 10.1]},"properties": {"name": "Dinagat Islands"}}'
            form.validate()
            assert form.extent.errors[0] == 'A polygon or multi-polygon is required'

    def test_validate_ogc_urn(self):

        result = utils.validate_ogc_urn('urn:ogc:def:crs:EPSG:27700')
        assert result == True

        result = utils.validate_ogc_urn('urn:ogc:def:crs:EPSG:1234')
        assert result == True

        result = utils.validate_ogc_urn('XXXXX')
        assert result == False

        result = utils.validate_ogc_urn('urn:ogc:def:crs:XXX::27700')
        assert result == False

    def get_valid_create_form_without_charge(self):

        with self.app.test_request_context():

            form = RegistrationForm()

            form.title_number.data = "TEST1234"
            form.first_name1.data =  "Kurt"
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

    def get_valid_create_form_with_charge(self):

        with self.app.test_request_context():

            form = RegistrationForm()

            form.title_number.data = "TEST1234"
            form.first_name1.data =  "Kurt"
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

            charge_form = ChargeForm()
            charge_form.chargee_name.data = "Company 1"
            charge_form.charge_date.data = datetime.datetime.strptime("01-02-2001", "%d-%m-%Y")
            charge_form.chargee_line1.data = "21 The Street"
            charge_form.chargee_town.data = "Plymouth"
            charge_form.chargee_country.data = "UK"
            charge_form.chargee_postcode.data = "PL1 1AA"
            form.charges.append_entry(charge_form)

            form.extent.data = '{   "type": "Feature",   "crs": {     "type": "name",     "properties": {       "name": "urn:ogc:def:crs:EPSG:27700"     }   },   "geometry": {      "type": "Polygon",     "coordinates": [       [ [530857.01, 181500.00], [530857.00, 181500.00], [530857.00, 181500.00], [530857.00, 181500.00], [530857.01, 181500.00] ]       ]   },   "properties" : {      } }'

            return form

    def test_postcode_validation(self):

        form = self.get_valid_create_form_without_charge()
        form.postcode.data = 'XXXXX'

        valid = form.validate()
        assert valid == False

        form.postcode.data = 'sw1a1aa'
        valid = form.validate()
        assert valid == True

        form.postcode.data = 'sw1a 1aa'
        valid = form.validate()
        assert valid == True

        form.postcode.data = 'SW1A1AA'
        valid = form.validate()
        assert valid == True


    def test_create_form(self):

        form = self.get_valid_create_form_without_charge()
        valid = form.validate()
        assert valid

    def test_health(self):
        response = self.client.get('/health')
        assert response.status == '200 OK'

    def test_validate_post_code_method(self):
        form = self.get_valid_create_form_without_charge()

        form.price_paid.data = '20000.19'
        result = validate_price_paid(None, form.price_paid)
        assert result == None

        form.price_paid.data = '20000.99'
        result = validate_price_paid(None, form.price_paid)
        assert result == None

        form.price_paid.data = '20000.00'
        result = validate_price_paid(None, form.price_paid)
        assert result == None

        form.price_paid.data = '20000'
        result = validate_price_paid(None, form.price_paid)
        assert result == None

        form.price_paid.data = '20000.103'
        try:
            validate_price_paid(None, form.price_paid)
        except ValidationError as e:
            assert e.message == 'Please enter the price paid as pound and pence'


    def test_valid_pounds_pence(self):
        form = self.get_valid_create_form_without_charge()
        form.price_paid.data = '20000.10'
        valid = form.validate()
        assert valid == True

        form.price_paid.data = '999999'
        valid = form.validate()
        assert valid == True

        form.price_paid.data = '0.01'
        valid = form.validate()
        assert valid == True

        form.price_paid.data = '100.1'
        valid = form.validate()
        assert valid == True

    def test_format_postcode(self):
        form = self.get_valid_create_form_with_charge()
        form.postcode.data = 'pl11aa'
        new = _format_postcode(form.postcode.data)
        assert new == 'PL1 1AA'

        form = self.get_valid_create_form_without_charge()
        form.postcode.data = 'pl132aa'
        new = _format_postcode(form.postcode.data)
        assert new == 'PL13 2AA'

        form = self.get_valid_create_form_without_charge()
        form.postcode.data = 'pl13 2aa'
        new = _format_postcode(form.postcode.data)
        assert new == 'PL13 2AA'

    def test_charge_data(self):
        form = self.get_valid_create_form_with_charge()
        valid = form.validate()
        assert valid == True
        for charge in charges:
            print "chargee name"
            print charge.chargee_name


#    @responses.activate
#    def test_registration(self):
        #title_num = 'TEST1234'
        #responses.add(responses.POST, 'http://0.0.0.0:8001/titles/' + title_num, body='', status=200)

        #response = self.client.post('/registration', data = dict(form = self.get_valid_create_form_without_charge()))
