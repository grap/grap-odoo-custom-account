# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    _EBP_ANALYTIC_MODE_SELECTION = [
        ("no", "No Analytic"),
        ("fiscal_analytic", "Fiscal Analytic"),
        ("normal", "Normal Analytic"),
    ]

    # Columns section
    ebp_export_tax = fields.Boolean(
        string="Export according Taxes",
        help="If checked, when you export moves from this account,"
        " it will create one account for each Tax Code",
    )

    ebp_code_no_tax = fields.Char(
        string="Tax Suffix if undefined",
        help="When exporting Entries to EBP, this suffix will be"
        " appended to the Account Number to make it a new Account,"
        " if 'Export to EBP according to Tax Codes' is checked, and"
        " if no taxes is defined on the account move line.",
    )

    ebp_analytic_mode = fields.Selection(
        string="Analytic Export Mode",
        compute="_compute_ebp_analytic_mode",
        selection=_EBP_ANALYTIC_MODE_SELECTION,
    )

    # Compute Section
    @api.depends("company_id", "user_type_id")
    def _compute_ebp_analytic_mode(self):
        analytic_user_type_ids = [
            self.env.ref("account.data_account_type_expenses").id,
            self.env.ref("account.data_account_type_revenue").id,
        ]
        for account in self:
            if account.company_id.fiscal_type in ["fiscal_child", "fiscal_mother"]:
                # If we are in a CAE, we export "company analytic"
                # for all accounts
                account.ebp_analytic_mode = "fiscal_analytic"
            elif account.company_id.ebp_analytic_enabled:
                # If we are in an normal company, we will export
                # only for expense and revenue account. (classical analytic)
                if account.user_type_id.id in analytic_user_type_ids:
                    account.ebp_analytic_mode = "normal"
                else:
                    account.ebp_analytic_mode = "no"
            else:
                # If we are in an holding (group)
                # we don't have to export account moves
                account.ebp_analytic_mode = "no"
