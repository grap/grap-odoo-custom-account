# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # in V12, it was only 'EBP' export
    openupgrade.logged_query(env.cr, "UPDATE account_export SET export_type = 'ebp';")
    # In V12, it was .csv file
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_export
            SET file_name = substring(file_name, 0, length(file_name) - 4) || '.csv'
            WHERE file_name ilike '%.xlsx';
        """,
    )
