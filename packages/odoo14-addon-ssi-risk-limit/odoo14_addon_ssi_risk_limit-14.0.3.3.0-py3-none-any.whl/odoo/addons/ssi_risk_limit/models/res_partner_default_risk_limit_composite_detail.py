# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartnerDefaultRiskLimitCompositeDetail(models.Model):
    _name = "res_partner.default_risk_limit_composite_detail"
    _description = "Partner - Risk Limit Composite Detail"

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="cascade",
    )
    composite_detail_id = fields.Many2one(
        string="Risk Limit - Composite Item",
        comodel_name="risk_limit_type.composite_item",
        required=True,
    )
    item_ids = fields.Many2many(
        string="Items",
        comodel_name="risk_limit_item",
        related="composite_detail_id.item_ids",
        store=False,
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
