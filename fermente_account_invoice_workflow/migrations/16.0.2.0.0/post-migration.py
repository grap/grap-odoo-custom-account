# Copyright (C) 2026-Today: GRAP (http://www.grap.coop)
# @author: Quentin DUPONT
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # State replaced by Boolean
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
            SET is_verified = True, state = 'draft'
            WHERE state = 'verified';
        """,
    )
