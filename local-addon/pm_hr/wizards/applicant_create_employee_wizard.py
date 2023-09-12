# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields


class WizardPmApplicantEmployee(models.TransientModel):
    _name = 'wizard.pm.applicant.employee'
    _description = "Create Employee and User of Faculty"

    # role_line_ids = fields.One2many(
    #     comodel_name="res.users.role.line",
    #     inverse_name="user_id",
    #     string="Role lines",
    # )
    role_ids = fields.One2many(
        inverse_name='wizard_id',
        comodel_name="pm.users.role.line",
        required=True,
        string="Roles",
        ondelete="cascade"
    )
    email_login = fields.Char('Email Address', required=True)

    def create_employee(self):
        for record in self:
            is_employee = self._context.get('from_employee', False)
            user = None
            roles = record.role_ids
            login = record.email_login
            role_line_ids = []
            active_id = self.env.context.get('active_ids', []) or []
            if not is_employee:
                print('from applicant')
                applicant = self.env['hr.applicant'].browse(active_id)
                employee = applicant.create_employee()
                user = self.env['res.users'].create_user_from_applicant(applicant,login)

            if is_employee:
                print("from employee")
                employee = self.env['hr.employee'].browse(active_id)
                print(employee)
                user_vals = {
                    'name': employee.name,
                    'login': login,
                    'partner_id': employee.address_home_id.id,
                    }
                user = self.env['res.users'].create(user_vals)

            if user:
                for role in roles:
                    role_line_ids.append({
                        'user_id': user.id,
                        'role_id': role.role_id.id,
                    })
                self.env['res.users.role.line'].create(role_line_ids)
            employee.write({
               'user_id': user.id
            })

class ResUsersRoleLine(models.TransientModel):
    _name = "pm.users.role.line"
    wizard_id = fields.Many2one('wizard.pm.applicant.employee')
    role_id = fields.Many2one(
        comodel_name="res.users.role", required=True, string="Role"
    )

