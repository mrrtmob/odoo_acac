# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmIngredientOrigin(models.Model):
    _name = 'pm.ingredient.origin'
    _description = 'Ingredient Origin'
    _inherit = "mail.thread"
    _order = 'name'

    name = fields.Char(required=True)
