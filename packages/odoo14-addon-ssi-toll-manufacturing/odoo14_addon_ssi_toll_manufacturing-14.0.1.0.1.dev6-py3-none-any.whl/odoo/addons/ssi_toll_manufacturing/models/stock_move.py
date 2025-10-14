# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move"]

    toll_manufacturing_acceptance_ids = fields.Many2many(
        string="# Toll Manufacturing Acceptance",
        comodel_name="toll_manufacturing_acceptance",
        relation="rel_tma_2_stock_move",
        column1="move_id",
        column2="tma_id",
    )
    customer_supplied_raw_material_ids = fields.Many2many(
        string="Customer Supplied Raw Material",
        comodel_name="toll_manufacturing_acceptance.customer_supplied_raw_material",
        relation="rel_customer_supplied_raw_material_2_stock_move",
        column1="move_id",
        column2="detail_id",
    )
