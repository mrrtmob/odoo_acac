# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo import exceptions
from odoo.http import request

_STATE = [('draft', 'Draft'),
            ('submit', 'Submitted'),
            ("first_approved", "First Approval"),
            ("second_approved", "Verified"),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled'),
            ('reject', 'Rejected')
          ]


class SalaryAdvancePayment(models.Model):
    _name = "salary.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', readonly=True, default=lambda self: 'Adv/')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id.id)
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(), help="Submit date")
    reason = fields.Text(string='Reason', help="Reason")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Advance', required=True)
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    record_url = fields.Char('Link', compute='_compute_record_url', store=True)
    exceed_condition = fields.Boolean(string='Exceed than Maximum',
                                      help="The Advance is greater than the maximum percentage in salary structure")
    department = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    help='Department of the employee')
    state = fields.Selection(_STATE, string='Status', default='draft', track_visibility='onchange')
    debit = fields.Many2one('account.account', string='Debit Account')
    credit = fields.Many2one('account.account', string='Credit Account')
    journal = fields.Many2one('account.journal', string='Journal')
    employee_contract_id = fields.Many2one('hr.contract', string='Contract')
    is_hr_user = fields.Boolean('Approver', compute="compute_is_hr_user", readonly=True, default=False)

    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=salary.advance' % (record.id)
            record.record_url = base_url

    def compute_is_hr_user(self):
        self.is_hr_user = False
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('pm_hr.group_human_resource_manager'):
            print('hr', True)
            self.is_hr_user = True
        else:
            print('hr', False)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=False,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        readonly=True,
        track_visibility="onchange",
        index=True,
    )
    is_assignee = fields.Boolean('Approver', compute="compute_is_approver", readonly=True, default=False)
    approval_record_id = fields.Many2one('pm.approval')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        department_id = self.employee_id.department_id.id
        contract = self.env['hr.contract'].sudo().search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'open')
        ])
        self.department = department_id
        self.employee_contract_id = contract.id

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal': domain,
            },

        }
        return result

    def get_approver(self, state):
        approval = self.approval_record_id
        if approval:
            approval.state = state
            self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
            return approval.approve
        else:
            return True

    def submit_to_manager(self):
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'salary.advance')])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
        })
        self.write({
            'state': 'submit',
            'approval_record_id': approval.id,
            'assigned_to': approval.approve
        })

    def cancel(self):
        self.state = 'cancel'

    def reject(self):
        self.state = 'reject'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('salary.advance.seq') or ' '
        res_id = super(SalaryAdvancePayment, self).create(vals)
        return res_id

    @api.depends('assigned_to')
    def compute_is_approver(self):
        if self.env.user == self.assigned_to:
            self.is_assignee = True
        else:
            self.is_assignee = False


    def get_approver(self, state):
        approval = self.approval_record_id
        if approval:
            approval.state = state
            self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
            return approval.approve
        else:
            return True

    def approve_request(self):
        """This Approve the employee salary advance request.
                   """
        emp_obj = self.env['hr.employee']
        address = emp_obj.browse([self.employee_id.id]).address_home_id
        if not address.id:
            raise ValidationError('Define home address for the employee. i.e address under private information of the employee.')
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise ValidationError('Advance can be requested once in a month')
        if not self.employee_contract_id:
            raise ValidationError('Define a contract for the employee')
        struct_id = self.employee_contract_id.struct_id
        adv = self.advance
        amt = self.employee_contract_id.wage
        if adv > amt and not self.exceed_condition:
            raise ValidationError('Advance amount is greater than allotted')

        if not self.advance:
            raise ValidationError('You must Enter the Salary Advance amount')
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'), ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date)])
        if payslip_obj:
            raise ValidationError("This month salary already calculated")

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('Request can be done after "%s" Days From prevoius month salary') % struct_id.advance_date)

        approver = self.get_approver('first_approved')
        return self.write({'state': 'first_approved', 'assigned_to': approver})

    def approve_request_acc_dept(self):
        """This Approve the employee salary advance request from accounting department.
                   """
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise ValidationError('Advance can be requested once in a month')
        if not self.debit or not self.credit or not self.journal:
            raise ValidationError("You must enter Debit & Credit account and journal to approve ")
        if not self.advance:
            raise ValidationError('You must Enter the Salary Advance amount')

        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            reference = request.name
            journal_id = request.journal.id
            move = {
                'narration': 'Salary Advance Of ' + request_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
            }

            debit_account_id = request.debit.id
            credit_account_id = request.credit.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': request_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': request_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move.update({'line_ids': line_ids})
            print("move.update({'line_ids': line_ids})",move.update({'invoice_line_ids': line_ids}))
            draft = move_obj.create(move)
            draft.post()
            self.state = 'approve'
            self.approval_record_id.state = 'approved'
            return True
