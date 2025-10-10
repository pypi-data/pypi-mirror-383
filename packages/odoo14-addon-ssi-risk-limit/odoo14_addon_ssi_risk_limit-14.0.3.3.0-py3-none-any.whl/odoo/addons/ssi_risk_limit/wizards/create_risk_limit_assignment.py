# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo import fields, models


class CreateRiskLimitAssignment(models.TransientModel):
    _name = "create_risk_limit_assignment"
    _description = "Create Risk Limit Assignment"

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        relation="create_risk_limit_assignment_res_partner_rel",
        column1="wizard_id",
        column2="partner_id",
        default=lambda self: self._default_partner_ids(),
    )

    def _default_partner_ids(self):
        # Default to active_id or active_ids from context
        active_ids = self.env.context.get("active_ids", [])
        return self.env["res.partner"].browse(active_ids)

    def action_confirm(self):
        for record in self.sudo():
            result = record._confirm()
        return result

    def _confirm(self):
        # Create partner evaluation for each type
        RiskLimitAssignment = self.env["risk_limit_assignment"]
        RiskLimitType = self.env["risk_limit_type"]
        risk_limit_assignment_ids = []
        for partner in self.partner_ids:
            for risk_limit_type in RiskLimitType.search([]):
                data = {
                    "date": date.today(),
                    "type_id": risk_limit_type.id,
                }
                temp_risk_limit_assignment = RiskLimitAssignment.new(data)
                if partner.id in temp_risk_limit_assignment.allowed_partner_ids.ids:
                    data.update(
                        {
                            "partner_id": partner.id,
                        }
                    )
                    risk_limit_assignment = RiskLimitAssignment.create(data)
                    risk_limit_assignment.action_compute_item()
                    risk_limit_assignment_ids.append(risk_limit_assignment.id)
                    break
        # Open the created evaluations
        return {
            "name": "Risk Limit Assignments",
            "type": "ir.actions.act_window",
            "res_model": "risk_limit_assignment",
            "view_mode": "tree,form",
            "domain": [("id", "in", risk_limit_assignment_ids)],
        }
