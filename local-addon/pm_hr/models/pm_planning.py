# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PmActivityType(models.Model):
    _inherit = 'hr.plan.activity.type'

    @api.model
    def _get_self_model(self):
        model_id = self.env['ir.model'].search([('model', '=', 'hr.employee')]).id
        return model_id

    on_time = fields.Boolean('Schedule base on Time')
    model_id = fields.Many2one('ir.model', default=_get_self_model, index=True)


    trg_date_id = fields.Many2one('ir.model.fields', string='Activity Date',
                                  help="""When should the condition be triggered.
                                      If present, will be checked by the scheduler. If empty, will be checked at creation and update.""",
                                  domain="[('model_id', '=', model_id), ('ttype', 'in', ('date', 'datetime'))]")
    trg_description = fields.Char('Date', related='trg_date_id.field_description', store=True)
    trg_date_range = fields.Integer(string='After/Before date',
                                    help="""Delay after the trigger date.
                                        You can put a negative number if you need a delay before the
                                        trigger date, like sending a reminder 15 minutes before a meeting.""")
    trg_date_range_type = fields.Selection(
        [('minutes', 'Minutes'), ('hour', 'Hours'), ('day', 'Days'), ('month', 'Months')],
        string='Delay type', default='day')
    trg_date_calendar_id = fields.Many2one("resource.calendar", string='Use Calendar',
                                           help="When calculating a day-based timed condition, it is possible to use a calendar to compute the date based on working days.")


