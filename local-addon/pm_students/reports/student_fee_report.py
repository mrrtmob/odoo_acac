# -*- coding: utf-8 -*-

import calendar
from odoo import http
from odoo.http import request
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import xlsxwriter
import base64
import io
from odoo.http import Response



class PmStudentPaymentSummaryReport(models.AbstractModel):
    _name = 'report.pm_students.payment_summary_report'
    _description = 'Payment Summary Report'
    _inherit = 'report.report_xlsx.abstract'

    def get_months(self, month):
        res = []
        start_month = int
        end_month = int
        if 1 <= month <= 6:
            start_month = 1
            end_month = 6
        elif 7 <= month <= 12:
            start_month = 7
            end_month = 12

        for month_idx in range(start_month, end_month + 1):
            res.append({'month': month_idx, 'month_name': calendar.month_abbr[month_idx]})

        return res

    def generate_xlsx_report(self, workbook, data, students):
        form = data['form']
        print(data)
        student_ids = form['student']
        fees = self.env['pm.student.fee'].search([('student_id', 'in', student_ids)])
        paids = self.get_paid_invoices(fees)
        months = self.get_months(int(form['month']))

        sheet = workbook.add_worksheet('Student Payment Report')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#fffbed', 'border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 13, 'bg_color': '#f2eee4', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        sheet.merge_range('B2:J2', 'Student Detail', title)
        sheet.write('K2', 'Nature of school', title)
        sheet.merge_range('L2:AF2', 'Payments status', title)

        row = 2
        col = 1

        # Header row
        sheet.set_column(2, 4, 20)
        sheet.set_column(11, 30)
        sheet.set_column(12, 31, 7)
        sheet.write(row, col, 'Status', header_row_style)
        sheet.write(row, col + 1, 'Class', header_row_style)
        sheet.write(row, col + 2, 'Display Name', header_row_style)

        month_row = 5
        month_col = 11
        month_col_end = 32

        for month_idx in range(month_col, month_col_end):
            for month in months:
                print(month['month_name'])
                sheet.write(month_row, month_idx, month['month_name'], header_row_style)








    def get_paid_invoices(self, fees):
        res = {}
        for fee in fees:
            student_name = fee.student_id.name
            product_name = fee.product_id.name
            if student_name not in res:
                res[student_name] = {}
            if product_name not in res[student_name]:
                res[student_name][product_name] = []
            payments = fee.paid_fee_line_ids
            for paid in payments:
                res[student_name][product_name].append({
                    'month': paid.month,
                    'amount': paid.amount
                })
        print("*********")
        print(res)

    def get_payment_summary(self, fees):
        paid_invoices = {}
        invoice = {}
        for fee in fees:
            if fee.student_id.name not in invoice:
                invoice[fee.student_id.name] = []
            if fee.student_id.name not in paid_invoices:
                paid_invoices[fee.student_id.name] = []
            invoiced = fee.invoiced_fee_line_ids
            for inv in invoiced:
                invoice[fee.student_id.name].append({
                    'month': inv.month,
                    'amount': inv.amount
                })
            paids = fee.paid_fee_line_ids
            for paid in paids:
                paid_invoices[fee.student_id.name].append({
                    'month': paid.month,
                    'amount': paid.amount
                })
        print("***************")
        print(paid_invoices)
        print("***************")
        print(invoice)

        return {'paid': paid_invoices, 'invoiced': invoice}

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     print("hit here !!")
    #     self.excel_template()
    #     form = data['form']
    #     student_ids = form['student']
    #     fees = self.env['pm.student.fee'].search([('student_id', 'in', student_ids)])
    #     paids = self.get_paid_invoices(fees)
    #     # summary = self.get_payment_summary(fees)
    #     # print(paids)
    #
    #     # print(data)
    #     # months = self.get_months(int(form['month']))
    #     # print(months)
    #     # print("**********")


