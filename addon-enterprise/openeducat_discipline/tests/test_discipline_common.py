# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo.tests import common


class TestDisciplineCommon(common.SavepointCase):
    def setUp(self):
        super(TestDisciplineCommon, self).setUp()
        self.op_discipline = self.env['op.discipline']
        self.op_misbehave_category = self.env['op.misbehaviour.category']
        self.op_elearning_rule = self.env['elearning.rules']
        self.op_student_wise_wizard = self.env['student.wise']
        self.op_misbehaviour_type_wizard = self.env['misbehaviour.type']
        self.op_take_action_wizard = self.env['take.action']
        self.op_progression_wizard = self.env['discipline.progress.wizard']
        self.op_mail_compose_message = self.env['mail.compose.message']
