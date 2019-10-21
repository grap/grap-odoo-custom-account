# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pytz
import time
from datetime import datetime

from odoo import api, models, tools


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_confirm_bank(self):
        """
        Call normal super function for statement, except for PoS statement,
        that will call button_confirm_bank_point_of_sale() function.
        """
        self.filtered(
            lambda x: x.pos_session_id).button_confirm_bank_point_of_sale()

        super(self.filtered(
            lambda x: not x.pos_session_id).button_confirm_bank())

    @api.multi
    def button_confirm_bank_point_of_sale(self):
        print("====================")
        print("HACKING THE SYSTEM")
        print("====================")

        def _prepare_local_date(obj, date):
            context_tz = pytz.timezone(obj.env.user.tz)
            timestamp = datetime.strptime(
                date, tools.DEFAULT_SERVER_DATETIME_FORMAT
            )
            utc_timestamp = pytz.utc.localize(timestamp, is_dst=False)
            tz_timestamp = utc_timestamp.astimezone(context_tz)
            return tz_timestamp.strftime("%Y-%m-%d")

        AccountMove = self.env["account.move"]
        AccountBankStatementLine = self.env["account.bank.statement.line"]

        for statement in self:
            move_ids = []
            groups = {}
            # parse the lines to group the ids according to the key fields
            for statement_line in statement.line_ids:
                pos_order = statement_line.pos_statement_id

                partner_id = False
                statement_date = statement.date
                if pos_order:
                    statement_date = _prepare_local_date(
                        self, pos_order.date_order
                    )
                    if pos_order.state == "invoiced":
                        # We keep partner information only if
                        # an invoice has been generated
                        partner_id = statement_line.partner_id.id
                keys = (
                    statement_line.account_id.id,
                    partner_id,
                    statement_date,
                )
                groups.setdefault(keys, [])
                groups[keys].append(statement_line.id)

            # for each group, create account_move and account_move_lines
            i = 0
            for key in groups.keys():
                i += 1
                statement_lines = AccountBankStatementLine.browse(groups[key])
                move = statement.create_move_point_of_sale(
                    key, statement_lines, statement.name + "/" + str(i)
                )
                move_ids.append(move.id)
                # Mark statement line as reconciled with a move
                statement_lines.write({"journal_entry_id": move.id})

            if move_ids:
                moves = AccountMove.browse(move_ids)
                moves.post()

        return self.write(
            {
                "state": "confirm",
                "closing_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    @api.multi
    def create_move_point_of_sale(self, key, statement_lines, move_name):
        self.ensure_one()

        AccountMove = self.env["account.move"]
        AccountMoveLine = self.env["account.move.line"]

        move_vals = self._prepare_move_point_of_sale(
            key, statement_lines, move_name
        )

        move = AccountMove.create(move_vals)

        move_line_vals = self._prepare_bank_move_line_point_of_sale(
            key, statement_lines, move
        )
        AccountMoveLine.create(move_line_vals)

        move_line_vals = self._prepare_counterpart_move_line_point_of_sale(
            key, statement_lines, move
        )
        AccountMoveLine.create(move_line_vals)

        return move

    @api.multi
    def _prepare_move_point_of_sale(self, key, statement_lines, move_name):
        self.ensure_one()
        (account_id, partner_id, move_date) = key
        return {
            "journal_id": self.journal_id.id,
            "partner_id": partner_id,
            "date": move_date,
            "name": move_name,
            "ref": self.pos_session_id.name,
        }

    @api.multi
    def _prepare_bank_move_line_point_of_sale(
        self, key, statement_lines, move
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
            "date": move.date,
            "move_id": move.id,
            "account_id": account_id,
            "partner_id": partner_id,
            "credit": credit,
            "debit": debit,
            "statement_id": self.id,
            "journal_id": self.journal_id.id,
        }

    @api.multi
    def _prepare_counterpart_move_line_point_of_sale(
        self, key, statement_lines, move
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
            "date": move.date,
            "move_id": move.id,
            "account_id": account_id,
            "partner_id": partner_id,
            "credit": credit,
            "debit": debit,
            "statement_id": self.id,
            "journal_id": self.journal_id.id,
        }
