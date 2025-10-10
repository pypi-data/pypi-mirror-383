# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerDefaultRiskLimitDetail(models.Model):
    _name = "res_partner.default_risk_limit_detail"
    _description = "Partner - Default Risk Limit Detail"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
    )
    detail_id = fields.Many2one(
        string="Risk Limit Type - Item",
        comodel_name="risk_limit_type.item",
        required=True,
    )
    item_id = fields.Many2one(
        string="Item",
        comodel_name="risk_limit_item",
        related="detail_id.item_id",
        store=False,
    )
    restrict_single = fields.Boolean(
        string="Restrict Single Risk",
        default=False,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
    )
    amount = fields.Monetary(
        string="Amount",
        required=True,
        currency_field="currency_id",
    )
