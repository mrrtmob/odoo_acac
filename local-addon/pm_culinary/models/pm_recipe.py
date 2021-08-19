# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

_TYPE = [
    ('cold_appetizer', 'Cold Appetizers'),
    ('hot_appetizer', 'Hot Appetizers'),
    ('soup', 'Soups'),
    ('intermediate_course', 'Intermediate Courses'),
    ('main_course', 'Main Courses'),
    ('entremet', 'Entremets'),
    ('dessert', 'Dessert')
]


class PmRecipeCategory(models.Model):
    _name = "pm.recipe.category"
    _inherit = "mail.thread"
    name = fields.Char()
    parent_id = fields.Many2one('pm.recipe.category', 'Parent Category', index=True, ondelete='cascade')
    code = fields.Char()
    category_image = fields.Binary('Image')
    recipe_count = fields.Integer("Recipes", compute="_compute_count_recipe")

    @api.depends('name')
    def _compute_count_recipe(self):
        for rec in self:
            rec.recipe_count = self.env['pm.recipe'].search_count([('category_id', '=', rec.id)])




class PmRecipe(models.Model):
    _name = "pm.recipe"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Recipe"
    name = fields.Char("Recipe Name", track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submitted', 'Submitted'),
         ('rejected', 'Rejected'),
         ('approved', 'Approved')],
        'State', default='draft', track_visibility='onchange')
    category_id = fields.Many2one('pm.recipe.category', 'Category')
    recipe_image = fields.Binary('Image')
    is_sub_recipe = fields.Boolean('Can be used as a sub-recipe', default=False, track_visibility='onchange')
    cost_per_portion = fields.Float('Cost Per Portion', compute='_compute_cost', store=True, track_visibility='onchange')
    preparation = fields.Html('Preparation')
    instruction = fields.Html('Instruction')
    type = fields.Selection(_TYPE)
    recipe_line_ids = fields.One2many('pm.recipe.line', 'recipe_id')
    cuisine = fields.Char(track_visibility='onchange')
    recipe_approver_email = fields.Char('Approver Email')
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        track_visibility='onchange',
        required=True)
    record_url = fields.Char('Link', compute='_compute_record_url', store=True)
    approver = fields.Many2one('res.users', 'Approve By', readonly=True)
    date_of_test = fields.Date(track_visibility='onchange')
    number_of_portion = fields.Integer('Yield', required=True, default=10, tracking=True)
    cost = fields.Float('Total Cost', compute='_compute_cost', store=True, track_visibility='onchange')
    price_per_portion = fields.Float('Selling Price per Portion', compute='_compute_price_per_portion', track_visibility='onchange')
    ingredients = fields.One2many('pm.recipe.line', 'recipe_id', 'Ingredients & Preparation Instructions',
                                  domain=[('line_type', '=', 'ingredient')])
    sub_recipes = fields.One2many('pm.recipe.line', 'recipe_id', 'Sub Recipes', domain=[('line_type', '=', 'sub_recipe')])
    ingredients_cost = fields.Float('Estimated Ingredients Cost', compute='_compute_cost')
    sub_recipes_cost = fields.Float('Estimated Sub Recipes Cost', compute='_compute_cost')
    price = fields.Float('Selling Price', compute='_compute_price', tracking=True)
    cost_in_percentage = fields.Float('Cost (%)', required=True, default=30, tracking=True)
    makes = fields.Float(tracking=True, default=1)
    uor = fields.Selection(
        [('kg', 'kg'),
         ('l', 'l')],
        'UoR',
        tracking=True
    )
    cost_per_uor = fields.Float('Cost per UOR', compute='_compute_cost_per_uor')

    nutrition = fields.Html('Nutritional Information')
    allergic = fields.Html('Allergic')
    color = fields.Integer(string='Color Index')
    is_expired = fields.Boolean(string='Expired', default=False, compute="_compute_expire", store=True)

    @api.depends('write_date')
    def _compute_expire(self):
        for rec in self:
            today = fields.Date.today()
            d = timedelta(days=60)
            expired_date = today - d
            print("WTF")
            print(rec.write_date)
            print("Expire")
            print(expired_date)
            if rec.write_date.date() < expired_date:
               rec.is_expired = True

    @api.constrains('number_of_portion')
    def _check_number_of_portion(self):
        for record in self:
            if record.number_of_portion < 1:
                raise ValidationError(
                    _("Yield must be greater than 0."))

    @api.onchange('number_of_portion')
    def _update_ingredient_qty(self):
        print('_update_ingredient_qty')
        for record in self:
            record.cost_per_portion = record.cost / record.number_of_portion
            record.price_per_portion = record.price / record.number_of_portion
            lines = record.ingredients
            for line in lines:
                line.quantity = line.initial_quantity * (record.number_of_portion / 10)

    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError(
                    _("Price must be greater than 0."))

    @api.depends('ingredients.cost', 'sub_recipes.cost')
    def _compute_cost(self):
        print("_compute_cost!!")
        for record in self:
            record.ingredients_cost = sum(record.ingredients.mapped('cost'))
            record.sub_recipes_cost = sum(record.sub_recipes.mapped('cost'))

            record.cost = record.ingredients_cost + record.sub_recipes_cost

            # NOTE: update the recipe lines which use this recipe
            main_recipe_lines = self.env['pm.recipe.line'].search([('sub_recipe_id', '=', record.id)])
            record.cost_per_portion = record.cost / record.number_of_portion

            for main_recipe_line in main_recipe_lines:
                main_recipe_line._compute_cost()

    @api.depends('cost', 'cost_in_percentage')
    def _compute_price(self):
        for record in self:
            record.price = (record.cost / record.cost_in_percentage) * 100




    @api.depends('price')
    def _compute_price_per_portion(self):
        print("_compute_price_per_portion!!")
        for record in self:
            if record.number_of_portion:
                record.price_per_portion = record.price / record.number_of_portion

    # def     send_mail(self):
    #     template_id = 62
    #     print('sending....')
    #     self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    @api.depends('name')
    def _compute_record_url(self):
        for record in self:
            base_url = request.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=pm.recipe' % (record.id)
            record.record_url = base_url

    @api.depends('cost', 'makes')
    def _compute_cost_per_uor(self):
        for record in self:
            if record.makes > 0:
                record.cost_per_uor = record.cost / record.makes
            else:
                record.cost_per_uor = 0

    def act_submit(self):
        print('submit!!')
        self.state = 'submitted'
        approval_type = self.env['pm.approval.type'].search([('base_model', '=', 'pm.recipe')])
        approval = self.env['pm.approval'].create({
            'approval_type_id': approval_type.id,
            'record_id': self.id,
        })
        self.message_subscribe(partner_ids=[approval.approve.partner_id.id])
        self.approver = approval.approve

    def act_approve(self):
        approval = self.env['pm.approval'].search(
            [('record_id', '=', self.id), ('approval_type_id.base_model', '=', 'pm.recipe')])
        if approval:
            approval.state = 'approved'
        self.state = 'approved'

        # template_id = 69
        # print('sending.... Recipe mail')
        # self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)

    def act_reject(self):
        approval = self.env['pm.approval'].search(
            [('record_id', '=', self.id), ('approval_type_id.base_model', '=', 'pm.recipe')])
        if approval:
            approval.state = 'rejected'
        self.state = 'rejected'

    def act_reset(self):
        self.state = 'draft'


    # This function is disable as an adjustment for Culinary to create recipe

    # def write(self, val):
    #     if self.state == "approved":
    #         head_of_culinary = self.env.user.has_group('pm_culinary.group_acac_culinary_head')
    #         if not head_of_culinary:
    #             raise ValidationError("Recipe record has already been approved, Please contact the administration")
    #     res = super(PmRecipe, self).write(val)
    #     return res
