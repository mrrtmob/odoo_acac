# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################
from odoo.tests import common


class TestStudentAttendanceCommon(common.SavepointCase):
    def setUp(self):
        super(TestStudentAttendanceCommon, self).setUp()
        self.op_student_attendance_line = self.env['op.attendance.line']
        self.op_student = self.env['op.student']
