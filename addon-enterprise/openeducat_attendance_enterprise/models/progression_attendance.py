# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class StudentProgression(models.Model):
    _inherit = ["op.student.progression"]

    @api.depends("attendance_lines")
    def _compute_total_attendance(self):
        self.total_attendance = len(self.attendance_lines)

    attendance_lines = fields.One2many('op.attendance.line',
                                       'progression_id',
                                       string='Progression Attendance')
    total_attendance = fields.Integer('Total Attendance',
                                      compute="_compute_total_attendance",
                                      store=True)
