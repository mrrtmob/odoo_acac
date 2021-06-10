# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class OpBatch(models.Model):
    _inherit = "op.batch"

    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    color = fields.Integer(string='Color Index', default=0)

    studnet_count = fields.Integer(
        compute="_compute_batch_dashboard_data", string='Studnet Count')

    def _compute_batch_dashboard_data(self):
        for batch in self:
            studnet_list = self.env['op.student'].search_count(
                [('course_detail_ids.batch_id', 'in', [batch.id])])
            batch.studnet_count = studnet_list

    def action_onboarding_batch_layout(self):
        self.env.user.company_id.onboarding_batch_layout_state = 'done'
