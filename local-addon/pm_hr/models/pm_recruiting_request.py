# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("first_approved", "HR Verify"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]



class PmRecruitingRequest(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = 'pm.recruiting.request'
    _description = 'Recruiting Request'

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'pm.recruiting.request')])
        next = sequence.get_next_char(sequence.number_next_actual)
        return next

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    survey_id = fields.Many2one(
        'survey.survey', "Interview Form",
        domain=[('category', '=', 'hr_recruitment')],
        help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")

    name = fields.Char(
        string="Reference",
        required=True,
        default=_get_default_name,
        track_visibility="onchange",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=False,
        default=_company_get,
        track_visibility="onchange",
    )
    appraisal_id = fields.Many2one('hr.appraisal', string="Appraisal Form")

    show_recruitment_form = fields.Boolean(compute='_compute_show_form', default=False)
    show_promotion_form = fields.Boolean(compute='_compute_show_form', default=False)
    show_transfer_form = fields.Boolean(compute='_compute_show_form', default=False)
    show_termination_form = fields.Boolean(compute='_compute_show_form', default=False)
    show_replacement_form = fields.Boolean(compute='_compute_show_form', default=False)

    transfer_to = fields.Many2one('hr.department')
    promoted_to = fields.Many2one('hr.job', domain="[('department_id', '=', transfer_to)]")
    current_wage = fields.Monetary('Current Salary',
                                   related='employee_id.contract_id.wage',
                                   store=True,
                                   currency_field="currency_id",
                                   help="Employee's monthly gross wage.",
                                   readonly=1)
    promoted_wage = fields.Monetary('Promoted Salary', currency_field="currency_id",)
    promotion_date = fields.Date()

    @api.onchange('employee_id')
    def on_change_employee(self):
        employee = self.employee_id
        self.job_position_id = employee.job_id.id
        self.department_id = employee.department_id



    @api.onchange('recruitment_type')
    def _compute_show_form(self):
        self.show_recruitment_form = False
        self.show_promotion_form = False
        self.show_transfer_form = False
        self.show_termination_form = False
        self.show_replacement_form = False
        if self.recruitment_type == 'replacement':
            print(1)
            self.show_replacement_form = True
        elif self.recruitment_type == 'new_position':
            print(2)
            self.show_recruitment_form = True
        elif self.recruitment_type == 'transfer':
            print(3)
            self.show_transfer_form = True
        elif self.recruitment_type == 'promotion':
            print(4)
            self.show_promotion_form = True
        elif self.recruitment_type == 'termination' or 'rehire':
            print(5)
            self.show_termination_form = True

    description = fields.Text()
    start_date = fields.Date('Preferred Start Date')
    department_id = fields.Many2one('hr.department', 'Department')
    job_position_id = fields.Many2one('hr.job', 'Job Position',
                                      domain="[('department_id', '=', department_id)]")
    recruitment_type = fields.Selection([
        ('new_position', 'New Position'),
        ('transfer', 'Transfer'),
        ('promotion', 'Promotion'),
        ('replacement', 'Replacement'),
        ('rehire', 'Rehire'),
        ('termination', 'Termination'),
    ], string='Request Type', default='new_position', required=True)
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    job_description = fields.Html(related='job_position_id.job_description', store=True, readonly=1)
    job_requirement = fields.Html(related='job_position_id.job_requirement', store=True, readonly=1)

    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )

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
    approved_by = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        track_visibility="onchange",
        readonly=True,
        index=True,
    )
    approved_date = fields.Date(
        string="Approved Date",
        track_visibility="onchange",
        readonly=True,
    )
    expected_recruit = fields.Integer('Expected New Employees')
    is_sufficient_budget = fields.Boolean('Sufficient Budget')
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    budget = fields.Monetary(
        string="Budget",
        currency_field="currency_id",
        store=True,
        default=0.0,
    )
    is_additional_budget = fields.Boolean('Requires Additional Budget')
    remarks = fields.Text()
    is_assignee = fields.Boolean('Approver', compute="compute_is_approver", readonly=True, default=False)
    approval_record_id = fields.Many2one('pm.approval')
    read_only = fields.Boolean(string="check field", compute='_compute_read_only')

    @api.depends('state', 'is_assignee')
    def _compute_read_only(self):
        for request in self:
            request.read_only = False
            if request.state != 'draft' and not request.is_assignee:
                request.read_only = True

        print('I am read only')
        print(self.read_only)




    @api.depends('assigned_to')
    def compute_is_approver(self):
        if self.env.user == self.assigned_to:
            self.is_assignee = True
        else:
            self.is_assignee = False



    @api.model
    def create(self, vals):
        #Generate Sequence Code
        vals['name'] = self.env['ir.sequence'].next_by_code('pm.recruiting.request')
        res = super(PmRecruitingRequest, self).create(vals)
        return res

    def get_approver(self, state):
        approval = self.approval_record_id
        approval.state = state
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        return approval.approve

    def button_submit(self):

        if not self.is_sufficient_budget and self.recruitment_type not in ['termination']:
            raise UserError("Please confirm Sufficient Budget")
        state = 'submitted'
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'pm.recruiting.request')])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
        })
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])

        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('pm_hr.group_human_resource_manager'):
            state = 'first_approved'

        return self.write({'state': state, 'assigned_to': approval.approve, 'approval_record_id': approval.id})

    def button_verify(self):
        approver = self.get_approver('first_approved')
        return self.write({'state': 'first_approved', 'assigned_to': approver})

    def button_approve(self):
        for request in self:
            type = request.recruitment_type
            approver = self.env.user
            approve_date = fields.Datetime.now()
            if type == 'promotion':
                promotion_obj = self.env['pm.promotion']
                contract = request.employee_id.contract_id
                print(contract)
                vals = {
                    'employee_id': request.employee_id.id,
                    'promotion_date': request.promotion_date,
                    'new_salary': request.promoted_wage,
                    'previous_designation': request.job_position_id.id,
                    'new_designation': request.promoted_to.id,
                    'previous_salary': request.current_wage,
                    'contract_id': contract.id,
                    'description': request.remarks,
                    'state': 'approved'
                }
                promotion = promotion_obj.create(vals)

            elif type == 'transfer':
                transfer_obj = self.env['pm.transfers']
                vals = {
                    'employee_id': request.employee_id.id,
                    'transfer_date': request.promotion_date,
                    'approved_date': approve_date,
                    'job_id': request.job_position_id.id,
                    'department_id': request.department_id.id,
                    'new_department_id': request.transfer_to.id,
                    'new_job_id': request.promoted_to.id,
                    'new_salary': request.promoted_wage,
                    'remark': request.remarks,
                    'state': 'approved',
                    'approved_by': approver.id,
                }
                print(vals)
                transfer = transfer_obj.create(vals)

            elif type == 'new_position' or type == 'replacement':
                request.job_position_id.write({
                    'status': 'recruit',
                    'no_of_recruitment': self.expected_recruit
                })
                request.message_post_with_view(
                    'pm_hr.recruitment_request_template',
                    values={'request': request})

            elif type == 'termination':
                resign_obj = self.env['hr.resignation']
                contract = request.employee_id.contract_id
                vals = {
                    'employee_id': request.employee_id.id,
                    'expected_revealing_date': request.promotion_date,
                    'employee_contract': contract.name,
                    'resignation_type': 'fired',
                    'reason': request.remarks,
                    'state': 'approved',
                }
                resignation = resign_obj.create(vals)
                resignation.button_final_approval()
            request.get_approver('approved')

        return self.write({'state': 'approved', 'approved_by': approver, 'approved_date': approve_date})




