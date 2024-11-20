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
    "depends": ["account"],
    "external_dependencies": {"python": ["unidecode"]},
    "data": [
        "views/menu.xml",
        "views/view_res_partner.xml",
        "wizards/view_wizard_res_partner_add_export_code.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "installable": True,
}
