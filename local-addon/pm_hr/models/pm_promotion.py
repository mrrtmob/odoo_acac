from odoo import fields, models, api, _
from datetime import datetime, date

_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]



class PmHrPromotion(models.Model):
    _name = 'pm.promotion'
    _description = 'HR Promotion'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))

    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    # look up to employee
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    # look up to contract of employee automatically
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=False)
    promotion_date = fields.Date('Promotion Date', required=True)
    # automatically get from current contract
    previous_designation = fields.Many2one('hr.job', string='Previous Designation', readonly=False)
    # new position and look up for job position
    new_designation = fields.Many2one('hr.job', string='New Designation', required=True)
    # automatically get from current contract
    previous_salary = fields.Monetary('Previous Salary', readonly=False)
    new_salary = fields.Monetary('New Salary', required=True, tracking=True, help="New Salary after promote.")
    new_benefit = fields.Char('New Benefit')
    description = fields.Char('Description')

    # use this for show currency
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_contract(self):
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        self.contract_id = contract
        self.previous_salary = contract['wage']
        self.previous_designation = contract['job_id']

    def update_employee_details(self):
        print('Hit Promotion Function')
        promotion_ids = self.env['pm.promotion'].search(
            [('promotion_date', '=', date.today()), ('state', '=', 'approved')])
        print(promotion_ids)

        for promotion in promotion_ids:
            employee = promotion.employee_id
            contract = promotion.contract_id
            new_job = promotion.new_designation
            new_department = new_job.department_id
            employee.write({
                'job_id': new_job.id,
                'job_title': new_job.name,
                'department_id': new_department.id
            })
            if contract:
                contract.write({
                    'job_id': new_job.id,
                    'wage': promotion.new_salary,
                })
            print('Successfully Updated')

    def button_submit(self):
        print("submit")


