# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TollManufacturingAcceptanceSupplierProcuredRawMaterial(models.Model):
    _name = "toll_manufacturing_acceptance.supplier_procured_raw_material"
    _description = "Toll Manufacturing Acceptance - Supplier Procured Raw Material"
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
        comodel_name="toll_manufacturing_order.supplier_procured_raw_material",
        string="# Toll Manufacturing Order - Supplier Procured Raw Material",
        required=True,
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        required=True,
    )
    tax_ids = fields.Many2many(
        relation="rel_tma_supplier_procured_raw_material_2_tax",
    )
