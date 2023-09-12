# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmCulinary(models.Model):
    _name = "pm.culinary"
    _description = "Culinary App"
    state = fields.Selection([
        ('okay', ' Okay'),
        ('not okay', ' Not Okay'),
    ], 'Status')