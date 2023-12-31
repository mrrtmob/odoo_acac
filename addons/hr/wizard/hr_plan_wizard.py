# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta



class HrPlanWizard(models.TransientModel):
    _name = 'hr.plan.wizard'
    _description = 'Plan Wizard'

    plan_id = fields.Many2one('hr.plan', default=lambda self: self.env['hr.plan'].search([], limit=1))
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )

    def action_launch(self):
        for activity_type in self.plan_id.plan_activity_type_ids:
            responsible = activity_type.get_responsible_id(self.employee_id)

            if self.env['hr.employee'].with_user(responsible).check_access_rights('read', raise_exception=False):

                if not activity_type.on_time:
                    date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type.activity_type_id)
                else:
                    no_days = activity_type.trg_date_range
                    date_field = activity_type.trg_date_id.name
                    employee_date = self.employee_id[date_field]
                    date_deadline = datetime.now()

                    print(employee_date)
                    print(relativedelta(days=no_days))

                    if employee_date:
                        date_deadline = (employee_date + relativedelta(days=no_days))

                plan_type = 'on'
                if self.plan_id.id == 2:
                    plan_type = 'off'

            self.employee_id.activity_schedule(
                    activity_type_id=activity_type.activity_type_id.id,
                    summary=activity_type.summary,
                    note=activity_type.note,
                    plan_type=plan_type,
                    user_id=responsible.id,
                    date_deadline=date_deadline
                )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }
