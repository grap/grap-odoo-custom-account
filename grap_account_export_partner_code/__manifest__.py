# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GRAP - Account Export - Partner Code",
    "summary": "Add an account export code field on partner model",
    "version": "12.0.1.0.2",
    "category": "GRAP Custom",
    "license": "AGPL-3",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "depends": [
        # GRAP
        "grap_account_export",
    ],
    "external_dependencies": {"python": ["unidecode"]},
    "data": [
        "views/view_res_partner.xml",
        "wizards/view_wizard_res_partner_add_export_code.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "installable": True,
}
