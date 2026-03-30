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

    journal_type = fields.Selection(string="Journal Type", related="journal_id.type")

    @api.depends("move_id.is_payment_checked")
    def _compute_bank_is_checked(self):
        for payment in self:
            payment.is_checked = payment.move_id.is_payment_checked

    def _inverse_bank_is_checked(self):
        for payment in self.filtered(
            lambda x: x.payment_type != "transfer" and x.state != "draft"
        ):
            payment.move_id.write({"is_payment_checked": payment.is_checked})

    def action_post(self):
        res = super().action_post()
        for payment in self:
            if (
                payment.payment_type in ["outbound", "inbound"]
                and payment.journal_id.type == "bank"
                and not self.env.user.has_group("account.group_account_manager")
            ):
                payment.move_id.write({"is_payment_checked": False})
        return res
