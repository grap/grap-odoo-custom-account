# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    export_suffix_on_tax_required = fields.Boolean(
        string="Export according to Taxes",
        help="If checked, when you export moves from this account,"
        " it will create one account for each Tax Code",
    )

    export_suffix_on_tax_default = fields.Char(
        string="Tax Suffix if undefined",
        help="When exporting Entries, this suffix will be"
        " appended to the Account Number to make it a new Account,"
        " if 'Export according to Taxes' is checked, and"
        " if no taxes is defined on the account move line.",
    )
