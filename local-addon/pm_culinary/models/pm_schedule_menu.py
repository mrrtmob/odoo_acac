# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PmScheduleMenu(models.Model):
    _name = 'pm.schedule.menu'
    _description = 'Schedule Menu'
    _order = 'schedule_id, sequence, id'

    name = fields.Char("Description")
    schedule_id = fields.Many2one('pm.schedule', 'Schedule', index=True, required=True, ondelete='cascade')
    menu_id = fields.Many2one('pm.menu', 'Menu', index=True, domain=[('state', '=', 'approved')])
    sequence = fields.Integer(string='Sequence', default=10)
    cost_per_portion = fields.Float('Cost')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    price_per_portion = fields.Float('Selling Price')
    display_type = fields.Selection(
        [('line_section', "Section"),
         ('line_note', "Note")],
        default=False,
        help="Technical field for UX purpose."
    )
    yield_percentage = fields.Float('Yield (%)', default=0)
    quantity = fields.Float('Quantity', default=1)

    @api.constrains('schedule_id', 'menu_id')
    def _check_menu_id(self):
        for record in self:
            if not record.display_type:
                if record.menu_id:
                    count = record.search_count([
                        ('schedule_id', '=', record.schedule_id.id),
                        ('menu_id', '=', record.menu_id.id)
                    ])

                    if count > 1:
                        raise ValidationError(
                            _("%s must not be duplicated in this schedule.") % record.menu_id.name)
                else:
                    raise ValidationError(_("Menu cannot be blank."))

    # @api.constrains('yield_percentage')
    # def _check_yield_percentage(self):
    #     for record in self:
    #         if not record.display_type:
    #             if record.yield_percentage <= 0:
    #                 raise ValidationError(_("Yield (%) must be greater than 0%"))
    #             elif record.yield_percentage > 100:
    #                 raise ValidationError(_("Yield (%) must not be greater than 100%"))

    @api.onchange('menu_id', 'quantity')
    def _onchange_menu_id_and_yield_percentage(self):
        self.cost_per_portion = self.menu_id.total_cost * self.quantity
        self.price_per_portion = self.menu_id.selling_price * self.quantity

    @api.model
    def create(self, values):
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(menu_id=False)

        line = super(PmScheduleMenu, self).create(values)

        return line

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_(
                "You cannot change the type of a schedule menu. Instead you should delete the current line and create a new line of the proper type."))

        return super(PmScheduleMenu, self).write(values)
