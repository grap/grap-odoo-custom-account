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

    def _filtered_supplier_moves(self):
        return self.filtered(lambda x: x.move_type in ["in_invoice", "in_refund"])

    def action_move_verify(self):
        draft_supplier_move = self._filtered_supplier_moves().filtered(
            lambda x: x.state == "draft"
        )
        if draft_supplier_move:
            draft_supplier_move._check_supplier_information()
            draft_supplier_move.write({"state": "verified"})

    def action_post(self):
        supplier_move = self._filtered_supplier_moves()

        if supplier_move:
            # Check access right
            supplier_move._check_supplier_validation_access()
            # Check fields
            supplier_move._check_supplier_information()

            # Reset to draft verified moves to avoid error in super
            # of action_move_open
            verified_move = supplier_move.filtered(
                lambda x: x.state == "verified"
            ).with_context(tracking_disable=True)
            verified_move.write({"state": "draft"})

        res = super().action_post()

        if len(self) == 1:
            self.env.user.notify_info(
                message=_("New Account Move: %(name)s") % {"name": self.name}
            )
        else:
            self.env.user.notify_info(
                message=_("%(move_qty)s New Account Moves: %(names)s")
                % {"names": ",".join(self.mapped("name")), "move_qty": len(self)}
            )

        return res

    def button_draft(self):
        supplier_move = self._filtered_supplier_moves()
        verified_moves = supplier_move.filtered(lambda x: x.state == "verified")
        if verified_moves:
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
        self.ensure_one()
        message = []
        if "expense_sheet_id" in self._fields and self.expense_sheet_id:
            # Do not check fields, if the account move
            # come from hr_expense
            return
        if not self.invoice_date:
            message.append(_("Bill Date"))
        if not self.invoice_date_due:
            message.append(_("Due Date"))
        if not self.supplier_invoice_number:
            message.append(_("Vendor Invoice Number"))
        if message:
            raise UserError(
                _(
                    "Verify a supplier move requires to set the"
                    " following fields :\n\n - %(message)s"
                )
                % {"message": ("\n - ".join(message))}
            )
