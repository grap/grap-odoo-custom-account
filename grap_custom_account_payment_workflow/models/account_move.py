# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_payment_checked = fields.Boolean(
        string="Payment Checked", default=True,
        help="Uncheck this box if you want to mark this move to be"
        " checked manually with the bank statement")

    journal_type = fields.Selection(
        related="journal_id.type")
