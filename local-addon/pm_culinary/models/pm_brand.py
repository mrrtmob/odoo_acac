# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmBrand(models.Model):
    _name = 'pm.brand'
    _description = 'Brand'
    _inherit = "mail.thread"
    _order = 'name'

    name = fields.Char(required=True)
    logo = fields.Binary()
