from odoo import models, api
from datetime import datetime
import time


class EmployeeCertificateReport(models.AbstractModel):
    _name = "report.pm_hr.employee_certificate_report"
    _description = "Transcript Report"

    def get_data(self, data):
        return self.env['hr.employee'].browse(data['active_id'])

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))

        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'get_data': self.get_data(data),
            'date_from': data['date_from'],
            'date_to': data['date_to'],
            'current_date': datetime.today(),
            'passport_id': data['passport_id'],
            'identification_id': data['identification_id'],
            'job_position': data['job_position'],
            'approver': data['approver'],
            'approver_position': data['approver_position']
        }
        return docargs
