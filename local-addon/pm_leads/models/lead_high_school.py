# -*- coding: utf-8 -*-

from odoo import fields, models


class HighSchool(models.Model):
    _name = 'pm.high_school'
    _description = 'High School'
    name = fields.Char('Name', required=True)