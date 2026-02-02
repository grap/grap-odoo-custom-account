from . import export_type_format_ebp

_MOVES_COLUMNS = [
    "move_number",
    "journal_code",
    "date",
    "move_number_2",
    "account_code",
    "analytic_code",
    "line_description",
    "amount",
    "direction",
    "account_type",
    "analytic_code_2",
]

_MOVES_HEADER = {
    "move_number": "Num piece",
    "journal_code": "code jal",
    "date": "date",
    "move_number_2": "Num de facture",
    "account_code": "compteg",
    "analytic_code": "compte tiers",
    "line_description": "libelle",
    "amount": "montant",
    "direction": "sens",
    "account_type": "type",
    "analytic_code_2": "section",
}

_MOVES_SIZE = {
    "move_number": 15,
    "account_code": 15,
    "line_description": 40,
}

_ACCOUNTS_COLUMNS = export_type_format_ebp._ACCOUNTS_COLUMNS
_ACCOUNTS_HEADER = export_type_format_ebp._ACCOUNTS_HEADER
_ACCOUNTS_SIZE = export_type_format_ebp._ACCOUNTS_SIZE


def _get_formated_moves_data(export, moves_data):
    res = []
    move_count = 0

    for move_data in moves_data:
        move_count += 1
        is_odd = bool(move_count % 2)
        for key, lines in move_data.items():
            (_x1, account_code, analytic_code, _x4, _x5, _x6) = key
            line = lines[0]
            move = lines.move_id
            line_description = line.name and line.name or line.account_id.name
            if move.ref:
                line_description += f" ({move.ref})"
            if line.partner_id:
                line_description += f" ({line.partner_id.name})"

            # In case we are in a 'normal' company (out of CAE)
            # The Mache want also the code of the company in the
            # analytic column. (as a constant)
            if move.company_id.fiscal_type == "normal":
                analytic_code = move.company_id.code

            value = {
                "is_odd": is_odd,
                "move_number": move.name,
                "journal_code": move.journal_id.export_code,
                "date": move.date.strftime("%d%m%y"),
                "move_number_2": move.name,
                "account_code": account_code,
                "analytic_code": analytic_code,
                "line_description": line_description,
                "amount": line.credit
                and sum(lines.mapped("credit"))
                or sum(lines.mapped("debit")),
                "direction": line.credit and "C" or "D",
                "account_type": "G",
                "analytic_code_2": "",
            }
            second_line_value = value.copy()
            second_line_value.update(
                {
                    "account_type": "A",
                    "analytic_code_2": analytic_code,
                }
            )
            res += [value, second_line_value]

    return res


def _get_formated_accounts_data(export, accounts_data):
    return export_type_format_ebp._get_formated_accounts_data(export, accounts_data)
