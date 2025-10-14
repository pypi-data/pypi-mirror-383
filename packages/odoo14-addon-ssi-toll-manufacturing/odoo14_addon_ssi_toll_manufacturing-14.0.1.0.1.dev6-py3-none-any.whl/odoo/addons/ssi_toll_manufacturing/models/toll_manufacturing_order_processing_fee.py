# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TollManufacturingOrderProcessingFee(models.Model):
    _name = "toll_manufacturing_order.processing_fee"
    _description = "Toll Manufacturing Order - Processing Fee"
    _inherit = [
        "mixin.product_line_account",
    ]

    order_id = fields.Many2one(
        comodel_name="toll_manufacturing_order",
        string="# Toll Manufacturing Order",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        required=True,
    )
    tax_ids = fields.Many2many(
        relation="rel_tmo_processing_fee_2_tax",
    )

    def _create_acceptance_line(self, acceptance):
        self.ensure_one()
        self.env["toll_manufacturing_acceptance.processing_fee"].create(
            {
                "acceptance_id": acceptance.id,
                "detail_id": self.id,
                "product_id": self.product_id.id,
                "name": self.name,
                "uom_quantity": self.uom_quantity,
                "uom_id": self.uom_id.id,
                "price_unit": self.price_unit,
                "tax_ids": [(6, 0, self.tax_ids.ids)],
                "account_id": self.account_id.id,
            }
        )
