# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAccount(models.Model):
    _inherit = "account.account"

    export_suffix_on_tax_required = fields.Boolean(
        string="Export according to Taxes",
        tracking=200,
        help="If checked, when you export moves from this account,"
        " it will create one account for each Tax Code",
    )

    export_suffix_on_tax_default = fields.Char(
        string="Tax Suffix if undefined",
        tracking=201,
        help="When exporting Entries, this suffix will be"
        " appended to the Account Number to make it a new Account,"
        " if 'Export according to Taxes' is checked, and"
        " if no taxes is defined on the account move line.",
    )

    export_code_emulation = fields.Char(compute="_compute_export_code_emulation")

    export_code_emulation_tooltip = fields.Char(
        compute="_compute_export_code_emulation"
    )

    export_code_emulation_error = fields.Char(compute="_compute_export_code_emulation")

    @api.depends(
        "account_type",
        "company_id.fiscal_type",
        "export_suffix_on_tax_required",
        "export_suffix_on_tax_default",
    )
    def _compute_export_code_emulation(self):
        for account in self:
            code, message = account._get_account_code(False)
            account.export_code_emulation = code
            account.export_code_emulation_error = message
            account.export_code_emulation_tooltip = "BOB"

    def _get_account_code(self, line):
        self.ensure_one()

        # Base Account Code
        result = self.code

        if self.account_type in ["asset_receivable", "liability_payable"]:
            # Company Suffix
            if line and line.company_id.fiscal_type in ["fiscal_child"]:
                result += self.company_id.code
            elif self.company_id.fiscal_type in ["fiscal_child", "fiscal_mother"]:
                result += "YYY"

            # Partner Suffix
            if line and line.partner_id:
                result += line.partner_id.export_suffix
            else:
                result += "AAAA"

        # Tax Suffix
        if self.export_suffix_on_tax_required:
            if line:
                if line.tax_ids:
                    if line.tax_ids[0].export_suffix:
                        # Tax code is defined
                        result += line.tax_ids[0].export_suffix
                    else:
                        # Incorrect Tax setting
                        raise ValidationError(
                            _(
                                "The account %(account_code)s - %(account_name)s"
                                " is set 'export with tax"
                                " suffix' but no tax suffix is defined for"
                                " the tax %(tax_name)s.\n Move %(move_name)s",
                                account_code=self.code,
                                account_name=self.name,
                                tax_name=line.tax_ids[0].name,
                                move_name=line.move_id.name,
                            )
                        )
                elif self.export_suffix_on_tax_default:
                    # Default Tax Code is defined
                    result += self.export_suffix_on_tax_default
                else:
                    # Incorrect account setting
                    raise ValidationError(
                        _(
                            "The account %(account_code)s - %(account_name)s"
                            " is set 'export with tax"
                            " suffix' but no default code is defined on"
                            " the account.\n Move %(move_name)s",
                            account_code=self.code,
                            account_name=self.name,
                            move_name=line.move_id.name,
                        )
                    )
            elif self.export_suffix_on_tax_default:
                result += "T"

        Config = self.env["ir.config_parameter"].sudo()
        max_size = int(
            Config.get_param(
                "fermente_account_export.parameter_max_size_account_code", 10
            )
        )

        message_error = False
        if len(result) > max_size:
            message_error = _(
                "Account code '%(account_code)s' is too long to be exported"
                " to the accounting software. The maximum length is %(max_size)s.",
                account_code=result,
                max_size=max_size,
            )

            if line:
                raise ValidationError(message_error)

        if line:
            return result

        return result, message_error
