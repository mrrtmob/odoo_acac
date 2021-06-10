# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo.tests import common
import odoo.tests


class TestSkillCommon(common.SavepointCase):
    def setUp(self):
        super(TestSkillCommon, self).setUp()
        self.op_skill = self.env['op.skill']
        self.op_skill_category = self.env['op.skill.category']
        self.op_skill_line = self.env['op.skill.line']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"

    def test_skill_portal(self):
        self.start_tour("/", 'skill_portal', login="student")
