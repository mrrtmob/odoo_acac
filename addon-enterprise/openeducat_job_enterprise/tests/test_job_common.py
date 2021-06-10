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


class TestJobCommon(common.SavepointCase):
    def setUp(self):
        super(TestJobCommon, self).setUp()
        self.op_job = self.env['op.job.post']
        self.op_job_applicant = self.env['op.job.applicant']
        self.op_job_stage = self.env['job.post.stage']


@odoo.tests.tagged('post_install', '-at_install')
class TestUi(odoo.tests.HttpCase):

    def setUp(self):
        super(TestUi, self).setUp()
        # login changed for only for Test Case Purpose
        student = self.env['res.users'].search(
            [('login', '=', 'student@openeducat.com')])
        student.login = 'student'
        parent = self.env['res.users'].search(
            [('login', '=', 'parent@openeducat.com')])
        parent.login = 'parent'

    def test_job(self):
        self.start_tour("/", 'test_job', login="student")
        self.start_tour("/", 'test_job', login="parent")

    def test_campus_job_checkout(self):
        self.start_tour("/", 'test_campus_job', login="student")
        self.start_tour("/", 'test_campus_job', login="parent")

    def test_job_post_description_checkout(self):
        self.start_tour("/", 'test_job_description', login="student")
        self.start_tour("/", 'test_job_description', login="parent")

    #  Controller Commented
    # def test_job_post_apply(self):
    #     self.start_tour("/", 'test_job_apply', login="student")
