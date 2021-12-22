# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Quentin DUPONT <quentin.dupont@grap.coop>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "GRAP - Change l10n_fr",
    "summary": "Custom changes of l10n_fr module for GRAP",
    "version": "12.0.1.1.6",
    "category": "Custom",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "license": "AGPL-3",
    "depends": [
        "l10n_fr",
        "account_fiscal_position_type",
        "account_fiscal_position_usage_group",
        "account_product_fiscal_classification",
    ],
    "data": [
        "data/account_account_template.xml",
        "data/account_chart_template.xml",
        "data/account_fiscal_position_template.xml",
        "data/account_fiscal_position_tax_template.xml",
        "data/account_product_fiscal_classification_template.xml",
        "data/account_tax_template.xml",
        "views/view_account_tax_template.xml",
    ],
    "installable": True,
}
