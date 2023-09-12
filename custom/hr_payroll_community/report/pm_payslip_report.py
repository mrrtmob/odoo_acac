#-*- coding:utf-8 -*-

from odoo import api, models

class PMPayslipReport(models.AbstractModel):
    _name = 'report.pm_general.pm_report_payslipdetails'
    _description = 'Payslip Report'

    def get_employee_detail(self, payslip):
        employee = payslip.employee_id
        allocation = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', employee.id),
            ('holiday_status_id.name', '=', 'AL'),
            ('holiday_status_id.active', '=', True),
            ('state', '=', 'validate'),
        ], limit=1)
        print(allocation)

        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('holiday_status_id.code', '=', 'AL'),
            ('request_date_from', '>=', payslip.date_from),
            ('request_date_from', '<=', payslip.date_to),
            ('state', '=', 'validate'),
        ])

        leaves_this_month = sum(leaves.mapped('number_of_days'))
        earn_this_month = allocation.number_per_interval
        remaining = employee.remaining_leaves
        previous_balance = remaining + (earn_this_month - leaves_this_month)


        print("AL Earned This Month", earn_this_month)
        print("AL Taken This Month", leaves_this_month)
        print("Remaining Balance", remaining)
        print("Previous Balance", previous_balance)

        data = {
            'al_earned': earn_this_month,
            'al_taken': float(leaves_this_month),
            'al_remaining': remaining,
            'al_previous': previous_balance,
            'name': employee.name,
            'number': employee.employee_number,
            'position': employee.job_title,
            'department': employee.department_id.name,
            'join_date': employee.joining_date,
            'nssf_no': employee.nssf_no,
            'bank_no': employee.bank_account_no,
            'tax_income_no': employee.tax_income_no
        }
        print(data)
        return data
    def get_payslip_lines(self, payslip):
        lines = payslip.line_ids
        benefit = []
        deduct = []
        company_contribution = []
        net = 0
        gross = 0
        addition = []
        termination = []
        other_addition = 0
        other_deduction = 0
        for line in lines:
            if line.total != 0:
                if line.code == 'BASIC':
                    gross = line.total
                elif line.code == 'NET':
                    net = line.total

                elif line.code == 'ADDS':
                    other_addition = line.total

                elif line.code == 'DEDS':
                    print("OD")
                    other_deduction = line.total * -1
                    print(other_deduction)

                elif line.code in ['TP', 'TPOSP', 'TPSP']:
                    termination.append(line.total)

                elif line.category_id.code == 'ALW':
                    benefit.append(line.total)
                elif line.category_id.code == 'DED':
                    print("hit deduct rule")
                    deduct.append({
                        'name': line.name,
                        'total': line.total * -1
                    })

                elif line.category_id.code == 'ADDS':
                    addition.append({
                        'name': line.name,
                        'total': +line.total
                    })

                elif line.category_id.code == 'COMP':
                    company_contribution.append({
                        'name': line.name,
                        'total': +line.total
                    })

        addition.append({'name': 'Benefits', 'total': sum(benefit)})
        addition.append({'name': 'Termination Payment', 'total': sum(termination)})
        data = {
            'addition': addition,
            'net': net,
            'gross': gross,
            'deduct': deduct,
            'company_contribution': company_contribution,
            'other_addition': other_addition,
            'other_deduction': other_deduction,
        }
        print(data)
        return data



    @api.model
    def _get_report_values(self, docids, data=None):
        payslip = self.env['hr.payslip'].browse(docids)
        date = payslip.date_to
        employee = self.get_employee_detail(payslip)
        paysliip_lines = self.get_payslip_lines(payslip)
        month_name = date.strftime("%B")
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'doc_lines': paysliip_lines,
            'employee': employee,
            'payment_date': date,
            'month': month_name
        }
