# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    categ_id = fields.Many2one(required=False, default=None)
    is_food = fields.Boolean(string='Is an Ingredient', default=False)
    ingredient_categ_id = fields.Many2one(
        'pm.ingredient.category',
        'Ingredient Category',
        help="Select category for the current ingredient")
    brand_id = fields.Many2one('pm.brand', 'Brand')
    ingredient_type = fields.Selection(
        [('main', 'Main Ingredient'),
         ('part', 'Part Ingredient')]
    )
    keyword = fields.Char()
    ingredient_origin_id = fields.Many2one(
        'pm.ingredient.origin',
        'Origin'
    )
    cost = fields.Float(compute='_compute_cost', store=True)
    qty_on_hand = fields.Float(default=0)
    qty_on_hand_uom = fields.Float('QTY On Hand(UoM)', compute="_compute_qty_on_hand_uom", store=True)
    rank = fields.Selection(
        [('a', 'A'),
         ('b', 'B'),
         ('c', 'C'),
         ('d', 'D')]
    )
    packing = fields.Char()
    internal_code = fields.Char('ACAC SKU')
    uor = fields.Selection(
        [('l', 'l'),
         ('kg', 'kg'),
         ('pc', 'pc'),
         ('m', 'm')],
        'UoR',
        required=True,
        tracking=True
    )
    supplier_id = fields.Many2one('res.partner', 'Supplier', domain=[('partner_type', '=', 'supplier')], required=True, index=True, tracking=True)
    supplier_product_code = fields.Char()
    supplier_unit_cost = fields.Float(required=True, tracking=True)
    supplier_minimum_order_qty = fields.Float('Supplier Minimum Order Qty (UOM)', required=True, tracking=True)
    supplier_qty_in_uor = fields.Float('Supplier Qty in UOR', default=1, required=True, tracking=True)
    minimum_order_qty = fields.Float('Minimum Order Qty (UOR)', compute='_compute_minimum_order_qty', store=True)
    supplier_product_uom_id = fields.Many2one('pm.product.uom', 'Supplier Product UOM', required=True, tracking=True)
    supplier_delivery_time = fields.Integer(default=1, required=True)
    name_in_khmer = fields.Char('Name in Khmer')
    waste_percentage = fields.Float('Waste (%)', default=0, tracking=True)

    @api.constrains('supplier_qty_in_uor')
    def _check_supplier_qty_in_uor(self):
        for record in self:
            if record.supplier_qty_in_uor <= 0:
                raise ValidationError(
                    _("Supplier Qty in UOR must be greater than 0."))

    @api.constrains('waste_percentage')
    def _check_waste_percentage(self):
        for record in self:
            if record.waste_percentage < 0 or record.waste_percentage > 100:
                raise ValidationError(
                    _("Waste (%) must be between 0% and 100%."))

    @api.depends('supplier_minimum_order_qty', 'supplier_qty_in_uor')
    def _compute_minimum_order_qty(self):
        for record in self:
            record.minimum_order_qty = record.supplier_minimum_order_qty * record.supplier_qty_in_uor

    @api.depends('supplier_unit_cost', 'supplier_qty_in_uor')
    def _compute_cost(self):
        for record in self:
            if record.supplier_qty_in_uor > 0:
                record.cost = record.supplier_unit_cost / record.supplier_qty_in_uor

    @api.depends('qty_on_hand', 'supplier_qty_in_uor')
    def _compute_qty_on_hand_uom(self):
        for record in self:
            if record.supplier_qty_in_uor > 0:
                record.qty_on_hand_uom = record.qty_on_hand / record.supplier_qty_in_uor



class ProductProduct(models.Model):
    _inherit = 'product.product'

    ingredient_nutrition_ids = fields.One2many('pm.ingredient.nutrition', 'product_id')
    search_rank = fields.Integer('Search Rank', compute="_compute_search_rank", store=True)

    @api.depends('name')
    def _compute_search_rank(self):
        print("***********")
        for product in self:
            count = self.env['pm.recipe.line'].search_count([('product_id', '=', product.id)])
            print(count)
            product.search_rank = self.env['pm.recipe.line'].search_count([('product_id', '=', product.id)])

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        print("Hit Search Function")
        args = args or []
        domain = []
        if name:
            domain = [('keyword', 'ilike', name)]
        print(domain + args)
        return self._search(domain + args, limit=limit, order="search_rank desc", access_rights_uid=name_get_uid)




    def act_show_order_history(self):
        return {
            'name': _('Order History'),
            'view_mode': 'graph,tree',
            'views': [[self.env.ref('pm_culinary.purchase_order_line_view_graph').id, 'graph'], [self.env.ref('pm_culinary.purchase_order_line_view_tree').id, 'tree']],
            'res_model': 'purchase.order.line',
            'domain': [('state', '=', 'purchase')],
            'context': {'search_default_product_id': self.id},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
