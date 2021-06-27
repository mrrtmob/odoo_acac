# -*- coding: utf-8 -*-


from odoo import models, fields, api




class ResUsers(models.Model):
    _inherit = "res.users"

    def create_user_from_applicant(self, records, login):
        user_id = False
        for rec in records:
            user_vals = {
                'name': rec.partner_name,
                'login': login,
                'partner_id': rec.partner_id.id,
            }
            user_id = self.create(user_vals)
        return user_id

    def _compute_can_edit(self):
        can_edit = self.env['ir.config_parameter'].sudo().get_param('hr.hr_employee_self_edit') or self.env.user.has_group('hr.group_hr_manager')
        for user in self:
            user.can_edit = can_edit

