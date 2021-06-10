# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields


class Opskillcategory(models.Model):
    _name = "op.skill.category"
    _description = "Skills Category Creation"

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=64, required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
