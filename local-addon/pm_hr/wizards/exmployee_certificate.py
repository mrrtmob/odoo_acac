from odoo import api, fields, models, _
import time
from odoo.exceptions import ValidationError


class EmployeeCertificate(models.TransientModel):
    _name = 'employee.certificate'
    _description = 'Employee Certificate'

    date_from = fields.Date(string='From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='To', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    approver = fields.Many2one("hr.employee" ,required=True, string="Approver", help="The person who signs on the certificate")
 
    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.date_from)
            end_date = fields.Date.from_string(record.date_to)
            if start_date > end_date:
                raise ValidationError(
                    _("End Date cannot be set before Start Date."))


    def print_report(self):
        employee_id = self.env.context.get('active_id')
        employee = self.env['hr.employee'].search([('id', '=', employee_id)])
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee': employee,
            'active_id': employee_id,
            'passport_id': employee.passport_id,
            'identification_id': employee.identification_id,
            'job_position': employee.job_id.name,
            'approver': self.approver.name,
            'approver_position': self.approver.job_id.name
        }

        return self.env.ref('pm_hr.act_get_employee_certificate').report_action(self, data=data)



