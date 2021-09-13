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
                                 'Product(s)',
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




class PMStudentFeeLine(models.Model):
    _name = 'pm.student.fee.line'
    student_fee_id = fields.Many2one(comodel_name='pm.student.fee')
    amount = fields.Monetary()
    invoice_id = fields.Many2one('account.move', 'Invoice ID')
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


