from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PmExam(models.Model):
    _inherit = "op.exam"
    exam_type = fields.Selection(
        [('quiz', 'Quiz'), ('written', 'Written Exam'),
         ('practical', 'Practical Exam'), ('assignment', 'Assignment'),
         ('portfolio', 'Portfolio'), ('mid_term', 'Mid Term Exam'),
         ('open_book_exam', 'Open Book Exam'), ('presentation', 'Presentation'),
         ('final_exam', 'Final Exam'), ('Practical comprehensive Exam', 'Practical comprehensive Exam'),
         ('re-sit', 'Re-sit Exam')],
        'Exam Type', default="", required=True)
    grade_weightage = fields.Integer('Exam Weigh')
    exam_code = fields.Char('Exam Code', size=16, required=False)
    start_time = fields.Datetime('Start Time', required=False)
    end_time = fields.Datetime('End Time', required=False)
    total_marks = fields.Integer('Total Marks', required=True, default=100)
    min_marks = fields.Integer('Passing Marks', required=True, default=55)
    session_id = fields.Many2one('op.exam.session', 'Exam Schedule',
                                 domain=[('state', 'not in',
                                          ['cancel', 'done'])])
    subject_id = fields.Many2one('op.subject', string='Subject', readonly=True)
    result_line = fields.One2many(
        'op.result.line', 'exam_id', 'Result Line', readonly=True)
    class_exam_ids = fields.One2many(
        'pm.class.exam', 'exam_id', 'Class Exam(s)', readonly=True)
    batch_id = fields.Many2one('op.batch', 'Term', store=True, readonly=True)
    faculty_id = fields.Many2one('op.faculty', 'Faculty', related='session_id.faculty_id', store=True)
    class_exam_count = fields.Integer(compute="_compute_exam_count")
    name = fields.Char(required=False, string="Name")

    @api.onchange('exam_type', 'session_id.batch_id', 'session_id.subject_id')
    def _compute_exam_name(self):
        type = self._fields['exam_type'].selection
        code_dict = dict(type)
        type_name = code_dict.get(self.exam_type)

        if self.session_id.subject_id.name and type_name and self.session_id.batch_id:
            self.name = self.session_id.subject_id.name + ': ' + type_name + ': ' + self.session_id.batch_id.name


    def _compute_exam_count(self):
        for rec in self:
            rec.class_exam_count = len(rec.class_exam_ids)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_exam', False):
            lst = []
            lst.append(self.env.context.get('exam_session_id'))
            print(lst)
            semester = self.env['op.exam'].search([('session_id', 'in', lst)])
            return semester.name_get()
        return super(PmExam, self).name_search(
            name, args, operator=operator, limit=limit)

    @api.model
    def create(self, val):
        self_ref = self.env['op.exam.session'].browse(val['session_id'])
        subject_id = self_ref.subject_id.id
        val['subject_id'] = subject_id
        res = super(PmExam, self).create(val)
        return res

    @api.constrains('session_id', 'grade_weightage')
    def _check_total_grading_wieght(self):
        for record in self:
            wieght = 0
            for exam in record.session_id.exam_ids:
                print(exam.grade_weightage)
                wieght += exam.grade_weightage
            print(wieght)
            if wieght > 100:
                raise ValidationError("Total grading for all exams should not be more than 100")

    @api.onchange('session_id')
    def onchange_session_id(self):
        subject_id = self.session_id.subject_id
        self['subject_id'] = subject_id


class PmExamSession(models.Model):
    _inherit = "op.exam.session"
    _description = "Exam Schedule"

    def _get_default_faculty(self):
        if (self.user_has_groups('openeducat_core.group_op_faculty') and
                not self.user_has_groups('openeducat_core.group_op_back_office_admin') and
                not self.user_has_groups('openeducat_core.group_op_back_office')):
            return self.env['op.faculty'].search([('emp_id.user_id.id', '=', self.env.user.id)])

        return None

    name = fields.Char(compute='_compute_name', string='Exam Schedule', store=True, required=False)
    semester_id = fields.Many2one(
        'pm.semester', 'Semester', store=True)
    subject_id = fields.Many2one('op.subject', 'Subject', required=True)
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, track_visibility='onchange')
    exam_type = fields.Many2one(
        'op.exam.type', 'Exam Type', required=False, track_visibility='onchange')
    evaluation_type = fields.Selection(
        [('normal', 'Normal'), ('grade', 'Grade')],
        'Evolution type', default="grade",
        required=False, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('cancel', 'Cancelled'),
        ('submitted', 'Submitted'),
        ('done', 'Done')
    ], 'State', default='draft', track_visibility='onchange')
    is_resit = fields.Boolean('Resit Exam?')
    faculty_id = fields.Many2one('op.faculty', 'Faculty', required=True, default=_get_default_faculty,
                                 track_visibility='onchange')

    exam_count = fields.Integer(compute="_compute_exam_count")
    class_exam_count = fields.Integer(compute="_compute_exam_count")


    def _compute_exam_count(self):
        for rec in self:
            exams = rec.exam_ids
            rec.exam_count = len(exams)
            rec.class_exam_count = len(exams.class_exam_ids)

    def act_done(self):
        exams = self.exam_ids.class_exam_ids
        state = exams.mapped('state')
        is_all_done = len(set(state)) <= 1
        if is_all_done and 'done' in state:
            self.state = 'done'
        else:
            raise ValidationError("All class exams have to be done first")


    @api.depends('subject_id', 'semester_id', 'batch_id', 'is_resit')
    def _compute_name(self):
        for session in self:
            if session.subject_id and session.semester_id \
                    and session.batch_id:
                session_name = session.subject_id.name + ':' + \
                               session.batch_id.name + ':' + \
                               str(session.semester_id.name)\

                if session.is_resit:
                    print('hit me :D')
                    session_name = session_name + '(Resit)'
                    print(session_name)
                session.name = session_name

    @api.onchange('batch_id')
    def _onchange_batch_id(self):
        self.semester_id = False

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_session', False):
            print('fak')
            lst = []
            lst.append(self.env.context.get('semester_id'))
            session = self.env['op.exam.session'].search([('semester_id', 'in', lst)])
            print('ff')
            print(session)
            return session.name_get()
        return super(PmExamSession, self).name_search(
            name, args, operator=operator, limit=limit)

    def act_submitted(self):
        self.state = 'submitted'

    def act_schedule(self):
        for record in self:
            weight = sum(x.grade_weightage for x in record.exam_ids)
            if weight == 100:
                self.state = 'schedule'
            else:
                raise ValidationError("Total weight of subject exam must equal to 100 to schedule")


class OpResultTemplateCustom(models.Model):
    _inherit = "op.result.template"
    name = fields.Char(compute='_compute_name', store=True, required=False)
    exam_session_id = fields.Many2one(
        'op.exam.session', 'Exam Schedule',
        required=True, track_visibility='onchange')
    batch_id = fields.Many2one('op.batch', 'Term')
    semester_id = fields.Many2one('pm.semester', 'Semester')
    @api.model
    def _get_default_course(self):
        course = self.env['op.course'].search(
            ['|', ('code', '=', 'CUL'), ('name', '=', '2-Year Diploma in Culinary Art')], limit=1)
        return course.id

    course_id = fields.Many2one('op.course', 'Course', required=True, default=_get_default_course)

    @api.depends('exam_session_id', 'semester_id', 'batch_id')
    def _compute_name(self):
        for record in self:
            subject_id = record.exam_session_id.subject_id
            if subject_id and record.semester_id \
                    and record.batch_id:
                record_name = subject_id.name + ':' + \
                              record.batch_id.name + ':' + \
                              str(record.semester_id.name) + \
                              ' Result Template'
                if record.exam_session_id.is_resit:
                    record_name = record_name + ' (Resit)'
                record.name = record_name

    @api.constrains('exam_session_id')
    def _check_exam_session(self):
        print('Overide for nothing')

    def button_draft(self):
        self.write({'state': 'draft'})

    def generate_result(self):
        for record in self:
            exam_session = self.exam_session_id
            if exam_session.state != 'done':
                raise ValidationError("Exam Schedule should be done: %s" % exam_session.name)

            marksheet_reg_id = self.env['op.marksheet.register'].create({
                'name': 'Mark Sheet for %s' % record.exam_session_id.name,
                'semester_id': record.exam_session_id.semester_id.id,
                'exam_session_id': record.exam_session_id.id,
                'generated_date': fields.Date.today(),
                'generated_by': self.env.uid,
                'state': 'draft',
                'result_template_id': record.id
            })
            student_dict = {}
            for exam in record.exam_session_id.exam_ids:
                for attendee in exam.attendees_line:
                    result_line_id = self.env['op.result.line'].create({
                        'student_id': attendee.student_id.id,
                        'exam_id': exam.id,
                        'marks': str(attendee.marks and attendee.marks or 0),
                    })
                    if attendee.student_id.id not in student_dict:
                        student_dict[attendee.student_id.id] = []
                    student_dict[attendee.student_id.id].append(result_line_id)
            for student in student_dict:
                marksheet_line_id = self.env['op.marksheet.line'].create({
                    'student_id': student,
                    'marksheet_reg_id': marksheet_reg_id.id,
                })
                for result_line in student_dict[student]:
                    result_line.marksheet_line_id = marksheet_line_id
            record.state = 'result_generated'


class OpMarksheetRegisterCustom(models.Model):
    _inherit = "op.marksheet.register"
    _description = "Subject Marksheet"
    exam_session_id = fields.Many2one(
        'op.exam.session', 'Exam Schedule',
        required=True, track_visibility='onchange')
    semester_id = fields.Many2one(
        'pm.semester', 'Semester', store=True)
    rank_low = fields.Float('Rank Below 60 (%):', compute='_compute_low')
    rank_middle = fields.Float('Rank 60-80 (%):', compute='_compute_middle')
    rank_top = fields.Float('Rank Above 80 (%):', compute='_compute_top')

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_validate(self):
        validated_result = self.env['op.marksheet.register'].search([
            ('exam_session_id', '=', self.exam_session_id.id),
            ('state', '=', 'validated')])

        if validated_result:
            raise ValidationError("Result for %s has already been validated once" % validated_result.exam_session_id.name)

        # When Result for a subject is validated, all the final results can be seen in student portal

        attendees = self.exam_session_id.exam_ids.attendees_line
        for attendee in attendees:
            if not attendee.show_student:
                print(attendee.exam_id.name)
                attendee.show_student = True

        self.write({'state': 'validated'})



    def _compute_low(self):
        low = 0
        middle = 0
        top = 0
        total = len(self.marksheet_line)
        for line in self.marksheet_line:
            if line.result <= 60:
                low += 1
            if line.result >= 60 and line.result <= 80:
                middle += 1
            if line.result >= 80:
                top += 1
        if low > 0 or middle > 0 or top > 0:
            self.rank_low = low / total * 100
            self.rank_middle = middle / total * 100
            self.rank_top = top / total * 100
        else:
            self.rank_low = 0
            self.rank_middle = 0
            self.rank_top = 0


class OpMarksheetLineCustom(models.Model):
    _inherit = "op.marksheet.line"
    result = fields.Integer("Result", compute='_compute_result',
                            store=True)
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade', store=True)
    semester_id = fields.Many2one(
        'pm.semester', 'Semester',
        required=False, related='marksheet_reg_id.semester_id', store=True, track_visibility='onchange')
    grade_point = fields.Float('Grade Points', digits=(12, 1))

    @api.depends('result')
    def _compute_grade(self):
        print('trigger')
        for record in self:
            grades = self.env['op.grade.configuration'].search([])
            print(record.result)
            result = record.result
            session = record.marksheet_reg_id.exam_session_id
            # if session is for resit exam, result will only be equal to 55
            if session.is_resit:
                result = 55
            for grade in grades:
                if grade.min_per <= result and grade.max_per >= result:
                    record.grade = grade.result
                    record.grade_point = grade.grade_point

    @api.depends('result')
    def _compute_status(self):
        for record in self:
            record.status = 'pass'
            if record.result < 55:
                record.status = 'fail'

    @api.depends('result_line.subject_percentage')
    def _compute_result(self):
        for record in self:
            record.result = round(sum([
                x.subject_percentage for x in record.result_line]))


class OpResultLineCustom(models.Model):
    _inherit = "op.result.line"
    subject_percentage = fields.Float("Subject Percentage", store=True, readonly=True,
                                      compute='_compute_subject_percentage')
    grade_weightage = fields.Integer("Exam Weigh", related='exam_id.grade_weightage', store=True)

    @api.depends('marks', 'exam_id.grade_weightage')
    def _compute_subject_percentage(self):
        for record in self:
            record.subject_percentage = record.marks * record.exam_id.grade_weightage * 0.01

    @api.depends('marks')
    def _compute_grade(self):
        for record in self:
            grades = self.env['op.grade.configuration'].search([])
            for grade in grades:
                if grade.min_per <= record.marks and grade.max_per >= record.marks:
                    record.grade = grade.result
