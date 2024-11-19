# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountAccountTemplate(models.Model):
    _inherit = "account.account.template"

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
