# Copyright (C) 2013-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien WESTE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GRAP - Custom Invoice workflow",
    "version": "12.0.1.0.7",
    "category": "Custom",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "license": "AGPL-3",
    "depends": [
        # OCA
        "account_invoice_supplier_ref_unique",
        "web_notify",
        # GRAP
        "intercompany_trade_account",
    ],
    "data": ["views/view_account_invoice.xml"],
    "demo": ["demo/res_groups.xml"],
    "installable": True,
}
