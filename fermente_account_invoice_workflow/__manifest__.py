# Copyright (C) 2013-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien WESTE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Fermente - Custom Invoice workflow",
    "version": "16.0.2.0.0",
    "category": "Custom",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "license": "AGPL-3",
    "depends": [
        # OCA
        "account_invoice_supplier_ref_unique",
        "web_notify",
    ],
    "data": ["views/view_account_move.xml"],
    "installable": True,
}
