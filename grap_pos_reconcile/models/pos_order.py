# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def _reconcile_payments(self):
        return True
