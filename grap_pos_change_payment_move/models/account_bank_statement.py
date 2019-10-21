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

        for statement in self:
            move_ids = []
            groups = {}
            # parse the lines to group the ids according to the key fields
            for statement_line in statement.line_ids:
                pos_order = statement_line.pos_statement_id

                partner_id = False
                if pos_order:
                    if pos_order.state == "invoiced":
                        # We keep partner information only if
                        # an invoice has been generated
                        partner_id = statement_line.partner_id.id
                keys = (
                    statement_line.account_id.id,
                    partner_id,
                    "2019-10-21",
                    # statement.date,
                )
                groups.setdefault(keys, [])
                groups[keys].append(statement_line.id)

            # for each group, create account_move and account_move_lines
            i = 0
            for key in groups.keys():
                i += 1
                statement_lines = AccountBankStatementLine.browse(groups[key])
                move = statement.create_move_pos(
                    key, statement_lines, statement.name + "/" + str(i)
                )
                move_ids.append(move.id)

            if move_ids:
                moves = AccountMove.browse(move_ids)
                moves.post()

        return self.write(
            {
                "state": "confirm",
                "date_done": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    @api.multi
    def create_move_pos(self, key, statement_lines, move_name):
        self.ensure_one()

        AccountMove = self.env["account.move"]

        dict_1 = self._prepare_bank_move_line_pos(key, statement_lines)
        dict_2 = self._prepare_counterpart_move_line_pos(key, statement_lines)
        lines_vals = [
            (0, 0, dict_1),
            (0, 0, dict_2),
        ]
        move_vals = self._prepare_move_pos(
            key, statement_lines, move_name, lines_vals
        )
        return AccountMove.create(move_vals)

    @api.multi
    def _prepare_move_pos(
            self, key, statement_lines, move_name, lines_vals):
        self.ensure_one()
        (account_id, partner_id, move_date) = key
        return {
            "journal_id": self.journal_id.id,
            "partner_id": partner_id,
            "date": move_date,
            "name": move_name,
            "ref": self.pos_session_id.name,
            "line_ids": lines_vals,
        }

    @api.multi
    def _prepare_bank_move_line_pos(
        self, key, statement_lines
    ):
        self.ensure_one()
        (account_id, partner_id, move_date) = key
        amount = 0
        for statement_line in statement_lines:
            amount += statement_line.amount

        debit = ((amount < 0) and -amount) or 0.0
        credit = ((amount > 0) and amount) or 0.0

        return {
            "name": self.name,
            "date": move_date,
            "account_id": account_id,
            "partner_id": partner_id,
            "credit": credit,
            "debit": debit,
            "journal_id": self.journal_id.id,
        }

    @api.multi
    def _prepare_counterpart_move_line_pos(
        self, key, statement_lines
    ):
        self.ensure_one()
        (x, partner_id, move_date) = key
        amount = 0
        for statement_line in statement_lines:
            amount += statement_line.amount

        account_id = (
            (amount <= 0) and self.journal_id.default_debit_account_id.id
        ) or self.journal_id.default_credit_account_id.id
        debit = ((amount > 0) and amount) or 0.0
        credit = ((amount < 0) and -amount) or 0.0

        return {
            "name": self.name,
            "date": move_date,
            "account_id": account_id,
            "partner_id": partner_id,
            "credit": credit,
            "debit": debit,
            "journal_id": self.journal_id.id,
        }
