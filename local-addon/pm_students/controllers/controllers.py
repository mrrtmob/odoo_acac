# -*- coding: utf-8 -*-
from odoo import http

from collections import deque
import io
import json

from odoo import http
from odoo.http import request
from odoo.tools import ustr
# from odoo.tools.misc import xlsxwriter
import xlsxwriter


class PmStudents(http.Controller):

    @http.route('/student/report/payment', auth='public')
    def excel_template(self):
        output = io.BytesIO()
        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook('Expenses01.xlsx')
        worksheet = workbook.add_worksheet()

        # Some data we want to write to the worksheet.
        expenses = (
            ['Rent', 1000],
            ['Gas', 100],
            ['Food', 300],
            ['Gym', 50],
        )

        # Start from the first cell. Rows and columns are zero indexed.
        row = 0
        col = 0

        # Iterate over the data and write it out row by row.
        for item, cost in (expenses):
            worksheet.write(row, col, item)
            worksheet.write(row, col + 1, cost)
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total')
        worksheet.write(row, 1, '=SUM(B1:B4)')
        print(worksheet)

        workbook.close()
        xlsx_data = output.getvalue()
        response = request.make_response(xlsx_data,
                                         headers=[('Content-Type',
                                                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                                                  ('Content-Disposition', 'attachment; filename=table.xlsx')])

        return response
