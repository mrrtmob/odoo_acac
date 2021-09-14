# -*- coding: utf-8 -*-

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class PmStudentPaymentSummaryReport(models.AbstractModel):
    _name = 'report.pm_students.payment_summary_report'
    _description = 'Payment Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print("hit here !!")
        print(data)
        print(docids)

