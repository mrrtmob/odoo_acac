# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class TakeAction(models.TransientModel):
    _name = "take.action"
    _description = "Take Action Based on Misbehaviour"

    fine = fields.Boolean('Fine')
    fine_amount = fields.Integer(' Fine Amount')
    suspend = fields.Boolean('Suspend')
    suspend_from_date = fields.Date("Suspend From Date")
    suspend_to_date = fields.Date("Suspend To Date")
    discipline_id = fields.Many2one('op.discipline',
                                    string='Discipline Record')
    action_remark = fields.Text("Remark")

    @api.constrains('suspend_from_date', 'suspend_to_date')
    def check_dates(self):
        if self.suspend:
            for record in self:
                suspend_from_date = \
                    fields.Date.from_string(record.suspend_from_date)
                suspend_to_date = \
                    fields.Date.from_string(record.suspend_to_date)
                if suspend_to_date < suspend_from_date:
                    raise ValidationError(
                        _("To Date cannot be set before From Date."))

    def take_action(self):
        discipline = self.env['op.discipline']. \
            browse([self.env.context.get('active_id', False)])
        if self.fine and not self.suspend:
            self.get_fine_data(discipline)
        elif self.suspend and not self.fine:
            self.get_suspend_data(discipline)
        elif self.suspend and self.fine:
            self.get_fine_data(discipline)
            self.get_suspend_data(discipline)
        else:
            discipline.state = 'done'

    def get_suspend_data(self, discipline):
        suspend = self.env["suspended.student"].create({
            'student_id': discipline.student_id.id,
            'suspend_from_date': self.suspend_from_date,
            'suspend_to_date': self.suspend_to_date,
            'misbehaviour_category_id': discipline.misbehaviour_category_id.id,
            'discipline_id': discipline.id})
        self.ensure_one()
        template = \
            self.env.ref('openeducat_discipline.'
                         'email_suspension_from_school_template',
                         False)
        template.send_mail(suspend.id, force_send=True)
        discipline.state = 'suspended'

    def get_fine_data(self, discipline):
        accounts = self.env['account.move']
        account_id = False
        if self.fine_amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        df_product_1 = self.env.ref('openeducat_discipline.df_product_1')
        invoice = accounts.create({
            'partner_id': discipline.student_id.partner_id.id,
            'type': 'out_invoice',
            'invoice_date': fields.date.today(),

        })
        line_values = {'name': df_product_1.name,
                       'account_id': account_id,
                       'price_unit': self.fine_amount,
                       'quantity': 1.0,
                       'discount': 0.0,
                       'product_uom_id': df_product_1.uom_id.id,
                       'product_id': df_product_1.id, }
        invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
        invoice._compute_invoice_taxes_by_group()
        self.state = 'invoice'
        self.invoice_id = invoice.id
        discipline.state = 'done'
        return True
