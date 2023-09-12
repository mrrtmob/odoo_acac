# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmBrand(models.Model):
    _name = 'pm.brand'
    _description = 'Brand'
    _inherit = "mail.thread"
    _order = 'name'

    name = fields.Char(required=True)
    logo = fields.Binary()

    def write(self, vals):
      # Temporarily fixing image issue when update a record
      if 'logo' in vals and vals['logo']:
          self.env.cr.execute("""DELETE FROM ir_attachment WHERE res_model = '%s' AND res_field = '%s' AND res_id = %d""" % (self._name, 'logo', self.id))

      return super(PmBrand, self).write(vals)