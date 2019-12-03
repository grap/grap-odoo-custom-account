# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class AccountAccount(models.Model):
    _inherit = "account.account"

    ebp_analytic_mode = fields.Selection(
        selection_add=[("fiscal_analytic", "Fiscal analytic")]
    )

    # Compute Section
    @api.depends("company_id", "user_type_id")
    def _compute_ebp_analytic_mode(self):
        for account in self:
            if account.company_id.fiscal_company.fiscal_type == "fiscal_mother":
                account.ebp_analytic_mode = "fiscal_analytic"
            else:
                account.ebp_analytic_mode = account._compute_ebp_analytic_mode()

    # Constraints section
    @api.constrains(
        "code", "type", "company_id.fiscal_type", "is_intercompany_trade_fiscal_company"
    )
    def _constrains_code_length(self):
        for account in self:
            if account.company_id.fiscal_type == "fiscal_mother":
                if (
                    account.is_intercompany_trade_fiscal_company
                    and len(account.code) > 6
                ):
                    raise UserError(
                        _(
                            "The account code for a partner account cannot"
                            " exceed 6 characters for Fiscal Mother Company"
                            " (Intercompany Trade) so as to permit the EBP"
                            " export"
                        )
                    )
                elif (
                    not account.is_intercompany_trade_fiscal_company
                    and account.type in ("receivable", "payable")
                    and len(account.code) > 3
                ):
                    raise UserError(
                        _(
                            "The account code for a partner account cannot"
                            " exceed 3 characters for Fiscal Mother Company"
                            " (Regular Case) so as to permit the EBP"
                            " export"
                        )
                    )
                elif account.company_id.fiscal_type == "normal":
                    if (
                        account.type in ("receivable", "payable")
                        and len(account.code) > 6
                    ):
                        raise UserError(
                            _(
                                "The account code for a partner account cannot"
                                " exceed 6 characters for Normal Company"
                                " so as to permit the EBP export"
                            )
                        )
