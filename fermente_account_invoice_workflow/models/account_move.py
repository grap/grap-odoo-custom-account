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

    def action_invoice_verify(self):
        self.ensure_one()
        self._check_supplier_information()
        draft_invoices = self.filtered(lambda x: x.state == "draft")
        if draft_invoices:
            draft_invoices.write({"state": "verified"})
        return True

    def action_post(self):
        purchase_invoices = self.filtered(lambda x: x.journal_id.type == "purchase")
        if purchase_invoices:
            # Check access right
            purchase_invoices._check_supplier_validation_access()
            # Check fields
            purchase_invoices._check_supplier_information()

        # Reset to draft verified invoices to avoid error in super
        # of action_invoice_open
        verified_invoices = self.filtered(lambda x: x.state == "verified").with_context(
            tracking_disable=True
        )
        verified_invoices.write({"state": "draft"})

        res = super().action_post()

        for invoice in self:
            self.env.user.notify_info(
                message=_("New Invoice Number: %(name)s") % {"name": invoice.name}
            )

        return res

    def button_draft(self):
        verified_invoices = self.filtered(lambda x: x.state == "verified")
        verified_invoices.write({"state": "draft"})
        cancel_invoices = self - verified_invoices
        return super(AccountMove, cancel_invoices).button_draft()

    def _check_supplier_validation_access(self):
        if not self.env.user.has_group("account.group_account_manager"):
            raise UserError(
                _(
                    "You can not confirm supplier invoices because you're not "
                    "a member of the group 'Accounting / Accountant'"
                )
            )

    def _check_supplier_information(self):
        for invoice in self:
            message = []
            if not invoice.invoice_date:
                message.append(_("Bill Date"))
            if not invoice.invoice_date_due:
                message.append(_("Due Date"))
            if not invoice.supplier_invoice_number:
                message.append(_("Vendor Invoice Number"))
            if message:
                raise UserError(
                    _(
                        "Verify a supplier invoice requires to set the"
                        " following fields :\n\n - %(message)s"
                    )
                    % {"message": ("\n - ".join(message))}
                )
