# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class Campaign(models.Model):
    _inherit = 'utm.campaign'

    cost = fields.Float('Actual Cost')
    cost_per_lead = fields.Float(String="Cost per lead", compute='_get_cost_per_lead', store=True)
    lead_ids = fields.One2many('crm.lead', 'campaign_id', 'Leads')
    leads_count = fields.Integer(compute='_get_leads_count', store=True)
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

    @api.depends('lead_ids.campaign_id')
    def _get_leads_count(self):
        for record in self:
            record.leads_count = len(record.lead_ids)

    @api.depends('cost', 'leads_count')
    def _get_cost_per_lead(self):
        for r in self:
            r.cost_per_lead = 0

            if r.leads_count > 0:
                r.cost_per_lead = r.cost / r.leads_count
