# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class OpSubject(models.Model):
    _inherit = "op.subject"

    course_id = fields.Many2one('op.course', 'Course')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        res = super(OpSubject, self).create(vals)
        res.course_id.write({'subject_ids': [(4, res.id)]})
        return res

    def write(self, vals):
        self.course_id.write({'subject_ids': [(3, self.id)]})
        super(OpSubject, self).write(vals)
        self.course_id.write({'subject_ids': [(4, self.id)]})
        return self

    def action_onboarding_subject_layout(self):
        self.env.user.company_id.onboarding_subject_layout_state = 'done'
