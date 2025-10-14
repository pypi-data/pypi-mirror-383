# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class TollManufacturingOrderType(models.Model):
    _name = "toll_manufacturing_order_type"
    _description = "Toll Manufacturing Order Type"
    _inherit = ["mixin.master_data"]
