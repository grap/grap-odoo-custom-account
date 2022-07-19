# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unidecode import unidecode

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    accounting_export_code = fields.Char(
        string="Accounting Export Code",
        help="When exporting Entries, this suffix will be"
        " appended to the Account Number to make it a Partner Account.",
    )

    # Constraints section
    _sql_constraints = [
        (
            "accounting_export_code_company_id_uniq",
            "unique (accounting_export_code, company_id)",
            "The Accounting Export Code must be unique per Company!",
        )
    ]

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
