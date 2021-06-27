# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _name = "purchase.request.line.make.purchase.order"
    _description = "Purchase Request Line Make Purchase Order"

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
        domain=[("is_company", "=", True)],
        context={"res_partner_search_mode": "supplier", "default_is_company": True},
    )
    remarks = fields.Char('Remarks')
    item_ids = fields.One2many(
        comodel_name="purchase.request.line.make.purchase.order.item",
        inverse_name="wiz_id",
        string="Items",
    )
    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase Order",
        domain=[("state", "=", "draft")],
    )
    sync_data_planned = fields.Boolean(
        string="Merge on PO lines with equal Scheduled Date"
    )

    @api.model
    def _prepare_item(self, line):

        return {
            "line_id": line.id,
            "request_id": line.request_id.id,
            "product_id": line.product_id.id,
            "name": line.name or line.product_id.name,
            "product_qty": line.qty_to_order,
            "product_uom_id": line.product_uom.id,
            "unit_price": line.unit_price,
            "total_price": line.unit_price * line.qty_to_order,
        }

    @api.model
    def _check_valid_request_line(self, request_line_ids):
        picking_type = False
        company_id = False

        for line in self.env["purchase.request.line"].browse(request_line_ids):
            if line.request_id.state == "done":
                raise UserError(_("The purchase has already been completed."))

            if line.purchase_state == "done":
                raise UserError(_("The purchase has already been completed."))

            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines from the same company."))
            else:
                company_id = line_company_id

            line_picking_type = line.request_id.picking_type_id or False
            if not line_picking_type:
                raise UserError(_("You have to enter a Picking Type."))
            if picking_type is not False and line_picking_type != picking_type:
                raise UserError(
                    _("You have to select lines from the same Picking Type.")
                )
            else:
                picking_type = line_picking_type

    @api.model
    def check_group(self, request_lines):
        if len(list(set(request_lines.mapped("request_id.group_id")))) > 1:
            raise UserError(
                _(
                    "You cannot create a single purchase order from "
                    "purchase requests that have different procurement group."
                )
            )

    @api.model
    def get_items(self, request_line_ids):
        request_line_obj = self.env["purchase.request.line"]
        items = []
        request_lines = request_line_obj.browse(request_line_ids)
        self._check_valid_request_line(request_line_ids)
        self.check_group(request_lines)
        for line in request_lines:
            items.append([0, 0, self._prepare_item(line)])
        return items

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        request_line_ids = []
        if active_model == "purchase.request.line":
            request_line_ids += self.env.context.get("active_ids", [])
        elif active_model == "purchase.request":
            request_ids = self.env.context.get("active_ids", False)
            request_line_ids += (
                self.env[active_model].browse(request_ids).mapped("line_ids.id")
            )
        if not request_line_ids:
            return res
        res["item_ids"] = self.get_items(request_line_ids)
        request_lines = self.env["purchase.request.line"].browse(request_line_ids)
        supplier_ids = request_lines.mapped("supplier_id").ids
        if len(supplier_ids) == 1:
            res["supplier_id"] = supplier_ids[0]
        return res


    def make_purchase_order(self):
        request_id = self.env.context.get("active_ids", False)
        pr_id = request_id[0]
        pr = self.env['purchase.request'].browse(pr_id)
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier_id.id,
            'state': 'purchase',
            'origin': pr.origin,
            'request_id': pr.id,
            'expense_type': pr.expense_type,
            'remarks': self.remarks,
            'company_id': pr.company_id.id,
            'state': 'draft'
        })
        po_lines = []
        for item in self.item_ids:
            print('validate')
            print(item.product_qty)
            if item.product_qty <= 0:
                raise UserError(
                    _("Please input positive number on quantity")
                )
            if item.unit_price <= 0:
                raise UserError(
                    _("Please input positive number on unit price")
                )

            data = {
                'product_id': item.product_id.id or item.product_id,
                'name': item.product_id.name,
                'product_uom': item.product_id.uom_id.id or False,
                'product_qty': item.product_qty,
                'price_unit': item.unit_price,
                'date_planned': pr.date_start,
                'order_id': po.id,
            }
            po_lines.append(data)
        self.env['purchase.order.line'].create(po_lines)



class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _name = "purchase.request.line.make.purchase.order.item"
    _description = "Purchase Request Line Make Purchase Order Item"

    wiz_id = fields.Many2one(
        comodel_name="purchase.request.line.make.purchase.order",
        string="Wizard",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    line_id = fields.Many2one(
        comodel_name="purchase.request.line", string="Purchase Request Line"
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        related="line_id.request_id",
        string="Purchase Request",
        readonly=False,
    )
    unit_price = fields.Float('Unit Cost', readonly=False, required=False)
    total_price = fields.Float('Total', compute='_compute_total_price')

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        readonly=False,
    )
    name = fields.Char(string="Description", required=False)
    product_qty = fields.Float(
        string="Quantity to purchase", digits="Product Unit of Measure",
        readony=False,
    )
    qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure",
        readony=False,
    )

    product_uom_id = fields.Many2one(
        'pm.product.uom', 'UOM', related='product_id.supplier_product_uom_id', readonly=True
    )
    keep_description = fields.Boolean(
        string="Copy descriptions to new PO",
        help="Set true if you want to keep the "
        "descriptions provided in the "
        "wizard in the new PO.",
    )
    @api.depends('product_qty', 'unit_price')
    def _compute_total_price(self):
        for record in self:
            if record.product_qty and record.unit_price:
                record.total_price = record.product_qty * record.unit_price
            else:
                record.total_price = 0

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            code = self.product_id.code
            sup_info_id = self.env["product.supplierinfo"].search(
                [
                    "|",
                    ("product_id", "=", self.product_id.id),
                    ("product_tmpl_id", "=", self.product_id.product_tmpl_id.id),
                    ("name", "=", self.wiz_id.supplier_id.id),
                ]
            )
            if sup_info_id:
                p_code = sup_info_id[0].product_code
                p_name = sup_info_id[0].product_name
                name = "[{}] {}".format(
                    p_code if p_code else code, p_name if p_name else name
                )
            else:
                if code:
                    name = "[{}] {}".format(code, name)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.supplier_product_uom_id
            self.product_qty = 1.0
            self.name = name
