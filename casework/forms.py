# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, RadioField, DecimalField, HiddenField, TextAreaField, FieldList, DateField, FormField
from wtforms.validators import DataRequired, Optional

from casework.validators import validate_postcode, validate_price_paid, validate_extent
import simplejson


class ChargeForm(Form):
    """
    Charge Form
    """

    charge_date = DateField('Charge date', format='%d-%m-%Y', validators=[DataRequired()])
    chargee_name = StringField('Company name', validators=[DataRequired()])
    chargee_registration_number = StringField('Company registration number', validators=[DataRequired()])
    chargee_address = TextAreaField('Address', validators=[DataRequired()])


class RegistrationForm(Form):
    """
    The names of the variables here MUST match the name attribute of the fields
    in the index.html for WTForms to work
    Nope: you just have to use the form object you pass to the template and use
    the form object to do the work for you
    """

    title_number = HiddenField('Title Number')
    first_name1 = StringField('First name 1', validators=[DataRequired()])
    surname1 = StringField('Surname 1', validators=[DataRequired()])
    first_name2 = StringField('First name 2')
    surname2 = StringField('Surname 2')

    house_number = StringField('House number', validators=[DataRequired()])
    road = StringField('Road', validators=[DataRequired()])
    town = StringField('Town', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired(), validate_postcode])

    property_tenure = RadioField(
        'Property tenure',
        choices=[
            ('Freehold', 'Freehold'),
            ('Leasehold', 'Leasehold')
        ]
    )

    property_class = RadioField(
        'Property class',
        choices=[
            ('Absolute', 'Absolute'),
            ('Good', 'Good'),
            ('Qualified', 'Qualified'),
            ('Possessory', 'Possessory')
        ]
    )

    price_paid = DecimalField(
        'Price paid (&pound;)',
        validators=[Optional(), validate_price_paid],
        places=2,
        rounding=None)

    charges = FieldList(FormField(ChargeForm), min_entries=0)

    charges_template = FieldList(FormField(ChargeForm), min_entries=1)

    extent = TextAreaField('GeoJSON', validators=[DataRequired(), validate_extent])

    def remove_templated_form_elements_and_validate(self):
        old_form_charges_template = self.charges_template
        del self.charges_template
        form_is_validated = self.validate()
        self.charges_template = old_form_charges_template
        return form_is_validated


    def to_json(self):
        arr = []
        for charge in self['charges'].data:
            dt = charge.pop('charge_date')
            print "xXX", dt
            charge['charge_date'] = str(dt)
            arr.append(charge)

        data = simplejson.dumps({
            "title_number": self['title_number'].data,
            "proprietors": [
                {
                    "first_name": self['first_name1'].data,
                    "last_name": self['surname1'].data
                },
                {
                    "first_name": self['first_name2'].data,
                    "last_name": self['surname2'].data
                }
            ],
            "property": {

                "address": {
                    "house_number": self['house_number'].data,
                    "road": self['road'].data,
                    "town": self['town'].data,
                    "postcode": format_postcode(self['postcode'].data)
                },
                "tenure": self['property_tenure'].data,
                "class_of_title": self['property_class'].data
            },
            "payment": {
                "price_paid": self['price_paid'].data,
                "titles": [
                    self['title_number'].data
                ]
            },
            "charges": arr,
            "extent": self['extent'].data
        })

        return data

    def format_postcode(postcode):
        out = postcode.upper()
        if ' ' not in postcode:
            i = len(postcode) - 3
            out = out[:i] + ' ' + out[i:]

        return out

