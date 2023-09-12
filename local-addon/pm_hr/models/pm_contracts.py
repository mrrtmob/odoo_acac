from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, timedelta


class PmInheritContracts(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("hr.contract")

    education_allowance = fields.Monetary('Education Allowance')
    annual_leave = fields.Integer('Annual Leave')
    public_holiday = fields.Integer('Public Holiday')
    tax_deduction = fields.Float("Tax Deduction($)", compute="_compute_tax_rate", store=True)
    tax_rate = fields.Float("Tax Rate(%)", compute="_compute_tax_rate", store=True)
    senoirity_start_date = fields.Date('Senoirity Start Date')

    name = fields.Char(
        string="Contract Reference",
        required=True,
        default=_get_default_code,
        track_visibility="onchange",
    )

    state = fields.Selection(selection_add=[('terminated', 'Terminated')])

    record_url = fields.Char('Link', compute="_compute_record_url", store=True)

    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=hr.contract' % (record.id)
            record.record_url = base_url


    def contract_scheduler(self):
        print("gege")
        contracts = self.env['hr.contract'].sudo().search(
            [('state', '=', 'open'),
             ('trial_date_end', '!=', False)])
        today = fields.Date.today()
        for con in contracts:
            d = timedelta(days=7)
            end_date = con.trial_date_end
            print(end_date)
            remind_date = end_date - d
            print(remind_date)

            if today == remind_date or today == end_date:
                print(con.name)
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('pm_hr', 'contract_prohibition_reminder')[1]
                    print(template_id)
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(con.id, force_send=True)




    @api.depends('wage')
    def _compute_tax_rate(self):
        for rec in self:
            if rec.wage:
                tax_config = self.env['pm.tax.configuration'].search([])
                salary = rec.wage
                rate = 0
                for tax in tax_config:
                    if tax.min_salary <= salary <= tax.max_salary:
                        rate = tax.tax_rate
                rec.tax_rate = rate
                rec.tax_deduction = salary * rate / 100
