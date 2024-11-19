# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Fermente - Account Export",
    "summary": "Add a placeholder menu for Accounting Export",
    "version": "16.0.1.0.0",
    "category": "Fermente Custom",
    "license": "AGPL-3",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "depends": [
        # Odoo
        "account",
        # OCA
        "account_fiscal_year",
        # GRAP
        "fiscal_company_base",
        # "intercompany_trade_base",
        # "intercompany_trade_fiscal_company",
    ],
    "external_dependencies": {"python": ["unidecode"]},
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/view_res_partner.xml",
        "wizards/view_wizard_res_partner_add_export_code.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "installable": True,
}
