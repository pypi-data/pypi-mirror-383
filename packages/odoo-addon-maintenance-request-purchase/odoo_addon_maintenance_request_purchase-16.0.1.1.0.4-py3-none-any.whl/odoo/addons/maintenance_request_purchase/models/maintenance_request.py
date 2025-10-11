# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaintenanceRequest(models.Model):

    _inherit = "maintenance.request"

    purchase_order_ids = fields.Many2many(
        "purchase.order",
        "maintenance_purchase_order",
        "maintenance_request_id",
        "purchase_order_id",
        groups="purchase.group_purchase_user",
        string="Purchase Orders",
        copy=False,
    )
    purchases_count = fields.Integer(
        compute="_compute_purchases_count",
        store=True,
        groups="purchase.group_purchase_user",
    )

    total_purchase_amount = fields.Monetary(
        compute="_compute_total_purchase_amount",
        store=True,
        groups="purchase.group_purchase_user",
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        related="company_id.currency_id",
        store=True,
        readonly=True,
    )

    @api.depends(
        "purchase_order_ids.amount_total",
        "purchase_order_ids.currency_id",
        "company_id.currency_id",
        "purchase_order_ids.state",
    )
    def _compute_total_purchase_amount(self):
        date = self.env.context.get("actual_date") or fields.Date.today()
        for record in self:
            company_currency = record.company_id.currency_id
            total = sum(
                po.currency_id._convert(
                    po.amount_total,
                    company_currency,
                    record.company_id,
                    date,
                )
                for po in record.purchase_order_ids.filtered(
                    lambda po: po.state in ("purchase", "done")
                )
            )
            record.total_purchase_amount = total

    @api.depends("purchase_order_ids")
    def _compute_purchases_count(self):
        for record in self:
            record.purchases_count = len(record.purchase_order_ids.ids)
