from odoo import fields, models, api


class JobOfferLetter(models.AbstractModel):
    _name = 'report.pm_hr.offer_letter_report'
    _description = 'Description'

    def get_applicant_data(self, applicant_id):
        applicant = self.env['hr.applicant'].browse(applicant_id)
        if applicant:
            data = {
                'name': applicant.partner_name,
                'salary': applicant.wage,
                'period': applicant.contract_period,
                'annual_leave': applicant.annual_leave,
                'public_leave': applicant.public_holiday,
                'housing_allowance': applicant.housing_allowance,
                'education_allowance': applicant.education_allowance,
                'travel_allowance': applicant.travel_allowance,
                'meal_allowance': applicant.meal_allowance,
                'medical_allowance': applicant.medical_allowance,
                'other_allowance': applicant.other_allowance,
                'desired_start_date': applicant.desired_start_date,
                'address': applicant.address,
                'position': applicant.job_id.name,
                'title_id' : applicant.title_id.name
            }
            return data

    @api.model
    def _get_report_values(self, docids, data=None):
        print('odoo data: ', data)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        print(docs)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'get_data': data,
            'applicant': self.get_applicant_data(docids)
        }
        return docargs
