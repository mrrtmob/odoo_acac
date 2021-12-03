from odoo import models, fields , api
from odoo.exceptions import ValidationError
class OpPlacementOffer(models.Model):
    _inherit = "op.placement.offer"
    p_end_date = fields.Date('End Date')
    p_address = fields.Text('Address')
    p_city = fields.Char('City', size=64)
    p_zip = fields.Char('Zip', size=8)
    training_period = fields.Char(default=None)
    p_state_id = fields.Many2one(
        'res.country.state', 'States')
    p_country_id = fields.Many2one(
        'res.country', 'Country', required=True)
    p_accommodation = fields.Boolean('Accommodation')
    p_transportation = fields.Boolean('Transportation') 
    p_completed = fields.Boolean('Completed')
    p_contact1 = fields.Many2one('res.partner', 'Contact Person 1', required=True)
    p_contact2 = fields.Many2one('res.partner', 'Contact Person 2')
    p_absences = fields.Integer('Absences')
    p_project1 = fields.Boolean('Project 1')
    p_project1_deadline = fields.Date('Project1 Deadline')
    p_project2 = fields.Boolean('Project 2')
    p_project2_deadline = fields.Date('Project2 Deadline')
    p_portfolio = fields.Float('Portfolio Score')
    p_status = fields.Selection( [('in_progress', 'In Progress'), 
        ('passed', 'Passed'),
        ('i', 'Incomplete'),
        ('failed', 'Failed')],
        'Status', store=True , track_visibility='onchange')
    p_grade = fields.Float("Grade (%)")
    batch_id = fields.Many2one(
        'op.batch', 'Term', required=True, track_visibility='onchange')
    semester_id = fields.Many2one('pm.semester', 'Semester', required=True, domain=[('is_internship', '=', True)])
    subject_id = fields.Many2one('op.subject', 'Subject', required=True)
    gpa = fields.Float('GPA', readonly=True, digits=(12, 1), compute='_compute_gpa', store=True)
    color = fields.Integer(string='Color Index', default=0, compute="_compute_result_color")
    benefit = fields.Text("Benefits")
    contact_one_email = fields.Char(related="p_contact1.email")
    contact_one_mobile = fields.Char(related="p_contact1.mobile")
    contact_two_email = fields.Char(related="p_contact2.email")
    contact_two_mobile = fields.Char(related="p_contact2.mobile")

    @api.model
    def _get_default_course(self):
        course = self.env['op.course'].search(['|', ('code', '=', 'CUL'), ('name', '=', '2-Year Diploma in Culinary Art')], limit=1)
        return course.id
    course_id = fields.Many2one('op.course', 'Course', required=True,  default=_get_default_course)


    @api.depends('p_status')
    def _compute_result_color(self):
        for rec in self:
            if rec.p_status == 'passed':
                rec.color = 10

            elif rec.p_status == 'failed':
                rec.color = 9


    @api.model
    def create(self, val):
        res = super(OpPlacementOffer, self).create(val)
        notification_obj = self.env['pm.menu.notification']
        notification_obj.update_notification('internship', res.student_id.id)
        return res


    @api.depends('p_grade')
    def _compute_gpa(self):
        print('trigger')
        for record in self:
            grades = self.env['op.grade.configuration'].search([])
            for grade in grades:
                if grade.min_per <= record.p_grade and grade.max_per >= record.p_grade:
                    record.gpa = grade.grade_point


    @api.depends('p_grade' , 'p_completed')
    def _compute_get_student_status(self):
        for record in self:
            print('record.p_completed')
            print(record.p_completed)
            print(record.p_grade)
            if record.p_completed: 
                if record.p_grade >= 55:
                    record.p_status = "passed"
                else:
                    record.p_status = "failed"
            else:
                record.p_status = "in_progress"

