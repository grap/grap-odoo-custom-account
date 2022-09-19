# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from psycopg2.extensions import AsIs
from unidecode import unidecode

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    accounting_export_code = fields.Char(
        string="Accounting Export Code",
        help="When exporting Entries, this accounting_code will be"
        " appended to the Account Number to make it a Partner Account.",
    )

    journal_item_count = fields.Integer(search="_search_journal_item_count")

    # Constraints section
    _sql_constraints = [
        (
            "accounting_export_code_company_id_uniq",
            "unique (accounting_export_code, company_id)",
            "The Accounting Export Code must be unique per Company!",
        )
    ]

    # Search Section
    def _search_journal_item_count(self, operator, value):
        if operator not in ("=", "!=", "<", "<=", ">", ">=", "in", "not in"):
            return []
        query = (
            "SELECT partner_id, count(*)"
            " FROM account_move_line"
            " GROUP BY partner_id"
            " HAVING  count(*) %s %s;"
        )
        self.env.cr.execute(
            query,
            (
                AsIs(operator),
                value,
            ),
        )
        ids = [x[0] for x in self.env.cr.fetchall()]
        return [("id", "in", ids)]

    # Custom Section
    @api.model
    def _get_existing_accounting_export_codes(
        self, company_ids=False, ignore_partner=False
    ):
        """Return a dictionnary {'company_id': [list_of_existing_codes]}"""
        res = {}
        domain = [("accounting_export_code", "!=", False)]
        if company_ids:
            domain.append(("company_id", "in", company_ids))
        if ignore_partner:
            domain.append(("id", "!=", ignore_partner.id))

        for x in self.with_context(active_test=False).search_read(
            domain, ["company_id", "accounting_export_code"]
        ):
            res.setdefault(x["company_id"][0], [])
            res[x["company_id"][0]].append(x["accounting_export_code"])
        return res

    @api.model
    def _accounting_export_sanitize(self, name):
        """Sanitize a text (partner name)
        returning a clean text like 'Bob - #hello' -> BOB HELLO"""
        # Upper name
        res = name.upper()

        # Replace special Non Alphabetic Char by space
        res = "".join([c if c.isalpha() else " " for c in res])

        # Remove accent
        res = unidecode(res)

        # Strip text
        res = res.strip()

        # Remove duplicated spaces
        res = re.sub(" +", " ", res)
        return res

    @api.model
    def _accounting_export_get_base_text(self, name):
        """First sanitize a text, then try to extract
        a Four letter char.
        If the name contains a word that have at least 4 char
        returns the first 4 letters,
        Otherwise, return the bigger word, completed by
        001. Exemple :
        - Relais Vert -> RELA
        - Coeur d'artichaut -> ARTI
        - Ba -> BA01
        """
        name = self._accounting_export_sanitize(name)
        if not name:
            return ""

        # Get the bigger word of the sentence
        split_name = name.split(" ")
        bigger_word = split_name[0]
        for k in range(0, len(split_name)):
            if len(bigger_word) < len(split_name[k]):
                bigger_word = split_name[k]

        if len(bigger_word) >= 4:
            return bigger_word[:4]

        # Complete with 0
        return bigger_word + "0" * (3 - len(bigger_word)) + "1"

    @api.multi
    def _guess_accounting_export_code(self, reserved_codes):
        self.ensure_one()
        base_accounting_code = self._accounting_export_get_base_text(self.name)

        # if no proposal, return empty
        if not base_accounting_code:
            return False

        # if the proposal is not used, return it
        if base_accounting_code not in reserved_codes:
            return base_accounting_code

        # We cut and add a numeric suffix, and check
        # if it is reserved.
        # Exemple, if RELA is reserved,
        # 1) try "REL2", "REL3"
        # 2) Then try "RE10", "RE11"
        # 3) Then try "R100", "R101"
        for x in range(2, 1000):
            new_proposal = base_accounting_code[: (4 - len(str(x)))] + str(x)
            if new_proposal not in reserved_codes:
                return new_proposal

        return False
