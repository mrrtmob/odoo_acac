# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    name_in_khmer = fields.Char('Name in Khmer')
    code = fields.Char()
    grade = fields.Selection(
        [('a', 'A'),
         ('b', 'B'),
         ('c', 'C')]
    )
    tax_payer_type = fields.Selection(
        [('non_registered', 'Non-Registered'),
         ('small', 'Small'),
         ('medium', 'Medium'),
         ('large', 'Large')]
    )
    supplier_industry_id = fields.Many2one('pm.supplier.industry', 'Industry')
    partner_type = fields.Selection(
        [('other', 'Other'),
         ('supplier', 'Supplier'),
         ('account_holder', 'Account Holder')],
        default='other'
    )
