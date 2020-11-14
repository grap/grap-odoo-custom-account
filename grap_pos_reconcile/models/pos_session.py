# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.multi
    def action_pos_session_close(self):
        AccountMove = self.env["account.move"]
        res = False
        for session in self:
            res = super(PosSession, session).action_pos_session_close()
            # Get Receivable move lines
            moves = AccountMove.search([("ref", "=", session.name)])
            all_aml = moves.mapped("line_ids") | session.mapped(
                "order_ids.invoice_id.move_id.line_ids"
            )
            all_aml = all_aml.filtered(
                lambda r: not r.reconciled
                and r.account_id.internal_type == "receivable"
            )
            # Reconcile per partner
            for partner in all_aml.mapped("partner_id"):
                to_reconcile = self.env["account.move.line"]
                for aml in all_aml:
                    if aml.partner_id.id == partner.id:
                        to_reconcile = to_reconcile | aml
                to_reconcile.reconcile()
            # reconcile finaly, lines without partners
            all_aml.filtered(lambda x: not x.partner_id).reconcile()
        return res
