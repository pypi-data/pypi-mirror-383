# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TollManufacturingAcceptanceProcessingFee(models.Model):
    _name = "toll_manufacturing_acceptance.processing_fee"
    _description = "Toll Manufacturing Acceptance - Processing Fee"
    _inherit = [
        "mixin.product_line_account",
    ]

    acceptance_id = fields.Many2one(
        comodel_name="toll_manufacturing_acceptance",
        string="# Toll Manufacturing Acceptance",
        required=True,
        ondelete="cascade",
    )
    detail_id = fields.Many2one(
        comodel_name="toll_manufacturing_order.processing_fee",
        string="# Toll Manufacturing Order - Processing Fee",
        required=False,
    )
    product_id = fields.Many2one(
        required=True,
    )
    tax_ids = fields.Many2many(
        relation="rel_tmo_acceptance_fee_2_tax",
    )
