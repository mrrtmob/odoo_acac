from odoo import api, fields, models


class LeadConversion(models.Model):
    _name = 'pm_lead_conversion'
    _description = 'Lead Conversion'
    name = fields.Char('Lead Conversion')
    conversion_rate = fields.Float(String="Conversion Rate %", compute='_get_conversion_rate', store=True)

    @api.model
    def _get_conversion_rate(self):
        # calculate conversion rate for dashboard
        convert_rate = self.env['pm_lead_conversion'].search([('id', '=', 1)])
        total = self.env['crm.lead'].search_count([])
        admission = self.env['crm.lead'].search_count([('type', '=', 'admission')])
        if admission > 0:
            # result = admission * 100 / total
            result = (admission / total) * 100
        convert_rate.conversion_rate = result
        return result
