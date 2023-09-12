# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import calendar

class PMStudentFee(models.Model):
    _name = 'pm.student.fee'
    _rec_name = 'product_id'
    student_id = fields.Many2one('op.student', 'Student Name', required=True)
    product_id = fields.Many2one('product.product',
                                 'Product',
                                 domain=[('type', '=', 'service')],
                                 required=True)
    date = fields.Date()
    total_invoiced = fields.Monetary(compute="_compute_total_invoiced", store=True)
    total_paid = fields.Monetary(compute="_compute_total_paid", store=True)
    remaining_balance = fields.Monetary(compute="_compute_remaining_balance", store=True)
    remarks = fields.Text("Remarks")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    invoiced_fee_line_ids = fields.One2many(string="Invoiced", comodel_name='pm.student.fee.line', inverse_name="student_fee_id",
                                            domain=[('status', '=', 'invoiced')])
    paid_fee_line_ids = fields.One2many(string="Paid", comodel_name='pm.student.fee.line', inverse_name="student_fee_id",
                                        domain=[('status', '=', 'paid')])
    remaining_percentage = fields.Integer("Percentage", _compute="_compute_remaining_balance", store=True)

    def batch_generate_payment_reports(self):
        students = self.env['op.student'].search([])
        for student in students:
            student.generate_student_payment()

    @api.depends('paid_fee_line_ids.amount', 'invoiced_fee_line_ids.amount')
    def _compute_total_paid(self):
        for rec in self:
            rec.total_paid = sum(x.amount for x in rec.paid_fee_line_ids)

    @api.depends('paid_fee_line_ids.amount', 'invoiced_fee_line_ids.amount')
    def _compute_total_invoiced(self):
        for rec in self:
            rec.total_invoiced = sum(x.amount for x in rec.invoiced_fee_line_ids)

    @api.depends('total_paid', 'total_invoiced')
    def _compute_remaining_balance(self):
        for rec in self:
            rec.remaining_balance = rec.total_invoiced - rec.total_paid
            if rec.total_paid == 0:
                rec.remaining_percentage = 0
            else:
                rec.remaining_percentage = rec.total_paid/rec.total_invoiced * 100.









class PMStudentFeeLine(models.Model):
    _name = 'pm.student.fee.line'
    student_fee_id = fields.Many2one(comodel_name='pm.student.fee', ondelete='cascade')
    amount = fields.Monetary()
    invoice_id = fields.Many2one('account.move', 'Invoice ID')
    invoiced = fields.Monetary(compute="_compute_report_amount", store=True)
    paid = fields.Monetary(compute="_compute_report_amount", store=True)
    invoice_line_id = fields.Many2one('account.move.line', string="Invoice Line ID")
    product_id = fields.Many2one('product.product',
                                 'Product',
                                 related="student_fee_id.product_id",
                                 domain=[('type', '=', 'service')],
                                 store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    month = fields.Selection([('Jan', 'January'),
                                ('Feb', 'February'),
                                ('Mar', 'March'),
                                ('Apr', 'April'),
                                ('May', 'May'),
                                ('Jun', 'June'),
                                ('Jul', 'July'),
                                ('Aug', 'August'),
                                ('Sep', 'September'),
                                ('Oct', 'October'),
                                ('Nov', 'November'),
                                ('Dec', 'December')])
    date = fields.Date()
    status = fields.Selection([
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
    ])

    @api.depends('amount', 'status')
    def _compute_report_amount(self):
        for rec in self:
            if rec.status == 'paid':
                rec.paid = rec.amount
                rec.invoiced = False
            elif rec.status == 'invoiced':
                rec.invoiced = rec.amount
                rec.paid = False

    def action_get_invoice(self):
        value = True
        if self.invoice_id:
            form_view = self.env.ref('account.view_move_form')
            tree_view = self.env.ref('account.view_invoice_tree')
            value = {
                'domain': str([('id', '=', self.invoice_id.id)]),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                'type': 'ir.actions.act_window',
                'res_id': self.invoice_id.id,
                'target': 'current',
                'nodestroy': True
            }
        return value


