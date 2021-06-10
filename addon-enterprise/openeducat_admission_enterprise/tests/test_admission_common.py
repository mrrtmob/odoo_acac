# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo.tests import common, TransactionCase
from ..controller.onboard import OnboardingController
from odoo.addons.website.tools import MockRequest


class TestAdmissionCommon(common.SavepointCase):
    def setUp(self):
        super(TestAdmissionCommon, self).setUp()
        self.op_student = self.env['op.student.fees.details']
        self.res_company = self.env['res.company']
        self.op_register = self.env['op.admission.register']
        self.op_admission = self.env['op.admission']


class AdmissionController(TransactionCase):

    def setUp(self):
        super().setUp()


class TestAdmissionController(AdmissionController):

    def setUp(self):
        super(TestAdmissionController, self).setUp()

    def test_case_1_onboard(self):
        self.admission_controller = OnboardingController()

        with MockRequest(self.env):
            self.onboard = self.admission_controller.openeducat_admission_onboarding()
