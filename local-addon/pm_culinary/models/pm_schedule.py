# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request


class PmSchedule(models.Model):
    _name = 'pm.schedule'
    _description = 'Schedule'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'name'

    name = fields.Char(required=True,track_visibility='onchange')
    schedule_menu_ids = fields.One2many('pm.schedule.menu', 'schedule_id')
    event_date = fields.Datetime(required=True)
    purpose = fields.Char()
    record_url = fields.Char('Link', compute='_compute_record_url', store=True)
    approver = fields.Many2one('res.users', 'Approve By', readonly=True)
    description = fields.Text()
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submitted', 'Submitted'),
         ('rejected', 'Rejected'),
         ('approved', 'Approved')],
        'State',
        default='draft',
        track_visibility='onchange'
    )
    number_of_portion = fields.Integer('Number of Portion', required=True, default=1)
    cost = fields.Float('Total Cost', compute='_compute_cost_and_price', store=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    price = fields.Float('Selling Price', compute='_compute_cost_and_price', store=True)
    account_number = fields.Char()

    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=pm.schedule' % (record.id)
            record.record_url = base_url

    @api.constrains('event_date')
    def _check_event_date(self):
        for record in self:
            today_date = fields.Datetime.from_string(fields.Datetime.now())
            event_date = fields.Datetime.from_string(record.event_date)

            if event_date < today_date:
                raise ValidationError(
                    _("Event Date cannot be set before Now."))

    @api.constrains('number_of_portion')
    def _check_number_of_portion(self):
        for record in self:
            if record.number_of_portion < 1:
                raise ValidationError(
                    _("Number of Portion must be greater than 0."))

    @api.depends('schedule_menu_ids', 'number_of_portion')
    def _compute_cost_and_price(self):
        for record in self:
            total_cost_per_portion = sum(record.schedule_menu_ids.mapped('cost_per_portion'))
            total_price_per_portion = sum(record.schedule_menu_ids.mapped('price_per_portion'))

            record.cost = total_cost_per_portion * record.number_of_portion
            record.price = total_price_per_portion * record.number_of_portion

    # def send_mail(self):
    #     template_id = 67
    #     print('sending.... schedule mail')
    #     self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def act_submit(self):
        print('submit!!')
        self.state = 'submitted'
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'pm.schedule')])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
        })
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        print('send mail')
        self.approver = approval.approve

    def act_approve(self):
        for record in self:
            pr = self.env['purchase.request'].create({
                'date_start': self.event_date,
                'description': self.description,
                'requested_by': self.create_uid.id,
                'is_food_item': True,
                'is_automated': True,
                'expense_type': 'culinary',
                'schedule_dish_id': self.id
            })
            lines_dicts = {}
            schedule_yield = self.number_of_portion
            for menu_line in record.schedule_menu_ids:
                for menu in menu_line.menu_id:
                    for recipe in menu.menu_line_ids.recipe_id:
                        weigh = schedule_yield / recipe.number_of_portion
                        for line in recipe.recipe_line_ids:
                            if line.sub_recipe_id:
                                for sub_recipe in line.sub_recipe_id.recipe_line_ids:
                                    ap = menu_line.yield_percentage * sub_recipe.as_purchased / 100
                                    product_id = sub_recipe.product_id.id
                                    quantity = ap * line.quantity / 100 * weigh
                                    cost = quantity * sub_recipe.product_id.cost
                                    if product_id not in lines_dicts:
                                        lines_dicts[product_id] = {
                                            'product_id': sub_recipe.product_id.id,
                                            'name': sub_recipe.product_id.name,
                                            'product_uor': sub_recipe.uor,
                                            'product_qty': quantity,
                                            'request_id': pr.id,
                                        }
                                    else:
                                        lines_dicts[product_id]['product_qty'] += quantity
                            elif line.product_id:
                                ap = menu_line.yield_percentage * line.as_purchased / 100
                                product_id = line.product_id.id
                                quantity = ap * weigh
                                cost = line.cost * weigh
                                if product_id not in lines_dicts:
                                    lines_dicts[product_id] = {
                                            'product_id': line.product_id.id,
                                            'name': line.product_id.name,
                                            'product_uor': line.uor,
                                            'product_qty': quantity,
                                            'request_id': pr.id,
                                        }
                                else:
                                    lines_dicts[product_id]['product_qty'] += quantity
        # Convert Dictionary to List
        data = [value for value in lines_dicts.values()]
        pr_line = self.env['purchase.request.line'].create(data)
        if pr_line:
            print('created successfully')
        approval = self.env['pm.approval'].search(
            [('record_id', '=', self.id), ('approval_type_id.base_model', '=', 'pm.schedule')])
        if approval:
            approval.state = 'approved'
        self.state = 'approved'

        # template_id = 70
        # print('sending.... Schedule mail')
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def act_reject(self):
        approval = self.env['pm.approval'].search(
            [('record_id', '=', self.id), ('approval_type_id.base_model', '=', 'pm.schedule')])
        if approval:
            approval.state = 'rejected'
        self.state = 'rejected'

    def act_reset(self):
        self.state = 'draft'

    def write(self, val):
        if self.state == "approved":
            head_of_culinary = self.env.user.has_group('pm_culinary.group_acac_culinary_head')
            if not head_of_culinary:
                raise ValidationError("Schedule Dish has already been approved, Please contact the administration")
        res = super(PmSchedule, self).write(val)
        return res