# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _name = "stock.rule"
    _inherit = ["stock.rule"]

    def _get_custom_move_fields(self):
        _super = super()
        result = _super._get_custom_move_fields()
        result += [
            "toll_manufacturing_acceptance_ids",
            "customer_supplied_raw_material_ids",
            "price_unit",
        ]
        return result
