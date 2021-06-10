from odoo import models, fields

_MENU_NAME = [
    ('announcement', 'Announcement'),
    ('discipline', 'Discipline'),
    ('attendance', 'Attendance'),
    ('exam', 'Exams'),
    ('grade', 'Grade'),
    ('internship', 'Internship'),
    ('payment_schedule', 'Payment Schedule'),
    ('class_schedule', 'Class Schedule'),
]

class PmMenuNotification(models.Model):
    _name = "pm.menu.notification"
    _description = "Menu Notification for Mobile APP"
    student_id = fields.Many2one("op.student", string='Student')
    menu_name = fields.Selection(_MENU_NAME, 'Menu')
    base_model = fields.Many2one('ir.model', 'Base Model')
    record_count = fields.Integer("Count")
    is_seen = fields.Boolean(default=False)

    def clear_notification(self, menu_name, student_id):
        print("Hit Clear Notification")
        record = self.search([
            ('student_id', '=', student_id),
            ('menu_name', '=', menu_name),
        ], limit=1)

        if record:
            count = 0
            record.write({'record_count': count, 'is_seen': True})

    def update_notification(self, menu_name, student_id):

        record = self.search([
            ('student_id', '=', student_id),
            ('menu_name', '=', menu_name),
        ], limit=1)

        if not record:
            print("New")
            data = {
                'menu_name': menu_name,
                'student_id': student_id,
                'record_count': 1,
                'is_seen': False,
            }
            self.create(data)

        else:
            count = record.record_count + 1
            record.write({'record_count': count, 'is_seen': False})






