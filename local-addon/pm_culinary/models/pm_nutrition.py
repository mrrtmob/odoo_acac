# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmNutrition(models.Model):
    _name = 'pm.nutrition'
    _description = 'Nutrition'
    _inherit = "mail.thread"
    _order = 'name'

    name = fields.Char(required=True)
    measurement_unit = fields.Selection(
        [('mcg', 'Microgram (mcg)'),
         ('mg', 'Milligram (mg)'),
         ('g', 'Gram (g)')],
        required=True
    )
