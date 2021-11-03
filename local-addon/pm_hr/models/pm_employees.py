from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import datetime
from datetime import timedelta

class PmInheritEmployeeFamily(models.Model):
    _inherit = 'hr.employee.family'
    name = fields.Char("Name")
    occupation = fields.Char('Occupation')
    phone = fields.Char('Contact No')
    email = fields.Char('Email')

class PmEmployeeSession(models.Model):
    _name = 'pm.employee.session'
    name = fields.Char("Session")

class PmEmployeeBudgetLine(models.Model):
    _name = 'pm.employee.budget.line'
    name = fields.Char("Budget Line")

class PmDepartmentCustom(models.Model):
    _inherit = 'hr.department'
    code = fields.Char("Code")

class PmDepartmentBudget(models.Model):
    _name = 'pm.department.budget'
    name = fields.Char("Department Budget Allocation")




class PmEmployeeMedical(models.Model):
    _name = 'pm.employee.medical'
    name = fields.Char('Medical Test')
    employee_id = fields.Many2one('hr.employee')
    student_id = fields.Many2one('op.student')
    date = fields.Date("Tested Date")
    hospital = fields.Char("Clinic/Hospital")
    condition = fields.Char('Result')
    remarks = fields.Char()

class PmEmployeeVaccination(models.Model):
    _name = 'pm.employee.vaccination'
    name = fields.Char('Vaccine Name')
    employee_id = fields.Many2one('hr.employee')
    date = fields.Date("Date")
    location = fields.Char("Location")
    remarks = fields.Char("Remarks")

class PmInheritMailActivity(models.Model):
    _inherit = 'mail.activity'
    plan_type = fields.Selection([
        ('on', 'Onboarding'),
        ('off', 'Offboarding'),
    ])

    def action_done(self):
        self.unlink()


class PmEmployees(models.Model):
    _inherit = 'hr.employee'
    #name = fields.Char(string="Employee Legal Name", related='resource_id.name', store=True, readonly=False, tracking=True)
    title = fields.Many2one('res.partner.title', string='Title', store=True)
    medical_history_ids = fields.One2many('pm.employee.medical',
                                          inverse_name="employee_id")
    vaccination_history_ids = fields.One2many('pm.employee.vaccination', inverse_name='employee_id')
    first_name = fields.Char(string="First Name", required=False)
    last_name = fields.Char(string="Last Name", required=False)
    fte = fields.Integer("Full-Time Equivalent")
    session_id = fields.Many2one(comodel_name="pm.employee.session", string="Session")
    department_budget_id = fields.Many2one(comodel_name="pm.department.budget", string="Department Budget Allocation")
    budget_line_id = fields.Many2one(comodel_name="pm.employee.budget.line", string="Budget Line")
    # for current residential address
    cra_street = fields.Char('Street...')
    ph_remaining = fields.Float("Public Holiday", defualt=0)
    cra_city = fields.Char('City', size=64)
    cra_zip = fields.Char('Zip', size=8)
    cra_state_id = fields.Many2one(
        'res.country.state', 'States')
    cra_country_id = fields.Many2one(
        'res.country', 'Country', )
    is_hr_user = fields.Boolean('Approver', compute="compute_is_hr_user", readonly=True)
    certificate = fields.Selection(selection_add=[('diploma', 'Diploma'), ('high_school', 'High School')])

    private_email = fields.Char("Email", readonly=False)
    phone = fields.Char(string="Phone", readonly=False)


    @api.depends('name')
    def compute_is_hr_user(self):
        self.is_hr_user = False
        print("Hit Hz")
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('pm_hr.group_human_resource_manager'):
            print("True")
            self.is_hr_user = True



    # for home country address
    hca_street = fields.Char('Street..')
    hca_city = fields.Char('City..', size=64)
    hca_zip = fields.Char('Zip..', size=8)
    hca_state_id = fields.Many2one(
        'res.country.state', 'States..')
    hca_country_id = fields.Many2one(
        'res.country', 'Country..', )
    joining_date = fields.Date('Contract Signed Date', required=False, readonly=False)
    leaving_date = fields.Date('Last Day')
    godfather_id = fields.Many2one(comodel_name='res.users', string='Godfather', required=False, copy=False, index=True)
    type_of_visa = fields.Char('Type Of Visa')
    khmer_name = fields.Char('Name in Khmer', help="Last name and first name")
    relationship_id = fields.Many2one(comodel_name='hr.employee.relation', string="Relationship")
    emergency_mobile = fields.Char('Emergency Mobile')
    emergency_email = fields.Char('Emergency Email')
    is_finish_probation = fields.Boolean(compute='_compute_employee_probation', sting="Finished Probation Period", store=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave')

    ], string='Status', required=False)
    status_detail = fields.Char('Status Detail')

    # emergency address
    ema_street = fields.Char('Street...')
    ema_city = fields.Char('City', size=64)
    ema_zip = fields.Char('Zip', size=8)
    ema_state_id = fields.Many2one(
        'res.country.state', 'States')
    ema_country_id = fields.Many2one(
        'res.country', 'Country', )
    employee_count = fields.Integer(compute='_compute_employee_count', string='Promotion Count')
    employee_transfers_count = fields.Integer(compute='_compute_employee_transfers_count', string='Transfers Count')
    employee_training_count = fields.Integer(compute='_compute_employee_training_count', string='Training Count')
    employee_appraisal_count = fields.Integer(compute='_compute_employee_appraisal_count', string='Apprasial Count')
    nssf_no = fields.Char("NSSF No")
    tax_income_no = fields.Char("Income Tax Number")
    bank_account_no = fields.Char("Bank Account Number")
    passport_expiration_date = fields.Date("Passport Expiration Date")
    ID_expiration_date = fields.Date("ID Expiration Date")

    @api.depends('joining_date', 'contract_id.trial_date_end')
    def _compute_employee_probation(self):
        for emp in self:
            is_finished = False
            d = datetime.date.today() - timedelta(days=90)
            if emp.joining_date and emp.joining_date < d:
                is_finished = True
            emp.is_finish_probation = is_finished


    @api.model
    def _get_next_employee_number(self):
        next = ''
        sequence = self.env['ir.sequence'].search([('code', '=', 'hr.employee')])
        if sequence:
            next = sequence.get_next_char(sequence.number_next_actual)
        return next

    employee_number = fields.Char(
        string="Employee Number",
        required=True,
        readonly=True,
        default=_get_next_employee_number,
        track_visibility="onchange",
    )

    @api.onchange('parent_id')
    def on_change_employee(self):
        self.coach_id = self.parent_id.id
        self.leave_manager_id = self.parent_id.user_id.id

    def launch_exit_plan(self):
        plan = self.env['hr.plan'].browse(2)
        print(plan, '*** Plan ***')
        for activity_type in plan.plan_activity_type_ids:
            responsible = activity_type.get_responsible_id(self)

            if self.env['hr.employee'].with_user(responsible).check_access_rights('read', raise_exception=False):
                # date_deadline = self.env['mail.activity']._calculate_date_deadline(activity_type.activity_type_id)

                no_days = activity_type.trg_date_range
                date_field = activity_type.trg_date_id.name

                employee_date = self[date_field]
                print(88)
                print(employee_date)
                print(no_days)

                date_deadline = (employee_date + relativedelta(
                    days=no_days))

                print('no_date', no_days)
                print('date XD', date_deadline)

                self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get('hr.employee').id,
                    'summary': activity_type.summary,
                    'note': activity_type.note,
                    'plan_type': 'off',
                    'activity_type_id': activity_type.activity_type_id.id,
                    'user_id': responsible.id,
                    'date_deadline': date_deadline,
                })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.id,
            'name': self.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }

    def _compute_employee_count(self):
        # read_group as sudo, since promotion count is displayed on form view
        employee_data = self.env['pm.promotion'].sudo().read_group([('employee_id', 'in', self.ids)],
                                                                  ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in employee_data)
        for employee in self:
            employee.employee_count = result.get(employee.id, 0)

    def _compute_employee_transfers_count(self):
        # read_group as sudo, since transfers count is displayed on form view
        employee_data = self.env['pm.transfers'].sudo().read_group([('employee_id', 'in', self.ids)],
                                                                  ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in employee_data)
        for employee in self:
            employee.employee_transfers_count = result.get(employee.id, 0)

    def _compute_employee_training_count(self):
        # read_group as sudo, since training count is displayed on form view
        employee_data = self.env['pm.training'].sudo().read_group([('employee_id', 'in', self.ids)],
                                                                   ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in employee_data)
        for employee in self:
            employee.employee_training_count = result.get(employee.id, 0)
    
    def _compute_employee_appraisal_count(self):
        employee_data = self.env['hr.appraisal'].sudo().read_group([('emp_id', 'in', self.ids)],
                                                                   ['emp_id'], ['emp_id'])
        result = dict((data['emp_id'][0], data['emp_id_count']) for data in employee_data)
        for employee in self:
            employee.employee_appraisal_count = result.get(employee.id, 0)    

    @api.model
    def create(self, vals):
        print("FFFFFFFF")
        print(self.env['ir.sequence'].next_by_code('hr.employee'))
        vals['employee_number'] = self.env['ir.sequence'].next_by_code('hr.employee')
        res = super(PmEmployees, self).create(vals)
        return res


    # def write(self, vals):
    #     if not self.is_hr_user:
    #         raise UserError("You are not authorized to edit the employee information. Please contact HR Department")
    #
    #     res = super(PmEmployees, self).write(vals)
    #     return res



