# Copyright (C) 2021 - Today: Coop IT Easy (http://coopiteasy.be)
# @author: Rémy TAYMANS (remy@coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # Set default configuration for pos.config to not change de previous
    # behaviour of this module
    query = "UPDATE pos_config SET sale_move_policy = 'groupby_account_tax';"
    cr.execute(query)
