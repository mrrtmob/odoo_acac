# -*- coding: utf-8 -*-
import datetime
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

date_format = "%Y-%m-%d"
RESIGNATION_TYPE = [('resigned', 'Normal Resignation'),
                    ('fired', 'Fired by the company')]

RESIGNATION_STATE = [('draft', 'Draft'),
                    ('confirm', 'Submitted'),
                    ("first_approved", "1st Acknowledged"),
                    ("second_approved", "2nd Acknowledge"),
                    ('approved', 'Final Confirmation')]

class ResignationType(models.Model):
    _name = 'hr.resignation.type'
    name = fields.Char("Name")


class HrResignation(models.Model):
    _name = 'hr.resignation'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'
    _description = "Resignation"
    resignation_type_id = fields.Many2one('hr.resignation.type', 'Resignation Type')

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id.id,
                                  help='Name of the employee for whom the request is creating')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    help='Department of the employee')
    resign_confirm_date = fields.Date(string="Submitted Date",
                                      help='Date on which the request is confirmed by the employee.',
                                      track_visibility="always")
    approved_revealing_date = fields.Date(string="Approved Last Day Of Employee",
                                          help='Date on which the request is confirmed by the manager.',
                                          track_visibility="always")
    joined_date = fields.Date(string="Join Date", required=False, readonly=True, related="employee_id.joining_date",
                              help='Joining date of the employee.i.e Start date of the first contract')

    expected_revealing_date = fields.Date(string="Last Day of Employee", required=True,
                                          help='Employee requested date on which he is revealing from the company.')
    reason = fields.Text(string="Reason", required=True, help='Specify reason for leaving the company')
    notice_period = fields.Char(string="Notice Period (Days)")
    state = fields.Selection(
        RESIGNATION_STATE,
        string='Status', default='draft', track_visibility="always")
    resignation_type = fields.Selection(selection=RESIGNATION_TYPE, default='resigned', help="Select the type of resignation: normal "
                                                                         "resignation or fired by the company")
    read_only = fields.Boolean(string="check field")
    employee_contract = fields.Char(String="Contract")
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        track_visibility="onchange",
        readonly=False,
        index=True,
    )
    is_assignee = fields.Boolean('Approver', compute="compute_is_approver", readonly=True, default=False)
    approval_record_id = fields.Many2one('pm.approval')

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

    def button_first_approval(self):
        approver = self.get_approver('first_approved')
        return self.write({'state': 'first_approved', 'assigned_to': approver})

    def button_second_approval(self):
        approver = self.get_approver('second_approved')
        return self.write({'state': 'second_approved', 'assigned_to': approver})

    def button_final_approval(self):
        state = 'approved'
        self.get_approver(state)
        employee = self.employee_id
        employee.leaving_date = self.expected_revealing_date
        employee.resign_date = str(datetime.now())
        self.write({'state': state})

        return employee.launch_exit_plan()

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        print(res_user.has_group('hr.group_hr_manager'))
        if res_user.has_group('hr.group_hr_manager'):
            self.read_only = True
        else:
            self.read_only = False
        print(self.read_only)

    # @api.onchange('employee_id')
    # def set_join_date(self):
    #     self.joined_date = self.employee_id.joining_date if self.employee_id.joining_date else ''

    @api.model
    def create(self, vals):
        # assigning the sequence for the record
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.resignation') or _('New')
        res = super(HrResignation, self).create(vals)
        return res

    @api.constrains('employee_id')
    def check_employee(self):
        # Checking whether the user is creating leave request of his/her own
        for rec in self:
            if not self.env.user.has_group('hr.group_hr_user'):
                if rec.employee_id.user_id.id and rec.employee_id.user_id.id != self.env.uid:
                    raise ValidationError(_('You cannot create request for other employees'))

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        # Check whether any resignation request already exists
        for rec in self:
            if rec.employee_id:
                resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                         ('state', 'in', ['confirm', 'approved'])])
                if resignation_request:
                    raise ValidationError(_('There is a resignation request in confirmed or'
                                            ' approved state for this employee'))
                if rec.employee_id:
                    no_of_contract = self.env['hr.contract'].sudo().search([('employee_id', '=', self.employee_id.id)])
                    for contracts in no_of_contract:
                        if contracts.state == 'open':
                            rec.employee_contract = contracts.name
                            rec.notice_period = contracts.notice_days

    @api.constrains('joined_date')
    def _check_dates(self):
        # validating the entered dates
        for rec in self:
            resignation_request = self.env['hr.resignation'].search([('employee_id', '=', rec.employee_id.id),
                                                                     ('state', 'in', ['confirm', 'approved'])])
            if resignation_request:
                raise ValidationError(_('There is a resignation request in confirmed or'
                                        ' approved state for this employee'))

    def confirm_resignation(self):
        if self.joined_date:
            if self.joined_date >= self.expected_revealing_date:
                raise ValidationError(_('Last date of the Employee must be anterior to Joining date'))
            for rec in self:
                assign_to = False
                approval = False
                manager = rec.employee_id.department_id.manager_id.user_id
                approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'hr.resignation')])
                approval = self.env['pm.approval'].create({
                    'approval_type_id': approval_type.id,
                    'record_id': self.id,
                })

                if manager:
                    assign_to = manager
                    approval.approve = manager
                else:
                    assign_to = approval.approve

                rec.write({
                    'assigned_to': assign_to,
                    'state': 'confirm',
                    'resign_confirm_date': str(datetime.now()),
                    'approval_record_id': approval.id,
                })
        else:
            raise ValidationError(_('Please set joining date for employee'))

    def cancel_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    def reject_resignation(self):
        for rec in self:
            rec.state = 'cancel'

    def reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.employee_id.active = True
            rec.employee_id.resigned = False
            rec.employee_id.fired = False

    # def button_final_approval(self):
    #
    #     for rec in self:
    #         if rec.expected_revealing_date and rec.resign_confirm_date:
    #             no_of_contract = self.env['hr.contract'].sudo().search([('employee_id', '=', self.employee_id.id)])
    #             for contracts in no_of_contract:
    #                 if contracts.state == 'open':
    #                     rec.employee_contract = contracts.name
    #                     rec.state = 'approved'
    #                     rec.approved_revealing_date = rec.resign_confirm_date + timedelta(days=contracts.notice_days)
    #                 else:
    #                     rec.approved_revealing_date = rec.expected_revealing_date
    #             # Changing state of the employee if resigning today
    #             if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
    #                 rec.employee_id.active = False
    #                 # Changing fields in the employee table with respect to resignation
    #                 rec.employee_id.resign_date = rec.expected_revealing_date
    #                 if rec.resignation_type == 'resigned':
    #                     rec.employee_id.resigned = True
    #                 else:
    #                     rec.employee_id.fired = True
    #                 # Removing and deactivating user
    #                 if rec.employee_id.user_id:
    #                     rec.employee_id.user_id.active = False
    #                     rec.employee_id.user_id = None
    #
    #             state = 'approved'
    #             approval = self.approval_record_id
    #             approval.state = state
    #
    #         else:
    #             raise ValidationError(_('Please enter valid dates.'))

    def update_employee_status(self):
        resignation = self.env['hr.resignation'].search([('state', '=', 'approved')])
        for rec in resignation:
            if rec.expected_revealing_date <= fields.Date.today() and rec.employee_id.active:
                rec.employee_id.active = False
                # Changing fields in the employee table with respect to resignation
                rec.employee_id.resign_date = rec.expected_revealing_date
                if rec.resignation_type == 'resigned':
                    rec.employee_id.resigned = True
                else:
                    rec.employee_id.fired = True
                # Removing and deactivating user
                if rec.employee_id.user_id:
                    rec.employee_id.user_id.active = False
                    rec.employee_id.user_id = None


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    resign_date = fields.Date('Resign Date', readonly=True, help="Date of the resignation")
    resigned = fields.Boolean(string="Resigned", default=False, store=True,
                              help="If checked then employee has resigned")
    fired = fields.Boolean(string="Fired", default=False, store=True, help="If checked then employee has fired")
