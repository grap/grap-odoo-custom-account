# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openupgradelib import openupgrade

logger = logging.getLogger(__name__)

column_renames = {
    "ebp.export": [
        ("data_moves", None),
        ("data_accounts", None),
        ("data_balance", None),
    ]
}


@openupgrade.migrate(no_version=True, use_env=True)
def migrate(cr, version):
    logger.info("[grap_account_export_ebp] Preserve data fields ...")
    openupgrade.rename_columns(cr, column_renames)
