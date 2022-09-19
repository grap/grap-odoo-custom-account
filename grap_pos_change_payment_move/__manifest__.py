# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Point Of Sale - Change Payment Move Lines",
    "version": "12.0.1.1.3",
    "category": "Point Of Sale",
    "author": "GRAP",
    "license": "AGPL-3",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "summary": "Make Bank accounting moves from PoS acceptable for accoutants",
    "depends": [
        "point_of_sale",
        # Coop It Easy
        "account_customer_wallet",
    ],
    "demo": ["demo/res_groups.xml", "demo/product_product.xml"],
    "installable": True,
}
