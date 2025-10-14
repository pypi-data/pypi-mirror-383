# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


class TollManufacturingAcceptance(models.Model):
    _name = "toll_manufacturing_acceptance"
    _description = "Toll Manufacturing Acceptance"
    _inherit = [
        "mixin.transaction_terminate",
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_partner",
        "mixin.many2one_configurator",
    ]

    # mixin.multiple_approval attributes
    _approval_from_state = "open"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False

    # Attributes related to add element on form view automatically
    _statusbar_visible_label = "draft,open,confirm,done"
    _policy_field_order = [
        "open_ok",
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "done_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_open",
        "action_confirm",
        "action_approve",
        "action_reject",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
        "action_recompute_all_fields",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_open",
        "dom_confirm",
        "dom_done",
        "dom_cancel",
        "dom_terminate",
        "dom_reject",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        default=lambda self: date.today(),
        states={"draft": [("readonly", False)]},
    )
    batch_acceptance_id = fields.Many2one(
        comodel_name="batch_toll_manufacturing_acceptance",
        string="# Batch Toll Manufacturing Acceptance",
        required=True,
        ondelete="restrict",
        help=(
            "Batch Toll Manufacturing Acceptance related to this Toll "
            "Manufacturing Acceptance."
        ),
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    order_id = fields.Many2one(
        comodel_name="toll_manufacturing_order",
        string="# Toll Manufacturing Order",
        required=True,
        ondelete="restrict",
        help="Toll Manufacturing Order related to this Toll Manufacturing Acceptance.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        related="order_id.currency_id",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        related="order_id.partner_id",
        store=True,
        readonly=True,
    )
    contact_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact Partner",
        related="order_id.contact_partner_id",
        store=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        related="order_id.product_id",
        store=True,
        readonly=True,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        related="product_id.uom_id",
        store=True,
        readonly=True,
    )
    quantity = fields.Float(
        string="Quantity",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    qty_to_receive = fields.Float(
        string="Qty. to Receive",
        compute="_compute_qty_receive",
        store=True,
        readonly=True,
    )
    qty_received = fields.Float(
        string="Qty. Received",
        compute="_compute_qty_receive",
        store=True,
        readonly=True,
    )

    customer_supplied_raw_material_ids = fields.One2many(
        comodel_name="toll_manufacturing_acceptance.customer_supplied_raw_material",
        inverse_name="acceptance_id",
        string="Customer Supplied Raw Materials",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    customer_supplied_rm_total_cost = fields.Monetary(
        string="Customer Supplied Raw Material Total Cost",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    supplier_procured_raw_material_ids = fields.One2many(
        comodel_name="toll_manufacturing_acceptance.supplier_procured_raw_material",
        inverse_name="acceptance_id",
        string="Supplier Procured Raw Materials",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    processing_fee_ids = fields.One2many(
        comodel_name="toll_manufacturing_acceptance.processing_fee",
        inverse_name="acceptance_id",
        string="Processing Fees",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    amount_supplier_procured_raw_material = fields.Monetary(
        string="Supplier Procured Raw Material Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    amount_processing_fee = fields.Monetary(
        string="Processing Fee Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    amount_tax = fields.Monetary(
        string="Tax Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        readonly=True,
    )

    total_cost = fields.Monetary(
        string="Total Cost",
        currency_field="currency_id",
        compute="_compute_cost",
        store=True,
        readonly=True,
    )
    unit_cost = fields.Monetary(
        string="Unit Cost",
        currency_field="currency_id",
        compute="_compute_cost",
        store=True,
        readonly=True,
    )

    # Procuurement Information
    procurement_group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source Location",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    destination_location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    raw_material_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Raw Material Route",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    finished_product_route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Finished Product Route",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fg_stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Finished Product Stock Moves",
        readonly=True,
        relation="rel_tma_2_stock_move",
        column1="tma_id",
        column2="move_id",
    )

    @api.depends(
        "fg_stock_move_ids",
        "quantity",
        "fg_stock_move_ids.state",
        "fg_stock_move_ids.quantity_done",
    )
    def _compute_qty_receive(self):
        for record in self.sudo():
            qty_to_receive = qty_received = 0.0
            for move in record.fg_stock_move_ids:
                if move.state in ["done"]:
                    qty_received += move.quantity_done
            qty_to_receive = record.quantity - qty_received
            record.qty_to_receive = qty_to_receive
            record.qty_received = qty_received

    @api.depends(
        "amount_total",
        "quantity",
        "customer_supplied_raw_material_ids.total_cost",
        "customer_supplied_raw_material_ids",
    )
    def _compute_cost(self):
        for record in self.sudo():
            customer_supplied_rm_total_cost = 0.0
            for (
                customer_supplied_raw_material
            ) in record.customer_supplied_raw_material_ids:
                customer_supplied_rm_total_cost += (
                    customer_supplied_raw_material.total_cost
                )
            total_cost = record.amount_total + customer_supplied_rm_total_cost
            unit_cost = total_cost / record.quantity if record.quantity else 0.0
            record.customer_supplied_rm_total_cost = customer_supplied_rm_total_cost
            record.total_cost = total_cost
            record.unit_cost = unit_cost

    @api.depends(
        "processing_fee_ids",
        "supplier_procured_raw_material_ids",
        "processing_fee_ids.price_subtotal",
        "processing_fee_ids.price_tax",
        "processing_fee_ids.price_total",
        "supplier_procured_raw_material_ids.price_subtotal",
        "supplier_procured_raw_material_ids.price_tax",
        "supplier_procured_raw_material_ids.price_total",
    )
    def _compute_amount(self):
        for record in self:
            amount_supplier_procured_raw_material = (
                amount_processing_fee
            ) = amount_untaxed = amount_tax = amount_total = 0.0
            for processing_fee in record.processing_fee_ids:
                amount_processing_fee += processing_fee.price_subtotal
                amount_untaxed += processing_fee.price_subtotal
                amount_tax += processing_fee.price_tax
                amount_total += processing_fee.price_total
            for (
                supplier_procured_raw_material
            ) in record.supplier_procured_raw_material_ids:
                amount_supplier_procured_raw_material += (
                    supplier_procured_raw_material.price_subtotal
                )
                amount_untaxed += supplier_procured_raw_material.price_subtotal
                amount_tax += supplier_procured_raw_material.price_tax
                amount_total += supplier_procured_raw_material.price_total

            record.amount_supplier_procured_raw_material = (
                amount_supplier_procured_raw_material
            )
            record.amount_processing_fee = amount_processing_fee
            record.amount_untaxed = amount_untaxed
            record.amount_tax = amount_tax
            record.amount_total = amount_total

    def action_load_customer_supplied_raw_material(self):
        for record in self.sudo():
            record._load_customer_supplied_raw_material()

    def action_load_supplier_procured_raw_material(self):
        for record in self.sudo():
            record._load_supplier_procured_raw_material()

    def action_load_processing_fee(self):
        for record in self.sudo():
            record._load_processing_fee()

    def action_create_rm_consumption(self):
        for record in self.sudo():
            record._create_rm_consumption()

    def action_create_fg_reception(self):
        for record in self.sudo():
            record._create_fg_picking()

    def _create_rm_consumption(self):
        self.ensure_one()
        for customer_supplied_raw_material in self.customer_supplied_raw_material_ids:
            customer_supplied_raw_material._create_rm_procurement()

    def _load_supplier_procured_raw_material(self):
        self.ensure_one()
        self.supplier_procured_raw_material_ids.unlink()
        for detail in self.order_id.supplier_procured_raw_material_ids:
            detail._create_acceptance_line(self)

    def _load_processing_fee(self):
        self.ensure_one()
        self.processing_fee_ids.unlink()
        for detail in self.order_id.processing_fee_ids:
            detail._create_acceptance_line(self)

    def _load_customer_supplied_raw_material(self):
        self.ensure_one()
        self.customer_supplied_raw_material_ids.unlink()
        for detail in self.order_id.customer_supplied_raw_material_ids:
            detail._create_acceptance_line(self)

    @ssi_decorator.post_open_action()
    def _01_create_procurement_group(self):
        self.ensure_one()

        if self.procurement_group_id:
            return True

        PG = self.env["procurement.group"]
        group = PG.create(self._prepare_create_procurement_group())
        self.write(
            {
                "procurement_group_id": group.id,
            }
        )

    def _prepare_create_procurement_group(self):
        self.ensure_one()
        return {
            "name": self.name,
        }

    def _create_fg_picking(self):
        self.ensure_one()
        group = self.procurement_group_id
        qty = self.qty_to_receive
        values = self._get_fg_procurement_data()

        procurements = []
        try:
            procurement = group.Procurement(
                self.product_id,
                qty,
                self.product_id.uom_id,
                values.get("location_id"),
                values.get("origin"),
                values.get("origin"),
                self.env.company,
                values,
            )

            procurements.append(procurement)
            self.env["procurement.group"].run(procurements)
        except UserError as error:
            raise UserError(error)

    def _get_fg_procurement_data(self):
        group = self.procurement_group_id
        origin = self.name
        warehouse = self.warehouse_id
        location = self.destination_location_id
        route = self.finished_product_route_id
        result = {
            "name": origin,
            "group_id": group,
            "origin": origin,
            "warehouse_id": warehouse,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.qty_to_receive,
            "partner_id": self.partner_id.id,
            "product_uom": self.product_id.uom_id.id,
            "location_id": location,
            "route_ids": route,
            "price_unit": self.unit_cost,
            "toll_manufacturing_acceptance_ids": [(4, self.id)],
        }
        return result

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "open_ok",
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "done_ok",
            "cancel_ok",
            "terminate_ok",
            "restart_ok",
            "reject_ok",
            "manual_number_ok",
            "restart_approval_ok",
        ]
        res += policy_field
        return res
