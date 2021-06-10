# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, _


class StudentAttendance(models.Model):
    _inherit = "op.attendance.line"
    _order = "check_in desc"
    _rec_name = "attendance_id"
    _description = "Attendance Lines"

    def _default_student(self):
        return self.env['op.student'].search([('user_id', '=', self.env.uid)],
                                             limit=1)

    attendance_id = fields.Many2one(
        'op.attendance.sheet', 'Attendance Sheet', required=False,
        tracking=True, ondelete="cascade")
    student_id = fields.Many2one('op.student', string="Student",
                                 default=_default_student, required=True,
                                 ondelete='cascade', index=True)
    check_in = fields.Datetime(string="Attendance Time",
                               default=fields.Datetime.now,
                               readonly=True, required=True)

    def name_get(self):
        result = []
        for attendance in self:
            result.append((
                attendance.id, _("%(stu_name)s signed in at %(check_in)s") % {
                    'stu_name': attendance.student_id.name,
                    'check_in': fields.Datetime.to_string(
                        fields.Datetime.context_timestamp(
                            attendance, fields.Datetime.from_string(
                                attendance.check_in))),
                }))
        return result
