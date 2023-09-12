from odoo import fields, models, api, _
from datetime import date

_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]



class PmHrTransfer(models.Model):
    _name = 'pm.transfers'
    _description = 'HR Transfer'
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
    # automatically get from selected employee
    department_id = fields.Many2one('hr.department', string='Current Department')
    # automatically get from selected employee
    job_id = fields.Many2one('hr.job', string='Current Job Position')
    new_department_id = fields.Many2one('hr.department', string='New Department', required=True)
    new_job_id = fields.Many2one('hr.job', string='New Job Position', required=True)
    new_salary = fields.Monetary('New Salary', required=False, tracking=True, help="New Salary after transferred.")
    previous_salary = fields.Monetary('Previous Salary', required=False, tracking=True)
    transfer_date = fields.Date('Transfer Date', required=True)
    approved_date = fields.Date('Approved Date', required=True)
    approved_by = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        track_visibility="onchange",
        readonly=True,
        index=True,
    )
    remark = fields.Char('Remark')
    field_history = fields.Char('Field History')

    # use this for show currency
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _compute_contract(self):
        employee = self.employee_id
        self.department_id = employee['department_id']
        self.job_id = employee['job_id']

    def update_employee_details(self):
        print('Hit Transfer Function')
        transfer_ids = self.env['pm.transfers'].search(
            [('transfer_date', '=', date.today()), ('state', '=', 'approved')])

        for transfer in transfer_ids:
            print('Hit Transfer Function')
            employee = transfer.employee_id
            contract = employee.contract_id
            new_manager = transfer.new_department_id.manager_id.id
            employee.write({
                'job_id': transfer.new_job_id.id,
                'department_id': transfer.new_department_id.id,
                'parent_id': new_manager,
            })
            if contract:
                contract.write({
                    'job_id': transfer.new_job_id.id,
                    'department_id': transfer.new_department_id.id,
                    'wage': transfer.new_salary,
                })
            print('Successfully Updated')

