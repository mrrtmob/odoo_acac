# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
import time
import datetime
import calendar
from odoo import api, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import date, datetime, time ,timedelta

class RepairReport(models.AbstractModel):
    _name = 'report.abs_monthly_attendance_report.emoloyee_report'
    _description = "Maintenance summary"

    def get_employee_leaves(self, employee, date_from, date_to):

        leave_count = self.env['hr.leave'].search_count([
            ('employee_id', '=', employee.id),
            ('request_date_from', '>=', date_from),
            ('request_date_from', '<=', date_to),
            ('state', '=', 'validate'),
        ])

        return leave_count



    #Get employee report value function
    def _get_report_values(self, docids, data=None):
        employee_ids = False
        manager_ids = False
        departments = False
        doc_model = False
        docs = False
        month = False
        self.model = self.env['hr.employee']
        if docids:
            active_id = docids
            docs = self.env['employe.order'].browse(docids)
            if docs:
                employee_ids = self.env['hr.employee'].search([])
                if employee_ids:
                    manager_ids = []
                    departments = []
                    for employee in employee_ids:
                        total_hour = 0
                        month_date=date(int(docs.year),int(docs.month),1)
                        docs.date_from=month_date.replace(day=1)
                        docs.date_to=month_date.replace(day=calendar.monthrange(month_date.year,month_date.month)[1])

                        attendaces = self.env['hr.attendance'].search([
                            ('employee_id', '=', employee.id),
                            ('create_date', '>=', docs.date_from),
                            ('create_date', '<=', docs.date_to),
                        ])
                        if attendaces:

                            leave_days = self.get_employee_leaves(employee, docs.date_from, docs.date_to)
                            print('Total leave', leave_days)
                            hours = attendaces.mapped('worked_hours')
                            total_hour = sum(hours)
                            print(employee.name)
                            print(hours)
                            print(total_hour)
                            employee.total_att_hour = total_hour
                            employee.present_day = len(attendaces)
                            today = docs.date_from
                            day = date(int(docs.year), int(docs.month), 1)
                            single_day = timedelta(days=1)
                            dayss = 0
                            while day.month == today.month:
                                if day.isoweekday() == 7:
                                    dayss += 1
                                day += single_day

                            week_day = dayss
                            print(week_day)
                            monthday = docs.date_to - docs.date_from
                            monthday += timedelta(days=1)
                            total_day = (monthday.days) - week_day - leave_days
                            total_hour = total_day * employee.resource_calendar_id.hours_per_day
                            employee.total_day = total_day
                            employee.total_hour = round(total_hour, 2)

                        if employee.parent_id and employee.parent_id not in manager_ids:
                            manager_ids.append(employee.parent_id)
                            month = calendar.month_name[int(docs.month)]

                        if employee.department_id and employee.department_id not in departments:
                            departments.append(employee.department_id)

        print("*************")
        print(departments)

        return {
                   'manager_ids': manager_ids,
                   'employee_ids': employee_ids,
                   'department_ids': departments,
                   'doc_model': self.model,
                   'docks': docs,
                   'month': month,
                   }
