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

    def write(self, vals):
      # Temporarily fixing image issue when update a record
      if 'image_1920' in vals and vals['image_1920']:
          # print(self._name)
          # print(self.id)
          # self.env.cr.execute("""SELECT COUNT(*) FROM ir_attachment WHERE res_model = '%s' AND res_id = %d""" % (self._name, self.id))
          # print(self.env.cr.fetchall())
          self.env.cr.execute("""DELETE FROM ir_attachment WHERE res_model = '%s' AND res_id = %d""" % (self._name, self.id))

      return super(ResPartner, self).write(vals)
