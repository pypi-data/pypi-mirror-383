# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class TollManufacturingOrder(models.Model):
    _name = "toll_manufacturing_order"
    _description = "Toll Manufacturing Order"
    _inherit = [
        "mixin.transaction_terminate",
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.transaction_partner",
        "mixin.many2one_configurator",
        "mixin.product_line",
    ]

    # mixin.multiple_approval attributes
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_button = False
    _automatically_insert_done_policy_fields = False
    _automatically_insert_open_button = False
    _automatically_insert_open_policy_fields = False

    # Attributes related to add element on form view automatically
    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "open_ok",
        "done_ok",
        "cancel_ok",
        "restart_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve",
        "action_reject",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "action_restart",
        "action_recompute_all_fields",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
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
    batch_id = fields.Many2one(
        comodel_name="batch_toll_manufacturing_order",
        string="# Batch",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    type_id = fields.Many2one(
        comodel_name="toll_manufacturing_order_type",
        string="Type",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.user.company_id.currency_id,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_id = fields.Many2one(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    uom_id = fields.Many2one(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    customer_supplied_raw_material_ids = fields.One2many(
        comodel_name="toll_manufacturing_order.customer_supplied_raw_material",
        inverse_name="order_id",
        string="Customer Supplied Raw Materials",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    supplier_procured_raw_material_ids = fields.One2many(
        comodel_name="toll_manufacturing_order.supplier_procured_raw_material",
        inverse_name="order_id",
        string="Supplier Procured Raw Materials",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    processing_fee_ids = fields.One2many(
        comodel_name="toll_manufacturing_order.processing_fee",
        inverse_name="order_id",
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

    acceptance_ids = fields.One2many(
        comodel_name="toll_manufacturing_acceptance",
        inverse_name="order_id",
        string="Toll Manufacturing Acceptances",
        readonly=True,
    )
    qty_accepted = fields.Float(
        string="Accepted Quantity",
        compute="_compute_qty_accepted",
        store=True,
        readonly=True,
    )
    qty_diff = fields.Float(
        string="Difference Quantity",
        compute="_compute_qty_accepted",
        store=True,
        readonly=True,
    )

    @api.depends("acceptance_ids", "acceptance_ids.quantity", "acceptance_ids.state")
    def _compute_qty_accepted(self):
        for record in self:
            qty_accepted = 0.0
            for acceptance in record.acceptance_ids:
                qty_accepted += acceptance.quantity
            record.qty_accepted = qty_accepted
            record.qty_diff = qty_accepted - record.quantity

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

    @api.onchange("batch_id")
    def onchange_type_id(self):
        self.type_id = False
        if self.batch_id:
            self.type_id = self.batch_id.type_id

    @api.onchange("batch_id")
    def onchange_partner_id(self):
        self.partner_id = False
        if self.batch_id:
            self.partner_id = self.batch_id.partner_id

    @api.onchange("batch_id")
    def onchange_contact_partner_id(self):
        self.contact_partner_id = False
        if self.batch_id:
            self.contact_partner_id = self.batch_id.contact_partner_id

    def onchange_name(self):
        pass

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "open_ok",
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
