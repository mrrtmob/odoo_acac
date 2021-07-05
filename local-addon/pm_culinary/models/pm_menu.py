# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
from odoo.exceptions import ValidationError


class PmMenu(models.Model):
    _name = 'pm.menu'
    _description = 'Menu'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name'

    name = fields.Char(required=True, track_visibility='onchange')
    menu_line_ids = fields.One2many('pm.menu.line', 'menu_id', 'Recipes')
    record_url = fields.Char('Link', compute='_compute_record_url', store=True)
    approver = fields.Many2one('res.users', 'Approve By', readonly=True)

    state = fields.Selection(
        [('draft', 'Draft'),
         ('submitted', 'Submitted'),
         ('rejected', 'Rejected'),
         ('approved', 'Approved')],
        'State',
        default='draft',
        track_visibility='onchange'
    )
    cost_per_portion = fields.Float('Cost Per Portion', compute='_compute_cost_per_portion', store=True,
                                    track_visibility='onchange')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    price_per_portion = fields.Float('Selling Price per Portion', compute='_compute_price_per_portion', store=True,
                                     track_visibility='onchange')
    cold_appetizers = fields.One2many('pm.menu.line', 'menu_id', 'Cold Appetizers', domain=[('line_type', '=', 'cold_appetizer')])
    soups = fields.One2many('pm.menu.line', 'menu_id', 'Soups', domain=[('line_type', '=', 'soup')])
    hot_appetizers = fields.One2many('pm.menu.line', 'menu_id', 'Hot Appetizers', domain=[('line_type', '=', 'hot_appetizer')])
    intermediate_courses = fields.One2many('pm.menu.line', 'menu_id', 'Intermediate Courses', domain=[('line_type', '=', 'intermediate_course')])
    main_courses = fields.One2many('pm.menu.line', 'menu_id', 'Main Courses', domain=[('line_type', '=', 'main_course')])
    cheeses = fields.One2many('pm.menu.line', 'menu_id', 'Cheeses', domain=[('line_type', '=', 'cheese')])
    entremets = fields.One2many('pm.menu.line', 'menu_id', 'Entremets', domain=[('line_type', '=', 'entremet')])
    desserts = fields.One2many('pm.menu.line', 'menu_id', 'Desserts', domain=[('line_type', '=', 'dessert')])

    @api.depends('menu_line_ids.cost_per_portion')
    def _compute_cost_per_portion(self):
        for record in self:
            record.cost_per_portion = sum(record.menu_line_ids.mapped('cost_per_portion'))

    @api.depends('menu_line_ids.price_per_portion')
    def _compute_price_per_portion(self):
        for record in self:
            record.price_per_portion = sum(record.menu_line_ids.mapped('price_per_portion'))

    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=pm.menu' % (record.id)
            record.record_url = base_url

    # def send_mail(self):
    #     template_id = 66
    #     print('sending.... recipe')
    #     self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def act_submit(self):
        print('submit!!')
        self.state = 'submitted'
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'pm.menu')])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
        })
        print(approval.approve)
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        print('send mail')
        self.approver = approval.approve
        self.send_mail()

    def act_approve(self):
        approval = self.env['pm.approval'].search(
            [('record_id', '=', self.id), ('approval_type_id.base_model', '=', 'pm.menu')])
        if approval:
            approval.state = 'approved'
        self.state = 'approved'

        # template_id = 71
        # print('sending.... Menu mail')
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def act_reject(self):
        approval = self.env['pm.approval'].search(
            [('record_id', '=', self.id), ('approval_type_id.base_model', '=', 'pm.menu')])
        if approval:
            approval.state = 'rejected'
        self.state = 'rejected'

    def act_reset(self):
        self.state = 'draft'

    def write(self, val):
        print(val)
        if self.state == "approved":
            head_of_culinary = self.env.user.has_group('pm_culinary.group_acac_culinary_head')
            if not head_of_culinary:
                raise ValidationError("Menu record has already been approved, Please contact the administration")
        res = super(PmMenu, self).write(val)
        return res
