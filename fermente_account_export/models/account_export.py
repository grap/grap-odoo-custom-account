# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
from io import StringIO

from unidecode import unidecode

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountExport(models.Model):
    _name = "account.export"
    _description = "Account Export"
    _order = "export_date desc"

    _ACCOUNT_REMOVE_CHAR_LIST = ["\n", ";", ",", '"']

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        readonly=True,
    )

    fiscal_year_id = fields.Many2one(
        comodel_name="account.fiscal.year",
        string="Fiscal year",
        required=True,
        readonly=True,
    )

    export_date = fields.Datetime(required=True, readonly=True)

    name = fields.Char(compute="_compute_name", store=True, readonly=True)

    description = fields.Text(
        readonly=True,
        help="Extra Description for Accountant Manager.",
    )

    exported_move_qty = fields.Integer(string="Moves Exported", readonly=True)

    exported_account_qty = fields.Integer(string="Accounts Exported", readonly=True)

    move_ids = fields.One2many(
        comodel_name="account.move",
        inverse_name="account_export_id",
        string="Moves",
        readonly=True,
    )

    move_qty = fields.Integer(
        compute="_compute_move_qty", string="Moves Quantity", store=True
    )

    data_moves = fields.Binary(string="Moves file", readonly=True)

    data_accounts = fields.Binary(string="Accounts file", readonly=True)

    data_balance = fields.Binary(string="Balance file", readonly=True)

    file_name_moves = fields.Char(compute="_compute_file_name_moves")

    file_name_accounts = fields.Char(compute="_compute_file_name_accounts")

    file_name_balance = fields.Char(compute="_compute_file_name_balance")

    # Compute Section
    def _compute_name(self):
        for export in self:
            export.name = _(
                "Export #%(export_id)d",
                export_id=export.id,
            )

    @api.depends("move_ids.account_export_id")
    def _compute_move_qty(self):
        for export in self:
            export.move_qty = len(export.move_ids)

    def _compute_file_name_moves(self):
        for export in self:
            export.file_name_moves = _(
                "export_%(export_id)d_MOVES.csv", export_id=export.id
            )

    def _compute_file_name_accounts(self):
        for export in self:
            export.file_name_accounts = _(
                "export_%(export_id)d_ACCOUNTS.csv", export_id=export.id
            )

    def _compute_file_name_balance(self):
        for export in self:
            export.file_name_balance = _(
                "export_%(export_id)d_BALANCE.csv", export_id=export.id
            )

    # Custom Section
    @api.model
    def _normalize(self, text):
        res = text
        for char in self._ACCOUNT_REMOVE_CHAR_LIST:
            res = res.replace(char, " ")
        return res

    def export(self, moves):
        """Export moves into 3 files and mark the moves as exported"""
        self.ensure_one()
        # Create files
        moves_file = StringIO()
        accounts_file = StringIO()
        balance_file = StringIO()

        # Export into files
        self._write_header_into_moves_file(moves_file)
        self._write_header_into_accounts_file(accounts_file)
        self._write_header_into_balance_file(balance_file)

        vals = self._export_to_files(moves, moves_file, accounts_file, balance_file)
        data_moves = base64.b64encode(moves_file.getvalue().encode("utf-8"))
        data_accounts = base64.b64encode(accounts_file.getvalue().encode("utf-8"))
        data_balance = base64.b64encode(balance_file.getvalue().encode("utf-8"))
        moves_file.close()
        accounts_file.close()
        balance_file.close()

        # Save Datas
        vals.update(
            {
                "data_moves": data_moves,
                "data_accounts": data_accounts,
                "data_balance": data_balance,
            }
        )
        self.write(vals)

        # Mark moves as exported
        moves.write({"account_export_id": self.id})

    @api.model
    def _export_to_files(self, moves, moves_file, accounts_file, balance_file):
        # dictionary to store accounts while we loop through move lines
        accounts_data = {}
        # Line counter
        i = 0

        for move in moves:
            # dictionary to summarize the lines of the move by account
            moves_data = {}
            for line in move.line_ids:
                if line.credit == line.debit:
                    # Ignoring line with null debit and credit
                    continue

                account_code = line.account_id._get_account_code(line)
                analytic_code = self._get_analytic_code(move)

                move_key = (account_code, analytic_code, line.credit > 0)

                # Collect data for the file of move lines
                if move_key not in moves_data.keys():
                    moves_data[move_key] = self._prepare_move_line_dict(move, line)
                else:
                    moves_data[move_key]["credit"] += line.credit
                    moves_data[move_key]["debit"] += line.debit
                    # Keep the earliest maturity date
                    if line.date_maturity < moves_data[move_key]["date_maturity"]:
                        moves_data[move_key]["date_maturity"] = line.date_maturity

                # Collect data for the file of accounts
                if account_code not in accounts_data.keys():
                    accounts_data[account_code] = self._prepare_account_dict(move, line)
                accounts_data[account_code]["credit"] += line.credit
                accounts_data[account_code]["debit"] += line.debit

            # Write to file
            self._write_into_moves_file(i, moves_data, moves_file)
            i += len(moves_data)

        # Write the accounts into the file
        self._write_into_accounts_file(i, accounts_data, accounts_file)

        # Write the balance of accounts into the file
        self._write_into_balance_file(i, accounts_data, balance_file)

        return {
            "exported_move_qty": len(moves),
            "exported_account_qty": len(accounts_data),
        }

    @api.model
    def _get_analytic_code(self, move):
        res = ""
        if move.company_id.fiscal_type == "fiscal_child":
            res = move.company_id.code
        return res

    @api.model
    def _prepare_move_line_dict(self, move, line):
        ref = (line.name and line.name or line.account_id.name) + (
            move.ref and " (%s)" % (move.ref) or ""
        )

        # Manage analytic cases
        if move.company_id.fiscal_type == "fiscal_child":
            ref = line.company_id.code + " " + ref

        return {
            "date": move.date,
            "journal": move.journal_id.export_code,
            "account_code": line.account_id._get_account_code(line),
            "ref": self._normalize(ref),
            "name": self._normalize(move.name),
            "credit": line.credit,
            "debit": line.debit,
            "date_maturity": line.date_maturity,
            "currency_name": move.company_id.currency_id.name,
            "analytic_code": self._get_analytic_code(move),
        }

    @api.model
    def _write_header_into_moves_file(self, moves_file):
        # Move File header
        data = [
            _("Line"),
            _("Date"),
            _("Journal Code"),
            _("Account Number"),
            _("Name"),
            _("Move Number"),
            _("Amount (related to the direction)"),
            _("Direction"),
            _("Due Date"),
            _("Currency"),
            _("Analytic Account"),
        ]
        self._write_into_file(data, moves_file)

    @api.model
    def _write_into_moves_file(self, count, moves_data, moves_file):
        i = count

        for _key, line in moves_data.items():
            i += 1
            data = [
                # Line number
                "%d" % i,
                # Date (dd/mm/yy)
                line["date"].strftime("%d/%m/%y"),
                # Journal
                self._normalize(line["journal"]),
                # Account number
                # (possibly with the partner code appended to it)
                line["account_code"],
                # Manual title
                '"%s"' % line["ref"][:40],
                # Accountable receipt number
                '"%s"' % line["name"][:15],
            ]
            if line["credit"]:
                data += [
                    # Amount
                    "%f" % abs(line["credit"]),
                    # [C]redit or [D]ebit
                    "C",
                ]
            else:
                data += [
                    # Amount
                    "%f" % abs(line["debit"]),
                    # [C]redit or [D]ebit
                    "D",
                ]
            data += [
                # Date of maturity (ddmmyy)
                line["date_maturity"] and line["date_maturity"].strftime("%d%m%y"),
                # Currency
                line["currency_name"],
            ]
            data += [line["analytic_code"]]
            self._write_into_file(data, moves_file)

    @api.model
    def _prepare_account_dict(self, move, line):
        res = {
            "name": "",
            "partner_name": "",
            "address": "",
            "zip": "",
            "city": "",
            "country": "",
            "contact": "",
            "phone": "",
            "fax": "",
            "credit": 0,
            "debit": 0,
            "allow_analytic": "",
            "payment_mode": "CH30",
            "rgpd": "N",
        }

        if (
            line.partner_id
            and line.partner_id.export_suffix
            and line.account_id.account_type
            in ["asset_receivable", "liability_payable"]
        ):
            # Partner account
            partner = line.partner_id
            res.update(
                {
                    "name": self._normalize(partner.name),
                    "partner_name": self._normalize(partner.name),
                    "address": self._normalize(
                        (partner.street or "")
                        + (partner.street2 and (" " + partner.street2) or "")
                    ),
                    "zip": partner.zip or "",
                    "city": self._normalize(partner.city or ""),
                    "country": self._normalize(partner.country_id.name or ""),
                    "contact": self._normalize(partner.email or ""),
                    "phone": partner.phone or partner.mobile or "",
                }
            )
        elif (
            line.account_id.export_suffix_on_tax_required
            and line.tax_ids
            and line.tax_ids[0].export_suffix
        ):
            res.update(
                {
                    "name": (
                        self._normalize(line.account_id.name)
                        + "("
                        + self._normalize(line.tax_ids[0].name)
                        + ")"
                    )
                }
            )
        else:
            # Normal account
            res.update({"name": self._normalize(line.account_id.name)})

        if move.company_id.fiscal_type == "fiscal_child":
            res.update({"allow_analytic": "1"})

        return res

    @api.model
    def _write_header_into_accounts_file(self, accounts_file):
        pass

    @api.model
    def _write_into_accounts_file(self, count, accounts_data, accounts_file):
        for account_code, account_data in accounts_data.items():
            data = [
                self._normalize(account_code),
                self._normalize(account_data["name"])[:60],
                self._normalize(account_data["partner_name"])[:30],
                self._normalize(account_data["address"])[:100],
                self._normalize(account_data["zip"])[:5],
                self._normalize(account_data["city"])[:30],
                self._normalize(account_data["country"])[:35],
                self._normalize(account_data["contact"])[:35],
                self._normalize(account_data["phone"])[:20],
                self._normalize(account_data["fax"])[:20],
                account_data["allow_analytic"],
                account_data["payment_mode"],
                account_data["rgpd"],
            ]
            self._write_into_file(data, accounts_file)

    @api.model
    def _write_header_into_balance_file(self, balance_file):
        # Move File header
        data = [
            _("Account Number"),
            _("Account name"),
            _("Debit"),
            _("Credit"),
            _("Debit Balance"),
            _("Credit Balance"),
        ]
        self._write_into_file(data, balance_file)

    @api.model
    def _write_into_balance_file(self, count, accounts_data, balance_file):
        for account_code, account_data in accounts_data.items():
            credit = account_data["credit"] or 0
            debit = account_data["debit"] or 0
            if credit > debit:
                credit_balance = credit - debit
                debit_balance = 0
            else:
                credit_balance = 0
                debit_balance = debit - credit
            data = [
                account_code.replace(",", ""),
                (account_data["name"] or "").replace(",", "")[:60],
                str(debit),
                str(credit),
                str(debit_balance),
                str(credit_balance),
            ]
            self._write_into_file(data, balance_file)

    @api.model
    def _write_into_file(self, data_list, file):
        tmp = ",".join([x and x or "" for x in data_list])
        file.write(unidecode(tmp))
        file.write("\r\n")
