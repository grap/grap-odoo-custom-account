# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Point Of Sale - Change Sale Move Lines - Test",
    "version": "12.0.1.0.2",
    "category": "Point Of Sale",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "summary": "Test the module grap_pos_change_sale_move",
    "depends": ["grap_pos_change_sale_move", "l10n_generic_coa"],
    "license": "AGPL-3",
    "demo": [
        "demo/account_account.xml",
        "demo/account_tax.xml",
        "demo/product_product.xml",
    ],
    "installable": True,
}
