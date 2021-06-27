# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

APPROVAL_STATE =    [("draft", "Draft"),
                    ("pending", "Pending"),
                    ("quote_gathering", "Quote Gathering"),
                    ("quote_submitted", "Quote Submitted"),
                    ("submitted", "Submitted"),
                    ("to approve", "Final Approval"),
                    ("first_approved", "First Approval"),
                    ("second_approved", "Final Approval"),
                    ("to_approve_first", "First Approval"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("done", "Done")]

class PmApprovalType(models.Model):
    _name = 'pm.approval.type'
    _description = 'Approval Type'
    name = fields.Char('Name')
    description = fields.Char('Description')
    base_model = fields.Many2one('ir.model', 'Base Model')
    approval_rule_ids = fields.One2many('pm.approval.rule', 'approval_type_id', 'Approval Rules(s)')
    type = fields.Selection([
        ('culinary', 'Culinary'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ], required=False)
    show_type = fields.Boolean(compute='_compute_show_type', default=False)
    show_pr_state = fields.Boolean(compute='_compute_show_type', default=False)
    show_po_state = fields.Boolean(compute='_compute_show_type', default=False)


    @api.depends('base_model')
    def _compute_show_type(self):
        for record in self:
            record.show_type = False
            record.show_po_state = False
            record.show_pr_state = False
            record.show_resign_state = False

            if record.base_model.model == 'purchase.request':
                    record.show_pr_state = True
                    record.show_type = True
            if record.base_model.model == 'purchase.order':
                    record.show_type = True
                    record.show_po_state = True


class PmApproval(models.Model):
    _name = 'pm.approval'
    _description = 'Approval'
    _order = 'id desc'
    name = fields.Char('Name', compute="_compute_record_name", store=True)
    record_id = fields.Integer('Record ID')
    approval_type_id = fields.Many2one('pm.approval.type', 'Approval Types')
    state = fields.Selection(
        APPROVAL_STATE
        , 'State', default='pending', track_visibility='onchange')
    approve = fields.Many2one('res.users', 'Approve By', readonly=True, compute='_compute_approve', store=True)
    procurement_type = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], readonly=False)

    @api.depends('approval_type_id')
    def _compute_record_name(self):
        for record in self:
            base_model = record.approval_type_id.base_model.model
            record_ref = self.env[base_model].browse(record.record_id)
            if record_ref:
                if base_model == 'op.discipline':
                   record.name = record_ref.misbehaviour_category_id.name
                else:
                    record.name = record_ref.name

    @api.depends('state',
                 'approval_type_id.approval_rule_ids.approve_id',
                 'approval_type_id.approval_rule_ids.state')
    def _compute_approve(self):
        for record in self:
            model = record.approval_type_id.base_model.model
            print('hit po')
            print(model)
            if model == 'purchase.request':
                print(22)
                for approve_rule in record.approval_type_id.approval_rule_ids:
                    if approve_rule.pr_state == record.state:
                        record.approve = approve_rule.approve_id

            if model == 'purchase.order':
                for approve_rule in record.approval_type_id.approval_rule_ids:
                    print('---------------Rule State-----------')
                    print(approve_rule.po_state)
                    print('---------------PO State-----------')
                    print(record.state)
                    if approve_rule.po_state == record.state and approve_rule.procurement_type == record.procurement_type:
                        print('hit condition')
                        record.approve = approve_rule.approve_id

            else:
                print(11)
                for approve_rule in record.approval_type_id.approval_rule_ids:
                    if approve_rule.state == record.state:
                        record.approve = approve_rule.approve_id

    @api.model
    def view_record(self, id):
            record_ref = self.browse(id)
            model = record_ref.approval_type_id.base_model.model
            print(model)
            if model == 'op.discipline':
                action = self.env.ref('openeducat_discipline.act_open_op_discipline_view')
                form = self.env.ref('openeducat_discipline.view_op_discipline_form', False)
            elif model == 'pm.recipe':
                action = self.env.ref('pm_culinary.pm_view_recipe_action')
                form = self.env.ref('pm_culinary.view_pm_recipe_form', False)
            elif model == 'pm.menu':
                action = self.env.ref('pm_culinary.menu_action')
                form = self.env.ref('pm_culinary.pm_menu_view_form', False)
            elif model == 'pm.schedule':
                action = self.env.ref('pm_culinary.schedule_action')
                form = self.env.ref('pm_culinary.pm_schedule_view_form', False)
            elif model == 'purchase.request':
                action = self.env.ref('purchase_request.purchase_request_form_action')
                form = self.env.ref('purchase_request.view_purchase_request_form', False)
            elif model == 'purchase.order':
                action = self.env.ref('purchase.purchase_form_action')
                form = self.env.ref('purchase.purchase_order_form', False)

            elif model == 'hr.resignation':
                action = self.env.ref('hr_resignation.view_employee_resignation')
                form = self.env.ref('hr_resignation.employee_resignation_form', False)

            elif model == 'pm.recruiting.request':
                action = self.env.ref('pm_hr.pm_hr_recruiting_action')
                form = self.env.ref('pm_hr.view_recruitment_request_form', False)

            elif model == 'hr.job':
                action = self.env.ref('hr_recruitment.action_hr_job_config')
                form = self.env.ref('hr.view_hr_job_form', False)

            elif model == 'salary.advance':
                action = self.env.ref('ohrms_salary_advance.action_my_salary_advance')
                form = self.env.ref('ohrms_salary_advance.view_salary_advance_form', False)

            else:
                raise ValidationError("Record Not Found!")
            return {
                'name': action.name,
                'help': action.help,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(form.id, 'form')],
                'res_model': action.res_model,
                'res_id': record_ref.record_id,
                'target': 'current',
                'context': {},
            }

class PmApprovalRule(models.Model):
    _name = 'pm.approval.rule'
    _description = 'Approval Rule'
    name = fields.Text(string='Description')
    state = fields.Selection([
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('first_approved', 'First Approval'),
        ('second_approved', 'Second Approval'),
        ('approved', 'Approved')], 'State', default='pending', track_visibility='onchange', required=False)
    pr_state = fields.Selection([
        ("pending", "Pending"),
        ("quote_gathering", "Quote Gathering"),
        ("quote_submitted", "Quote Submitted"),
        ("submitted", "Submitted"),
        ("to_approve", "To Approve"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("done", "Done")],
        'State',
        track_visibility='onchange')
    po_state = fields.Selection([
        ("to_approve_first", "First Approval"),
        ("to approve", "Final Approval"),
        ("purchase", "Approved")],
        'Purchase Order State')

    approve_id = fields.Many2one('res.users', string='Approved By', tracking=True, required=False)
    type = fields.Selection([
        ('culinary', 'Culinary'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ], required=False)
    procurement_type = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], readonly=False)
    approval_type_id = fields.Many2one('pm.approval.type', 'Approval Types')
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection(
        [('line_section', "Section"),
         ('line_note', "Note")],
        default=False,
        help="Technical field for UX purpose."
    )




