# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    export_code = fields.Char(
        help="This code will be used when exporting entries in the journal column"
        " Let empty if you don't want to export the accounting moves that are"
        " in this journal.",
    )
