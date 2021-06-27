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


class TestPlacementJobCommon(common.SavepointCase):
    def setUp(self):
        super(TestPlacementJobCommon, self).setUp()
        self.op_activity_announcement = self.env['op.activity.announcement']
        self.op_job_applicant = self.env['op.job.applicant']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):
    def setUp(self):
        super(TestUi, self).setUp()
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = "student"
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = "parent"

    def test_01_activity_details(self):
        self.start_tour("/", "test_activity_details", login="student")
        self.start_tour("/", "test_activity_details", login="parent")

    def test_01_activity_apply(self):
        self.start_tour("/", "test_activity_announcement_apply", login="student")
        self.start_tour("/", "test_activity_announcement_apply", login="parent")

    def test_01website_activity(self):
        self.start_tour("/", "test_activity_announcement_apply", login="student")
        self.start_tour("/", "test_activity_announcement_apply", login="parent")
