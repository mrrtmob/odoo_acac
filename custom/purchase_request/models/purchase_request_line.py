# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]

class PurchaseDescriptionLine(models.Model):
    _name = "purchase.description.line"
    _description = "Purchase Description Line"
    name = fields.Char(string="Product", track_visibility="onchange")
    qty = fields.Float(string="Quantity")
    description = fields.Text(string="Description")
    product_uom = fields.Many2one('pm.product.uom', 'UoM', tracking=True)

    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )


class PurchaseRequestLine(models.Model):

    _name = "purchase.request.line"
    _description = "Purchase Request Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(string="Name", track_visibility="onchange")
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Product Unit of Measure",
        track_visibility="onchange",
    )
    product_qty = fields.Float(
        string="QTY", track_visibility="onchange",
        digits=(12, 3)
    )
    product_qty_uom = fields.Float(
        string="Quantity (UOM)",
        track_visibility="onchange",
        compute='_compute_qty_uom',
        store=True,
        digits=(12, 3)
    )
    request_id = fields.Many2one(
        comodel_name="purchase.request",
        string="Purchase Request",
        ondelete="cascade",
        readonly=True,
        index=True,
        auto_join=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="request_id.company_id",
        string="Company",
        store=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        track_visibility="onchange",
    )
    requested_by = fields.Many2one(
        comodel_name="res.users",
        related="request_id.requested_by",
        string="Requested by",
        store=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        related="request_id.assigned_to",
        string="Assigned to",
        store=True,
    )
    date_start = fields.Date(related="request_id.date_start", store=True)
    description = fields.Text(
        string="PR Description",
        store=True,
        readonly=False,
    )
    origin = fields.Char(
        related="request_id.origin", string="Source Document", store=True
    )
    date_required = fields.Date(
        string="Request Date",
        required=True,
        track_visibility="onchange",
        default=fields.Date.context_today,
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    specifications = fields.Text(string="Remarks")
    request_state = fields.Selection(
        string="Request state",
        related="request_id.state",
        selection=_STATES,
        store=True,
    )
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        related='product_id.supplier_id',
        track_visibility="onchange",
        store=True,
    )
    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False
    )

    purchased_qty = fields.Float(
        string="Quantity in RFQ or PO",
        digits="Product Unit of Measure",
        compute="_compute_purchased_qty",
    )
    purchase_lines = fields.Many2many(
        comodel_name="purchase.order.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_request_line_id",
        column2="purchase_order_line_id",
        string="Purchase Order Lines",
        readonly=True,
        copy=False,
    )
    purchase_state = fields.Selection(
        compute="_compute_purchase_state",
        string="Purchase Status",
        selection=lambda self: self.env["purchase.order"]._fields["state"].selection,
        store=True,
    )
    move_dest_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="created_purchase_request_line_id",
        string="Downstream Moves",
    )

    orderpoint_id = fields.Many2one(
        comodel_name="stock.warehouse.orderpoint", string="Orderpoint"
    )
    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_request_line_id",
        string="Purchase Request Allocation",
    )

    qty_in_progress = fields.Float(
        string="Qty In Progress",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity in progress.",
    )
    qty_on_hand = fields.Float(
        string='On Hand (UOR)',
        related='product_id.product_tmpl_id.qty_on_hand',
        store=True
    )
    qty_on_hand_uom = fields.Float(
        string='On Hand (UOM)',
        related='product_id.product_tmpl_id.qty_on_hand_uom',
        store=True
    )
    qty_done = fields.Float(
        string="Qty Done",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty",
        store=True,
        help="Quantity completed",
    )
    qty_cancelled = fields.Float(
        string="Qty Cancelled",
        digits="Product Unit of Measure",
        readonly=True,
        compute="_compute_qty_cancelled",
        store=True,
        help="Quantity cancelled",
    )
    qty_to_buy = fields.Boolean(
        compute="_compute_qty_to_buy",
        string="There is some pending qty to buy",
        store=True,
    )
    qty_to_order = fields.Float('QTY Order (UOM)')
    pending_qty_to_receive = fields.Float(
        compute="_compute_qty_to_buy",
        digits="Product Unit of Measure",
        copy=False,
        string="Pending Qty to Receive",
        store=True,
    )
    estimated_cost = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute='_compute_estimated_cost',
        store=True,
        default=0.0,
        help="Estimated cost of Purchase Request Line, not propagated to PO.",
    )
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        track_visibility="onchange",
    )
    product_uor = fields.Selection(
        [('l', 'l'),
         ('kg', 'kg'),
         ('pc', 'pc'),
         ('m', 'm')],
        'UOR',
        readonly='True', store=True, related='product_id.uor'
    )

    product_uom = fields.Many2one('pm.product.uom', 'UOM', store=True, related='product_id.supplier_product_uom_id',
                                  tracking=True, readonly=True)
    unit_price = fields.Float('Unit Cost', related='product_id.supplier_unit_cost', store=True,
                              readonly=True, tracking=True)
    minimum_order = fields.Float('Min Order (UOM)', store=True, related='product_id.supplier_minimum_order_qty',
                                tracking=True, readonly=True)
    qty_needed_uor = fields.Float('Needed(UOR)')
    qty_needed_uom = fields.Float('Needed(UOM)', compute='_compute_qty_needed_uom', store=True)
    packing = fields.Char('Packing', related='product_id.packing', readonly=True, store=True)
    delivery_time = fields.Integer('Delivery Time', related='product_id.supplier_delivery_time', readonly=True, store=True)
    is_danger = fields.Boolean('Danger', default=False, store=False, readonly=True)

    qty_uor_name = fields.Char('QTY(UOR)', compute='compute_qty_uor_name', store=False, required=False)
    qty_uom_name = fields.Char('QTY(UOM)', compute='compute_qty_uom_name', store=False, required=False)

    @api.depends('product_qty')
    def compute_qty_uor_name(self):
        for record in self:
            print(record.product_qty)
            print(record.product_uor)
            if record.product_qty > 0 and record.product_uor:
                print('hit condition')
                record.qty_uor_name = str(record.product_qty) + ' ' + record.product_uor
            else:
                record.qty_uor_name = ''

    @api.depends('product_qty_uom')
    def compute_qty_uom_name(self):
        for record in self:
            if record.product_qty_uom > 0 and record.product_uom.name:
                record.qty_uom_name = str(record.product_qty_uom) + ' ' + record.product_uom.name
            else:
                record.qty_uom_name = ''

    @api.depends('qty_to_order', 'unit_price')
    def _compute_estimated_cost(self):
        for record in self:
            record.estimated_cost = record.qty_to_order * record.unit_price


    @api.onchange('qty_to_order')
    def _compute_is_danger(self):
        for record in self:
            if record.qty_to_order < record.minimum_order:
                record.is_danger = True
            else:
                record.is_danger = False


    @api.depends('qty_on_hand_uom', 'product_qty_uom')
    def _compute_qty_needed_uom(self):
        for record in self:
            needed = record.product_qty_uom - record.qty_on_hand_uom
            if needed < 0:
                record.qty_needed_uom = 0
            else:
                if needed < record.minimum_order:
                    record.qty_needed_uom = record.minimum_order
                else:
                    record.qty_needed_uom = needed

    @api.depends('product_id', 'product_qty')
    def _compute_qty_uom(self):
        for record in self:
            if record.product_id.supplier_qty_in_uor > 0:
                record.product_qty_uom = record.product_qty / record.product_id.supplier_qty_in_uor
            else:
                record.product_qty_uom = 0


    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "request_id.state",
    )
    def _compute_qty_to_buy(self):
        for pr in self:
            qty_to_buy = sum(pr.mapped("product_qty")) - sum(pr.mapped("qty_done"))
            pr.qty_to_buy = qty_to_buy > 0.0
            pr.pending_qty_to_receive = qty_to_buy

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty(self):
        for request in self:
            done_qty = sum(
                request.purchase_request_allocation_ids.mapped("allocated_product_qty")
            )
            open_qty = sum(
                request.purchase_request_allocation_ids.mapped("open_product_qty")
            )
            request.qty_done = done_qty
            request.qty_in_progress = open_qty

    @api.depends(
        "purchase_request_allocation_ids",
        "purchase_request_allocation_ids.stock_move_id.state",
        "purchase_request_allocation_ids.stock_move_id",
        "purchase_request_allocation_ids.purchase_line_id.order_id.state",
        "purchase_request_allocation_ids.purchase_line_id",
    )
    def _compute_qty_cancelled(self):
        for request in self:
            if request.product_id.type != "service":
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.stock_move_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
            else:
                qty_cancelled = sum(
                    request.mapped("purchase_request_allocation_ids.purchase_line_id")
                    .filtered(lambda sm: sm.state == "cancel")
                    .mapped("product_qty")
                )
                # done this way as i cannot track what was received before
                # cancelled the purchase order
                qty_cancelled -= request.qty_done
            if request.product_uom_id:
                request.qty_cancelled = (
                    max(
                        0,
                        request.product_id.uom_id._compute_quantity(
                            qty_cancelled, request.product_uom_id
                        ),
                    )
                    if request.purchase_request_allocation_ids
                    else 0
                )
            else:
                request.qty_cancelled = qty_cancelled

    @api.depends(
        "product_id",
        "name",
        "product_uom_id",
        "product_qty",
        "analytic_account_id",
        "date_required",
        "specifications",
        "purchase_lines",
    )
    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True
        for rec in self.filtered(lambda p: p.purchase_lines):
            rec.is_editable = False

    # @api.depends("product_id", "product_id.seller_ids")
    # def _compute_supplier_id(self):
    #     for rec in self:
    #         rec.supplier_id = False
    #         if rec.product_id:
    #             if rec.product_id.seller_ids:
    #                 rec.supplier_id = rec.product_id.seller_ids[0].name

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = "[{}] {}".format(name, self.product_id.code)
            if self.product_id.description_purchase:
                name += "\n" + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_uor = self.product_id.product_tmpl_id.uor
            self.product_qty = 1
            self.name = name

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({"cancelled": True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({"cancelled": False})

    def _compute_purchased_qty(self):
        for rec in self:
            rec.purchased_qty = 0.0
            for line in rec.purchase_lines.filtered(lambda x: x.state != "cancel"):
                if rec.product_uom_id and line.product_uom != rec.product_uom_id:
                    rec.purchased_qty += line.product_uom._compute_quantity(
                        line.product_qty, rec.product_uom_id
                    )
                else:
                    rec.purchased_qty += line.product_qty

    @api.depends("purchase_lines.state", "purchase_lines.order_id.state")
    def _compute_purchase_state(self):
        for rec in self:
            temp_purchase_state = False
            if rec.purchase_lines:
                if any([po_line.state == "done" for po_line in rec.purchase_lines]):
                    temp_purchase_state = "done"
                elif all([po_line.state == "cancel" for po_line in rec.purchase_lines]):
                    temp_purchase_state = "cancel"
                elif any(
                    [po_line.state == "purchase" for po_line in rec.purchase_lines]
                ):
                    temp_purchase_state = "purchase"
                elif any(
                    [po_line.state == "to approve" for po_line in rec.purchase_lines]
                ):
                    temp_purchase_state = "to approve"
                elif any([po_line.state == "sent" for po_line in rec.purchase_lines]):
                    temp_purchase_state = "sent"
                elif all(
                    [
                        po_line.state in ("draft", "cancel")
                        for po_line in rec.purchase_lines
                    ]
                ):
                    temp_purchase_state = "draft"
            rec.purchase_state = temp_purchase_state

    @api.model
    def _get_supplier_min_qty(self, product, partner_id=False):
        seller_min_qty = 0.0
        if partner_id:
            seller = product.seller_ids.filtered(lambda r: r.name == partner_id).sorted(
                key=lambda r: r.min_qty
            )
        else:
            seller = product.seller_ids.sorted(key=lambda r: r.min_qty)
        if seller:
            seller_min_qty = seller[0].min_qty
        return seller_min_qty

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id
        # TODO: Not implemented yet.
        #  Make sure we use the minimum quantity of the partner corresponding
        #  to the PO. This does not apply in case of dropshipping
        supplierinfo_min_qty = 0.0
        if not po_line.order_id.dest_address_id:
            supplierinfo_min_qty = self._get_supplier_min_qty(
                po_line.product_id, po_line.order_id.partner_id
            )

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        if new_pr_line:
            rl_qty = po_line.product_uom_qty
        else:
            for prl in po_line.purchase_request_lines:
                for alloc in prl.purchase_request_allocation_ids:
                    rl_qty += alloc.product_uom_id._compute_quantity(
                        alloc.requested_product_uom_qty, purchase_uom
                    )
        qty = max(rl_qty, supplierinfo_min_qty)
        return qty

    def _can_be_deleted(self):
        self.ensure_one()
        return self.request_state == "draft"

    def unlink(self):
        if self.mapped("purchase_lines"):
            raise UserError(
                _("You cannot delete a record that refers to purchase lines!")
            )
        for line in self:
            if not line._can_be_deleted():
                raise UserError(
                    _(
                        "You can only delete a purchase request line "
                        "if the purchase request is in draft state."
                    )
                )
            else:

                line.request_id.message_post_with_view('purchase_request.track_pr_line_template_delete',
                                                       values={'line': line, 'qty_uom_name': line.qty_uom_name,
                                                               'estimated_cost': line.estimated_cost},
                                                       subtype_id=self.env.ref('mail.mt_note').id)




        return super(PurchaseRequestLine, self).unlink()

    # @api.model
    # def create(self, val):
    #     line = super(PurchaseRequestLine, self).create(val)
    #     msg = _("Extra line with %s ") % (line.product_id.display_name,)
    #     line.request_id.message_post(body=msg)
    #     return line

    def write(self, val):

        print('after:', self.estimated_cost)
        if 'qty_to_order' in val:
            for line in self:
                line.request_id.message_post_with_view('purchase_request.track_pr_line_template',
                                                    values={'line': line, 'product_qty': val['qty_to_order']},
                                                    subtype_id=self.env.ref('mail.mt_note').id)
            for line in self:
                cost = line.unit_price * val['qty_to_order']
                line.request_id.message_post_with_view('purchase_request.track_pr_line_template_qty_order',
                                                    values={'line': line, 'qty_to_order': val['qty_to_order'],
                                                            'estimated_cost': cost},
                                                    subtype_id=self.env.ref('mail.mt_note').id)

        return super(PurchaseRequestLine, self).write(val)




