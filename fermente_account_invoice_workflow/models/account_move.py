# Copyright (C) 2013 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[
            ("verified", "Verified"),
            ("posted",),
        ],
        ondelete={
            "verified": "set default",
        },
    )

    def action_move_verify(self):
        self.ensure_one()
        self._check_supplier_information()
        draft_moves = self.filtered(lambda x: x.state == "draft")
        if draft_moves:
            draft_moves.write({"state": "verified"})
        return True

    def action_post(self):
        purchase_moves = self.filtered(lambda x: x.journal_id.type == "purchase")
        if purchase_moves:
            # Check access right
            purchase_moves._check_supplier_validation_access()
            # Check fields
            purchase_moves._check_supplier_information()

        # Reset to draft verified moves to avoid error in super
        # of action_move_open
        verified_moves = self.filtered(lambda x: x.state == "verified").with_context(
            tracking_disable=True
        )
        verified_moves.write({"state": "draft"})

        res = super().action_post()

        for move in self:
            self.env.user.notify_info(
                message=_("New move Number: %(name)s") % {"name": move.name}
            )

        return res

    def button_draft(self):
        verified_moves = self.filtered(lambda x: x.state == "verified")
        verified_moves.write({"state": "draft"})
        cancel_moves = self - verified_moves
        return super(AccountMove, cancel_moves).button_draft()

    def _check_supplier_validation_access(self):
        if not self.env.user.has_group("account.group_account_manager"):
            raise UserError(
                _(
                    "You can not confirm supplier moves because you're not "
                    "a member of the group 'Accounting / Accountant'"
                )
            )

    def _check_supplier_information(self):
        for move in self:
            message = []
            if not move.move_date:
                message.append(_("Bill Date"))
            if not move.move_date_due:
                message.append(_("Due Date"))
            if not move.supplier_move_number:
                message.append(_("Vendor move Number"))
            if message:
                raise UserError(
                    _(
                        "Verify a supplier move requires to set the"
                        " following fields :\n\n - %(message)s"
                    )
                    % {"message": ("\n - ".join(message))}
                )
