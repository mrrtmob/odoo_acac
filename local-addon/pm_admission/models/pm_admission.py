# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from odoo.http import request

class OpAdmissionRegisterCustom(models.Model):
    _inherit = "op.admission.register"
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True)
    product_id = fields.Many2one(
        'product.product', 'Course Fees', required=False,
        domain=[('type', '=', 'service')], readonly=True,
        states={'draft': [('readonly', False)]}, track_visibility='onchange')

class OpAdmission(models.Model):
    _inherit = 'op.admission'
    batch_id = fields.Many2one('op.batch', 'Term', domain=[], required=True, readonly=False)
    name = fields.Char(
        'Name', size=128, required=False, translate=False)
    readonly = fields.Boolean(compute="_compute_read_only")
    class_id = fields.Many2one('op.classroom', 'Class', required=False)

    birth_place = fields.Many2one('res.country.state', 'Birth Place')
    payment_option = fields.Selection([('normal', 'Normal'),
                                       ('exempted', 'Exempted'),
                                       ('haft_scholarship', '50% Scholarship'),
                                       ('full_scholarship', '100% Scholarship'),
                                       ('installment', 'Installment')], default='normal')
    fill_application = fields.Boolean('Fill Application')
    marital_status = fields.Selection([('single', 'Single'),
                                       ('married', 'Married')])
    constrains = fields.Text('Special Wishes')
    shoe_size_id = fields.Many2one('pm.shoe.size')
    uniform_size_id = fields.Many2one('pm.uniform.size')
    shoe_size = fields.Selection([
        ('xxs', 'XXS'),
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'Xl'),
        ('xxl', 'XXL'),
    ], 'Shoe Size')
    khmer_name = fields.Char('Name in Khmer')
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
    primary_language = fields.Many2one('pm.student.language', string='Other Language')
    other_language = fields.Many2many('pm.student.language', string='Other languages', help="Other languages")
    english_score = fields.Float('English Score (%)')
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
    hobby = fields.Char('Hobby')
    family_size = fields.Integer('Family Size')
    family_status = fields.Selection([('p', 'Poor'),
                                      ('n', 'Normal'),
                                      ('r', 'Rich')])
    campaign_id = fields.Many2one('utm.campaign', 'Campaign')
    source_id = fields.Many2one('utm.source', 'Source')
    referred = fields.Char('Referred By')
    passport_number = fields.Char('Passport Number')
    id_card = fields.Char('ID Card')
    medical_checkup = fields.Boolean('Medical Check up', default=True)
    motivational_letter = fields.Boolean('Motivational Letter')
    special_medical = fields.Text('Special Medical Condition')
    is_scholarship = fields.Boolean('Scholarship')
    lead_id = fields.Integer()
    p_street = fields.Char('Street...')
    p_street2 = fields.Char('Street...')
    p_city = fields.Char('City', size=64)
    p_zip = fields.Char('Zip', size=8)
    p_state_id = fields.Many2one(
        'res.country.state', 'States')
    p_country_id = fields.Many2one(
        'res.country', 'Country', )

    application_number = fields.Char(
        'Application Number', copy=False, readonly=True, store=True)

    # new fields
    application_date = fields.Datetime(
        'Application Date', required=True, copy=False,
        default=lambda self: fields.Datetime.now())
    application_fee = fields.Boolean('Application Fee', required=True, default=True)
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
    status_detail = fields.Char('Status detail')
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
                                         inverse_name='admission_id',
                                         string='Participation',
                                         help="Participation")
    additional_source = fields.Char('Additional Source Info')
    parents = fields.Char('Parents')
    siblings = fields.Integer('Siblings')
    other_depends = fields.Char('Other dependents')
    application_form = fields.Boolean('Application Form', default=True, required=True)
    pictures = fields.Boolean('Pictures')
    schooling_year = fields.Char('No. Schooling years')
    lead_educational_achievement = fields.One2many('pm.lead.educational.achievement',
                                                   inverse_name="admission_id",
                                                   string='Educational Achievements',
                                                   help="Educational Achievements")
    lead_working_experience = fields.One2many('pm.lead.working.experience',
                                              inverse_name="admission_id",
                                              string='Working Experience',
                                              help="Working Experience")
    contact_name = fields.Many2one('res.partner', string='Emergency Contact')
    email_from = fields.Char('Email', help="Email address of the contact", tracking=40, index=True)
    user_id = fields.Many2one('res.users', string='ACAC Contact', index=True, tracking=True,
                              default=lambda self: self.env.user)
    acac_contact = fields.Char('ACAC Contact')
    scholar_application = fields.Boolean('Scholar Application')
    financial_status = fields.Boolean('Proof of Financial Status')
    family_income = fields.Float('Source of Family income')
    rank = fields.Selection([('first_contact', 'First Contact'),
                             ('potential', 'Potential'),
                             ('high_potential', 'High Potential')])
    facebook = fields.Char('Facebook')
    phone = fields.Char('Mobile 1')
    admission_url = fields.Char('Link', compute="_compute_admission_url", store=True)
    visa_number = fields.Char('Visa Number')
    visa_expiry = fields.Date('Expiry Date')
    product_id = fields.Many2one(
        'product.product', 'Course Fees', required=False,
        domain=[('type', '=', 'service')],track_visibility='onchange')


    @api.depends('state')
    def _compute_read_only(self):
        for rec in self:
            if rec.state == 'done':
                rec.readonly = True
            else:
                rec.readonly = False

    @api.onchange('register_id')
    def onchange_register(self):
        print('gege')
        print(self.register_id.batch_id)
        self.course_id = self.register_id.course_id
        self.batch_id = self.register_id.batch_id
        print(self.course_id)
        print(self.batch_id)

    @api.onchange('course_id')
    def onchange_course(self):
        # self.batch_id = False
        term_id = False
        if self.course_id and self.course_id.fees_term_id:
            term_id = self.course_id.fees_term_id.id
        self.fees_term_id = term_id


    @api.onchange('product_id')
    def onchange_product(self):
        print('gaga')
        self.fees = self.product_id.lst_price

    @api.depends('name')
    def _compute_admission_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=op.admission' % (record.id)
            record.admission_url = base_url

    def submit_form(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_admission', 'student_admission_submission')[1]
        except ValueError:
            template_id = False
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
        self.state = 'submit'

        action = self.env.ref("crm.crm_lead_all_leads").read()[0]
        return action

    def confirm_in_progress(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_admission', 'student_payment_confirm')[1]
        except ValueError:
            template_id = False
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
        self.state = 'confirm'

        action = self.env.ref("crm.crm_lead_all_leads").read()[0]
        return action

    def admission_confirm(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_admission', 'student_admission_confirm')[1]
        except ValueError:
            template_id = False
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
        self.state = 'admission'

        action = self.env.ref("crm.crm_lead_all_leads").read()[0]
        return action

    def confirm_cancel(self):
        lead = self.env['crm.lead'].browse(self.lead_id)
        lead.type = 'lead'
        self.unlink()

        action = self.env.ref("crm.crm_lead_all_leads").read()[0]
        return action


    @api.onchange('student_id')
    def onchange_student_id(self):

        student = self.env['op.student'].search(
            [('id', '=', self.student_id.id)])
        print(student)
        if self.student_id and self.is_student:
            self['prev_course_id'] = student['prev_course_id']
            self['high_school_id'] = student['high_school_id']
            self['english_score'] = student['english_score']

            # additional information
            self['khmer_name'] = student['khmer_name']
            self['id_card'] = student['id_card']
            self['passport_number'] = student['passport_number']
            self['marital_status'] = student['marital_status']
            self['nationality'] = student['nationality']
            self['primary_language'] = student['primary_language']
            self['other_language'] = student['other_language']
            self['shoe_size'] = student['shoe_size']
            self['uniform_size'] = student['uniform_size']
            self['job_position'] = student['job_position']
            self['working_experience'] = student['working_experience']
            self['constrains'] = student['constrains']
            self['hobby'] = student['hobby']
            self['facebook'] = student['facebook']
            self['visa_number'] = student['visa_number']
            self['visa_expiry'] = student['visa_expiry']
            self['image'] = student['image_1920']

            # family info
            self['family_status'] = student['family_status']
            self['family_business'] = student['family_business']
            self['family_income'] = student['family_income']
            self['family_size'] = student['family_size']

            #
            self['campaign_id'] = student['campaign_id']
            self['source_id'] = student['source_id']
            self['referred'] = student['referred']

            # Extra
            self['medical_checkup'] = student['medical_checkup']
            self['special_medical'] = student['special_medical']
            self['motivational_letter'] = student['motivational_letter']

    @api.onchange('is_student')
    def onchange_is_student(self):
        if not self.is_student:
            self['prev_course_id'] = False
            self['high_school_id'] = False
            self['english_score'] = False

            # additional information
            self['khmer_name'] = False
            self['id_card'] = False
            self['passport_number'] = False
            self['marital_status'] = False
            self['nationality'] = False
            self['primary_language'] = False
            self['other_language'] = False
            self['shoe_size'] = False
            self['uniform_size'] = False
            self['job_position'] = False
            self['working_experience'] = False
            self['constrains'] = False
            self['hobby'] = False
            self['facebook'] = False
            self['visa_number'] = False
            self['visa_expiry'] = False

            # family info
            self['family_status'] = False
            self['family_business'] = False
            self['family_income'] = False
            self['family_size'] = False

            #
            self['campaign_id'] = False
            self['source_id'] = False
            self['referred'] = False

            # Extra
            self['medical_checkup'] = False
            self['special_medical'] = False
            self['motivational_letter'] = False

    @api.model
    def create(self, val):



        student = self.env['op.student'].search(
            [('id', '=', self.student_id.id)])
        if self.student_id and self.is_student:
            self['prev_course_id'] = student['prev_course_id']
            self['high_school_id'] = student['high_school_id']
            self['english_score'] = student['english_score']

            # additional information
            self['khmer_name'] = student['khmer_name']
            self['id_card'] = student['id_card']
            self['passport_number'] = student['passport_number']
            self['marital_status'] = student['marital_status']
            self['nationality'] = student['nationality']
            self['primary_language'] = student['primary_language']
            self['other_language'] = student['other_language']
            self['shoe_size'] = student['shoe_size']
            self['uniform_size'] = student['uniform_size']
            self['job_position'] = student['job_position']
            self['working_experience'] = student['working_experience']
            self['constrains'] = student['constrains']
            self['hobby'] = student['hobby']
            self['facebook'] = student['facebook']
            self['visa_number'] = student['visa_number']
            self['visa_expiry'] = student['visa_expiry']

            # family info
            self['family_status'] = student['family_status']
            self['family_business'] = student['family_business']
            self['family_income'] = student['family_income']
            self['family_size'] = student['family_size']

            #
            self['campaign_id'] = student['campaign_id']
            self['source_id'] = student['source_id']
            self['referred'] = student['referred']

            # Extra
            self['medical_checkup'] = student['medical_checkup']
            self['special_medical'] = student['special_medical']
            self['motivational_letter'] = student['motivational_letter']

    @api.onchange('is_student')
    def onchange_is_student(self):
        if not self.is_student:
            self['prev_course_id'] = False
            self['high_school_id'] = False
            self['english_score'] = False

            # additional information
            self['khmer_name'] = False
            self['id_card'] = False
            self['passport_number'] = False
            self['marital_status'] = False
            self['nationality'] = False
            self['primary_language'] = False
            self['other_language'] = False
            self['shoe_size'] = False
            self['uniform_size'] = False
            self['job_position'] = False
            self['working_experience'] = False
            self['constrains'] = False
            self['hobby'] = False

            # family info
            self['family_status'] = False
            self['family_business'] = False
            self['family_income'] = False
            self['family_size'] = False

            #
            self['campaign_id'] = False
            self['source_id'] = False
            self['referred'] = False

            # Extra
            self['medical_checkup'] = False
            self['special_medical'] = False
            self['motivational_letter'] = False

    # @api.onchange('batch_id')
    # def onchange_batch_id(self):
    #     if self.batch_id and self.batch_id.state != 'active':
    #         msg = 'The selected term is not active: (%s) state: (%s)' % (self.batch_id.name,
    #                                                                      self.batch_id.state)
    #         raise ValidationError(_(msg))

    @api.model
    def create(self, val):

        print('=====batch=====')
        print(val['batch_id'])
        if val['batch_id']:
            print('hit 1')
            batch = self.env['op.batch'].browse(val['batch_id'])
            if batch.state != 'active':
                print('hit 2')
                msg = 'The selected term is not active:- (%s)' % (
                    batch.name)
                raise ValidationError(_(msg))

        lead_id = val.get('lead_id')
        if lead_id:
            lead_ref = self.env['crm.lead'].browse(lead_id)
            lead_ref.type = "admission"

        res = super(OpAdmission, self).create(val)
        attachment = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', lead_id)])

        if attachment:
            for att in attachment:
                att.write({
                    'res_model': 'op.admission',
                    'res_id': res.id
                })
        return res

    def enroll_student(self):
        for record in self:
            messages = ''
            if not record.class_id:
                messages += 'Class | '
            if not record.contact_name:
                messages += 'Emergency Contact | '
            if len(messages):
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Please fill in the following fields:',
                        'message': _(messages),
                        'type': 'danger',  # types: success,warning,danger,info
                        'sticky': True,  # True/False will display for few seconds if false
                    },
                }
                return notification

            if record.register_id.max_count:
                total_admission = self.env['op.admission'].search_count(
                    [('register_id', '=', record.register_id.id),
                     ('state', '=', 'done')])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (
                        record.register_id.max_count)
                    raise ValidationError(_(msg))
            if not record.student_id:
                vals = record.get_student_vals()
                record.partner_id = vals.get('partner_id')
                record.student_id = student_id = self.env[
                    'op.student'].create(vals).id
            else:
                record.student_id.course_detail_ids.p_active = False
                student_id = record.student_id.id
                record.student_id.write({
                    'course_detail_ids': [[0, False, {
                        'course_id':
                            record.course_id and record.course_id.id or False,
                        'batch_id':
                            record.batch_id and record.batch_id.id or False,
                        'p_active': True,
                    }]],
                })

            attachment = self.env['ir.attachment'].search([('res_model', '=', 'op.admission'), ('res_id', '=', record.id)])
            print(attachment)
            if attachment:
                for att in attachment:
                    attchment_clone = att.copy()
                    print('******')
                    print(attchment_clone)
                    attchment_clone.write({
                        'res_model': 'op.student',
                        'res_id': student_id
                    })
                    print('true true')


            if record.fees_term_id:
                val = []
                product = self.env['product.product'].search([('barcode', '=', '168@168')])
                print('...........product............')
                product_id = product.id
                for line in record.fees_term_id.line_ids:
                    no_days = line.due_days
                    no_alert_days = no_days - 7
                    state = 'draft'
                    price = line.total
                    print(price)
                    amount = price
                    date = (datetime.today() + relativedelta(
                        days=no_days)).date()
                    alert_date = (datetime.today() + relativedelta(
                        days=no_alert_days)).date()
                    dict_val = {
                        'semester': line.semester,
                        'fees_line_id': line.id,
                        'amount': amount,
                        'date': date,
                        'alert_date': alert_date,
                        'product_id': product_id,
                        'state': state,
                    }
                    val.append([0, False, dict_val])
                print(val)

                record.student_id.write({
                    'fees_detail_ids': val
                })
            record.write({
                'nbr': 1,
                'state': 'done',
                'admission_date': fields.Date.today(),
                'student_id': student_id,
                'is_student': True,
            })


    def get_student_vals(self):
        for student in self:
            langs = [[6, False, student.other_language.mapped('id')]]
            educat = [[6, False, student.lead_educational_achievement.mapped('id')]]
            working = [[6, False, student.lead_working_experience.mapped('id')]]
            partition = [[6, False, student.lead_participation.mapped('id')]]

            student_user = self.env['res.users'].with_context(no_reset_password=False).create({
                'name': student.name,
                'login': student.email,
                'image_1920': self.image or False,
                'is_student': True,
                'company_id': self.env.ref('base.main_company').id,
                'groups_id': [
                    (6, 0,
                     [self.env.ref('base.group_portal').id])]
            })
            details = {
                'phone': student.phone,
                'mobile': student.mobile,
                'email': student.email,
                'street': student.street,
                'street2': student.street2,
                'city': student.city,
                'country_id':
                    student.country_id and student.country_id.id or False,
                'state_id': student.state_id and student.state_id.id or False,
                'image_1920': student.image,
                'zip': student.zip
            }
            student_user.partner_id.write(details)
            student_user.with_context(create_user=True).action_reset_password()
            details.update({
                'title': student.title and student.title.id or False,
                'first_name': student.first_name,
                'birth_place': student.birth_place.id,
                'middle_name': student.middle_name,
                'khmer_name': student.khmer_name,
                'last_name': student.last_name,
                'birth_date': student.birth_date,
                'gender': student.gender,
                'image_1920': student.image or False,
                'course_detail_ids': [[0, False, {
                    'course_id':
                        student.course_id and student.course_id.id or False,
                    'batch_id':
                        student.batch_id and student.batch_id.id or False,
                    'class_ids': [[6, 0, [student.class_id.id]]],

                 }]],
                'user_id': student_user.id,
                'partner_id': student_user.partner_id.id,
                'batch_id':
                        student.batch_id and student.batch_id.id or False,
                'fill_application': student.marital_status,
                'marital_status': student.marital_status,
                'constrains': student.constrains,
                'shoe_size': student.shoe_size,
                'shoe_size_id': student.shoe_size_id.id,
                'uniform_size': student.uniform_size,
                'uniform_size_id': student.uniform_size_id.id,
                'primary_language': student.primary_language.id,
                'other_language': langs,
                'english_score': student.english_score,
                'highest_education': student.highest_education,
                'working_experience': student.working_experience,
                'job_position': student.job_position,
                'current_address': student.current_address,
                'hobby': student.hobby,
                'family_size': student.family_size,
                'family_status': student.family_status,
                'passport_number': student.passport_number,
                'id_card': student.id_card,
                'campaign_id': student.campaign_id.id,
                'source_id': student.source_id.id,
                'referred': student.referred,
                'medical_checkup': student.medical_checkup,
                'is_scholarship': student.is_scholarship,
                'scholarship_status': student.scholarship_status.id,
                'motivational_letter': student.motivational_letter,
                'special_medical': student.special_medical,
                'enroll_reason_id': student.enroll_reason_id.id,
                'high_school_id': student.high_school_id.id,
                'facebook': student.facebook,
                'visa_number': student.visa_number,
                'visa_expiry': student.visa_expiry,
                'nationality': student.nationality.id,
                'rank': student.rank,
                'status_detail': student.status_detail,
                'lead_source': student.lead_source,
                'additional_source': student.additional_source,
                'parents': student.parents,
                'siblings': student.siblings,
                'other_depends': student.other_depends,
                'application_form': student.application_form,
                'pictures': student.pictures,
                'schooling_year': student.schooling_year,
                'lead_educational_achievement': educat,
                'lead_working_experience': working,
                'lead_participation': partition,
                'family_income': student.family_income,

                'scholar_application': student.scholar_application,
                'financial_status': student.financial_status,
                'contact_name': student.contact_name.id,
                'application_fee': student.application_fee,

                'p_street': student.p_street,
                'p_street2': student.p_street2,
                'p_city': student.p_city,
                'p_zip': student.p_zip,
                'p_state_id': student.p_state_id.id,
                'p_country_id': student.p_country_id.id,
            })
            print('*&(7e2132')
            print(details)
            return details

    def write(self, vals):
      # Temporarily fixing image issue when update a record
      if vals['image']:
          self.env.cr.execute("""DELETE FROM ir_attachment WHERE res_model = '%s' AND res_field = '%s' AND res_id = %d""" % (self._name, 'image', self.id))

      return super(OpAdmission, self).write(vals)