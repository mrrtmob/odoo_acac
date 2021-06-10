# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmSupplierIndustry(models.Model):
    _name = 'pm.supplier.industry'
    _description = 'Supplier Industry'
    _inherit = "mail.thread"
    _order = 'name'

    name = fields.Char(required=True)
