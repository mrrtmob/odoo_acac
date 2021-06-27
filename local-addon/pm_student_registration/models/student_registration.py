from odoo import api, fields, models


class StudentRegistration(models.Model):
    _name = 'student.registration'

    gender = fields.Char(required=True)
    firstName = fields.Char()
    lastName = fields.Char()
    nationality = fields.Char()
    birthDate = fields.Date()
    email = fields.Char()
    phone = fields.Integer()
    current_address = fields.Char()
    city = fields.Char()
    province = fields.Char()
    zip = fields.Char()
    country = fields.Char()
    highest_education = fields.Char()    # many2one field
    # highest_education = fields.One2many(
    #     'pm_lead_educational_achievement', 'id')
    school_name = fields.Char()
    experience_detail = fields.Char()
    company = fields.Char()
    position_held = fields.Char()
    p_with_card = fields.Boolean()
    p_later = fields.Boolean()
    # source
    s_internet = fields.Boolean()
    s_education = fields.Boolean()
    s_school = fields.Boolean()
    s_advertise = fields.Boolean()
    s_culinary = fields.Boolean()
    s_friend = fields.Boolean()
    s_other = fields.Boolean()
    s_specify = fields.Char()
