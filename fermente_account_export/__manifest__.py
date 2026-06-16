# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Fermente - Account Export",
    "summary": "Add a placeholder menu for Accounting Export",
    "version": "16.0.3.0.0",
    "category": "Fermente Custom",
    "license": "AGPL-3",
    "author": "GRAP",
    "website": "https://github.com/grap/grap-odoo-custom-account",
    "depends": [
        # Odoo
        "account",
        "mail",
        # OCA
        "account_fiscal_year",
        "report_xlsx",
        "res_company_code",
        "account_usability",
        # GRAP
        "fiscal_company_base",
    ],
    "external_dependencies": {"python": ["unidecode", "openupgradelib"]},
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "views/menu.xml",
        "views/view_account_account.xml",
        "views/view_account_account_template.xml",
        "views/view_account_chart_template.xml",
        "views/view_account_journal.xml",
        "views/view_account_move.xml",
        "views/view_account_tax.xml",
        "views/view_account_tax_template.xml",
        "views/view_account_export.xml",
        "views/view_res_partner.xml",
        "wizards/view_wizard_res_partner_add_export_code.xml",
        "wizards/view_wizard_account_export.xml",
        "wizards/view_res_config_settings.xml",
        "reports/report_account_export_xlsx.xml",
    ],
    "demo": [
        "demo/res_partner.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
