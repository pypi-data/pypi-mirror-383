# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TollManufacturingAcceptanceCustomerSuppliedtRawMaterial(models.Model):
    _name = "toll_manufacturing_acceptance.customer_supplied_raw_material"
    _description = "Toll Manufacturing Acceptance - Customer Supplied Raw Material"
    _table = "tma_customer_supplied_raw_material"
    _inherit = [
        "mixin.product_line",
    ]

    acceptance_id = fields.Many2one(
        comodel_name="toll_manufacturing_acceptance",
        string="# Toll Manufacturing Acceptance",
        required=True,
        ondelete="cascade",
    )
    detail_id = fields.Many2one(
        comodel_name="toll_manufacturing_order.customer_supplied_raw_material",
        string="# Toll Manufacturing Order - Customer Supplied Raw Material",
        required=True,
        ondelete="restrict",
    )
    product_id = fields.Many2one(
        required=True,
    )
    stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        string="Stock Moves",
        readonly=True,
        relation="rel_customer_supplied_raw_material_2_stock_move",
        column1="detail_id",
        column2="move_id",
    )
    qty_to_consume = fields.Float(
        string="Qty. to Consume",
        compute="_compute_consume",
        store=True,
        readonly=True,
    )
    qty_consumed = fields.Float(
        string="Qty. Consumed",
        compute="_compute_consume",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        related="acceptance_id.currency_id",
        store=True,
        readonly=True,
    )
    total_cost = fields.Monetary(
        string="Total Cost",
        currency_field="currency_id",
        compute="_compute_consume",
        store=True,
    )

    @api.depends(
        "stock_move_ids", "stock_move_ids.state", "stock_move_ids.quantity_done"
    )
    def _compute_consume(self):
        for record in self.sudo():
            qty_to_consume = qty_consumed = total_cost = 0.0
            for move in record.stock_move_ids:
                if move.state in ["done"]:
                    qty_consumed += move.quantity_done
                for svl in move.stock_valuation_layer_ids.filtered(
                    lambda r: r.quantity != 0.0
                ):
                    total_cost += abs(svl.value)
            qty_to_consume = record.quantity - qty_consumed
            record.qty_to_consume = qty_to_consume
            record.qty_consumed = qty_consumed
            record.total_cost = total_cost

    def _create_rm_procurement(self):
        self.ensure_one()
        group = self.acceptance_id.procurement_group_id
        qty = self.qty_to_consume
        values = self._get_rm_procurement_data()
        procurements = []
        try:
            procurement = group.Procurement(
                self.product_id,
                qty,
                self.uom_id,
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

    def _get_rm_procurement_data(self):
        self.ensure_one()
        group = self.acceptance_id.procurement_group_id
        origin = self.acceptance_id.name
        warehouse = self.acceptance_id.warehouse_id
        criteria = [
            ("usage", "=", "production"),
            ("warehouse_id", "=", warehouse.id),
        ]
        locations = self.env["stock.location"].search(criteria, limit=1)
        if not locations:
            raise UserError(
                _("Please set the Production Location for the Warehouse %s")
                % (warehouse.name)
            )
        location = locations[0]
        route = self.acceptance_id.raw_material_route_id
        result = {
            "name": origin,
            "group_id": group,
            "origin": origin,
            "warehouse_id": warehouse,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.qty_to_consume,
            "partner_id": self.acceptance_id.partner_id.id,
            "product_uom": self.product_id.uom_id.id,
            "location_id": location,
            "route_ids": route,
            "customer_supplied_raw_material_ids": [(4, self.id)],
        }
        return result
