# Copyright (C) 2015 - Today: GRAP (http://www.grap.coop)
# @author: Julien WESTE
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    _SEARCH_DATE_BEGIN = "01/01/2017"

    export_suffix = fields.Char(
        copy=False,
        help="When exporting Entries, this suffix will be"
        " appended to the Account Number to make it a new Account.",
    )

    export_suffix_required = fields.Boolean(
        compute="_compute_export_suffix_required",
        search="_search_export_suffix_required",
        string="Require Export Suffix",
    )

    # Columns section
    def _compute_export_suffix_required(self):
        required_tax_ids = [x[0] for x in self._get_export_suffix_required()]
        for tax in self:
            tax.export_suffix_required = tax.id in required_tax_ids

    def _get_export_suffix_required(self):
        self._cr.execute(
            """
            SELECT amlt.account_tax_id, count(*)
            FROM account_move_line_account_tax_rel amlt
            INNER JOIN account_move_line aml
            ON aml.id = amlt.account_move_line_id
            INNER JOIN account_account aa
            ON aa.id = aml.account_id
            WHERE aa.export_suffix_on_tax_required is True
            AND amlt.account_tax_id in %s
            AND aml.date >= %s
            GROUP BY amlt.account_tax_id
        """,
            (tuple(self.ids), self._SEARCH_DATE_BEGIN),
        )
        res = self._cr.fetchall()
        return res

    @api.model
    def _search_export_suffix_required(self, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        assert value in (True, False), "Invalid domain value"

        with_line = (operator == "=" and value is True) or (
            operator == "!=" and value is False
        )

        # Get ids accessible in the current context
        res = self.search([])._get_export_suffix_required()
        return [("id", with_line and "in" or "not in", [x[0] for x in res])]
