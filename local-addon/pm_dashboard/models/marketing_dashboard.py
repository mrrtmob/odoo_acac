from odoo import models, api
from datetime import date


class MarketingDashboard(models.AbstractModel):
    _name = 'marketing.dashboard'

    @api.model
    def get_lead_conversion_top_campaigns(self):
        top_campaigns = self.env['utm.campaign'].search([], order='leads_count desc', limit=4)

        result = []

        for top_campaign in top_campaigns:
            conversions_count = self.env['crm.lead'].search_count(
                [('campaign_id', '=', top_campaign.id),
                 ('type', '=', 'admission')]
            )
            cost_per_conversion = top_campaign.cost / conversions_count if conversions_count > 0 else 0

            result_campaign = {
                'name': top_campaign.name,
                'cost': top_campaign.cost,
                'leads_count': top_campaign.leads_count,
                'cost_per_lead': top_campaign.cost_per_lead,
                'conversions_count': conversions_count,
                'cost_per_conversion': cost_per_conversion
            }

            result.append(result_campaign)

        return result

    @api.model
    def get_student_intake_by_ranks(self):
        first_contact_leads_count = self.env['crm.lead'].search_count([('rank', '=', 'first_contact')])
        potential_leads_count = self.env['crm.lead'].search_count([('rank', '=', 'potential')])
        high_potential_leads_count = self.env['crm.lead'].search_count([('rank', '=', 'high_potential')])

        result = {
            'first_contact_leads_count': first_contact_leads_count,
            'potential_leads_count': potential_leads_count,
            'high_potential_leads_count': high_potential_leads_count
        }

        return result

    @api.model
    def get_ytd_campaigns(self):
        beginning_of_this_year = date(date.today().year, 1, 1)
        ytd_campaigns = self.env['utm.campaign'].search(
            [('create_date', '>=', beginning_of_this_year),
             ('create_date', '<', date.today())],
            order='create_date asc'
        )

        result = []

        for ytd_campaign in ytd_campaigns:
            month_name = ytd_campaign.create_date.strftime("%B")
            month_number = ytd_campaign.create_date.month
            variance = ytd_campaign.budget - ytd_campaign.cost
            result_campaign = {
                'name': ytd_campaign.name,
                'month_name': month_name,
                'month_number': month_number,
                'budget': ytd_campaign.budget,
                'cost': ytd_campaign.cost,
                'variance': variance
            }

            result.append(result_campaign)

        return result
