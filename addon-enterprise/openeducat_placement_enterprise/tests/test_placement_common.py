# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo.tests import common


class TestPlacementCommon(common.SavepointCase):
    def setUp(self):
        super(TestPlacementCommon, self).setUp()
        self.op_placement = self.env['op.placement.offer']
        self.op_placement_cell = self.env['op.placement.cell']
