# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TollManufacturingOrderCustomerSuppliedtRawMaterial(models.Model):
    _name = "toll_manufacturing_order.customer_supplied_raw_material"
    _description = "Toll Manufacturing Order - Customer Supplied Raw Material"
    _table = "tmo_customer_supplied_raw_material"
    _inherit = [
        "mixin.product_line",
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

    def _create_acceptance_line(self, acceptance):
        self.ensure_one()
        self.env["toll_manufacturing_acceptance.customer_supplied_raw_material"].create(
            {
                "acceptance_id": acceptance.id,
                "detail_id": self.id,
                "product_id": self.product_id.id,
                "name": self.name,
                "uom_id": self.uom_id.id,
                "uom_quantity": self.uom_quantity,
            }
        )
