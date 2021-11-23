# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class PmRecipeLine(models.Model):
    _name = "pm.recipe.line"
    _description = "Recipe Lines"
    _order = 'recipe_id, sequence, id'

    name = fields.Char("Description")
    product_id = fields.Many2one(
        'product.product',
        'Ingredient',
        domain="[('product_tmpl_id.is_food','=',True), ('product_tmpl_id.rank', '=', 'a')]"
    )
    quantity = fields.Float('Qty', digits=(12, 2))
    initial_quantity = fields.Float('Initial Quantity', digits=(12, 3), default=10)
    # NOTE: unused
    uom_id = fields.Many2one('uom.uom', 'Unit',
                             domain="[('measure_type', '!=', 'working_time'),('measure_type', '!=', 'length')]")
    # NOTE: unused
    uom_name = fields.Char('Unit of Measure Name', related='uom_id.name', readonly=True)
    uor = fields.Selection(
        [('l', 'l'),
         ('kg', 'kg'),
         ('pc', 'pc'),
         ('m', 'm')],
        'UoR',
        related='product_id.product_tmpl_id.uor'
    )
    preparation = fields.Text('Pre-preparation')
    recipe_id = fields.Many2one('pm.recipe', 'Recipe')
    ingredient_categ_id = fields.Many2one(related='product_id.product_tmpl_id.ingredient_categ_id', string='Category')
    cost = fields.Float(compute='_compute_cost', store=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True)
    sub_recipe_id = fields.Many2one(
        'pm.recipe',
        'Sub Recipe',
        domain=[('is_sub_recipe', '=', True)],
        index=True
    )
    is_quantity_percentage = fields.Float(default=False, compute='_compute_is_quantity_percentage', store=True)
    sub_recipe_ingredients = fields.One2many('pm.recipe.line', related='sub_recipe_id.ingredients', readonly=True)
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection(
        [('line_section', "Section"),
         ('line_note', "Note")],
        default=False,
        help="Technical field for UX purpose."
    )
    line_type = fields.Selection(
        [('ingredient', "Ingredient"),
         ('sub_recipe', "Sub Recipe")],
        compute="_compute_line_type",
        store=True
    )
    sub_recipe_needed_makes = fields.Float('Sub Recipe Needed Makes')
    sub_recipe_uor = fields.Selection(
        [('kg', 'kg'),
         ('l', 'l')],
        'Sub Recipe UOR',
        related='sub_recipe_id.uor'
    )
    waste_percentage = fields.Float('Waste (%)', related='product_id.product_tmpl_id.waste_percentage')
    as_purchased = fields.Float('AP', digits=(12, 3), compute='_compute_as_purchased', store=True)

    @api.constrains('uor')
    def _check_uor(self):
        for record in self:
            if record.product_id:
                if not record.uor:
                    raise ValidationError(
                        _("Ingredient Unit cannot be blank."))

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.product_id:
                if record.quantity <= 0:
                    raise ValidationError(
                        _("Ingredient Qty must be greater than 0."))
            elif record.sub_recipe_id:
                if record.quantity <= 0:
                    raise ValidationError(
                        _("Sub Recipe Qty (%) must be greater than 0."))

    @api.constrains('recipe_id', 'product_id', 'sub_recipe_id')
    def _check_product_id_and_sub_recipe_id(self):
        for record in self:
            if not record.display_type:
                if record.sub_recipe_id:
                    count = record.search_count([
                        ('recipe_id', '=', record.recipe_id.id),
                        ('sub_recipe_id', '=', record.sub_recipe_id.id)
                    ])

                    if count > 1:
                        raise ValidationError(_("%s must not be duplicated in this recipe.") % record.sub_recipe_id.name)

                    if record.sub_recipe_id.id == record.recipe_id.id:
                        raise ValidationError(_("%s cannot be a sub-recipe in this recipe.") % record.sub_recipe_id.name)
                else:
                    if not record.product_id:
                        raise ValidationError(_("Ingredient or Sub Recipe cannot be blank."))
    @api.depends('recipe_id.number_of_portion')
    def onChnageRecipeYeild(self):
        print("Yosh")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.display_type and not record.name:
                raise ValidationError(_("Section name cannot be blank."))

    @api.depends('sub_recipe_id')
    def _compute_is_quantity_percentage(self):
        for record in self:
            if record.sub_recipe_id:
                record.is_quantity_percentage = True

    @api.depends('quantity', 'waste_percentage')
    def _compute_as_purchased(self):
        for record in self:
            if record.product_id:
                # record.as_purchased = record.quantity + (record.quantity * record.waste_percentage / 100)
                record.as_purchased = record.quantity * (100 / (100 - record.waste_percentage))

    @api.depends('product_id.product_tmpl_id.cost', 'product_id.product_tmpl_id.uom_id', 'uom_id','as_purchased')
    def _compute_cost(self):
        for record in self:
            print("_compute_cost recipe line")
            if record.product_id:
                record.cost = record.product_id.product_tmpl_id.cost * record.as_purchased
            elif record.sub_recipe_id:
                print("yo")
                print(record.quantity)
                percentage = record.quantity / record.sub_recipe_id.makes
                print(percentage)
                print(record.sub_recipe_id.cost)
                record.cost = record.sub_recipe_id.cost * percentage
            else:
                record.cost = 0

    @api.depends('product_id', 'sub_recipe_id', 'display_type')
    def _compute_line_type(self):
        for record in self:
            if record.product_id:
                record.line_type = 'ingredient'
            elif record.sub_recipe_id:
                record.line_type = 'sub_recipe'
            else:
                # NOTE: only ingredients have section
                record.line_type = 'ingredient'

    @api.depends('sub_recipe_id.makes', 'quantity')
    def _compute_sub_recipe_needed_makes(self):
        for record in self:
            record.sub_recipe_needed_makes = record.sub_recipe_id.makes * record.quantity / 100

    @api.model
    def create(self, values):
        print(values['quantity'])
        if values.get('display_type', self.default_get(['display_type'])['display_type']):
            values.update(product_id=False, sub_recipe_id=False)

        values['initial_quantity'] = values['quantity']


        line = super(PmRecipeLine, self).create(values)
        line.product_id._compute_search_rank()

        return line

    def write(self, values):
        if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
            raise UserError(_(
                "You cannot change the type of a recipe line. Instead you should delete the current line and create a new line of the proper type."))

        return super(PmRecipeLine, self).write(values)
