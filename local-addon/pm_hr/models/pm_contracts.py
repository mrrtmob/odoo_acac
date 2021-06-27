from odoo import models, fields, api, _


class PmInheritContracts(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _get_default_code(self):
        return self.env["ir.sequence"].next_by_code("hr.contract")

    education_allowance = fields.Char('Education Allowance')
    annual_leave = fields.Integer('Annual Leave')
    public_holiday = fields.Integer('Public Holiday')
    tax_deduction = fields.Float("Tax Deduction($)", compute="_compute_tax_rate", store=True)
    tax_rate = fields.Float("Tax Rate(%)", compute="_compute_tax_rate", store=True)

    name = fields.Char(
        string="Contract Reference",
        required=True,
        default=_get_default_code,
        track_visibility="onchange",
    )

    state = fields.Selection(selection_add=[('terminated', 'Terminated')])


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
