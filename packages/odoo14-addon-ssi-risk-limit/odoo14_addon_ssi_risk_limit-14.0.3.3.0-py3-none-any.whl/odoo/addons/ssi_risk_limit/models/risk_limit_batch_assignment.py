# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import ceil

from odoo import _, api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class RiskLimitBatchAssignment(models.Model):
    _name = "risk_limit_batch_assignment"
    _description = "Risk Limit Batch Assignment"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_open",
        "mixin.transaction_confirm",
        "mixin.many2one_configurator",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_open_policy_fields = False
    _automatically_insert_open_button = False

    _statusbar_visible_label = "draft,confirm,open"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "open_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "open"

    date = fields.Date(
        string="Date",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="risk_limit_type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    allowed_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Allowed Partners",
        compute="_compute_allowed_partner_ids",
        store=False,
        compute_sudo=True,
    )
    partner_ids = fields.Many2many(
        string="Partners",
        comodel_name="res.partner",
        relation="rel_risk_limit_batch_assignment_2_partner",
        column1="batch_assignment_id",
        columne2="partner_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    risk_limit_assignment_ids = fields.One2many(
        string="Risk Limit Assignments",
        comodel_name="risk_limit_assignment",
        inverse_name="batch_id",
        readonly=True,
    )

    # queue
    queue_job_batch_id = fields.Many2one(
        string="Queue Job Batch",
        comodel_name="queue.job.batch",
        readonly=True,
        copy=False,
    )

    queue_job_ids = fields.One2many(
        string="Queue Jobs",
        comodel_name="queue.job",
        related="queue_job_batch_id.job_ids",
        store=False,
    )
    queue_job_batch_state = fields.Selection(
        string="Queue Job Batch State",
        related="queue_job_batch_id.state",
        store=True,
    )

    @api.depends("type_id")
    def _compute_allowed_partner_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.partner",
                    method_selection=record.type_id.partner_selection_method,
                    manual_recordset=record.type_id.partner_ids,
                    domain=record.type_id.partner_domain,
                    python_code=record.type_id.partner_python_code,
                )
            record.allowed_partner_ids = result

    def action_load_partner(self):
        for record in self.sudo():
            record._load_partner()

    def action_confirm_assignment(self):
        for record in self.sudo():
            record._confirm_assignment()

    def action_start_assignment(self):
        for record in self.sudo():
            record._start_assignment()

    def action_approve_assignment(self):
        for record in self.sudo():
            record._approve_assignment()

    def action_reject_assignment(self):
        for record in self.sudo():
            record._reject_assignment()

    def action_cancel_assignment(self):
        for record in self.sudo():
            record._cancel_assignment()

    def action_restart_assignment(self):
        for record in self.sudo():
            record._restart_assignment()

    def action_finish_assignment(self):
        for record in self.sudo():
            result = record._finish_assignment()
        return result

    def _open_assignment(self):
        self.ensure_one()
        action = self.env.ref("ssi_risk_limit.risk_limit_assignment_action").read()[0]
        action["domain"] = [("batch_id", "=", self.id)]
        return action

    def _create_job_batch(self, batch_name):
        self.ensure_one()
        batch = self.env["queue.job.batch"].get_new_batch(batch_name)
        self.write(
            {
                "queue_job_batch_id": batch.id,
            }
        )

    def _process_risk_limit_assignment(
        self,
        action_method,
        state_filter,
        batch_action_name,
        split_action_name,
        state_condition=None,
    ):
        self.ensure_one()
        batch_name = f"{batch_action_name} batch risk limit assignment ID {self.id}"
        self._create_job_batch(batch_name)
        data_per_split = 100
        if state_condition:
            effected_assigments = self.risk_limit_assignment_ids.filtered(
                state_condition
            )
        else:
            effected_assigments = self.risk_limit_assignment_ids.filtered(
                lambda r: r.state == state_filter
            )
        num_split = ceil(len(effected_assigments) / data_per_split)
        for split_number in range(1, num_split + 1):
            assignments = effected_assigments[
                (data_per_split * split_number)
                - data_per_split : split_number * data_per_split
            ]
            description = f"{split_action_name} batch {self.id}"
            description += f" split {split_number}"
            getattr(
                assignments.with_context(job_batch=self.queue_job_batch_id).with_delay(
                    description=_(description)
                ),
                action_method,
            )()
            self.queue_job_batch_id.enqueue()

    def _confirm_assignment(self):
        self._process_risk_limit_assignment(
            action_method="action_confirm",
            state_filter="draft",
            batch_action_name="Confirm",
            split_action_name="Confirm",
        )

    def _finish_assignment(self):
        self._process_risk_limit_assignment(
            action_method="action_done",
            state_filter="open",
            batch_action_name="Finish",
            split_action_name="Finish",
        )

    def _approve_assignment(self):
        self._process_risk_limit_assignment(
            action_method="action_approve_approval",
            state_filter="confirm",
            batch_action_name="Approve",
            split_action_name="Approve",
        )

    def _reject_assignment(self):
        self._process_risk_limit_assignment(
            action_method="action_reject_approval",
            state_filter="confirm",
            batch_action_name="Reject",
            split_action_name="Reject",
        )

    def _cancel_assignment(self):
        self._process_risk_limit_assignment(
            action_method="action_cancel",
            state_filter=None,
            batch_action_name="Cancel",
            split_action_name="Cancel",
            state_condition=lambda r: r.state != "cancel",
        )

    def _restart_assignment(self):
        self._process_risk_limit_assignment(
            action_method="action_restart",
            state_filter="cancel",
            batch_action_name="Restart",
            split_action_name="Restart",
        )

    def _load_partner(self):
        self.ensure_one()
        self.write({"partner_ids": [(6, 0, self.allowed_partner_ids.ids)]})

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "done_ok",
            "open_ok",
            "cancel_ok",
            "reject_ok",
            "restart_ok",
            "restart_approval_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.post_approve_action()
    def _01_create_assignment(self):
        self.ensure_one()
        RiskLimit = self.env["risk_limit_assignment"]
        for partner in self.partner_ids:
            RiskLimit.create(
                {
                    "type_id": self.type_id.id,
                    "date": self.date,
                    "partner_id": partner.id,
                    "batch_id": self.id,
                }
            )

    @ssi_decorator.post_done_action()
    def _01_process_assignment(self):
        self.ensure_one()
        for assignment in self.risk_limit_assignment_ids:
            assignment.action_compute_item()
            assignment.with_context(bypass_policy_check=True).action_confirm()
            assignment.with_context(bypass_policy_check=True).action_open()

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch
