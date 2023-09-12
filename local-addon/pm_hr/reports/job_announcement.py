from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import UserError
import time


class ModelName(models.AbstractModel):
    _name = 'report.pm_hr.job_announcement_report'
    _description = 'Description'

    @api.model
    def _get_report_values(self, docids, data=None):
        job = self.env['hr.job'].browse(docids)
        # if job.state != 'approved':
        #     raise UserError("The Job Position is not yet approved")

        print(job)
        docargs = {
            'doc_model': 'hr.job',
            'job': job,
            'time': time
        }
        return docargs