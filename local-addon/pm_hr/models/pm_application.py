# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

_SATISFACTION = [
    ("4", "Very Satisfied"),
    ("3", "Satisfied"),
    ("2", "Below Average"),
    ("1", "Dissatisfied"),
]

class PMPersonalityType(models.Model):
    _name = 'pm.personality.type'
    name = fields.Char()

class EmployeeSkillCustom(models.Model):
    _inherit = 'hr.employee.skill'
    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')

class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'
    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')


class ResumeLineCustom(models.Model):
    _inherit = 'hr.resume.line'
    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', required=False, ondelete='cascade')
    # employee_id = fields.Many2one('hr.employee', required=True, ondelete='cascade')

class EmployeeSkillCustom(models.Model):
    _inherit = 'hr.employee.skill'
    skill_level_id = fields.Many2one('hr.skill.level', required=False)



class PmApplicant(models.Model):
    _inherit = 'hr.applicant'
    resume_line_ids = fields.One2many('hr.resume.line', 'applicant_id', string="Resumé lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'applicant_id', string="Skills")

    question_ids = fields.One2many(
        comodel_name="pm.applicant.question",
        inverse_name="applicant_id",
    )
    personality_ids = fields.One2many(
        comodel_name="pm.applicant.personality",
        inverse_name="applicant_id",
    )
    motivation_ids = fields.One2many(
        comodel_name="pm.applicant.motivation",
        inverse_name="applicant_id",
    )
    administrative_ids = fields.One2many(
        comodel_name="pm.applicant.basic",
        inverse_name="applicant_id",
    )
    educational_achievement = fields.One2many('pm.lead.educational.achievement',
                                                   inverse_name="applicant_id",
                                                   string='Educational Achievements',
                                                   help="Educational Achievements")

    working_experience = fields.One2many('pm.lead.working.experience',
                                              inverse_name="applicant_id",
                                              string='Working Experience',
                                              help="Working Experience")

    title_id = fields.Many2one('res.partner.title', 'Title')
    major = fields.Char()
    interviewer = fields.Many2many(
        comodel_name="res.users",
        string='Interviewers',
    )
    desired_start_date = fields.Date('Desired Start Date')
    address = fields.Text('Address')
    interview_date = fields.Datetime('Interview Date')
    interviewer_place = fields.Char('Interview Held at')
    practical_score = fields.Float('Practical/Logical Score', track_visibility="onchange")
    jd_score = fields.Float('Job Description Score', track_visibility="onchange")
    personality_test = fields.Many2many(
        comodel_name="pm.personality.type",
        string="Personality Test"
    )
    interview_score = fields.Float('Interview Score', compute='_compute_interview_score', store=True)
    total_score = fields.Float('Total Score', compute='_compute_applicant_score', store=True)
    is_saved = fields.Boolean(default=False)

    contract_period = fields.Char('Contract Period' , default='3 months')
    wage = fields.Float('Gross Salary')
    annual_leave = fields.Char('Annual Leave', default="15")
    public_holiday = fields.Char('Public Holiday', default="15")
    education_allowance = fields.Float('Education Allowance')
    housing_allowance = fields.Float('Housing Allowance')
    travel_allowance = fields.Float('Travel Allowance')
    meal_allowance = fields.Float('Meal Allowance')
    medical_allowance = fields.Float('Medical Allowance')
    other_allowance = fields.Float('Other Allowance')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    show_practical_score = fields.Boolean(compute='_compute_show_practical_score', default=False)
    email_to = fields.Char('Recipient')
    current_salary = fields.Float(
        string="Current Salary",
        default=0.0,
    )

    technical_score = fields.Float('Average Score', compute='_compute_technical_score', default=0)
    technical_weighted = fields.Float('Weighted Score', compute='_compute_technical_score', default=0)
    personality_score = fields.Float('Average Score', compute='_compute_personality_score', default=0)
    personality_weighted = fields.Float('Weighted Score', compute='_compute_personality_score', default=0)
    motivation_score = fields.Float('Average Score', compute='_compute_motivation_score', default=0)
    motivation_weighted = fields.Float('Weighted Score', compute='_compute_motivation_score', default=0)
    basic_score = fields.Float('Average Score', compute='_compute_basic_score', default=0)
    basic_weighted = fields.Float('Weighted Score', compute='_compute_basic_score', default=0)

    @api.constrains('question_ids')
    def check_question_total_technical_weight(self):
        technical = 0
        for question in self.question_ids:
            if not question.no_scoring:
                technical += question.question_weight
        if technical != 100 and technical != 0:
            raise UserError("Total weight of Specific Functional questions must be equal to 100%")

    @api.constrains('administrative_ids')
    def check_question_total_basic_weight(self):
        basic = 0
        for question in self.administrative_ids:
            if not question.no_scoring:
                basic += question.question_weight
        if basic != 100 and basic != 0:
            raise UserError("Total weight of Basic / Administrative questions  must be equal to 100%")

    @api.constrains('personality_ids')
    def check_question_total_personality_weight(self):
        personality = 0
        for question in self.personality_ids:
            if not question.no_scoring:
                personality += question.question_weight
        if personality != 100 and personality != 0:
            raise UserError("Total weight of Characteristic / Personality questions must be equal to 100%")

    @api.constrains('motivation_ids')
    def check_question_total_motivation_weight(self):
        motivation = 0
        for question in self.motivation_ids:
            if not question.no_scoring:
                motivation += question.question_weight
        if motivation != 100 and motivation != 0:
            raise UserError("Total weight of Motivations / Working Relationships question must be equal to 100%")


    @api.depends('question_ids')
    def _compute_technical_score(self):
        self.technical_score = 0
        self.technical_weighted = 0
        if self.question_ids:
            score = 0
            weighted_score = 0
            count = 0
            for question in self.question_ids:
                if not question.no_scoring:
                    score += question.score
                    count += 1
                    weighted_score += question.score * question.question_weight / 100
            if score > 0:
                self.technical_score = score / count
                self.technical_weighted = weighted_score

    @api.depends('personality_ids')
    def _compute_personality_score(self):
        self.personality_score = 0
        self.personality_weighted = 0
        if self.personality_ids:
            score = 0
            weighted_score = 0
            count = 0
            for question in self.personality_ids:
                if not question.no_scoring:
                    score += question.score
                    count += 1
                    weighted_score += question.score * question.question_weight / 100
            if score > 0:
                self.personality_score = score / count
                self.personality_weighted = weighted_score



    @api.depends('motivation_ids')
    def _compute_motivation_score(self):
        self.motivation_score = 0
        self.motivation_weighted = 0
        if self.motivation_ids:
            score = 0
            count = 0
            weighted_score = 0
            for question in self.motivation_ids:
                if not question.no_scoring:
                    score += question.score
                    count += 1
                    weighted_score += question.score * question.question_weight / 100

            if score > 0:
                self.motivation_score = score / count
                self.motivation_weighted = weighted_score

    @api.depends('administrative_ids')
    def _compute_basic_score(self):
        self.basic_score = 0
        self.basic_weighted = 0
        if self.administrative_ids:
            score = 0
            count = 0
            weighted_score = 0
            for question in self.administrative_ids:
                if not question.no_scoring:
                    score += question.score
                    count += 1
                    weighted_score += question.score * question.question_weight / 100

            if score > 0:
                self.basic_score = score / count
                self.basic_weighted = weighted_score


    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        if not self.middle_name:
            self.name = str(self.first_name) + " " + str(
                self.last_name)
        else:
            self.name = str(self.first_name) + " " + str(
                self.middle_name) + " " + str(self.last_name)
        print(self.name)



    @api.constrains('practical_score', 'jd_score')
    def check_score_limit(self):
        if self.practical_score > 4 or self.jd_score > 4:
            raise UserError("Practical Score or Job Description Score should not be bigger than 4")

    @api.depends('job_id')
    def _compute_show_practical_score(self):
        if self.job_id.practical_test:
            self.show_practical_score = True
        else:
            self.show_practical_score = False


    @api.depends('technical_weighted',
                 'basic_weighted',
                 'personality_weighted',
                 'motivation_weighted')
    def _compute_interview_score(self):
        for applicant in self:
            job = applicant.job_id
            applicant_technical = applicant.technical_weighted * job.technical_weight / 100
            applicant_basic = applicant.basic_weighted * job.basic_weight / 100
            applicant_personality = applicant.personality_weighted * job.personality_weight / 100
            applicant_motivation = applicant.motivation_weighted * job.motivation_weight / 100

            applicant.interview_score = sum([applicant_technical, applicant_basic,
                                             applicant_personality, applicant_motivation])


    @api.depends('practical_score', 'interview_score', 'jd_score')
    def _compute_applicant_score(self):
        for appplicant in self:
            position = appplicant.job_id
            jd_score = position.jd_weight * appplicant.jd_score / 100
            interview_score = position.interview_weight * appplicant.interview_score / 100
            practical_score = position.practical_weight * appplicant.practical_score / 100

            appplicant.total_score = sum([jd_score, interview_score, practical_score])

    @api.onchange('stage_id')
    def onchange_stage(self):
        if self.stage_id.id == 4 or self.stage_id.name == 'Offer':
            if self.total_score == 0:
                raise UserError("Applicant's total score is required")
        # if self.stage_id.id == 5 or self.stage_id.name == 'Contract Signed':
        #     if self.struct_id == '' or self.desired_start_date == '':
        #         raise UserError("Salary Structure and Desired Start Date are required") 


    def _composer_format(self, res_model, res_id, template):
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model=res_model,
            default_res_id=res_id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def send_shortlisted_email(self):
        self.ensure_one()
        template = self.env.ref(
            'pm_hr.email_applicant_shortlisted',
            raise_if_not_found=False)
        return self._composer_format(res_model='hr.applicant',
                                     res_id=self.id,
                                     template=template)

    def send_interview_email(self):
        self.ensure_one()

        email_to = ''
        for applicant in self:
            if applicant.email_from and applicant.interviewer:
               email_to += str(applicant.email_from)
               for interviewer in applicant.interviewer:
                   email_to += ',' + str(interviewer.login)
            applicant.email_to = email_to


        template = self.env.ref(
            'pm_hr.email_applicant_interview',
            raise_if_not_found=False)
        return self._composer_format(res_model='hr.applicant',
                                     res_id=self.id,
                                     template=template)

    def unsuccessful_applicant(self):
        self.ensure_one()
        print('mmmmm')



        template = self.env.ref(
            'pm_hr.email_applicant_unsuccessful',
            raise_if_not_found=False)
        print(template)
        return self._composer_format(res_model='hr.applicant',
                                     res_id=self.id,
                                     template=template)

    def action_job_offer_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_hr', 'email_applicant_job_offer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'hr.applicant',
            'active_model': 'hr.applicant',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_light",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        ctx['model_description'] = _('Job Offer')

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    # def unsuccessful_applicant(self):
    #     #self.write({'active': False})
    #     '''
    #     This function opens a window to compose an email, with the edi purchase template message loaded by default
    #     '''
    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data.get_object_reference('pm_hr', 'email_applicant_unsuccessful')[1]
    #     except ValueError:
    #         template_id = False
    #     try:
    #         compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = dict(self.env.context or {})
    #     ctx.update({
    #         'default_model': 'hr.applicant',
    #         'active_model': 'hr.applicant',
    #         'active_id': self.ids[0],
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'custom_layout': "mail.mail_notification_light",
    #         'force_email': True,
    #         'mark_rfq_as_sent': True,
    #     })
    #
    #     ctx['model_description'] = _('Job Offer')
    #
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

    @api.model
    def _get_next_application_number(self):
        next = ''
        sequence = self.env['ir.sequence'].search([('code', '=', 'hr.applicant')])
        if sequence:
            next = sequence.get_next_char(sequence.number_next_actual)
        return next



    application_number = fields.Char(
        string="Application Number",
        required=True,
        readonly=True,
        default=_get_next_application_number,
        track_visibility="onchange",
    )

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)
    announcement_no = fields.Text('Announcement No')
    question_count = fields.Integer(compute='_compute_question_count')
    documents_count = fields.Integer(compute='_compute_document_ids', string="Document Count")
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Documents")

    def _compute_document_ids(self):
        attachments = self.env['ir.attachment'].search([
            '&', ('res_model', '=', 'hr.applicant'), ('res_id', '=', self.id)])
        for applicant in self:
            applicant.document_ids = attachments
            applicant.documents_count = len(attachments)


    def action_get_attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['context'] = {'default_res_model': self._name,
                             'default_res_id': self.ids[0]}
        action['domain'] = str(['&', ('res_model', '=', self._name),
                                ('res_id', 'in', self.ids)])
        return action


    def create_employee(self):
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                print("Hit Create Employee***************")

                applicant_skills = [[6, False, applicant.employee_skill_ids.mapped('id')]]
                applicant_exp = [[6, False, applicant.resume_line_ids.mapped('id')]]
                manager = applicant.department_id.manager_id

                now = datetime.now()
                employee_id = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id or False,
                    'job_title': applicant.job_id.name,
                    'address_home_id': address_id,
                    'status': 'active',
                    'parent_id': manager.id,
                    'joining_date': applicant.desired_start_date or datetime.now(),
                    'employee_skill_ids': applicant_skills,
                    'resume_line_ids': applicant_exp,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                                  and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                                  and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                                  and applicant.department_id.company_id.phone or False})
                applicant.write({'emp_id': employee_id.id})


                contract_val = {
                    'employee_id': employee_id.id,
                    'company_id': applicant.company_id.id,
                    'wage': applicant.wage,
                    'da': applicant.housing_allowance,
                    'job_id': applicant.job_id.id or False,
                    'department_id': applicant.department_id.id or False,
                    'travel_allowance': applicant.travel_allowance,
                    'education_allowance': applicant.education_allowance,
                    'meal_allowance': applicant.meal_allowance,
                    'medical_allowance': applicant.medical_allowance,
                    'other_allowance': applicant.other_allowance,
                    'public_holiday': applicant.public_holiday,
                    'annual_leave': applicant.annual_leave, 
                    'struct_id': applicant.struct_id.id or False,
                    'date_start': applicant.desired_start_date,
                    'trial_date_end': applicant.desired_start_date + relativedelta(months=+3)
                }
                
                contract_obj = self.env['hr.contract']
                contract_obj.create(contract_val)


                applicant.partner_id.write({'partner_share': True, 'employee': True})
                if applicant.job_id:
                    applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                    applicant.job_id.message_post(
                        body=_(
                            'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                        subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)
                applicant.message_post_with_view(
                    'hr_recruitment.applicant_hired_template',
                    values={'applicant': applicant},
                    subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)
        return employee_id


    @api.model
    def _compute_question_count(self):
        self.question_count = self.env['pm.applicant.question'].search_count([('applicant_id', '=', self.id)])

    @api.model_create_multi
    @api.model
    def create(self, vals):
        vals['is_saved'] = True
        vals['application_number'] = self.env['ir.sequence'].next_by_code('hr.applicant')
        res = super(PmApplicant, self).create(vals)

        position = res.job_id
        question_data = {
            'questions': [],
            'personality': [],
            'motivation': [],
            'basic': [],
        }
        questions = position.question_ids
        personality_question = position.personality_question_ids
        motivation_question = position.motivation_question_ids
        basic_question = position.basic_question_ids

        for question in questions:
            question_data['questions'].append({
                'interview_question_id': question.interview_question_id.id,
                'question_weight': question.question_weight,
                'applicant_id': res.id,
            })
        for question in personality_question:
            question_data['personality'].append({
                'interview_question_id': question.interview_question_id.id,
                'question_weight': question.question_weight,
                'applicant_id': res.id,
            })

        for question in motivation_question:
            question_data['motivation'].append({
                'interview_question_id': question.interview_question_id.id,
                'question_weight': question.question_weight,
                'applicant_id': res.id,
            })

        for question in basic_question:
            question_data['basic'].append({
                'interview_question_id': question.interview_question_id.id,
                'question_weight': question.question_weight,
                'applicant_id': res.id,
            })
        print(question_data)

        self.env['pm.applicant.question'].create(question_data['questions'])
        self.env['pm.applicant.personality'].create(question_data['personality'])
        self.env['pm.applicant.motivation'].create(question_data['motivation'])
        self.env['pm.applicant.basic'].create(question_data['basic'])

        return res

class PmApplicantQuestion(models.Model):
    _name = 'pm.applicant.question'
    _description = "Technical Question for Applicant"
    applicant_id = fields.Many2one('hr.applicant', 'Applicants', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    type = fields.Selection([
        ('basic', 'Basic'),
        ('technical', 'Technical'),
        ('personality', 'Personality'),
    ], string='Question Type', related='interview_question_id.type', store=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    application_answer = fields.Text()
    question_weight = fields.Float('Question Weight')
    score = fields.Float('Score')
    comment = fields.Char("Comment")
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)

    level_of_satisfaction = fields.Selection(_SATISFACTION)

    @api.constrains('score')
    def check_score_limit(self):
        for question in self:
            if question.score > 4:
                raise UserError('Score should not be bigger than 4')

    

class PmApplicantPersonality(models.Model):
    _name = 'pm.applicant.personality'
    _description = "Personality Question for Applicant"
    applicant_id = fields.Many2one('hr.applicant', 'Applicants', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    type = fields.Selection([
        ('basic', 'Basic'),
        ('technical', 'Technical'),
        ('personality', 'Personality'),
    ], string='Question Type', related='interview_question_id.type', store=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    application_answer = fields.Text()
    score = fields.Float('Score')
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)
    question_weight = fields.Float('Question Weight')
    comment = fields.Char("Comment")
    level_of_satisfaction = fields.Selection(_SATISFACTION)

    @api.constrains('score')
    def check_score_limit(self):
        for question in self:
            if question.score > 4:
                raise UserError('Score should not be bigger than 4')


class PmApplicantMotivation(models.Model):
    _name = 'pm.applicant.motivation'
    _description = "Motivation Question for Applicant"
    applicant_id = fields.Many2one('hr.applicant', 'Applicants', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    type = fields.Selection([
        ('basic', 'Basic'),
        ('technical', 'Technical'),
        ('personality', 'Personality'),
    ], string='Question Type', related='interview_question_id.type', store=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    application_answer = fields.Text()
    score = fields.Float('Score')
    comment = fields.Char("Comment")
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)
    question_weight = fields.Float('Question Weight')
    level_of_satisfaction = fields.Selection(_SATISFACTION)

    @api.constrains('score')
    def check_score_limit(self):
        for question in self:
            if question.score > 4:
                raise UserError('Score should not be bigger than 4')

class PmApplicantMotivation(models.Model):
    _name = 'pm.applicant.basic'
    _description = "Administrative Question for Applicant"
    applicant_id = fields.Many2one('hr.applicant', 'Applicants', index=True)
    interview_question_id = fields.Many2one('pm.interview.question', index=True)
    type = fields.Selection([
        ('basic', 'Basic'),
        ('technical', 'Technical'),
        ('personality', 'Personality'),
    ], string='Question Type', related='interview_question_id.type', store=True)
    expected_answer = fields.Html(related='interview_question_id.expected_answer', store=True)
    application_answer = fields.Text()
    score = fields.Float('Score')
    comment = fields.Char("Comment")
    no_scoring = fields.Boolean(related='interview_question_id.no_scoring', store=True)
    question_weight = fields.Float('Question Weight')
    level_of_satisfaction = fields.Selection(_SATISFACTION)


    @api.constrains('score')
    def check_score_limit(self):
        for question in self:
            if question.score > 4:
                raise UserError('Score should not be bigger than 4')
