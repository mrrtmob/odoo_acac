from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import datetime, timedelta

class PmSemester(models.Model):
    _name = "pm.semester"
    _description = "Semester"
    _inherit = "mail.thread"
    name = fields.Char("Semester Name", required=True)
    semester_code = fields.Char('Semester Code', size=16, required=True)
    color = fields.Integer(string='Color Index', default=0)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    course_id = fields.Many2one(
        'op.course', store=True, required=True)
    batch_id = fields.Many2one(
        'op.batch', "Term", store=True)
    is_internship = fields.Boolean('Internship Semester')
    semester_order = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')] , 'Semester Order', required=True)
    state = fields.Selection(
        [('pending', 'Pending'),
         ('active', 'Active'),
         ('finished', 'Finished')], 'Status',
        default="pending", required=True, track_visibility='onchange')
    subject_ids = fields.One2many(
        'op.subject', 'semester_id', 'Subject(s)')
    marksheet_ids = fields.One2many(
        'op.marksheet.register', 'semester_id', 'MarkSheet(s)')
    exam_session_ids = fields.One2many(
        'op.exam.session', 'semester_id', 'ExamSchedule(s)')
    start_date = fields.Date("Start Date" , required=True)
    total_credit = fields.Float("Total Credit", compute="_compute_total_credit", store=True)
    end_date = fields.Date("End Date" , required=True)
    student_semester_detail = fields.One2many('pm.student.semester.detail', 'semester_id', 'Detail(s)')
    _sql_constraints = [
        ('unique_semester_code',
         'unique(semester_code)', 'Code should be unique per Semester!')]

    record_url = fields.Char('Link', compute="_compute_record_url", store=True)
    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=pm.semester' % (record.id)
            record.record_url = base_url

    absence_count = fields.Integer(
        compute="_compute_semester_dashboard_data", string='Active')
    absence_first_count = fields.Integer(
        compute="_compute_semester_dashboard_data", string='Postponed')
    absence_second_count = fields.Integer(
        compute="_compute_semester_dashboard_data", string='Withdrawn')
    discipline_count = fields.Integer(
        compute="_compute_semester_dashboard_data", string='Dismissed')
    discipline_first_count = fields.Integer(
        compute="_compute_semester_dashboard_data", string='Graduated')
    discipline_second_count = fields.Integer(
        compute="_compute_semester_dashboard_data", string='Student')

    # def semester_scheduler(self):
    #     all_semesters = self.env['pm.semester'].sudo().search(
    #         [('state', '=', 'active'),
    #          ('end_date', '!=', False)])
    #     print(all_semesters)
    #     today = fields.Date.today()
    #     for sem in all_semesters:
    #         d = timedelta(days=14)
    #         end_date = sem.end_date
    #         remind_date = sem.end_date - d
    #
    #         if today == remind_date or today == end_date:
    #             ir_model_data = self.env['ir.model.data']
    #             try:
    #                 template_id = ir_model_data.get_object_reference('pm_general', 'semester_ending_reminder')[1]
    #                 print(template_id)
    #             except ValueError:
    #                 template_id = False
    #             self.env['mail.template'].browse(template_id).send_mail(sem.id, force_send=True)

    def semester_scheduler(self):
        obj = self.env['pm.student.course.subject'].search([])
        print(obj)
        for x in range(50):
            print("write")
            obj.write({
                'id': x
            })
        # self.env.cr.execute(query)


    def action_draft(self):
        self.write({'state': 'pending'})


    def _compute_semester_dashboard_data(self):
        for semester in self:
            discipline = self.env['pm.student.discipline'].search([('semester_id', '=', semester.id)])
            absence = self.env['pm.semester.attendance'].search([('semester_id', '=', semester.id)])
            discipline_state = discipline.mapped('state')
            absence_state = absence.mapped('state')
            semester.absence_count = len(absence)
            semester.discipline_count = len(discipline)
            semester.absence_first_count = absence_state.count('first_warning')
            semester.absence_second_count = absence_state.count('second_warning')
            semester.discipline_first_count = discipline_state.count('first_warning')
            semester.discipline_second_count = discipline_state.count('second_warning')



    @api.constrains('state')
    def validate_semester_active(self):
        print('hot constraint')
        for semester in self:
            batch = semester.batch_id
            states = batch.semester_ids.mapped('state')
            active_count = 0
            for state in states:
                if state == 'active':
                    active_count += 1
            print(active_count)
            if active_count > 1:
                raise ValidationError(_('Multiple semesters can not be active simultaneously'))


    def calculate_total_semester_credit(self):
        subjects = self.get_semester_subject()
        print(subjects)
        total_credit = sum(subjects.mapped('p_credits'))
        print(total_credit)
        self.total_credit = total_credit

    def start_semester(self):

         self.write({'state': 'active'})

    def execute_semester_end(self):
        self.state = 'finished'
        next_semester_order = int(self.semester_order) + 1
        next_sem = self.env['pm.semester'].search([
            ('course_id', '=', self.course_id.id),
            ('batch_id', '=', self.batch_id.id),
            ('semester_order', '=', next_semester_order)
        ])
        next_sem.write({
            'state': 'active'
        })
        no_pass = ['retake', 'fail']
        fail_students = []
        semester_detail = self.student_semester_detail
        for sd in semester_detail:
            print('name:', sd.student_id.name)
            print('Status:', sd.student_id.education_status)
            print('Semester Status:', sd.state)
            student_id = sd.student_id.id
            if sd.state not in no_pass:
                print('Pass Hz')
                sd.state = 'complete'
            else:
                print('Fail Hz')
                print(sd.student_id.name)
                print(sd.state)
                fail_students.append(student_id)

        print(fail_students)
        next_semester_detail = next_sem.student_semester_detail
        for nsd in next_semester_detail:
            print('name:', nsd.student_id.name)
            print('Status:', nsd.student_id.education_status)
            print('Semester Status:', nsd.state)
            student_id = nsd.student_id.id
            if student_id not in fail_students:
                nsd.state = 'ongoing'
                print('Move to next')
            else:
                continue

        #find related child ids
        #set status to pass if student status = pass

        #find new related child ids of next semester
        # set active to pass if student status = pass



    @api.depends('subject_ids')
    def _compute_total_credit(self):
        print('trigger credit')
        for record in self:
            subjects = self.get_semester_subject()
            print(subjects)
            total_credit = 0
            for subject in subjects:
                total_credit += subject.p_credits
            record.total_credit = total_credit

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_semester', False):
            lst = []
            lst.append(self.env.context.get('batch_id'))
            print(lst)
            semester = self.env['pm.semester'].search([('batch_id', 'in', lst)])
            return semester.name_get()
        return super(PmSemester, self).name_search(
            name, args, operator=operator, limit=limit)

    @api.model
    def get_semester_subject(self):
        for record in self:
            subjects = self.env['op.subject'].search([('course_id', '=', record.course_id.id),
                                                     ('semester', '=', record.semester_order)])
            return subjects

class PmSemesterDetail(models.Model):
    _name = "pm.student.semester.detail"
    _order = "id asc"
    _rec_name = "semester_id"
    semester_id = fields.Many2one(
        'pm.semester', 'Semester',
        required=True, track_visibility='onchange')
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one(
        'op.batch', "Term", store=True)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    state = fields.Selection([('ongoing', 'Ongoing'),
                                ('complete', 'Completed'),
                                ('incomplete', 'Incomplete'),
                                ('pending', 'Pending'),
                                ('retake', 'Retake'),
                                ('fail', 'Fail')], string='Status', required=True, track_visibility='onchange')
    remark = fields.Text('Remarks')

    color = fields.Integer(string='Color Index', default=0, compute="_compute_result_color", store=True)

    @api.depends('state')
    def _compute_result_color(self):
        for rec in self:

            if rec.state == 'ongoing':
                rec.color = 10
                # Green
            elif rec.state == 'complete':
                rec.color = 7
                # Blue
            elif rec.state == 'retake' or rec.state == 'fail':
                rec.color = 9
                # Red
            else:
                rec.color = 0

            # elif rec.state == 'incomplete' or rec.state == 'pending':
            #     rec.color = 3 #Yellow
            # elif rec.state == 'fail' or rec.state == 'retake':
            #     rec.color = 9 #red



class OpSemesterMarksheetRegister(models.Model):
    _name = "pm.semester.marksheet.register"
    _order = "id desc"
    _inherit = ["mail.thread"]
    _description = "Semester Marksheet"

    semester_id = fields.Many2one(
        'pm.semester', 'Semester',
        required=True, track_visibility='onchange')
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one(
        'op.batch', "Term", store=True)
    semester_result_ids = fields.One2many(
        'pm.semester.result', 'semester_mark_sheet_id', 'Results')
    generated_date = fields.Date(
        'Generated Date', required=True,
        default=fields.Date.today(), track_visibility='onchange')
    generated_by = fields.Many2one(
        'res.users', 'Generated By',
        default=lambda self: self.env.uid,
        required=True, track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'), ('validated', 'Validated'),
         ('cancelled', 'Cancelled')], 'Status',
        default="draft", required=True, track_visibility='onchange')
    total_pass = fields.Integer(
        'Total Pass', compute='_compute_total_pass',
        track_visibility='onchange', store=True)
    total_failed = fields.Integer(
        'Total Fail', compute='_compute_total_failed',
        track_visibility='onchange', store=True)
    name = fields.Char('Marksheet Register', size=256, required=True,
                       track_visibility='onchange')
    result_template_id = fields.Many2one(
        'pm.semester.result.template', 'Result Template',
        required=True, track_visibility='onchange')
    active = fields.Boolean(default=True)

    rank_low = fields.Float('Rank Below 60 (%):', compute='_compute_low')
    rank_middle = fields.Float('Rank 60-80 (%):', compute='_compute_middle')
    rank_top = fields.Float('Rank Above 80 (%):', compute='_compute_top')



    def testing(self):
        for record in self:
            grades = self.env['op.grade.configuration'].search([], order="id desc")
            print(grades)
            print(type(grades))
            for i in range(len(grades)):
                j = i +1
                if j < len(grades):
                    for line in record.semester_result_ids:
                        gpa = line.gpa
                        name = line.student_id.name
                        if grades[i].grade_point <= gpa and grades[j].grade_point >= gpa:
                            print('original', gpa)
                            print('lower', grades[i].grade_point)
                            print('higher', grades[j].grade_point)
                            scale_down = gpa - grades[i].grade_point
                            scale_up = grades[j].grade_point - gpa
                            print(scale_down)
                            print(scale_up)
                            if scale_down < scale_up:
                                print('scale_down')
                                gpa = grades[i].grade_point
                            else:
                                print('scale_up')
                                gpa = grades[j].grade_point
                            print('updated_gpa', gpa)


        print('testing')
    def _compute_low(self):
        print('hit low')
        low = 0
        middle = 0
        top = 0
        total = len(self.semester_result_ids)
        for line in self.semester_result_ids:
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


    @api.constrains('total_pass', 'total_failed')
    def _check_marks(self):
        for res in self:
            if (res.total_pass < 0.0) or (res.total_failed < 0.0):
                raise ValidationError(_('Enter proper pass or fail!'))

    @api.depends('semester_result_ids.status')
    def _compute_total_pass(self):
        for record in self:
            count = 0
            for results in record.semester_result_ids:
                if results.status == 'pass':
                    count += 1
            record.total_pass = count

    @api.depends('semester_result_ids.status')
    def _compute_total_failed(self):
        for record in self:
            count = 0
            for results in record.semester_result_ids:
                if results.status == 'fail':
                    count += 1
            record.total_failed = count

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_validate(self):
        for record in self:
            validated_result = self.env['pm.semester.marksheet.register'].search([
                                                                        ('semester_id', '=', record.semester_id.id),
                                                                        ('state', '=', 'validated')])
            if validated_result:
                raise ValidationError("Result for %s has already been validated once" % validated_result.semester_id.name)

            passed_student = []
            failed_student = []
            semester = record.semester_id
            student_semester_result = semester.student_semester_detail

            for res in record.semester_result_ids:
                if res.status == 'pass':
                    passed_student.append(res.student_id.id)
                elif res.status == 'fail':
                    failed_student.append(res.student_id.id)

                notification_obj = self.env['pm.menu.notification']
                notification_obj.update_notification('grade', res.student_id.id)

            for sr in student_semester_result:
                if sr.student_id.id in passed_student:
                    sr.state = 'complete'
                elif sr.student_id.id in failed_student:
                    sr.state = 'fail'
                else:
                    print('ort deng tver ey te')





        self.state = 'validated'

    def act_cancel(self):
        self.state = 'cancelled'

    def act_draft(self):
        self.state = 'draft'

class PmFailReasons(models.Model):

    _name = 'pm.semester.fail.reason'
    name = fields.Char('Reasons')

class PmSemesterResult(models.Model):
    _name = "pm.semester.result"
    semester_mark_sheet_id = fields.Many2one('pm.semester.marksheet.register', 'Semester Mark Sheet', ondelete='cascade', required=False)
    student_id = fields.Many2one('op.student', 'Student', required=True)
    term_result_id = fields.Many2one('pm.term.result', 'Term Result')
    semester_id = fields.Many2one(
        'pm.semester', 'Semester',
        required=True, track_visibility='onchange')
    semester_res_line = fields.One2many(
        'pm.semester.result.line', 'semester_result_id', 'Marksheets')
    result = fields.Integer("Result", compute='_compute_result', store=True)
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade', store=True)
    total_grade_point = fields.Float('Total Grade Points', compute="_compute_total_grade_point", store=True)
    gpa = fields.Float('GPA', readonly=True, digits=(12, 1), compute='_compute_gpa', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('validated', 'Validated'),
         ('cancelled', 'Cancelled')], 'Status',
        default="draft", required=True, track_visibility='onchange')
    name = fields.Char('Semester Result', size=256, required=False,
                       track_visibility='onchange')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], 'Status', compute='_compute_status', store=True)
    active = fields.Boolean(default=True)
    fail_reasons = fields.Many2many('pm.semester.fail.reason')
    fail_practical = fields.Boolean('Failed Practical Subject')
    fail_more_subjects = fields.Boolean('Failed more than two subjects')
    fail_minimun = fields.Boolean('Total Score Below 55%')



    @api.depends('semester_res_line.wiegh_grade_point')
    def _compute_total_grade_point(self):
        for record in self:
            total_grade_point = 0
            for line in record.semester_res_line:
                total_grade_point += line.wiegh_grade_point
            print(total_grade_point)
            record.total_grade_point = total_grade_point

    @api.depends('total_grade_point',
                 'semester_id.total_credit')
    def _compute_gpa(self):
        for record in self:
            total_credit = record.semester_id.total_credit
            print('========= total credit==============')
            print(total_credit)
            print('========= total grade point==============')
            print(record.total_grade_point)
            if total_credit and record.total_grade_point:
                print('total grade point', record.total_grade_point)
                gpa = record.total_grade_point / total_credit

                print('gpa1', gpa)
                print('gpa', self.scale_gpa(gpa))
                self.gpa = self.scale_gpa(gpa)

    def scale_gpa(self, gpa):
        grades = self.env['op.grade.configuration'].search([], order="id desc")
        for i in range(len(grades)):
            j = i + 1
            if j < len(grades):
                print('heh')
                if grades[i].grade_point <= gpa and grades[j].grade_point >= gpa:
                    print('huu')
                    scale_down = gpa - grades[i].grade_point
                    scale_up = grades[j].grade_point - gpa

                    if scale_down < scale_up:
                        print('up')
                        gpa = grades[i].grade_point
                    else:
                        print('down')

                        gpa = grades[j].grade_point
                    return gpa

    def action_validate(self):
        self.state = 'validated'

    def act_cancel(self):
        self.state = 'cancelled'

    def act_draft(self):
        self.state = 'draft'

    @api.depends('semester_res_line.total_score','semester_res_line.status')
    def _compute_result(self):
        for record in self:
            marks = {}
            sessions = {}
            for line in record.semester_res_line:
                subject_id = line.session_id.subject_id.id
                if subject_id not in marks:
                    marks[subject_id] = line.total_score
                else:
                    marks[subject_id] = line.total_score
                if subject_id not in sessions:
                    sessions[subject_id] = line.id
                elif subject_id in marks and line.session_id.is_resit:
                    line_ref = self.env['pm.semester.result.line'].browse(sessions[subject_id])
                    line_ref.exam_state = 'covered'
                    if line.status == 'pass':
                        line.exam_state = 'resit'
                        line.total_score = 55
                    else:
                        line.exam_state = 'fail_resit'

            print(sessions)
            total = sum(marks.values())
            subject_count = len(marks)
            if total and subject_count:
                record.result = round(total / subject_count)

    @api.depends('gpa')
    def _compute_grade(self):
        for record in self:
            result = ''
            grades = self.env['op.grade.configuration'].search([])
            for grade in grades:
                grade_config = round(grade.grade_point, 1)
                gpa = round(record.gpa, 1)
                if grade_config == gpa:
                    result = grade.result
                    print(grade.result)
            record.grade = result

    @api.depends('result', 'semester_res_line.status')
    def _compute_status(self):
        for record in self:
            record.status = 'pass'
            subject_fail_count = 0
            is_fail_practical_subject = False
            for result in record.semester_res_line:
                if result.exam_state != 'covered':
                    if result.status == 'fail' and result.session_id.subject_id.type != 'practical':
                        subject_fail_count += 1
                    elif result.status == 'fail' and result.session_id.subject_id.type == 'practical':
                        subject_fail_count += 1
                        is_fail_practical_subject = True
                else:
                    print('I am covered')
                    print(result.session_id)
            if record.result < 55:
                record.status = 'fail'
                #Fail Below 55% ID = 1
                record.write({'fail_reasons': [(4, 1)]})
                record.fail_minimun = True
            if is_fail_practical_subject:
                # Fail Pratical ID = 2
                record.status = 'fail'
                record.write({'fail_reasons': [(4, 2)]})
                record.fail_practical = True
            if subject_fail_count > 2:
                record.status = 'fail'
                # Fail more than two subject ID = 2
                record.write({'fail_reasons': [(4, 3)]})
                record.fail_more_subjects = True

class OpGradeConfiguration(models.Model):
    _inherit = "op.grade.configuration"
    grade_point = fields.Float('Grade Points', digits=(12, 1))

class PmSemesterResultLine(models.Model):
    _name = "pm.semester.result.line"
    _rec_name = "student_id"
    _description = "Semester Result Line"
    semester_result_id = fields.Many2one(
        'pm.semester.result', 'Semester Result', ondelete='cascade')
    student_id = fields.Many2one('op.student', 'Student', required=True)
    session_id = fields.Many2one('op.exam.session', 'Exam Schedule')
    subject_id = fields.Many2one('op.subject', 'Subject', store=True)
    grade = fields.Char('Grade', readonly=True, compute='_compute_grade', store=True)
    wiegh_grade_point = fields.Float('Grade Weight Point')
    total_score = fields.Integer("Result")
    generated_date = fields.Date(
        'Generated Date', required=True,
        default=fields.Date.today(), track_visibility='onchange')
    status = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], 'Status', compute='_compute_status', store=True)
    active = fields.Boolean(default=True)
    exam_state = fields.Selection([
        ('covered', 'Covered'),
        ('resit', 'Pass Resit Exam'),
        ('fail_resit', 'Fail Resit Exam'),
    ])

    @api.depends('total_score')
    def _compute_status(self):
        print('test')
        for record in self:
            if record.total_score < 55:
                record.status = 'fail'
            else:
                record.status = 'pass'

    @api.depends('total_score')
    def _compute_grade(self):
        for record in self:
            grades = self.env['op.grade.configuration'].search([])
            for grade in grades:
                if grade.min_per <= record.total_score and grade.max_per >= record.total_score:
                    record.grade = grade.result

class PmSemesterResultTemplate(models.Model):
    _name = "pm.semester.result.template"
    _inherit = ["mail.thread"]
    _description = "Semester Result Template"
    semester_id = fields.Many2one(
        'pm.semester', 'Semester', track_visibility='onchange')
    name = fields.Char(compute='_compute_name', size=256, store=True, required=False)
    result_date = fields.Date(
        'Result Date', required=True,
        default=fields.Date.today(), track_visibility='onchange')
    generated_date = fields.Datetime("Generated Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('result_generated', 'Result Generated')
    ], string='State', default='draft', track_visibility='onchange')
    active = fields.Boolean(default=True)
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one('op.batch', 'Term')

    def button_draft(self):
        self.write({'state': 'draft'})


    @api.depends('semester_id', 'batch_id')
    def _compute_name(self):
        for session in self:
            print('yes')
            if session.batch_id and session.semester_id \
                    and session.batch_id:
                session.name = session.batch_id.name + ':' + \
                               str(session.semester_id.name) + \
                               ' Result Template'

    @api.constrains('semester_id')
    def _check_exam_subject(self):
        for record in self:
            for exam in record.semester_id.exam_session_ids:
                print(exam.state)
                if exam.state != 'done':
                    raise ValidationError(
                        _('All Exam Schedules must be done before creating semester result template.'))

    def generate_semester_result(self):
        for record in self:
            result_dict = {}
            marksheets = record.semester_id.marksheet_ids
            session_ids = []
            for marksheet_reg in marksheets:
                if marksheet_reg.state == 'validated':
                    session_ids.append(marksheet_reg.exam_session_id.id)
                if marksheet_reg.state != 'validated' and marksheet_reg.exam_session_id.id in session_ids:
                    print('yosh :D')
                    raise ValidationError(
                        _('All subject results must be validated before generating semester result'))
            print(session_ids)

            semester_mark_sheet = self.env['pm.semester.marksheet.register'].create({
                'name': 'Semester Sheet for %s' % record.semester_id.name,
                'course_id': record.semester_id.batch_id.course_id.id,
                'batch_id': record.semester_id.batch_id.id,
                'semester_id': record.semester_id.id,
                'generated_date': fields.Date.today(),
                'generated_by': self.env.uid,
                'state': 'draft',
                'result_template_id': record.id
            })
            for marksheet in marksheets:
                if marksheet.state == 'validated':
                    session_id = marksheet.exam_session_id.id
                    for line in marksheet.marksheet_line:
                        subject_result = line.result
                        student_id = line.student_id.id
                        subject_id = line.marksheet_reg_id.exam_session_id.subject_id
                        wiegh_grade_point = line.grade_point * subject_id.p_credits
                        if student_id not in result_dict:
                            result_dict[student_id] = [{'score': subject_result, 'session_id': session_id, 'wiegh_grade_point': wiegh_grade_point, 'subject_id': subject_id.id}]
                        else:
                            result_dict[student_id].append({'score': subject_result, 'session_id': session_id, 'wiegh_grade_point': wiegh_grade_point, 'subject_id': subject_id.id})
            print(result_dict)
            for student_id in result_dict.keys():
                print(student_id)
                print(result_dict[student_id])
                subject_result = result_dict[student_id]
                semester_result_id = self.env['pm.semester.result'].create({
                            'name': record.semester_id.name,
                             'semester_id': record.semester_id.id,
                             'student_id': student_id,
                             'semester_mark_sheet_id': semester_mark_sheet.id,
                             'state': 'draft',
                         })
                for result in subject_result:
                    semester_result_line = self.env['pm.semester.result.line'].create({
                        'student_id': student_id,
                        'semester_result_id': semester_result_id.id,
                        'session_id': result['session_id'],
                        'total_score': result['score'],
                        'subject_id': result['subject_id'],
                        'wiegh_grade_point': result['wiegh_grade_point']
                    })
        record.state = 'result_generated'

class PmFinalResultTemplate(models.Model):
    _name = "pm.final.result.template"
    _inherit = ["mail.thread"]
    _description = "Final Result Template"
    name = fields.Char(compute='_compute_name', size=256, store=True, required=False)
    result_date = fields.Date(
        'Result Date', required=True,
        default=fields.Date.today(), track_visibility='onchange')
    generated_date = fields.Datetime("Generated Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('result_generated', 'Result Generated')
    ], string='State', default='draft', track_visibility='onchange')
    active = fields.Boolean(default=True)
    course_id = fields.Many2one('op.course', 'Course')
    batch_id = fields.Many2one('op.batch', 'Term', required=True,)

    def button_draft(self):
        self.write({'state': 'draft'})


    @api.depends('batch_id')
    def _compute_name(self):
        for session in self:
            if session.batch_id:
                session.name = session.batch_id.name + ':'+' Final Result Template'


    @api.constrains('semester_id')
    def _check_exam_subject(self):
        for record in self:
            for exam in record.semester_id.exam_session_ids:
                print(exam.state)
                if exam.state != 'done':
                    raise ValidationError(
                        _('All Exam Schedules must be done before creating semester result template.'))

    def generate_final_result(self):
        course = self.course_id
        for batch in self.batch_id:
            semesters = batch.semester_ids

            total_course_credit = sum(x.total_credit for x in semesters)
            students = self.env['op.student'].search(
                [('course_detail_ids.batch_id', '=', batch.id),
                 ('course_detail_ids.course_id', '=', course.id)])

            print(students)

            term_marksheet_obj = self.env['pm.term.marksheet.register']
            term_result_obj = self.env['pm.term.result']
            term_result_associate = self.env['pm.term.result.associate']

            batch_mark_sheet = term_marksheet_obj.create({
                'name': 'Result Sheet for %s' % batch.name,
                'batch_id': batch.id,
                'generated_date': fields.Date.today(),
                'generated_by': self.env.uid,
                'state': 'draft',
            })

            for student in students:
                res_associate = []

                wiegh_average_gpa = 0
                student_results = student.semester_result

                if student_results:
                    for res in student_results:
                        semester_credit = res.semester_id.total_credit
                        wiegh_average_gpa += res.gpa * semester_credit
                        val = {
                            'name': res.semester_id.name,
                            'semester_id': res.semester_id.id,
                            'gpa': res.gpa,
                            'status': res.status,
                        }
                        res_associate.append(val)

                    placement = self.env['op.placement.offer'].search(
                        [('student_id', '=', student.id), ('batch_id', '=', batch.id),
                         ('p_completed', '=', True)], order='join_date')
                    for pl in placement:
                        intership_grade_point = pl.gpa * pl.subject_id.p_credits
                        wiegh_average_gpa += intership_grade_point
                        status = ''
                        if pl.p_status == 'passed':
                            status = 'pass'
                        else:
                            status = 'fail'

                        val = {
                            'name': pl.semester_id.name,
                            'semester_id': pl.semester_id.id,
                            'gpa': pl.gpa,
                            'status': status,
                        }
                        res_associate.append(val)

                    gpa = round(wiegh_average_gpa / total_course_credit, 1)

                    term_res = term_result_obj.create({
                        'student_id': student.id,
                        'batch_id': batch.id,
                        'gpa': gpa,
                        'term_marksheet_register_id': batch_mark_sheet.id,
                    })

                    length = len(res_associate)

                    for i in range(length):
                        res_associate[i]['term_result_id'] = term_res.id

                    term_result_associate.create(res_associate)


        self.write({'state': 'result_generated'})

