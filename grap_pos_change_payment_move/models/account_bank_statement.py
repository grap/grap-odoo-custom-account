# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from odoo import api, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_confirm_bank(self):
        """
        Call normal super function for statement, except for PoS statement,
        that will call button_confirm_bank_pos() function.
        """
        pos_items = self.filtered(lambda x: x.pos_session_id)
        no_pos_items = self.filtered(lambda x: not x.pos_session_id)

        pos_items.button_confirm_bank_pos()
        super(AccountBankStatement, no_pos_items).button_confirm_bank()

    @api.multi
    def button_confirm_bank_pos(self):
        AccountMove = self.env["account.move"]
        AccountBankStatementLine = self.env["account.bank.statement.line"]

        for statement in self.filtered(lambda r: r.state == "open"):
            move_ids = []
            groups = {}
            # parse the lines to group the ids according to the key fields
            for statement_line in statement.line_ids:
                pos_order = statement_line.pos_statement_id

                partner_id = False
                if (
                    # We keep partner information if an invoice has been generated
                    pos_order
                    and pos_order.state == "invoiced"
                ):
                    partner_id = statement_line.partner_id.id
                keys = (
                    statement_line.account_id.id,
                    partner_id,
                    statement_line.date.strftime("%Y-%m-%d"),
                )
                groups.setdefault(keys, [])
                groups[keys].append(statement_line.id)

            # for each group, create account_move and account_move_lines
            i = 0
            for key in groups.keys():
                i += 1
                statement_lines = AccountBankStatementLine.browse(groups[key])
                move = AccountMove.create(self._prepare_pos_move(key, statement_lines))
                move_ids.append(move.id)

            if move_ids:
                moves = AccountMove.browse(move_ids)
                moves.post()

        return self.write(
            {"state": "confirm", "date_done": time.strftime("%Y-%m-%d %H:%M:%S")}
        )

    @api.multi
    def _prepare_pos_move(self, key, statement_lines):
        self.ensure_one()
        (account_id, partner_id, move_date) = key
        lines_vals = []
        lines_vals += self._prepare_pos_bank_move_lines(key, statement_lines)
        lines_vals += self._prepare_pos_counterpart_move_lines(key, statement_lines)
        return {
            "journal_id": self.journal_id.id,
            "date": move_date,
            "ref": self.pos_session_id.name,
            "line_ids": lines_vals,
        }

    @api.multi
    def _prepare_pos_bank_move_lines(self, key, statement_lines):
        self.ensure_one()
        (account_id, partner_id, move_date) = key
        amount = sum(statement_lines.mapped("amount"))

        line_vals = {
            "name": self.name,
            "date": move_date,
            "account_id": account_id,
            "partner_id": partner_id,
            "debit": ((amount < 0) and -amount) or 0.0,
            "credit": ((amount > 0) and amount) or 0.0,
            "journal_id": self.journal_id.id,
        }
        return [(0, 0, line_vals)]

    @api.multi
    def _prepare_pos_counterpart_move_lines(self, key, statement_lines):
        def _get_account_id(self, amount):
            return (
                (amount <= 0) and self.journal_id.default_debit_account_id.id
            ) or self.journal_id.default_credit_account_id.id

        self.ensure_one()
        lines_vals = []
        (x, partner_id, move_date) = key

        if self.journal_id.is_customer_wallet_journal:
            # We split counterpart per partner
            wallet_partners = statement_lines.mapped("partner_id")
            for wallet_partner in wallet_partners:
                wallet_statement_lines = statement_lines.filtered(
                    lambda x: x.partner_id == wallet_partner
                )

                amount = sum(wallet_statement_lines.mapped("amount"))
                lines_vals.append(
                    {
                        "name": self.name,
                        "date": move_date,
                        "account_id": _get_account_id(self, amount),
                        "partner_id": wallet_partner.id,
                        "debit": ((amount > 0) and amount) or 0.0,
                        "credit": ((amount < 0) and -amount) or 0.0,
                        "journal_id": self.journal_id.id,
                    }
                )

        else:

            amount = sum(statement_lines.mapped("amount"))
            lines_vals.append(
                {
                    "name": self.name,
                    "date": move_date,
                    "account_id": _get_account_id(self, amount),
                    "partner_id": partner_id,
                    "debit": ((amount > 0) and amount) or 0.0,
                    "credit": ((amount < 0) and -amount) or 0.0,
                    "journal_id": self.journal_id.id,
                }
            )

        return [(0, 0, line_vals) for line_vals in lines_vals]
