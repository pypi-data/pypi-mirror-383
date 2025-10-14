# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class BatchTollManufacturingAcceptancer(models.Model):
    _name = "batch_toll_manufacturing_acceptance"
    _description = "Batch Toll Manufacturing Acceptancer"
    _inherit = [
        "mixin.transaction_terminate",
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.transaction_partner",
        "mixin.many2one_configurator",
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
        "%(ssi_transaction_terminate_mixin.base_select_terminate_reason_action)d",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
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
    batch_id = fields.Many2one(
        string="# Batch Toll Manufacturing Order",
        comodel_name="batch_toll_manufacturing_order",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        related="batch_id.partner_id",
        store=True,
        readonly=True,
    )
    contact_partner_id = fields.Many2one(
        string="Contact Partner",
        comodel_name="res.partner",
        related="batch_id.contact_partner_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="batch_id.currency_id",
        store=True,
        readonly=True,
    )
    acceptance_ids = fields.One2many(
        string="Toll Manufacturing Acceptances",
        comodel_name="toll_manufacturing_acceptance",
        inverse_name="batch_acceptance_id",
        readonly=True,
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

    @api.depends(
        "acceptance_ids",
        "acceptance_ids.amount_supplier_procured_raw_material",
        "acceptance_ids.amount_processing_fee",
        "acceptance_ids.amount_untaxed",
        "acceptance_ids.amount_tax",
        "acceptance_ids.amount_total",
        "acceptance_ids.state",
    )
    def _compute_amount(self):
        for record in self:
            amount_supplier_procured_raw_material = (
                amount_processing_fee
            ) = amount_untaxed = amount_tax = amount_total = 0.0
            for order in record.acceptance_ids:
                amount_supplier_procured_raw_material += (
                    order.amount_supplier_procured_raw_material
                )
                amount_processing_fee += order.amount_processing_fee
                amount_untaxed += order.amount_untaxed
                amount_tax += order.amount_tax
                amount_total += order.amount_total
            record.amount_supplier_procured_raw_material = (
                amount_supplier_procured_raw_material
            )
            record.amount_processing_fee = amount_processing_fee
            record.amount_untaxed = amount_untaxed
            record.amount_tax = amount_tax
            record.amount_total = amount_total

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
