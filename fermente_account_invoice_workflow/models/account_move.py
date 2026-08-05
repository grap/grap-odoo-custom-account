# Copyright (C) 2013 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_verified = fields.Boolean(string="Verified Move", tracking=True, copy=False)

    is_verified_toggle = fields.Boolean(
        compute="_compute_is_verified_toggle",
        inverse="_inverse_is_verified_toggle",
        help="Technical field, used to have a single toggle button in tree view"
        " to mark supplier invoices as verified, instead of two columns"
        " for 'action_move_verify' / 'action_move_unverify' buttons.",
    )

    @api.depends("is_verified")
    def _compute_is_verified_toggle(self):
        for move in self:
            move.is_verified_toggle = move.is_verified

    def _inverse_is_verified_toggle(self):
        self.filtered(lambda x: x.is_verified_toggle).action_move_verify()
        self.filtered(lambda x: not x.is_verified_toggle).action_move_unverify()

    def action_move_verify(self):
        draft_supplier_moves = self._filtered_supplier_moves(
            only_draft=True, only_unverified=True
        )
        draft_supplier_moves._check_before_mark_as_verified()
        draft_supplier_moves.write({"is_verified": True})

    def action_move_unverify(self):
        draft_supplier_moves = self._filtered_supplier_moves(
            only_draft=True, only_verified=True
        )
        draft_supplier_moves.write({"is_verified": False})

    def button_draft(self):
        verified_moves = self._filtered_supplier_moves(only_verified=True)
        verified_moves.write({"is_verified": False})
        return super().button_draft()

    def _filtered_supplier_moves(
        self,
        only_draft=False,
        only_posted=False,
        only_verified=False,
        only_unverified=False,
    ):
        result = self.filtered(lambda x: x.move_type in ["in_invoice", "in_refund"])
        if only_draft:
            result = result.filtered(lambda x: x.state == "draft")
        if only_posted:
            result = result.filtered(lambda x: x.state == "posted")
        if only_unverified:
            result = result.filtered(lambda x: not x.is_verified)
        if only_verified:
            result = result.filtered(lambda x: x.is_verified)
        return result

    def _post(self, *args, **kwargs):
        supplier_moves = self._filtered_supplier_moves(only_draft=True)

        if supplier_moves:
            # Check access right
            supplier_moves._check_supplier_validation_access()
            # Check fields
            supplier_moves._check_before_mark_as_verified()
            # Set is_verified to True
            supplier_moves.filtered(lambda x: not x.is_verified).write(
                {"is_verified": True}
            )

        res = super()._post(*args, **kwargs)

        # Display a message for the user
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

    def _check_supplier_validation_access(self):
        if not self.env.user.has_group("account.group_account_manager"):
            raise UserError(
                _(
                    "You can not confirm supplier moves because you're not "
                    "a member of the group 'Accounting / Accountant'"
                )
            )

    def _check_before_mark_as_verified(self):
        if self.env.context.get("chart_template_create_demo_data"):
            # Prevent to raise an error when demo data are created
            # without all required fields
            return

        for move in self:
            message = []
            if "expense_sheet_id" in self._fields and move.expense_sheet_id:
                # Do not check fields, if the account move
                # come from hr_expense
                return
            if not move.invoice_date:
                message.append(_("Bill Date"))
            if not move.invoice_date_due:
                message.append(_("Due Date"))
            if not move.supplier_invoice_number:
                message.append(_("Vendor Invoice Number"))
            if message:
                raise UserError(
                    _(
                        "Verify a supplier move requires to set the"
                        " following fields :\n\n - %(message)s"
                    )
                    % {"message": ("\n - ".join(message))}
                )
