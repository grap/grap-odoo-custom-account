# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # res_partner.ebp_suffix (grap_account_export_ebp )
    # has been renamed into
    # res_partner.accounting_export_code (grap_account_export_partner_code)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner set accounting_export_code = ebp_suffix;
        """,
    )
