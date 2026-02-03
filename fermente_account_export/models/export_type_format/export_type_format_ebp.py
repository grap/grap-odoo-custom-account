_MOVES_COLUMNS = [
    "move_count",
    "line_count",
    "date",
    "journal_code",
    "account_code",
    "move_name",
    "line_description",
    "amount",
    "direction",
    "date_maturity",
    "currency_name",
    "analytic_code",
]

_MOVES_HEADER = {
    "move_count": "N° P.",
    "line_count": "N° L.",
    "date": "Date",
    "journal_code": "Code Journal",
    "account_code": "N. Compte",
    "line_description": "Nom",
    "move_name": "N. Piece",
    "amount": "Montant",
    "direction": "Direction",
    "date_maturity": "Date d'echeance",
    "currency_name": "Monnaie",
    "analytic_code": "Compte analytique",
}

_MOVES_SIZE = {
    "move_count": 5,
    "line_count": 5,
    "date": 10,
    "journal_code": 10,
    "account_code": 15,
    "line_description": 30,
    "move_name": 20,
    "amount": 10,
    "direction": 10,
    "date_maturity": 10,
    "currency_name": 10,
    "analytic_code": 10,
}


_ACCOUNTS_COLUMNS = [
    "account_code",
    "account_name",
    "partner_address",
    "partner_zip",
    "partner_city",
    "partner_country",
    "partner_email",
    "partner_phone",
    "allow_analytic",
    "payment_mode",
    "rgpd",
]

_ACCOUNTS_HEADER = {
    "account_code": "Code comptable",
    "account_name": "Nom du compte",
    "partner_address": "Addresse",
    "partner_zip": "Code Postal",
    "partner_city": "Ville",
    "partner_country": "Pays",
    "partner_email": "Email",
    "partner_phone": "Téléphone",
    "allow_analytic": "Analytique",
    "payment_mode": "Mode de paiement",
    "rgpd": "RPGD",
}

_ACCOUNTS_SIZE = {
    "account_code": 15,
    "account_name": 40,
    "partner_address": 20,
    "partner_zip": 8,
    "partner_city": 12,
    "partner_country": 15,
    "partner_email": 15,
    "partner_phone": 10,
    "allow_analytic": 10,
    "payment_mode": 10,
    "rgpd": 5,
}


def _get_formated_moves_data(export, moves_data):
    res = []
    move_count = 0
    line_count = 0

    for move_data in moves_data:
        move_count += 1
        is_odd = bool(move_count % 2)
        for key, lines in move_data.items():
            line_count += 1
            (_x1, account_code, analytic_code, _x4, _x5, _x6) = key
            line = lines[0]
            move = lines.move_id
            line_description = line.name and line.name or line.account_id.name
            if move.ref:
                line_description += f" ({move.ref})"

            # Manage analytic cases
            if move.company_id.fiscal_type == "fiscal_child":
                line_description = f"{line.company_id.code} {line_description}"

            res.append(
                {
                    "is_odd": is_odd,
                    "move_count": move_count,
                    "line_count": line_count,
                    "date": move.date.strftime("%Y-%m-%d"),
                    "journal_code": move.journal_id.export_code,
                    "account_code": account_code,
                    "line_description": line_description,
                    "move_name": move.name,
                    "amount": line.credit
                    and sum(lines.mapped("credit"))
                    or sum(lines.mapped("debit")),
                    "direction": line.credit and "C" or "D",
                    "date_maturity": line.date_maturity
                    and line.date_maturity.strftime("%Y-%m-%d")
                    or "",
                    "currency_name": move.company_id.currency_id.name,
                    "analytic_code": analytic_code,
                }
            )

    return res


def _get_formated_accounts_data(export, accounts_data):
    res = []
    for (account_code,), lines in accounts_data.items():
        line = lines[0]
        account = line.account_id
        partner = line.partner_id
        account_res = {
            "account_code": account_code,
            "partner_address": "",
            "partner_zip": "",
            "partner_city": "",
            "partner_country": "",
            "partner_email": "",
            "partner_phone": "",
            "allow_analytic": "",
            "payment_mode": "CH30",
            "rgpd": "N",
        }

        if (
            partner
            and partner.export_suffix
            and account.account_type in ["asset_receivable", "liability_payable"]
        ):
            account_res.update(
                {
                    "account_name": partner.name,
                    "partner_name": partner.name,
                    "partner_address": partner.street
                    or "" + (partner.street2 and (" " + partner.street2) or ""),
                    "partner_zip": partner.zip or "",
                    "partner_city": partner.city or "",
                    "partner_country": partner.country_id
                    and partner.country_id.name
                    or "",
                    "partner_email": partner.email or "",
                    "partner_phone": partner.phone or partner.mobile or "",
                }
            )
        elif (
            account.export_suffix_on_tax_required
            and line.tax_ids
            and line.tax_ids[0].export_suffix
        ):
            account_res[
                "account_name"
            ] = f"{line.account_id.name} ({line.tax_ids[0].name})"
        else:
            # Normal account
            account_res["account_name"] = line.account_id.name

        if account.company_id.fiscal_type == "fiscal_mother":
            account_res["allow_analytic"] = "1"

        res.append(account_res)

    # Reorder by account_code, and compute 'is_odd'
    # to improve display
    res.sort(key=lambda x: x["account_code"])
    i = 0
    for line in res:
        i += 1
        line["is_odd"] = bool(i % 2)
    return res
