# Copyright (C) 2013 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # We overwrite all selections to have the state in the correct
    # order.
    # TODO V13: replace by
    # selection_add=[("verified", "Verified"), ("draft", )]
    # ref: https://github.com/odoo/odoo/blob/13.0/odoo/fields.py
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("verified", "Verified"),
            ("open", "Open"),
            ("in_payment", "In Payment"),
            ("paid", "Paid"),
            ("cancel", "Cancelled"),
        ]
    )

    def action_invoice_verify(self):
        self._check_supplier_information()
        draft_invoices = self.filtered(lambda x: x.state == "draft")
        if draft_invoices:
            draft_invoices.write({"state": "verified"})
        return True

    def action_invoice_open(self):
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

        return super().action_invoice_open()

    def action_invoice_draft(self):
        verified_invoices = self.filtered(lambda x: x.state == "verified")
        verified_invoices.write({"state": "draft"})
        cancel_invoices = self - verified_invoices
        return super(AccountInvoice, cancel_invoices).action_invoice_draft()

    def _check_supplier_validation_access(self):
        if not self.env.user.has_group(
            "account.group_account_manager"
        ) and not self.env.context.get("intercompany_trade_create", False):
            raise UserError(
                _(
                    "You can not confirm supplier invoices because you're not"
                    "a member of the group"
                    "'Accounting & Finance / Billing Manager'"
                )
            )

    def _check_supplier_information(self):
        for invoice in self:
            # Ugly patch
            # "l10n_generic_coa" is autoinstalled, in demo mode
            # and the actions are loosing context, so it's not possible
            # to know if we are installing demo data from l10n_generic_coa
            # that will raise an error, because they don't have correct
            # values for the 3 checked fields
            if invoice.get_xml_id()[invoice.id].startswith("l10n_generic_coa"):
                continue
            message = []
            if not invoice.date_invoice:
                message.append(_("Invoice Date"))
            if not invoice.date_due:
                message.append(_("Due Date"))
            if not invoice.supplier_invoice_number:
                message.append(_("Supplier Invoice Number"))
            if message:
                raise UserError(
                    _(
                        "Verify a supplier invoice requires to set the"
                        " following fields :\n\n - %s" % ("\n - ".join(message))
                    )
                )
