# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    # res.partner
    ("res.partner", "res_partner", "accounting_export_code", "export_suffix"),
    # account.journal
    ("account.journal", "account_journal", "ebp_code", "export_code"),
    # account.move
    ("account.move", "account_move", "ebp_export_id", "account_export_id"),
    # account.tax
    ("account.tax", "account_tax", "ebp_suffix", "export_suffix"),
    ("account.tax", "account_tax", "has_ebp_suffix_required", "export_suffix_required"),
    # account.tax.template
    ("account.tax.template", "account_tax_template", "ebp_suffix", "export_suffix"),
    # account.account
    (
        "account.account",
        "account_account",
        "ebp_export_tax",
        "export_suffix_on_tax_required",
    ),
    (
        "account.account",
        "account_account",
        "ebp_code_no_tax",
        "export_suffix_on_tax_default",
    ),
    # account.account.template
    (
        "account.account.template",
        "account_account_template",
        "ebp_export_tax",
        "export_suffix_on_tax_required",
    ),
    (
        "account.account.template",
        "account_account_template",
        "ebp_code_no_tax",
        "export_suffix_on_tax_default",
    ),
    # account.export
    (
        "account.export",
        "account_export",
        "date",
        "export_date",
    ),
    (
        "account.export",
        "account_export",
        "data_moves",
        "data",
    ),
    (
        "account.export",
        "account_export",
        "file_name_moves",
        "file_name",
    ),
]


_model_renames = [
    ("ebp.export", "account.export"),
]

_table_renames = [
    ("ebp_export", "account_export"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    # force to recompute name with new syntax
    openupgrade.logged_query(env.cr, "alter table account_export drop column name;")
