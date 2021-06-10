# -*- coding: utf-8 -*-
# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.

##############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech Receptives(<http://www.techreceptives.com>).
#
##############################################################################

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    openeducat_attendance_onboard_panel = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding attendance layout step",
        default='not_done')
    onboarding_attendance_register_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding attendance register layout step",
        default='not_done')
    onboarding_attendance_sheet_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding attendance sheet layout step",
        default='not_done')
    onboarding_attendance_lines_layout_state = fields.Selection(
        [('not_done', "Not done"),
         ('just_done', "Just done"),
         ('done', "Done"),
         ('closed', "Closed")],
        string="State of the onboarding attendance lines layout step",
        default='not_done')

    @api.model
    def action_close_attendance_panel_onboarding(self):
        """ Mark the onboarding panel as closed. """
        self.env.user.company_id.openeducat_attendance_onboard_panel = 'closed'

    # attendance register layout start##

    @api.model
    def action_onboarding_attendance_register_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_attendance_enterprise.'
            'action_onboarding_attendance_register_layout').read()[0]
        return action

    # attendance sheet layout starts##

    @api.model
    def action_onboarding_attendance_sheet_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_attendance_enterprise.'
            'action_onboarding_attendance_sheet_layout').read()[0]
        return action

    # attendance lines layout start##

    @api.model
    def action_onboarding_attendance_lines_layout(self):
        """ Onboarding step for the quotation layout. """
        action = self.env.ref(
            'openeducat_attendance_enterprise.'
            'action_onboarding_attendance_lines_layout').read()[0]
        return action

    def update_attendance_onboarding_state(self):
        """ This method is called on the controller
        rendering method and ensures that the animations
            are displayed only one time. """
        steps = [
            'onboarding_attendance_register_layout_state',
            'onboarding_attendance_sheet_layout_state',
            'onboarding_attendance_lines_layout_state'
        ]
        return self.get_and_update_onbarding_state(
            'openeducat_attendance_onboard_panel', steps)
