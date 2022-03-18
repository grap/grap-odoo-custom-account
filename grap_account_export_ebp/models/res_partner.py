# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unidecode import unidecode

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    _SEARCH_DATE_BEGIN = "01/12/2012"

    # Columns section
    ebp_suffix = fields.Char(
        string="Suffix in EBP",
        help="When exporting Entries to EBP, this suffix will be"
        " appended to the Account Number to make it a Partner Account.",
    )

    has_ebp_move_line = fields.Boolean(
        compute="_compute_has_ebp_move_line",
        search="_search_has_ebp_move_line",
        string="Has Account Move Lines exportable in EBP",
    )

    # Constraints section
    _sql_constraints = [
        (
            "ebp_suffix_company_id_uniq",
            "unique (ebp_suffix, company_id)",
            "The EBP suffix must be unique per company!",
        )
    ]

    # Columns section
    @api.multi
    def _compute_has_ebp_move_line(self):
        AccountMoveLine = self.env["account.move.line"]
        for partner in self:
            partner.has_ebp_move_line = len(
                AccountMoveLine.search(
                    [
                        ("partner_id", "=", partner.id),
                        ("date", ">=", self._SEARCH_DATE_BEGIN),
                    ]
                )
            )

    @api.model
    def _search_has_ebp_move_line(self, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        assert value in (True, False), "Invalid domain value"

        with_line = (operator == "=" and value is True) or (
            operator == "!=" and value is False
        )

        self._cr.execute(
            "SELECT partner_id, count(*)"
            " FROM account_move_line"
            " WHERE date >= '01/12/2012'"
            " GROUP BY partner_id"
            " HAVING  count(*) > 0"
        )
        res = self._cr.fetchall()
        return [("id", with_line and "in" or "not in", [x[0] for x in res])]

    @api.model
    def _get_existing_ebp_suffixes(self):
        """Return a dictionnary {'company_id': [list_of_existing_suffixes]}"""
        res = {}
        for x in self.with_context(active_test=True).search_read(
            [], ["company_id", "ebp_suffix"]
        ):
            res.setdefault(x["company_id"][0], [])
            res[x["company_id"][0]].append(x["ebp_suffix"])
        return res

    @api.multi
    def _guess_ebp_suffix(self, reserved_suffixes):
        self.ensure_one()
        name = self.name
        # remove special caracters
        name2 = "".join(e for e in name if e.isalnum())
        # if nothing remains, return False
        if not name2:
            return False
        # first try: return the 4 fisrt caracters
        suffix = name2[: min(4, len(name2))].upper()
        suffix = unidecode(suffix)
        if suffix and not (suffix in reserved_suffixes):
            return suffix
        # second try: look for different words in the name
        # and try taking caracters from them
        for sep in [" ", """'""", "-"]:
            if sep in name:
                names = name.split(sep)
                for i in range(0, len(names)):
                    names[i] = "".join(e for e in names[i] if e.isalnum())
                for j in range(1, len(names)):
                    for n in range(3, 0, -1):
                        if len(names[0]) >= n:
                            suffix = names[0][:n].upper() + names[j][: (4 - n)].upper()
                            suffix = unidecode(suffix)
                            if suffix and not (suffix in reserved_suffixes):
                                return suffix
        # third try: takes first 3 caracters and add a one digit number
        for x in range(2, 10):
            suffix = name2[: min(3, len(name2))].upper() + str(x)
            suffix = unidecode(suffix)
            if suffix and not (suffix in reserved_suffixes):
                return suffix
        # fourth try: takes first 2 caracters and add a two digit number
        for x in range(10, 100):
            suffix = name2[: min(2, len(name2))].upper() + str(x)
            suffix = unidecode(suffix)
            if suffix and not (suffix in reserved_suffixes):
                return suffix
        # fifth try: takes first 1 caracters and add a three digit number
        for x in range(100, 1000):
            suffix = name2[:1].upper() + str(x)
            suffix = unidecode(suffix)
            if suffix and not (suffix in reserved_suffixes):
                return suffix
        return False
