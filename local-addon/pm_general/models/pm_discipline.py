from odoo.exceptions import ValidationError
from odoo import models, fields,api, _

class OpDiscipline(models.Model):
    _inherit = "op.discipline"
    misbehaviour_action = fields.Char('Action To Be Taken', required=False)
    misbehaviour_type = fields.Selection(
        [('major', 'Major'), ('minor', 'Minor')],
        'Misbehaviour Type', required=False)
    misbehaviour_category_id = fields.Many2one(
        'op.misbehaviour.category', 'Misbehaviour Category', required=False)
    point = fields.Float('Demerit Point', related='misbehaviour_category_id.p_demerit_points')
    company_id = fields.Many2one(
        'res.company', 'Company', required=False,
        default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        [('draft', 'Draft'), 
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        'State', default='draft', track_visibility='onchange')
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, track_visibility='onchange')
    semester_id = fields.Many2one('pm.semester', 'Semester')
    student_discipline_id = fields.Many2one('pm.student.discipline', 'Semester Discipline')
    approval_record_id = fields.Many2one('pm.approval')



    @api.depends('student_id')
    def _compute_get_student_class(self):
        for record in self:
            if record.student_id:
                student_course = self.env['op.student.course'].search([
                    ('student_id', '=', record.student_id.id), ('p_active', '=', True)
                ], limit=1)
                if student_course:
                    record.course_id = student_course.course_id
                    record.batch_id = student_course.batch_id
                    semester = self.env['pm.semester'].sudo().search(
                        [('state', '=', 'active'), ('batch_id', '=', student_course.batch_id.id)])
                    record.semester_id = semester

    def act_submit(self):
        dermit_point = self.misbehaviour_category_id.p_demerit_points
        if dermit_point < 0.5:
            'print less than one'
            self.deduct_point(dermit_point)
            self.state = 'approved'
        else:
            print('more than one')
            #send Email to Approver
            self.state = 'submitted'
            approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'op.discipline')])
            print(approval_type.id)
            approval = self.env['pm.approval'].create({
                'approval_type_id': approval_type.id,
                'record_id': self.id,
            })
            self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
            self.approval_record_id = approval.id

    def act_approve(self):
        dermit_point = self.misbehaviour_category_id.p_demerit_points
        self.deduct_point(dermit_point)
        approval = self.approval_record_id
        if approval:
            approval.state = 'approved'
        self.state = 'approved'
        notification_obj = self.env['pm.menu.notification']
        notification_obj.update_notification('discipline', self.student_id.id)


    def act_reject(self):
        self.state = 'rejected'
        approval = self.approval_record_id
        if approval:
            approval.state = 'rejected'

    def deduct_point(self, dermit_point):
        student_discipline = self.env['pm.student.discipline'].search(
            ['&', ('semester_id', '=', self.semester_id.id), ('student_id', '=', self.student_id.id)])
        remaining_point = student_discipline.discipline_point - dermit_point
        student_discipline.discipline_point = remaining_point
        self.student_discipline_id = student_discipline.id

        if remaining_point < 10 and remaining_point >= 7.5:
            student_discipline.state = 'okay'
        elif remaining_point <= 7.5 and remaining_point >= 6.5:
            student_discipline.state = 'first_warning'
            self.send_first_warning()
        elif remaining_point <= 6.5 and remaining_point >= 5.5:
            student_discipline.state = 'second_warning'
            self.send_second_warning()
        elif remaining_point < 5.5:
            student_discipline.state = 'dismissed'
            self.send_dismissed_letter()
            student_course = self.env['op.student.course'].search([
                ('student_id', '=', self.student_id.id),
                ('batch_id', '=', self.batch_id.id),
                ('p_active', '=', 'True')
            ], limit=1)
            print("Below 5.5")
            print("Dismissed")
            student_course.education_status = 'dismissed'


    def send_first_warning(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_general', 'pm_disciplinary_1st_warning')[1]
        except ValueError:
            template_id = False
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def send_second_warning(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_general', 'pm_disciplinary_2nd_warning')[1]
        except ValueError:
            template_id = False
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def send_dismissed_letter(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('pm_general', 'disciplinary_dismiss')[1]
        except ValueError:
            template_id = False
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    # def write(self, val):
    #     print("Hit Write")
    #     print(val)
    #     if self.state == "approved":
    #         raise ValidationError("Discipline record has already been approved, can not be modified")
    #     res = super(OpDiscipline, self).write(val)
    #     return res

class OpMisbehaviourCategory(models.Model):
    _inherit = "op.misbehaviour.category"
    p_demerit_points = fields.Float('Dermit Points')
    misbehaviour_template_id = fields.Many2one(
        'mail.template', 'Misbehaviour Template', required=False)

class PmStudentDiscipline(models.Model):
    _name = "pm.student.discipline"
    student_id = fields.Many2one('op.student', 'Student')
    semester_id = fields.Many2one('pm.semester', 'Semester')
    discipline_point = fields.Float('Discipline Point', default=10)
    state = fields.Selection(
        [
         ('default', 'Default Points'),
         ('okay', 'Okay'),
         ('first_warning', 'First Warning'),
         ('second_warning', 'Second Warning'),
         ('dismissed', 'Dismissed')],
        'State', track_visibility='onchange', default='default')
    semester_discipline = fields.One2many(
        'op.discipline', 'student_discipline_id', 'Discipline Records')


