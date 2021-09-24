# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Campaign(models.Model):
    _inherit = 'utm.campaign'

    cost = fields.Float('Actual Cost')
    cost_per_lead = fields.Float(String="Cost per lead", compute='_get_cost_per_lead', store=True , digits=(12, 2))
    budget = fields.Float('Plan Budget')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    description = fields.Char('Description')

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.start_date)
            end_date = fields.Date.from_string(record.end_date)
        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                _("End Date cannot be set before Start Date."))



    @api.depends('cost', 'crm_lead_count')
    def _get_cost_per_lead(self):
        for rec in self:
            print("Yo")
            rec.cost_per_lead = rec.cost / rec.crm_lead_count
            print(rec.cost_per_lead )
