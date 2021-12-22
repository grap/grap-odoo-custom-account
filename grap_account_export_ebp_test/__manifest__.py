# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GRAP - Export accounting moves to EBP - Test",
    "version": "12.0.1.0.4",
    "author": "GRAP",
    "category": "GRAP - Custom",
    "license": "AGPL-3",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "depends": ["grap_account_export_ebp", "l10n_generic_coa"],
    "demo": [
        "demo/res_partner.xml",
        "demo/account_account.xml",
        "demo/account_tax.xml",
        "demo/account_move.xml",
        "demo/account_fiscal_year.xml",
        "demo/account_journal.xml",
    ],
    "installable": True,
}
