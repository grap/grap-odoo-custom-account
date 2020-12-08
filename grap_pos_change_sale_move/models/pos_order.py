# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# Copyright (C) 2021 - Today: Coop IT Easy (http://coopiteasy.be)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Rémy TAYMANS (remy@coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _get_partner_required_if_specific_account(self, account_id):
        account = self.env["account.account"].browse(account_id)
        return account.code == "4197"

    def _get_group_by_keys(self):
        """Return keys used to aggregate the account moves."""
        if self:
            company = self[0].session_id.config_id.company_id
            pos_sale_move_policy = company.pos_sale_move_policy
            return {"partner": "partner" in pos_sale_move_policy}
        # In case of an empty self, we can give a random config as no
        # move.lines will be written (function using group_by_keys will
        # not be called).
        return {}

    # Overwrite this Odoo function.
    # Remove partner_id product_id and name from the keys.
    @api.model
    def _get_account_move_line_group_data_type_key(
        self, data_type, values, options=False
    ):
        options = options or {}
        groupby = self._get_group_by_keys()
        if data_type == "product":
            tax_ids = values["tax_ids"][0][2]

            product_key = ["product"]
            if groupby["partner"]:
                product_key.append(values["partner_id"])
            # remove product_id (0) and name (2), keep tax (1)
            product_key.append((False, tuple(tax_ids), False))
            product_key.append(values["analytic_account_id"])
            product_key.append(values["debit"] > 0)
            product_key.append(values.get("currency_id"))
            # Add new key "account_id"
            product_key.append(values["account_id"])

            return tuple(product_key)
        elif data_type == "tax":
            order_id = values.pop("order_id", False)

            tax_key = ["tax"]
            if groupby["partner"]:
                tax_key.append(values["partner_id"])
            tax_key.append(values["tax_line_id"])
            tax_key.append(values["debit"] > 0)
            if options.get("rounding_method") == "round_globally":
                tax_key = ("tax", values["tax_line_id"], order_id)

            return tuple(tax_key)
        elif data_type == "counter_part":
            counter_part_key = ["counter_part"]

            if groupby["partner"]:
                counter_part_key.append(values["partner_id"] or 0)
            counter_part_key.append(values["account_id"])
            counter_part_key.append(values["debit"] > 0)
            counter_part_key.append(values.get("currency_id"))

            return tuple(counter_part_key)
        return False

    # Overload this Odoo function.
    # Removing values partner_id / product_id / quantity
    def _prepare_account_move_and_lines(self, session=None, move=None):
        res = super()._prepare_account_move_and_lines(session=session, move=move)
        AccountAccount = self.env["account.account"]
        grouped_data = res.get("grouped_data")
        groupby = self._get_group_by_keys()
        for k, values in grouped_data.items():
            for value in values:
                if not self._get_partner_required_if_specific_account(
                    value["account_id"]
                ):
                    value["partner_id"] = False
                if not groupby["partner"]:
                    value["partner_id"] = False
                value["product_id"] = False
                value["quantity"] = False
                if k[0] == "product":
                    account = AccountAccount.browse(value["account_id"])
                    value["name"] = account.name
        return res
