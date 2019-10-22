# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TetsChangePaymentMove(TransactionCase):
    def setUp(self):
        super(TetsChangePaymentMove, self).setUp()
        # import pdb

        # pdb.set_trace()
        self.PosSession = self.env["pos.session"]
        self.PosOrder = self.env["pos.order"]
        self.AccountMove = self.env["account.move"]
        self.AccountJournal = self.env["account.journal"]
        self.pricelist = self.env.ref("product.list0")

        self.product_no_vat = self.env.ref(
            "grap_pos_change_payment_move.product_no_vat"
        )
        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.cash_journal = self.AccountJournal.search([("type", "=", "cash")])[0]
        self.pos_config = self.env.ref("point_of_sale.pos_config_main").copy()
        self.pos_config.open_session_cb()
        self.pos_session = self.pos_config.current_session_id

        self.sale_journal = self.pos_config.journal_id
        self.uid = 1

    # Tools function section
    def _open_session(self):
        return self.PosSession.create({"config_id": self.pos_config.id})

    # Tools function section
    def _sale(self, partner, product, vat_excl, vat_incl, to_invoice=False):
        # Create order
        account_id = self.env.user.partner_id.property_account_receivable_id.id
        statement_id = self.pos_config.current_session_id.statement_ids[0].id
        self.uid += 1
        order_data = {
            "id": u"0006-001-000%d" % (self.uid),
            "to_invoice": to_invoice,
            "data": {
                "pricelist_id": self.pricelist.id,
                "user_id": 1,
                "sequence_number": self.uid,
                "name": "Order 0006-001-000%d" % self.uid,
                "partner_id": partner and partner.id,
                "pos_session_id": self.pos_session.id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "price_unit": vat_incl,
                            "qty": 1,
                            "price_subtotal": vat_excl,
                            "price_subtotal_incl": vat_incl,
                            "tax_ids": [[6, False, product.taxes_id.ids]],
                        },
                    ]
                ],
                "statement_ids": [
                    [
                        0,
                        0,
                        {
                            "journal_id": self.pos_config.journal_ids[0].id,
                            "amount": vat_incl,
                            "name": fields.Datetime.now(),
                            "account_id": account_id,
                            "statement_id": statement_id,
                        },
                    ]
                ],
                "creation_date": u"2018-09-27 15:51:03",
                "fiscal_position_id": False,
                "uid": u"00001-001-000%d" % self.uid,
                "amount_paid": vat_incl,
                "amount_return": 0,
                "amount_tax": vat_incl - vat_excl,
                "amount_total": vat_incl,
            },
        }

        result = self.PosOrder.create_from_ui([order_data])
        order = self.PosOrder.browse(result[0])
        return order

    def _close_session(self):
        self.pos_session.action_pos_session_closing_control()

    def _get_payment_move(self, partner_id):
        return self.AccountMove.search(
            [
                ("ref", "=", self.pos_session.name),
                ("journal_id", "=", self.cash_journal.id),
                ("partner_id", "=", partner_id),
            ]
        )

    def _get_first_move_line(self, move, is_debit):
        self.assertEquals(
            len(move.line_ids),
            2,
            "Payment moves from Point of Sale should have two lines.",
        )
        if move.line_ids[0].debit and is_debit:
            return move.line_ids[0]
        else:
            return move.line_ids[1]

    # Test Section
    def test_01_test_many_uninvoiced_orders(self):
        # anonymous sale
        self._sale(False, self.product_no_vat, 50, 50)
        # Anonymous return
        self._sale(False, self.product_no_vat, -10, -10)
        # sale #1 with customer, without invoice
        self._sale(self.partner_agrolait, self.product_no_vat, 20, 20)
        # sale #2 with customer, without invoice
        self._sale(self.partner_agrolait, self.product_no_vat, 40, 40)

        self._close_session()

        payment_moves = self._get_payment_move(False)

        self.assertEquals(
            len(payment_moves),
            1,
            "Anonymous PoS orders (or uninvoiced PoS Orders) should generate"
            " a uniq payment move when closing the session",
        )

        bank_line = self._get_first_move_line(payment_moves[0], True)
        self.assertEquals(
            bank_line.debit, 100, "incorrect Debit value for 4 sales (50, -10, 20, 40)"
        )

    # Test Section
    def test_02_test_invoiced_orders(self):
        # sale #1 with customer, without invoice
        self._sale(self.partner_agrolait, self.product_no_vat, 1, 1)
        # sale #2 with customer, without invoice
        self._sale(self.partner_agrolait, self.product_no_vat, 10, 10)

        # sale #3 with customer, with invoice
        self._sale(self.partner_agrolait, self.product_no_vat, 20, 20, to_invoice=True)
        # sale #4 with customer, with invoice
        self._sale(self.partner_agrolait, self.product_no_vat, 40, 40, to_invoice=True)

        self._close_session()

        anonymous_payment_moves = self._get_payment_move(False)

        customer_payment_moves = self._get_payment_move(self.partner_agrolait.id)

        self.assertEquals(
            len(anonymous_payment_moves),
            1,
            "orders of a given partner, invoiced and not invoiced, should"
            " generate an anonymous move and one with customer.",
        )

        self.assertEquals(
            len(customer_payment_moves),
            1,
            "orders of a given partner, invoiced and not invoiced, should"
            " generate an anonymous move and one with customer.",
        )

        bank_line = self._get_first_move_line(anonymous_payment_moves[0], True)
        self.assertEquals(
            bank_line.debit, 11, "incorrect Debit value for 2 uninvoiced orders (1, 11)"
        )

        bank_line = self._get_first_move_line(customer_payment_moves[0], True)
        self.assertEquals(
            bank_line.debit, 60, "incorrect Debit value for 2 invoiced orders (20, 40)"
        )
