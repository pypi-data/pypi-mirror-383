# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = [
        "res.partner",
    ]

    risk_limit_ids = fields.Many2many(
        string="Risk Limits",
        comodel_name="risk_limit_assignment.detail",
        compute="_compute_risk_limit_ids",
        store=False,
        compute_sudo=True,
    )
    composite_risk_limit_ids = fields.Many2many(
        string="Composite Risk Limits",
        comodel_name="risk_limit_assignment.composite_detail",
        compute="_compute_composite_risk_limit_ids",
        store=False,
        compute_sudo=True,
    )
    risk_limit_assignment_ids = fields.One2many(
        string="Risk Limit Assignments",
        comodel_name="risk_limit_assignment",
        inverse_name="partner_id",
    )
    risk_limit_assignment_id = fields.Many2one(
        string="# Risk Limit Assignments",
        comodel_name="risk_limit_assignment",
        compute="_compute_risk_limit_assignment_id",
        store=True,
        compute_sudo=True,
    )

    # default risk limit
    default_risk_limit_type_id = fields.Many2one(
        string="Default Risk Limit Type",
        comodel_name="risk_limit_type",
    )
    default_risk_limit_detail_ids = fields.One2many(
        string="Default Risk Limit Details",
        comodel_name="res_partner.default_risk_limit_detail",
        inverse_name="partner_id",
    )
    default_risk_limit_composite_detail_ids = fields.One2many(
        string="Default Risk Limit Composite Details",
        comodel_name="res_partner.default_risk_limit_composite_detail",
        inverse_name="partner_id",
    )

    @api.depends(
        "risk_limit_assignment_ids",
        "risk_limit_assignment_ids.partner_id",
        "risk_limit_assignment_ids.state",
    )
    def _compute_risk_limit_assignment_id(self):
        for record in self:
            result = False
            if record.risk_limit_assignment_ids:
                result = record.risk_limit_assignment_ids[-1]
            record.risk_limit_assignment_id = result

    @api.depends(
        "risk_limit_assignment_id",
    )
    def _compute_risk_limit_ids(self):
        for record in self:
            result = []
            if record.risk_limit_assignment_id:
                result = record.risk_limit_assignment_id.detail_ids.ids
            record.risk_limit_ids = result

    @api.depends(
        "risk_limit_assignment_id",
    )
    def _compute_composite_risk_limit_ids(self):
        for record in self:
            result = []
            if record.risk_limit_assignment_id:
                result = record.risk_limit_assignment_id.composite_detail_ids.ids
            record.composite_risk_limit_ids = result

    def action_reload_risk_limit(self):
        for record in self.sudo():
            record._reload_risk_limit()

    def _reload_risk_limit(self):
        self.ensure_one()
        risk_limit_type = self.default_risk_limit_type_id
        self.default_risk_limit_detail_ids.unlink()
        self.default_risk_limit_composite_detail_ids.unlink()
        if risk_limit_type:
            for detail in risk_limit_type.item_ids:
                data = {
                    "detail_id": detail.id,
                    "partner_id": self.id,
                    "currency_id": detail.currency_id.id,
                    "amount": detail.default_amount,
                }
                self.env["res_partner.default_risk_limit_detail"].create(data)
            for composite_detail in risk_limit_type.composite_item_ids:
                data = {
                    "composite_detail_id": composite_detail.id,
                    "partner_id": self.id,
                    "currency_id": composite_detail.currency_id.id,
                    "amount": composite_detail.default_amount,
                }
                self.env["res_partner.default_risk_limit_composite_detail"].create(data)
