# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmProductUom(models.Model):
    _name = 'pm.product.uom'
    _description = 'UoM'
    _inherit = "mail.thread"
    _order = 'name'

    name = fields.Char(required=True)
