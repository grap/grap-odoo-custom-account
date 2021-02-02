# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_checked = fields.Boolean(
        string="Checked",
        compute="_compute_bank_is_checked",
        inverse="_inverse_bank_is_checked",
        store=True,
    )

    @api.depends("move_line_ids.move_id.is_payment_checked")
    def _compute_bank_is_checked(self):
        for payment in self:
            payment.is_checked = any(
                payment.mapped("move_line_ids.move_id.is_payment_checked")
            )

    def _inverse_bank_is_checked(self):
        for payment in self.filtered(
            lambda x: x.payment_type != "transfer" and x.state != "draft"
        ):
            payment.mapped("move_line_ids.move_id").write(
                {"is_payment_checked": payment.is_checked}
            )

    def post(self):
        res = super().post()
        for payment in self:
            if (
                payment.payment_type in ["outbound", "inbound"]
                and payment.journal_id.type == "bank"
                and not payment.journal_id.journal_user
                and not self.env.user.has_group("account.group_account_manager")
            ):
                payment.mapped("move_line_ids.move_id").write(
                    {"is_payment_checked": False}
                )
        return res
