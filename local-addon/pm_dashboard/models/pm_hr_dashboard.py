from odoo import fields, models, api
from datetime import timedelta, datetime, date
import pandas as pd
from dateutil.relativedelta import relativedelta
from odoo.http import request
from itertools import groupby
from operator import itemgetter
import calendar


class HrDashboard(models.Model):
    _name = 'pm.hr.dashboard'

    @api.model
    def get_employee_data(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        employees_count = self.env['hr.employee'].search_count([('active', '=', 't')])
        contract_count = self.env['hr.contract'].search_count([('state', '=', 'open')])
        job_applicant = self.env['hr.applicant'].search_count([('stage_id', '!=', 6)])
        leaves_alloc_req = self.env['hr.leave.allocation'].sudo().search_count(
            [('state', 'in', ['confirm', 'validate1'])])

        leaves_to_approve = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        today = datetime.strftime(datetime.today(), '%Y-%m-%d')

        probation_count = self.env['hr.employee'].search_count([('contract_id.trial_date_end', '>', today)])

        total_outstanding_leave = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1']),
                                                                            ('request_date_from', '>', today)])

        leaves_to_approve = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])

        query = """
                select count(id)
                from hr_leave
                WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s') and 
                state='validate'""" % (today, today)
        cr = self._cr
        cr.execute(query)
        leaves_today = cr.fetchall()
        first_day = date.today().replace(day=1)
        last_day = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)
        query = """
                        select count(id)
                        from hr_leave
                        WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s')
                        and  state='validate'""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        leaves_this_month = cr.fetchall()
        print('leaves_this_month sssssssssssss: ', leaves_this_month)

        # leaves_to_approve = self.env[''].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        result = {
            'employees_count': employees_count,
            'probation_count': probation_count,
            'contract_count': contract_count,
            'job_applicant': job_applicant,
            'leaves_to_approve': leaves_to_approve,
            'leaves_alloc_req': leaves_alloc_req,
            'leaves_today': leaves_today,
            'leaves_this_month': leaves_this_month,
            'total_outstanding_leave': total_outstanding_leave,
            'employee': employee
        }


        return result

    @api.model
    def get_dept_employee(self):
        cr = self._cr
        cr.execute("""select department_id, hr_department.name,count(*) 
    from hr_employee join hr_department on hr_department.id=hr_employee.department_id 
    group by hr_employee.department_id,hr_department.name""")
        dat = cr.fetchall()
        data = []
        for i in range(0, len(dat)):
            data.append({'label': dat[i][1], 'value': dat[i][2]})
        return data

    @api.model
    def get_department_leave(self):
        types = ['in_invoice', 'in_refund']
        # Fetch Bill
        bills = self.env['account.move'].search([('move_type', 'in', types)])
        data = {}
         #Loop bill & group by vendor name
        for bill in bills:
             vendor = bill.invoice_partner_display_name
             if vendor not in data:
                 data[vendor] = bill.amount_total
             else:
                 data[vendor] += bill.amount_total



        query = """
                       SELECT SUM(amount_total) as total, invoice_partner_display_name as vendor
                        FROM account_move where move_type IN ('in_invoice', 'in_refund')
                        GROUP BY invoice_partner_display_name """

        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()

        print("Res")
        print(results)
        print("data")
        print(data)



        month_list = []
        now = datetime.today()
        year = datetime.strftime(now, '%Y')
        month = datetime.strftime(now, '%m')
        first_day = now.replace(day=1)
        last_day = calendar.monthrange(2021, int(month))[1]
        date_from = datetime.strftime(first_day - relativedelta(months=5), '%Y-%m-%d')
        # date_to = datetime.strftime(datetime(int(year), int(month), int(last_day)), '%Y-%m-%d')
        date_to = datetime.strftime(now, '%Y-%m-%d')
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%b %Y')
            month_list.append(text)
        hr_leave = []
        # ('state', 'in', ['confirm', 'validate1'])
        leaves = self.env['hr.leave'].sudo().search([('state', '=', 'validate'),
                                                     ('date_from', '>', date_from),
                                                     ('date_from', '<', date_to),
                                                     ('department_id', '!=', 'null')])

        department_list = []
        raw_department = self.env['hr.department'].search([('active', '=', 't')])
        for department in raw_department:
            department_list.append({'id': department['id'], 'name': department['name']})

        print('department_list: ', department_list)

        for leave in leaves:
            l_id = leave['id']
            month_year = datetime.strftime(leave['date_from'], '%b %Y')
            department = leave['department_id']['name']
            department_id = leave['department_id']['id']
            hr_leave.append({'id': l_id, 'l_month': month_year, 'department': department, 'department_id': department_id})

        data = []
        for i_department in department_list:
            leaves_by_department = [d for d in hr_leave if d['department_id'] == i_department['id']]
            cal_percentage = 0
            if len(leaves_by_department) and len(hr_leave):
                cal_percentage = (len(leaves_by_department) * 100) / len(hr_leave)

            data.append({
                'name': i_department['name'],
                'leaves_data': leaves_by_department,
                'count': len(leaves_by_department),
                'percentage': "{:.0f}".format(cal_percentage)
            })

        results = {
            'month_list': month_list,
            'total_leaves': len(hr_leave),
            'department_list': department_list,
            'data': data
        }
        return results

    @api.model
    def join_resign_trends(self):
        cr = self._cr
        month_list = []
        join_trend = []
        resign_trend = []
        for i in range(11, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            join_trend.append(vals)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            resign_trend.append(vals)
        cr.execute('''select to_char(joining_date, 'Month YYYY') as l_month, count(id) from hr_employee 
            WHERE joining_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
            AND CURRENT_DATE + interval '1 month - 1 day'
            group by l_month''')
        join_data = cr.fetchall()
        cr.execute('''select to_char(resign_date, 'Month YYYY') as l_month, count(id) from hr_employee 
            WHERE resign_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
            AND CURRENT_DATE + interval '1 month - 1 day'
            group by l_month;''')
        resign_data = cr.fetchall()

        for line in join_data:
            match = list(filter(lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ', ''), join_trend))
            if match:
                match[0]['count'] = line[1]
        for line in resign_data:
            match = list(filter(lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ', ''), resign_trend))
            if match:
                match[0]['count'] = line[1]
        for join in join_trend:
            join['l_month'] = join['l_month'].split(' ')[:1][0].strip()[:3]
        for resign in resign_trend:
            resign['l_month'] = resign['l_month'].split(' ')[:1][0].strip()[:3]
        graph_result = [{
            'name': 'Join',
            'values': join_trend
        }, {
            'name': 'Resign',
            'values': resign_trend
        }]
        return graph_result

    @api.model
    def get_attrition_rate(self):
        month_attrition = []
        monthly_join_resign = self.join_resign_trends()
        month_join = monthly_join_resign[0]['values']
        month_resign = monthly_join_resign[1]['values']
        sql = """
            SELECT (date_trunc('month', CURRENT_DATE))::date - interval '1' month * s.a AS month_start
            FROM generate_series(0,11,1) AS s(a);"""
        self._cr.execute(sql)
        month_start_list = self._cr.fetchall()
        for month_date in month_start_list:
            self._cr.execute("""select count(id), to_char(date '%s', 'Month YYYY') as l_month from hr_employee
                where resign_date> date '%s' or resign_date is null and joining_date < date '%s'
                """ % (month_date[0], month_date[0], month_date[0],))
            month_emp = self._cr.fetchone()
            # month_emp = (month_emp[0], month_emp[1].split(' ')[:1][0].strip()[:3])
            match_join = \
                list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_join))[0][
                    'count']
            match_resign = \
                list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_resign))[0][
                    'count']
            month_avg = (month_emp[0] + match_join - match_resign + month_emp[0]) / 2
            attrition_rate = (match_resign / month_avg) * 100 if month_avg != 0 else 0
            vals = {
                # 'month': month_emp[1].split(' ')[:1][0].strip()[:3] + ' ' + month_emp[1].split(' ')[-1:][0],
                'month': month_emp[1].split(' ')[:1][0].strip()[:3],
                'attrition_rate': round(float(attrition_rate), 2)
            }
            month_attrition.append(vals)

        return month_attrition

    @api.model
    def get_employee_chart_data(self):
        now = datetime.now()
        today = datetime.strftime(datetime.today(), '%Y-%m-%d')
        start_date_last_year = date(now.year - 1, 1, 1)
        end_date_last_year = date(now.year - 1, 12, 31)
        start_date_this_year = date(now.year, 1, 1)

        employees = self.env['hr.employee']

        probation_count = employees.search_count([('contract_id.trial_date_end', '>', today), ('active', '=', 't')])
        contract_count = self.env['hr.contract'].search_count([('state', '=', 'open')])

        male_employee = employees.search_count([('gender', '=', 'male'), ('active', '=', 't')])
        female_employee = employees.search_count([('gender', '=', 'female'), ('active', '=', 't')])

        cambodian_employee = employees.search_count([('country_id', 'in', [116, 260]), ('active', '=', 't')])
        expat_employee = employees.search_count([('country_id', '!=', 116), ('country_id', '!=', 260), ('active', '=', 't')])

        turnover_rate_last_year = 0
        employees_start_last_year = employees.search_count([('joining_date', '=', start_date_last_year)])
        employees_end_last_year = employees.search_count([('joining_date', '<', end_date_last_year)])
        employees_left_last_year = employees.search_count([('joining_date', '<', end_date_last_year),
                                                           ('active', '!=', 't')])
        if employees_start_last_year > 0 or employees_end_last_year > 0:
            turnover_rate_last_year = employees_left_last_year / (
                        (employees_start_last_year + employees_end_last_year) / 2)

        turnover_rate_this_year = 0
        employees_start_this_year = employees.search_count([('joining_date', '=', start_date_this_year)])
        employees_end_this_year = employees.search_count([('joining_date', '<', today)])
        employees_left_this_year = employees.search_count([('joining_date', '<', today), ('active', '!=', 't')])
        if employees_start_this_year > 0 or employees_end_this_year > 0:
            turnover_rate_this_year = employees_left_this_year / (
                        (employees_start_this_year + employees_end_this_year) / 2)

        employee_by_contract = {
            'labels': ['Probation', 'Contracted'],
            'probation': probation_count,
            'contract': contract_count,
            'data': [probation_count, contract_count]
        }

        employee_by_gender = {
            'labels': ['Male', 'Female'],
            'male': male_employee,
            'female': female_employee,
            'data': [male_employee, female_employee]
        }

        employee_by_nationality = {
            'labels': ['Cambodian', 'Expats'],
            'cambodian': cambodian_employee,
            'expat': expat_employee,
            'data': [cambodian_employee, expat_employee]
        }

        turnover_rate = {
            'labels': ['Last Year', 'This Year'],
            'last_year': "{:.2f}".format(turnover_rate_last_year),
            'this_year': "{:.2f}".format(turnover_rate_this_year),
            'data': ["{:.2f}".format(turnover_rate_last_year), "{:.2f}".format(turnover_rate_this_year)],
        }

        return {
            'employee_by_contract': employee_by_contract,
            'employee_by_gender': employee_by_gender,
            'employee_by_nationality': employee_by_nationality,
            'turnover_rate': turnover_rate
        }

    @api.model
    def get_job_position(self):
        cr = self._cr
        cr.execute("""select department_id, hr_department.name,count(*) 
           from hr_job join hr_department on hr_department.id=hr_job.department_id 
           group by hr_job.department_id,hr_department.name""")
        dat = cr.fetchall()
        data = []
        for i in range(0, len(dat)):
            data.append({'label': dat[i][1], 'value': dat[i][2]})
        return data

    @api.model
    def get_hr_events(self):
        today = datetime.strftime(datetime.today(), '%Y/%m/%d')
        ten_day_ago = datetime.now() - timedelta(days=10)
        # print('ten_day_ago: ', ten_day_ago)

        onboarding_checklist = []
        offboarding_checklist = []
        onboarding = self.env['mail.activity'].search([
            ('res_model', '=', 'hr.employee'),
            ('date_deadline', '<', today),
            ('plan_type', '=', 'on'),
        ])
        offboarding = self.env['mail.activity'].search([
            ('res_model', '=', 'hr.employee'),
            ('date_deadline', '<', today),
            ('plan_type', '=', 'off'),
        ])

        if onboarding and offboarding:

            for index, on in enumerate(onboarding):
                onboarding_checklist.append({
                    'name': on['summary'],
                    'no': index + 1,
                    'owner': on['user_id']['partner_id']['name'],
                    'expired_date': on['date_deadline']
                })
            for index, off in enumerate(offboarding):
                offboarding_checklist.append({
                    'name': off['summary'],
                    'no': index + 1,
                    'owner': on['user_id']['partner_id']['name'],
                    'expired_date': on['date_deadline']
                })

        probation = []
        probation_list = self.env['hr.employee'].search([('contract_id.trial_date_end', '>', ten_day_ago),
                                                         ('contract_id.trial_date_end', '<', today)])
        for pro in probation_list:
            d = pro['contract_id']['trial_date_end']
            d_left = 0
            if d:
                d_calc = date(datetime.today().year, datetime.today().month, datetime.today().day) - \
                         date(d.year, d.month, d.day)
                d_left = d_calc.days
            probation.append({
                'name': pro['name'],
                'trial_date_end': datetime.strftime(d, '%Y/%m/%d'),
                'days_left': d_left
            })
        print('probation: ', probation)

        result = {
            'probation': probation,
            'onboarding': onboarding_checklist,
            'offboarding': offboarding_checklist
        }
        return result

    @api.model
    def get_outstanding_leave(self):
        today = datetime.strftime(datetime.today(), '%Y/%m/%d')
        outstanding_leave = []
        result = []
        total_outstanding_leave = self.env['hr.leave'].sudo().search([('state', 'in', ['confirm', 'validate1']),
                                                                      ('request_date_from', '>', today)])
        for total in total_outstanding_leave:
            outstanding_leave.append({
                'department_id': total['department_id']['id'],
                'department': total['department_id']['name']
            })
        sorted_outstanding = sorted(outstanding_leave, key=itemgetter('department'))
        for key, value in groupby(sorted_outstanding, key=itemgetter('department')):
            result.append({'department': key, 'count': len(list(value))})

        return result


