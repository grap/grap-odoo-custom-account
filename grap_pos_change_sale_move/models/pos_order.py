# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_partner_required_if_specific_account(self, account_id):
        account = self.env["account.account"].browse(account_id)
        return account.code == "4197"

    # Overwrite this Odoo function.
    # Remove partner_id product_id and name from the keys.
    @api.model
    def _get_account_move_line_group_data_type_key(
        self, data_type, values, options=False
    ):
        options = options or {}
        if data_type == "product":
            return (
                "product",
                # Remove partner_id
                self._get_partner_required_if_specific_account(values["account_id"])
                and values["partner_id"]
                or False,
                # remove product_id (1) and name (3)
                (False, tuple(values["tax_ids"][0][2]), False),
                values["analytic_account_id"],
                values["debit"] > 0,
                values.get("currency_id"),
                # Add new key "account_id"
                values["account_id"],
            )
        elif data_type == "tax":
            order_id = values.pop("order_id", False)
            tax_key = (
                "tax",
                # remove partner_id
                False,
                values["tax_line_id"],
                values["debit"] > 0,
                values.get("currency_id"),
            )
            if options.get("rounding_method") == "round_globally":
                tax_key = ("tax", values["tax_line_id"], order_id)
            return tax_key
        elif data_type == "counter_part":
            return (
                "counter_part",
                # remove partner_id
                False,
                values["account_id"],
                values["debit"] > 0,
                values.get("currency_id"),
            )
        return False

    # Overload this Odoo function.
    # Removing values partner_id / product_id / quantity
    def _prepare_account_move_and_lines(self, session=None, move=None):
        res = super()._prepare_account_move_and_lines(session=session, move=move)
        AccountAccount = self.env["account.account"]
        grouped_data = res.get("grouped_data")
        for k, values in grouped_data.items():
            for value in values:
                if not self._get_partner_required_if_specific_account(
                    value["account_id"]
                ):
                    value["partner_id"] = False
                value["product_id"] = False
                value["quantity"] = False
                if k[0] == "product":
                    account = AccountAccount.browse(value["account_id"])
                    value["name"] = account.name
        return res
