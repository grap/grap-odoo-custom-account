# Copyright (C) 2020-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GRAP - Custom Payment Workflow",
    "summary": "Add Payment Check workflow",
    "version": "12.0.1.0.4",
    "category": "Custom",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "license": "AGPL-3",
    "depends": ["account", "point_of_sale"],
    "data": ["views/view_account_move.xml", "views/view_account_payment.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_populate_data",
}
