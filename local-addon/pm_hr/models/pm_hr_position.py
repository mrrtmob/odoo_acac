# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

_STATES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("first_approved", "HR Verify"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]



class PmJobPosition(models.Model):
    _inherit = 'hr.job'
    question_count = fields.Integer(compute='_compute_question_count')
    personality_test = fields.Boolean(default=True)
    practical_test = fields.Boolean()
    is_assignee = fields.Boolean('Approver', compute="compute_is_approver", readonly=True, default=False)
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    approval_record_id = fields.Many2one('pm.approval')
    status = fields.Selection([
        ('open', 'Not Recruiting'),
        ('recruit', 'Recruitment in Progress'),
    ], default='open')
    due_date = fields.Date()
    question_ids = fields.One2many(
        comodel_name="pm.interview.template",
        inverse_name="job_position_id",
        string="Specific Functional Questions",
    )
    basic_question_ids = fields.One2many(
        comodel_name="pm.job.basic.question",
        inverse_name="job_position_id",
        string="Basic / Administrative Questions",
    )
    personality_question_ids = fields.One2many(
        comodel_name="pm.job.personality.question",
        inverse_name="job_position_id",
        string="Character / Personality",
    )
    motivation_question_ids = fields.One2many(
        comodel_name="pm.job.motivation.question",
        inverse_name="job_position_id",
        string="Motivations / Working Relationships",
    )
    jd_weight = fields.Float(default=20)
    interview_weight = fields.Float(default=50)
    practical_weight = fields.Float(default=30)
    technical_weight = fields.Float(default=30)
    personality_weight = fields.Float(default=30)
    motivation_weight = fields.Float(default=20)
    basic_weight = fields.Float(default=20)
    is_hr_user = fields.Boolean('Approver', compute="compute_is_hr_user", readonly=True, default=False)
    read_only = fields.Boolean(compute="compute_read_only", default=True)
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        readonly=True,
        track_visibility="onchange",
        index=True,
    )

    @api.depends('assigned_to')
    def compute_is_approver(self):
        if self.env.user == self.assigned_to:
            self.is_assignee = True
        else:
            self.is_assignee = False

    def compute_is_hr_user(self):
        self.is_hr_user = False
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            self.is_hr_user = True

    @api.depends('is_hr_user')
    def compute_read_only(self):
        self.read_only = True
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            self.read_only = False


    def get_approver(self, state):
        approval = self.approval_record_id
        approval.state = state
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        return approval.approve

    def button_submit(self):
        if self.job_description == '<p><br></p>':
            raise UserError("Please Input Job Description")

        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'hr.job')])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
        })
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])

        return self.write({'state': 'submitted', 'assigned_to': approval.approve, 'approval_record_id': approval.id})

    def button_verify(self):
        approver = self.get_approver('first_approved')
        return self.write({'state': 'first_approved', 'assigned_to': approver})

    def button_approve(self):
        self.get_approver('approved')
        return self.write({'state': 'approved'})


    @api.model
    def get_default_department(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        employee = self.env['hr.employee'].search([('user_id', '=',  self._uid)])
        if employee:
            return employee.department_id.id




    department_id = fields.Many2one('hr.department', string='Department', default=get_default_department)



    is_saved = fields.Boolean(default=False)
    background = fields.Text('Background',
                 default='Shift 360, a Swiss Foundation with representation in Cambodia, has received grants from '
                         'the Swedish International Development Cooperation (Sida) and the Enhanced Integrated '
                         'Framework/WTO (EIF) to support the development of the '
                         'Academy of Culinary Arts – Cambodia (ACAC.) ACAC will train chefs for the Hospitality '
                         'sector based on ASEAN standards. ACAC has been established by the Royal Government of '
                         'Cambodia as a Cambodian Public Private Partnership. ACAC will be governed by a nine-member '
                         'Board including senior Government officials and Representatives of the hospitality sector '
                         'associations. Once operational, ACAC will deliver a post-high school two-year certificate '
                         'program as well as short-term training/retraining programs on-campus and off-campus for '
                         'professionals already employed in the sector.', required=True)
    job_description = fields.Html()
    job_requirement = fields.Html()
    def _get_how2apply_default(self):
        # job_id = self.env.context.get('active_id')
        # job = self.env['hr.job'].search([('id', '=', job_id)])
        resutl = """<div">
                    <p>Interested individuals can apply by submitting an Expression of Interest and a detailed CV to:</p>
                    <br/>
                    <div style="text-align:center;font-weight:bold">
                        <p>Attn: Mrs. Srun Chanlay </p>  
                        <p>Email: operations.manager@acac.edu.kh </p> 
                        <p>CC: acac@shift360.ch </p> 
                        <p>Visit our website: www.acac.edu.kh</p> 
                    </div>
                </div>"""
        return resutl

    how2apply = fields.Html(default=_get_how2apply_default)

    @api.model
    def default_get(self, fields):
        vals = super(PmJobPosition, self).default_get(fields)
        interview_question = self.env['pm.interview.question']
        questions = interview_question.search([('type', '!=', 'technical')])
        personality_val = []
        basic_val = []
        motivation_val = []
        for question in questions:
            if question.type == 'basic':
                basic_val.append((0, 0, {'question_weight': 0, 'interview_question_id': question.id}))
            elif question.type == 'personality':
                personality_val.append((0, 0, {'question_weight': 0, 'interview_question_id': question.id}))
            elif question.type == 'motivation':
                motivation_val.append((0, 0, {'question_weight': 0, 'interview_question_id': question.id}))
        vals.update({'personality_question_ids': personality_val})
        vals.update({'basic_question_ids': basic_val})
        vals.update({'motivation_question_ids': motivation_val})

        return vals

    @api.model
    def create(self, vals):
        # Generate Sequence Code
        vals['is_saved'] = True
        res = super(PmJobPosition, self).create(vals)
        return res


    @api.constrains('jd_weight', 'interview_weight', 'practical_weight')
    def check_total_weight(self):
        for record in self:
            total = record.jd_weight + record.interview_weight + record.practical_weight
            if total != 100:
                raise ValidationError("Total weight of interview score must be equal to 100%")


    @api.constrains('question_ids')
    def check_question_total_technical_weight(self):
        technical = 0
        for question in self.question_ids:
            if not question.no_scoring:
                technical += question.question_weight
        if technical != 100 and technical != 0:
            raise UserError("Total weight of Specific Functional questions must be equal to 100%")

    @api.constrains('basic_question_ids')
    def check_question_total_basic_weight(self):
        basic = 0
        for question in self.basic_question_ids:
            if not question.no_scoring:
                basic += question.question_weight
        if basic != 100 and basic != 0:
            raise UserError("Total weight of Basic / Administrative questions  must be equal to 100%")

    @api.constrains('personality_question_ids')
    def check_question_total_personality_weight(self):
        personality = 0
        for question in self.personality_question_ids:
            if not question.no_scoring:
                personality += question.question_weight
        if personality != 100 and personality != 0:
            raise UserError("Total weight of Characteristic / Personality questions must be equal to 100%")

    @api.constrains('motivation_question_ids')
    def check_question_total_motivation_weight(self):
        motivation = 0
        for question in self.motivation_question_ids:
            if not question.no_scoring:
                motivation += question.question_weight
        if motivation != 100 and motivation != 0:
            raise UserError("Total weight of Motivations / Working Relationships question must be equal to 100%")

    def set_recruit(self):
        for record in self:
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            record.write({'status': 'recruit', 'no_of_recruitment': no_of_recruitment})
        return True

    def set_open(self):
        return self.write({
            'status': 'open',
            'no_of_recruitment': 0,
            'no_of_hired_employee': 0
        })



    @api.onchange('practical_test')
    def onchange_pratical_test(self):
        for job in self:
            if job.practical_test:
                job.jd_weight = 25
                job.interview_weight = 50
                job.practical_weight = 25
            else:
                job.jd_weight = 35
                job.interview_weight = 65
                job.practical_weight = 0



    @api.model
    def _compute_question_count(self):
        self.question_count = self.env['pm.interview.question'].search_count([('job_position_id', '=', self.id)])

    def view_pm_hr_interview_question_tree(self):
        action = self.env.ref(
            "pm_hr.pm_hr_interview_question"
        ).read()[0]
        questions = self.env['pm.interview.question'].search([('job_position_id', '=', self.id)])
        question_ids = questions.mapped('id')
        print('****Question*****')
        print(question_ids)

        action["domain"] = [("id", "in", question_ids)]

        return action

class PmInterviewTemplate(models.Model):
    _name = 'pm.interview.template'
    name = fields.Text(string='Description')
    job_position_id = fields.Many2one('hr.job', 'Job Position', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    category_weight = fields.Float('Category Weight')
    question_weight = fields.Float('Question Weight',  store=True)
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)

class PmBasicQuestion(models.Model):
    _name = 'pm.job.basic.question'
    name = fields.Text(string='Description')
    job_position_id = fields.Many2one('hr.job', 'Job Position', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    category_weight = fields.Float('Category Weight')
    question_weight = fields.Float('Question Weight')
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)

class PmPersonalityQuestion(models.Model):
    _name = 'pm.job.personality.question'
    name = fields.Text(string='Description')
    job_position_id = fields.Many2one('hr.job', 'Job Position', index=True )
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    category_weight = fields.Float('Category Weight')
    question_weight = fields.Float('Question Weight')
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)

class PmMotivationQuestion(models.Model):
    _name = 'pm.job.motivation.question'
    job_position_id = fields.Many2one('hr.job', 'Job Position', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    category_weight = fields.Float('Category Weight')
    question_weight = fields.Float('Question Weight')
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)



