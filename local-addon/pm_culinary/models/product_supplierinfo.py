# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    is_primary = fields.Boolean('Is a Primary Supplier', default=False)
