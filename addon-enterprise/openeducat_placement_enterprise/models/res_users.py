# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    placement_team_id = fields.Many2one('op.placement.cell',
                                        "Placement Team Members")
