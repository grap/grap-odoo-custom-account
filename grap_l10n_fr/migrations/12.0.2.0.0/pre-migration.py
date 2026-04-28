# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_TAX_MAPPING = {
    "TVA-VT-20.0-HT": "20.0%",
    "TVA-VT-10.0-HT": "10.0%",
    "TVA-VT-05.5-HT": "05.5%",
    "TVA-VT-02.1-HT": "02.1%",
    "TVA-VT-20.0-TTC": "20.0%",
    "TVA-VT-10.0-TTC": "10.0%",
    "TVA-VT-05.5-TTC": "05.5%",
    "TVA-VT-02.1-TTC": "02.1%",
    "10%": "10.0%",
    "20,0%": "20.0%",
    "2.1%": "02.1%",
    "5.5%": "05.5%",
    "0": "0.0%",
    "0%": "0.0%",
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    for old_value, new_value in _TAX_MAPPING.items():
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_tax
            set description = %s where description = %s;
            """,
            (new_value, old_value),
        )
