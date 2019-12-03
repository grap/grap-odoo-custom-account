# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GRAP - Export accounting moves to EBP",
    "version": "12.0.1.0.0",
    "author": "GRAP",
    "category": "GRAP - Custom",
    "license": "AGPL-3",
    "depends": ["account", "account_menu", "account_fiscal_year", "res_company_code"],
    "external_dependencies": {"python": ["unidecode"]},
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/menu.xml",
        "wizard/view_wizard_res_partner_add_suffix.xml",
        "wizard/view_wizard_ebp_export.xml",
        # "wizard/view_wizard_ebp_unexport.xml",
        "views/view_account_account.xml",
        "views/view_account_journal.xml",
        "views/view_account_move.xml",
        # "views/view_account_tax_code.xml",  # TO CHANGE
        "views/view_ebp_export.xml",
        "views/view_res_partner.xml",
        "views/view_res_company.xml",
    ],
    "demo": [
        "demo/res_groups.xml",
        "demo/account_journal.xml",
        "demo/account_account.xml",
        # "demo/account_move.xml",
    ],
    "installable": True,
}
