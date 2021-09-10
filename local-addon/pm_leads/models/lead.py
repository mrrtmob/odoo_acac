# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from lxml import etree
import datetime
import simplejson
from odoo.exceptions import ValidationError, UserError

class PmCustomResPartner(models.Model):
    _inherit = 'res.partner'
    is_displayed = fields.Boolean(compute="_compute_display_contact", store=True)

    @api.depends('name', 'display_name', 'phone', 'email')
    def _compute_display_contact(self):
        print("here")
        for contact in self:
            display = False
            if contact.name and contact.display_name and contact.phone or contact.email:
                print("true")
                display = True
            contact.is_displayed = display

class NotEnrollReason(models.Model):
    _name = 'pm.not_enroll_reason'
    _description = 'Reason Not to enroll'
    name = fields.Char('Not Enroll Reason')


class EnrollReason(models.Model):
    _name = 'pm.enroll_reason'
    _description = 'Reason to enroll'
    name = fields.Char('Enroll Reason')


class StudentLanguage(models.Model):
    _name = 'pm.student.language'
    _description = 'Student Language'
    name = fields.Char('Languages')



class StudentScholarShip(models.Model):
    _name = 'pm.scholarship.status'
    _description = 'Student Scholarship'
    name = fields.Char('Scholarship Status')
    percentage = fields.Float('Percentage (%)')

class LeadParticipation(models.Model):
    _name = 'participation.name'
    name = fields.Char()
    point = fields.Integer('Point')


class Participation(models.Model):
    _name = 'pm.lead.participation'
    _description = 'Lead Participation'
    participation_id = fields.Many2one('participation.name', 'Participation')
    point = fields.Integer('Point', related='participation_id.point', store=True)
    lead_id = fields.Many2one('crm.lead')
    admission_id = fields.Many2one('op.admission')
    student_id = fields.Many2one('op.student')


    # @api.onchange('name')
    # def onchange_participation(self):
    #     if self['name'] == 'visit_and_tour':
    #         self['point'] = 2
    #     elif self['name'] == 'live_of_student':
    #         self['point'] = 3
    #     elif self['name'] == 'open_day':
    #         self['point'] = 1
    #     elif self['name'] == 'other':
    #         self['point'] = 2
    #     else:
    #         self['point'] = 0

class PMJobTitle(models.Model):
    _name = 'pm.job.title'
    _description = 'Job Title'
    name = fields.Char('Job Title', required=True)

class PmInTake(models.Model):
    _name = 'pm.intake'
    _description = 'In Take'
    name = fields.Char('Intake', required=True)

class PmDesiredCourse(models.Model):
    _name = 'pm.desired.course'
    _description = 'Desired Courses'
    name = fields.Char('Desired Courses', required=True)



class EducationalAchievement(models.Model):
    _name = 'pm.lead.educational.achievement'
    _description = 'Educational Achievement'
    name = fields.Selection([
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master')
    ], 'Educational Achievements', required=True)
    high_school_id = fields.Many2one('pm.high_school', 'School Name', required=False, index=True)
    school = fields.Char('School Name', required=False)
    major = fields.Char('Major')
    is_equivalent = fields.Boolean('Is Equivalent')
    lead_id = fields.Many2one('crm.lead')
    admission_id = fields.Many2one('op.admission')
    student_id = fields.Many2one('op.student')
    applicant_id = fields.Many2one('hr.applicant')
    employee_id = fields.Many2one('hr.employee')


class WorkingExperience(models.Model):
    _name = 'pm.lead.working.experience'
    _description = 'Working Experience'
    title_id = fields.Many2one('pm.job.title', 'Job Title', required=True, index=True)
    company = fields.Char('Company', required=True)
    year = fields.Integer('Years', required=True)
    lead_id = fields.Many2one('crm.lead')
    admission_id = fields.Many2one('op.admission')
    student_id = fields.Many2one('op.student')
    applicant_id = fields.Many2one('hr.applicant')
    employee_id = fields.Many2one('hr.employee')


class Lead(models.Model):
    _inherit = 'crm.lead'
    image = fields.Image('image')
    hobby = fields.Char('Hobby')
    family_size = fields.Integer('Family Size')
    khmer_name = fields.Char('Name in Khmer')
    first_name = fields.Char('First Name', required=True)
    last_name = fields.Char('Last Name', required=True)
    email = fields.Char('Email')
    meet_date = fields.Date('Event / Meet Date')
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other')
    ], 'Gender', required=False)
    dob = fields.Date('Date of Birth')
    birth_place = fields.Many2one('res.country.state', 'Birth Place')
    type = fields.Selection(selection_add=[('admission', 'Admission')], ondelete={'admission': 'cascade'})
    rank = fields.Selection([('first_contact', 'First Contact'),
                             ('potential', 'Potential'),
                             ('high_potential', 'High Potential')], required=True)
    fill_application = fields.Boolean('Fill Application')
    marital_status = fields.Selection([('single', 'Single'),
                                       ('married', 'Married')])
    constrains = fields.Text('Special Wishes')
    shoe_size = fields.Selection([
        ('xxs', 'XXS'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'Xl'),
        ('xxl', 'XXL'),
    ], 'Shoe Size')
    uniform_size = fields.Selection([
        ('xxs', 'XXS'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'Xl'),
        ('xxl', 'XXL'),
    ], 'Uniform Size')
    nationality = fields.Many2one('res.country', 'Nationality')
    primary_language = fields.Many2one('pm.student.language', string='Language')
    other_language = fields.Many2many('pm.student.language', string='Other languages', help="Other languages")
    english_score = fields.Float('English Score (%)')
    family_income = fields.Float('Source of Family income')
    family_status = fields.Selection([('p', 'Poor'),
                                      ('n', 'Normal'),
                                      ('r', 'Rich')])
    high_school_id = fields.Many2one('pm.high_school', 'High School')
    highest_education = fields.Selection([('HS', 'High School'),
                                          ('BA', 'Bachelor Degree'),
                                          ('MA', 'Master Degree'),
                                          ('PHD', 'Doctoral Degree')])
    working_experience = fields.Text('Working Experience')
    job_position = fields.Text('Job Position')
    enroll_reason_id = fields.Many2one('pm.enroll_reason', string='Reason to Enroll')
    not_enroll_reason_id = fields.Many2one('pm.not_enroll_reason', string='Reason not to Enroll')
    current_address = fields.Char('Current Address')
    high_school_count = fields.Integer(String="Lead By High School", compute='_get_highSchool_count', store=True)
    passport_number = fields.Char('Passport Number')
    id_card = fields.Char('ID Card')
    medical_checkup = fields.Boolean('Medical Check up', default=True)
    motivational_letter = fields.Boolean('Motivational Letter')
    special_medical = fields.Text('Special Medical Condition')
    p_street = fields.Char('Street...')
    p_street2 = fields.Char('Street...')
    p_city = fields.Char('City', size=64)
    p_zip = fields.Char('Zip', size=8)
    p_state_id = fields.Many2one(
        'res.country.state', 'States')
    p_country_id = fields.Many2one(
        'res.country', 'Country', )
    application_date = fields.Datetime(
        'Application Date', required=True, copy=False,
        default=lambda self: fields.Datetime.now())
    application_fee = fields.Boolean('Application Fee')
    is_scholarship = fields.Boolean('Scholarship')
    cancel_reason = fields.Text('Admission Cancel Reasons')
    scholarship_status = fields.Many2one('pm.scholarship.status', string='Scholarship Status')
    status = fields.Selection([('1st_follow_up', '1st follow-up'),
                               ('2nd_follow_up', '2nd follow-up'),
                               ('3rd_follow_up', '3rd follow-up'),
                               ('visited_and_toured', 'Visited & toured academy'),
                               ('live_student', 'Live of a student'),
                               ('pick_up_application', 'Pick up application'),
                               ('submitted_application', 'Submitted application incomplete'),
                               ('schedule_for_interview', 'Schedule for interview'),
                               ('interviewed', 'interviewed'),
                               ('acceptance_letter', 'Acceptance letter issued')])
    # status = fields.Many2one('participation.name', readonly=1)
    status_detail = fields.Char('Status Detail')
    lead_source = fields.Selection([('social_media', 'Social media'),
                                    ('facebook', 'Facebook'),
                                    ('website', 'Website'),
                                    ('school_visit', 'School Visit'),
                                    ('acac_student', 'By ACAC student'),
                                    ('friend', 'Friend'),
                                    ('school_councelor', 'School councelor'),
                                    ('family', 'Family'),
                                    ('open_day', 'Open day'),
                                    ('fair_exhibition', 'Fair/exhibition'),
                                    ('nea', 'NEA'),
                                    ('other', 'other')])
    lead_participation = fields.One2many('pm.lead.participation',
                                          inverse_name='lead_id',
                                          string='Participation',
                                          help="Participation")
    additional_source = fields.Char('Additional Source Info')
    parents = fields.Char('Parents')
    siblings = fields.Integer('Siblings')
    other_depends = fields.Char('Other Dependents')
    application_form = fields.Boolean('Application Form')
    pictures = fields.Boolean('Pictures')
    schooling_year = fields.Char('No. Schooling years')
    lead_educational_achievement = fields.One2many('pm.lead.educational.achievement',
                                                    inverse_name="lead_id",
                                                    string='Educational Achievements',
                                                    help="Educational Achievements")
    lead_working_experience = fields.One2many('pm.lead.working.experience',
                                               inverse_name="lead_id",
                                               string='Working Experience',
                                               help="Working Experience")
    scholar_application = fields.Boolean('Scholar Application')
    financial_status = fields.Boolean('Proof of Financial Status')
    contact_name = fields.Many2one('res.partner', string='Emergency Contact')
    total_point = fields.Float(String="Total Point", compute='_calculate_total_point', store=True)
    acac_contact = fields.Char('ACAC Contact')
    facebook = fields.Char('Facebook')
    phone = fields.Char('Mobile 1')
    visa_number = fields.Char('Visa Number')
    visa_expiry = fields.Date('Expiry Date')
    intake = fields.Many2one('pm.intake', 'Intake')
    desired_course = fields.Many2one('pm.desired.course', 'Desired Course')

    return_date = fields.Date("Return Date")
    reminding_date = fields.Date(compute="_compute_remind_date", store=True)
    cancel_date = fields.Date("Cancel Date")
    is_reminded = fields.Boolean()

    # marketing score
    m_motivational_letter = fields.Boolean(
        'Motivation letter is not a standard type of letter and reveals a genuine interest  (2pts)')
    m_responded = fields.Boolean(
        'Responded quickly to e-mail messages and/or phone calls  (2pts)')
    m_applied = fields.Boolean(
        'Applied before the final exam or before final exam publication  (3pts)')
    m_regularly_contacts = fields.Boolean(
        'Regularly contacts the Academy	 (2pts)')
    m_regularly_visit = fields.Boolean(
        'Regular visit on ACAC Facebook page  (2pts)')
    m_overall_impression = fields.Integer(
        'Overall impression on the interest of the student (1pts - 3pts)')


    def lead_reminder_scheduler(self):
        leads = self.env['crm.lead'].search([('type', '=', 'lead'),
                                             ('return_date', '!=', None),
                                             ('is_reminded', '!=', False)])

        for lead in leads:
            today = datetime.date.today()
            print('today', today)
            if today == lead.return_date or today == lead.reminding_date:
                ir_model_data = self.env['ir.model.data']
                try:
                    template_id = ir_model_data.get_object_reference('pm_leads', 'lead_follow_up_reminder')[1]
                except ValueError:
                    template_id = False
                self.env['mail.template'].browse(template_id).send_mail(lead.id, force_send=True)
                if today == lead.return_date:
                    lead.is_reminded = True



    @api.depends('return_date')
    def _compute_remind_date(self):
        for lead in self:
            if lead.return_date:
                return_date = lead.return_date
                d = datetime.timedelta(days=3)
                date = return_date - d
                print(return_date)
                print(date)
                lead.reminding_date = date

    @api.depends('lead_participation.point',
                 'm_motivational_letter',
                 'lead_participation',
                 'm_responded',
                 'm_applied',
                 'm_regularly_contacts',
                 'm_regularly_visit',
                 'm_overall_impression',
                 'activity_ids')
    def _calculate_total_point(self):
        for record in self:
            record.total_point = sum(x.point for x in record.lead_participation)
            if record.m_motivational_letter:
                record.total_point = record.total_point + 2
            if record.m_responded:
                record.total_point = record.total_point + 2
            if record.m_applied:
                record.total_point = record.total_point + 3
            if record.m_regularly_contacts:
                record.total_point = record.total_point + 2
            if record.m_regularly_visit:
                record.total_point = record.total_point + 2
            if record.m_overall_impression:
                record.total_point = record.total_point + record.m_overall_impression
            if len(record.activity_ids) > 2:
                record.total_point = record.total_point - (len(record.activity_ids) - 1)

    @api.depends('lead_participation')
    def _compute_lead_status(self):
        print('hit me XFD')
        print(self.lead_participation)

    @api.constrains('dob')
    def _check_birthdate(self):
        for record in self:
            if record.dob and record.dob > fields.Date.today():
                raise ValidationError(_(
                    "Date of Birth can't be greater than current date!"))

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(Lead, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                submenu=submenu)
        if self.env.context.get('make_form_readonly'):  # Check for context value
            doc = etree.XML(res['arch'])  # Get the view architecture of record
            if view_type == 'form':  # Applies only if it is form view
                for node in doc.xpath("//field"):  # Get all the fields navigating through xpath
                    modifiers = simplejson.loads(node.get("modifiers"))  # Get all the existing modifiers of each field
                    modifiers['readonly'] = True  # Add readonly=True attribute in modifier for each field
                    node.set('modifiers',
                             simplejson.dumps(modifiers))  # Now, set the newly added modifiers to the field
                res['arch'] = etree.tostring(doc)  # Update the view architecture of record with new architecture
        return res

    @api.depends('high_school_id')
    def _get_highSchool_count(self):
        for r in self:
            if r.high_school_id and r.type == "lead":
                r.high_school_count = len(r.high_school_id)

    @api.model
    def create(self, val):
        res = super(Lead, self).create(val)
        cam_id = val.get('campaign_id')
        camp = self.env['utm.campaign']
        number_of_lead = self.search_count([('campaign_id', '=', cam_id)])
        campaign = camp.search([('id', '=', cam_id)])
        campaign_cost = campaign.cost
        campaign.cost_per_lead = campaign_cost / number_of_lead

        # calculate conversion rate for dashboard
        convert_rate = self.env['pm_lead_conversion'].search([('id', '=', 1)])
        total = self.env['crm.lead'].search_count([])
        admission = self.env['crm.lead'].search_count([('type', '=', 'admission')])
        if admission > 0:
            # result = admission * 100 / total
            result = (admission / total) * 100
            convert_rate.conversion_rate = result

        return res

    @api.model
    def admission_form(self, arg):
        view_id = self.env.ref('openeducat_admission.pm_admission_form').id

        return {
            'name': 'custom_admission_form',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'op.admission',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            # 'context': ctx,
        }

    @api.model
    def convert_to_admission(self, arg):


        view_id = self.env.ref('pm_admission.view_pm_admission_form').id
        lead_ref = self.env['crm.lead'].browse(arg)

        for lead in lead_ref:
            langs = [[6, False,lead.other_language.mapped('id')]]
            educat = [[6, False, lead.lead_educational_achievement.mapped('id')]]
            working = [[6, False, lead.lead_working_experience.mapped('id')]]
            partition = [[6, False, lead.lead_participation.mapped('id')]]

            ctx = {
                'default_street': lead.street,
                'default_image': lead.image,
                'default_street2': lead.street2,
                'default_mobile': lead.mobile,
                'default_phone': lead.phone,
                'default_birth_date': lead.dob,
                'default_birth_place': lead.birth_place.id,
                'default_city': lead.city,
                'default_zip': lead.zip,
                'default_current_address': lead.current_address,
                'default_state_id': lead.state_id.id,
                'default_country_id': lead.country_id.id,
                'default_first_name': lead.first_name,
                'default_last_name': lead.last_name,
                'default_khmer_name': lead.khmer_name,
                'default_email': lead.email_from,
                'default_lead_id': lead.id,
                'default_gender': lead.gender,
                'default_primary_language': lead.primary_language.id,
                'default_other_language': langs,
                'default_marital_status': lead.marital_status,
                'default_nationality': lead.nationality.id,
                'default_shoe_size': lead.shoe_size,
                'default_campaign_id': lead.campaign_id.id,
                'default_source_id': lead.source_id.id,
                'default_uniform_size': lead.uniform_size,
                'default_working_experience': lead.working_experience,
                'default_job_position': lead.job_position,
                'default_hobby': lead.hobby,
                'default_constrains': lead.constrains,
                'default_family_size': lead.family_size,
                'default_family_status': lead.family_status,
                'default_family_income': lead.family_income,
                'default_highest_education': lead.highest_education,
                'default_english_score': lead.english_score,
                'default_enroll_reason_id': lead.enroll_reason_id.id,
                'default_passport_number': lead.passport_number,
                'default_id_card': lead.id_card,
                'default_medical_checkup': lead.medical_checkup,
                'default_motivational_letter': lead.motivational_letter,
                'default_special_medical': lead.special_medical,
                'default_is_scholarship': lead.is_scholarship,
                'default_scholarship_status': lead.scholarship_status.id,
                'default_high_school_id': lead.high_school_id.id,

                'default_rank': lead.rank,
                'default_status_detail': lead.status_detail,
                'default_lead_source': lead.lead_source,
                'default_additional_source': lead.additional_source,
                'default_parents': lead.parents,
                'default_siblings': lead.siblings,
                'default_other_depends': lead.other_depends,
                'default_application_form': lead.application_form,
                'default_pictures': lead.pictures,
                'default_schooling_year': lead.schooling_year,
                'default_lead_educational_achievement': educat,
                'default_lead_working_experience': working,
                'default_lead_participation': partition,
                'default_visa_number': lead.visa_number,
                'default_visa_expiry': lead.visa_expiry,
                'default_facebook': lead.facebook,

                'default_scholar_application': lead.scholar_application,
                'default_financial_status': lead.financial_status,
                'default_contact_name': lead.contact_name.id,
                'default_application_fee': lead.application_fee,

                'default_p_street': lead.p_street,
                'default_p_street2': lead.p_street2,
                'default_p_city': lead.p_city,
                'default_p_zip': lead.p_zip,
                'default_p_state_id': lead.p_state_id.id,
                'default_p_country_id': lead.p_country_id.id,

            }

            print(ctx)

        messages = ''
        if not ctx['default_birth_date']:
            messages += 'Date of Birth <br/>'
        if not ctx['default_email']:
            messages += 'Email <br/>'
        if not ctx['default_special_medical'] and not ctx['default_medical_checkup']:
            messages += 'Medical Check up or Special Medical Condition <br/>'
        if not ctx['default_application_form']:
            messages += 'Application Form <br/>'
        if not ctx['default_application_fee']:
            messages += 'Application Fee <br/>'
        if not ctx['default_primary_language']:
            messages += 'Native Language</br>'

        if not ctx['default_gender']:
            messages += 'Gender</br>'

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'The following fields are invalid:',
                'message': _(messages),
                'type': 'danger',  # types: success,warning,danger,info
                'sticky': False,  # True/False will display for few seconds if false
            },
        }

        admission_form = {
            'name': 'Admission Conversion',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'op.admission',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': ctx,
        }

        if messages:
            return notification
        else:
            return admission_form