# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from datetime import datetime, time
from dateutil.relativedelta import relativedelta



class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _get_number_of_days(self, date_from, date_to, employee_id):
        print("Hit Me !!")
        if self.holiday_status_id.exclude_public_holidays or not self.holiday_status_id:
            instance = self.with_context(
                employee_id=employee_id, exclude_public_holidays=True
            )
        else:
            instance = self
        return super(HrLeave, instance)._get_number_of_days(
            date_from, date_to, employee_id
        )

class HrLeaveAllocationCustom(models.Model):
    _inherit = "hr.leave.allocation"

    def _update_accrual(self):
        print('Yikes')


        """
            Method called by the cron task in order to increment the number_of_days when
            necessary.
        """
        today = fields.Date.from_string(fields.Date.today())
        #
        # public_holidy_obj = self.env['hr.holidays.public']
        # ph_this_month = public_holidy_obj.get_holidays_list_by_month(today.month)
        #
        # print(ph_this_month)


        holidays = self.search(
            [('allocation_type', '=', 'accrual'), ('employee_id.active', '=', True), ('state', '=', 'validate'),
             ('holiday_type', '=', 'employee'),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             '|', ('nextcall', '=', False), ('nextcall', '<=', today)])

        print(holidays)

        for holiday in holidays:
            values = {}

            delta = relativedelta(days=0)

            if holiday.interval_unit == 'weeks':
                delta = relativedelta(weeks=holiday.interval_number)
            if holiday.interval_unit == 'months':
                delta = relativedelta(months=holiday.interval_number)
            if holiday.interval_unit == 'years':
                delta = relativedelta(years=holiday.interval_number)

            values['nextcall'] = (holiday.nextcall if holiday.nextcall else today) + delta

            period_start = datetime.combine(today, time(0, 0, 0)) - delta
            period_end = datetime.combine(today, time(0, 0, 0))


            # We have to check when the employee has been created
            # in order to not allocate him/her too much leaves
            start_date = holiday.employee_id._get_date_start_work()
            # If employee is created after the period, we cancel the computation
            if period_end <= start_date:
                holiday.write(values)
                continue

            # If employee created during the period, taking the date at which he has been created
            if period_start <= start_date:
                period_start = start_date


            employee = holiday.employee_id

            start_date = period_start.date()
            end_date = period_end.date()
            public_holidy_obj = self.env['hr.holidays.public']
            ph_this_month = public_holidy_obj.get_number_of_holidays(start_date, end_date)


            worked = employee._get_work_days_data_batch(
                period_start, period_end,
                domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')]
            )[employee.id]['days']
            left = employee._get_leave_days_data_batch(
                period_start, period_end,
                domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')]
            )[employee.id]['days']
            prorata = worked / (left + worked) if worked else 0

            employee.ph_remaining = employee.ph_remaining + ph_this_month

            days_to_give = holiday.number_per_interval + ph_this_month
            print('PH earn', ph_this_month)
            print('Day', days_to_give)
            if holiday.unit_per_interval == 'hours':
                # As we encode everything in days in the database we need to convert
                # the number of hours into days for this we use the
                # mean number of hours set on the employee's calendar
                days_to_give = days_to_give / (employee.resource_calendar_id.hours_per_day or HOURS_PER_DAY)

            values['number_of_days'] = holiday.number_of_days + days_to_give * prorata
            if holiday.accrual_limit > 0:
                values['number_of_days'] = min(values['number_of_days'], holiday.accrual_limit)

            holiday.write(values)
