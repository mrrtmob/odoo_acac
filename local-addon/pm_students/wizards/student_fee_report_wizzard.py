# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo import api, fields, models


class StudentPaymentReport(models.TransientModel):

    _name = "pm.student.payment.summary"
    _description = 'Payment Summary / Report'

    student = fields.Many2many('op.student', 'summary_student_rel', 'sum_id', 'student_id', string='Students(s)')
    name = fields.Char('Description', readonly=True)
    month_list = [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
                  ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
                  ('12', 'December')]
    month = fields.Selection(month_list, string='Month', required=False)
    year = fields.Selection(
        [('2015', '2015'), ('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020'),
         ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'), ('2025', '2025'), ('2026', '2026')],
        string='Year')


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        data['student'] = self.env.context.get('active_ids', [])
        students = self.env['op.student'].browse(data['student'])
        datas = {
            'ids': [],
            'model': 'op.student',
            'form': data
        }
        return self.env.ref('pm_students.action_report_payment_summary').report_action(students, data=datas)

