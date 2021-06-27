# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpJobApplication(models.Model):
    _inherit = "op.job.applicant"

    activity_id = fields.Many2one("op.activity.announcement",
                                  string="Activity",
                                  readonly=True)
