# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()

        self.PosSession = self.env["pos.session"]
        self.PosOrder = self.env["pos.order"]
        self.AccountJournal = self.env["account.journal"]
        self.AccountMove = self.env["account.move"]
        self.AccountMoveLine = self.env["account.move.line"]

        self.pricelist = self.env.ref("product.list0")

        self.product_no_vat = self.env.ref(
            "grap_pos_change_sale_move_test.product_no_vat"
        )
        self.product_vat_5_707 = self.env.ref(
            "grap_pos_change_sale_move_test.product_5_707"
        )
        self.product_vat_20_701 = self.env.ref(
            "grap_pos_change_sale_move_test.product_20_701"
        )
        self.product_vat_20_707 = self.env.ref(
            "grap_pos_change_sale_move_test.product_20_707"
        )
        self.product_vat_5_20_701 = self.env.ref(
            "grap_pos_change_sale_move_test.product_5_20_701"
        )
        self.partner_agrolait = self.env.ref("base.res_partner_2")

        self.cash_journal = self.AccountJournal.search([("type", "=", "cash")])[0]
        self.partner_account = self.env.ref("l10n_generic_coa.1_conf_a_recv")
        self.account_vat_5 = self.env.ref(
            "grap_pos_change_sale_move_test.account_vat_5"
        )
        self.account_vat_20 = self.env.ref(
            "grap_pos_change_sale_move_test.account_vat_20"
        )
        self.sale_vat_5 = self.env.ref("grap_pos_change_sale_move_test.sale_vat_5")
        self.sale_vat_20 = self.env.ref("grap_pos_change_sale_move_test.sale_vat_20")
        self.account_income_701 = self.env.ref(
            "grap_pos_change_sale_move_test.account_income_701"
        )
        self.account_income_707 = self.env.ref(
            "grap_pos_change_sale_move_test.account_income_707"
        )

        # Create a new pos config and open it
        self.pos_config = self.env.ref("point_of_sale.pos_config_main").copy()
        self.pos_config.open_session_cb()
        self.pos_session = self.pos_config.current_session_id

        self.sale_journal = self.pos_config.journal_id
        self.uid = 1  # set the user to be admin user
        self.order_uid = 1

    # Tools function section
    def _sale(self, partner, product, vat_excl, vat_incl, to_invoice=False):
        # Create order
        account_id = self.env.user.partner_id.property_account_receivable_id.id
        statement_id = self.pos_config.current_session_id.statement_ids[0].id
        self.order_uid += 1
        order_data = {
            "id": "0006-001-000%d" % (self.order_uid),
            "to_invoice": to_invoice,
            "data": {
                "pricelist_id": self.pricelist.id,
                "user_id": 1,
                "sequence_number": self.order_uid,
                "name": "Order 0006-001-000%d" % self.order_uid,
                "partner_id": partner and partner.id,
                "pos_session_id": self.pos_session.id,
                "lines": [
                    [
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "price_unit": vat_excl,
                            "qty": 1,
                            "price_subtotal": vat_excl,
                            "price_subtotal_incl": vat_incl,
                            "tax_ids": [(6, False, product.taxes_id.ids)],
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
                "creation_date": "2018-09-27 15:51:03",
                "fiscal_position_id": False,
                "uid": "00001-001-000%d" % self.order_uid,
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

    def _get_sale_moves(self, session=False):
        if session:
            return self.AccountMove.search(
                [
                    ("ref", "=", self.pos_session.name),
                    ("journal_id", "=", self.sale_journal.id),
                ]
            )
        else:
            return self.AccountMove.search([("journal_id", "=", self.sale_journal.id)])

    def _get_move_line(
        self, move, account, tax_ids, message, partner_id=None, max_nb_line=1
    ):
        domain = [("move_id", "=", move.id), ("account_id", "=", account.id)]
        if tax_ids:
            domain.append(("tax_ids", "in", tax_ids))
        else:
            domain.append(("tax_ids", "=", False))
        if partner_id:
            domain.append(("partner_id", "=", partner_id.id))
        elif partner_id is not None:
            domain.append(("partner_id", "=", False))
        res = self.AccountMoveLine.search(domain)
        # Filter base on the tax_ids
        res = res.filtered(lambda rec: sorted(rec.tax_ids.ids) == sorted(tax_ids))
        self.assertEquals(
            len(res), max_nb_line, "Expected %d line(s) for %s" % (max_nb_line, message)
        )
        return res

    # Test Section
    def test_01_move_many_orders_groupby_account_tax(self):
        company = self.pos_session.config_id.company_id
        company.pos_sale_move_policy = "groupby_account_tax"
        sale_entries_before = len(self._get_sale_moves(False))
        # sale #1
        self._sale(False, self.product_no_vat, 10, 10)
        # sale #2
        self._sale(False, self.product_no_vat, 40, 40)
        # sale #3
        self._sale(False, self.product_no_vat, 20, 20)

        self._close_session()

        sale_entries_after = len(self._get_sale_moves(False))

        self.assertEquals(
            sale_entries_before + 1,
            sale_entries_after,
            "Closing session with orders should generate 1 unique sale entry.",
        )

    def test_02_test_account_and_vat_groupby_account_tax(self):
        company = self.pos_session.config_id.company_id
        company.pos_sale_move_policy = "groupby_account_tax"
        # sale #1 product VAT 5% / Account 707
        self._sale(False, self.product_vat_5_707, 210, 220.5)
        # sale #2 product VAT 5% / Account 707
        self._sale(False, self.product_vat_5_707, 70, 73.5)
        # sale #3 product VAT 20% / Account 707
        self._sale(False, self.product_vat_20_707, 160, 192)
        # sale #4 product VAT 20% / Account 701
        self._sale(False, self.product_vat_20_701, 80, 96)
        # sale #5 product no VAT / Account 707 with customer
        self._sale(self.partner_agrolait, self.product_no_vat, 1000, 1000)
        # sale #6 product no VAT / Account 707 invoiced
        self._sale(
            self.partner_agrolait, self.product_no_vat, 50000, 50000, to_invoice=True
        )

        self._close_session()

        sale_moves = self._get_sale_moves(True)
        self.assertEquals(
            len(sale_moves),
            1,
            "Anonymous PoS orders (or uninvoiced PoS Orders) should generate"
            " a uniq sale move when closing the session",
        )
        sale_move = sale_moves[0]

        # Check Line quantity
        self.assertEquals(
            len(sale_move.line_ids),
            7,
            "Incorrect quantity of lines."
            "Expected : 4 sale lines + 2 tax lines + 1 counterpart",
        )

        # Check Customer Line
        line = self._get_move_line(
            sale_move, self.partner_account, [], "counter part line"
        )
        self.assertEquals(
            line.debit,
            220.5 + 73.5 + 96 + 192 + 1000,
            "incorrect Debit value for Counter part line.",
        )

        # Check VAT Line (5%)
        line = self._get_move_line(
            sale_move, self.account_vat_5, [], "vat line (vat 5)%"
        )
        self.assertEquals(
            line.credit, 10.5 + 3.5, "incorrect Credit value for VAT line (5%)."
        )
        self.assertEquals(
            line.tax_line_id.id,
            self.sale_vat_5.id,
            "Vat tax line (5%) doesn't have correct 'Originator tax'",
        )

        # Check VAT Line (20%)
        line = self._get_move_line(
            sale_move, self.account_vat_20, [], "vat line (vat 20%)"
        )
        self.assertEquals(
            line.credit, 32 + 16, "incorrect Credit value for VAT line (20%)."
        )
        self.assertEquals(
            line.tax_line_id.id,
            self.sale_vat_20.id,
            "Vat tax line (20%) doesn't have correct 'Originator tax'",
        )

        # Check Income Line 707 (no vat)
        line = self._get_move_line(
            sale_move, self.account_income_707, [], "Sale line 707 (No VAT)"
        )
        self.assertEquals(
            line.credit, 1000, "incorrect Credit value for Income 707 line (No VAT)."
        )

        # Check Income Line 707(5%)
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [self.sale_vat_5.id],
            "Sale line 707 (vat 5%)",
        )
        self.assertEquals(
            line.credit,
            210.0 + 70.0,
            "incorrect Credit value for Income 707 line (5%).",
        )

        # Check Income Line 707(20%)
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [self.sale_vat_20.id],
            "Sale line 707 (vat 20%)",
        )
        self.assertEquals(
            line.credit, 160, "incorrect Credit value for Income 707 line (20%)."
        )

        # Check Income Line 701(20%)
        line = self._get_move_line(
            sale_move,
            self.account_income_701,
            [self.sale_vat_20.id],
            "Sale line 701 (vat 20%)",
        )
        self.assertEquals(
            line.credit, 80, "incorrect Credit value for Income 701 line (20%)."
        )

        # Check the state of the account move
        self.assertEquals(sale_move.state, "posted", "Sale Move should be posted")

    def test_03_move_may_orders_groupby_account_tax_partner(self):
        company = self.pos_session.config_id.company_id
        company.pos_sale_move_policy = "groupby_account_tax_partner"
        sale_entries_before = len(self._get_sale_moves(False))
        # sale #1
        self._sale(False, self.product_no_vat, 10, 10)
        # sale #2
        self._sale(False, self.product_no_vat, 40, 40)
        # sale #3
        self._sale(self.partner_agrolait, self.product_no_vat, 20, 20)
        # sale #4
        self._sale(self.partner_agrolait, self.product_no_vat, 50, 50)

        self._close_session()

        sale_entries_after = len(self._get_sale_moves(False))

        self.assertEquals(
            sale_entries_before + 1,
            sale_entries_after,
            "Closing session with orders should generate 1 unique sale entry.",
        )

    def test_04_test_account_and_vat_groupby_account_tax_partner(self):
        company = self.pos_session.config_id.company_id
        company.pos_sale_move_policy = "groupby_account_tax_partner"
        # sale product no VAT / Account 707
        self._sale(False, self.product_no_vat, 10, 10)

        # sale product VAT 5% / Account 707
        self._sale(False, self.product_vat_5_707, 210, 220.5)
        # sale product VAT 5% / Account 707
        self._sale(False, self.product_vat_5_707, 70, 73.5)

        # sale product VAT 20% / Account 707
        self._sale(False, self.product_vat_20_707, 160, 192)

        # sale product VAT 20% / Account 701
        self._sale(False, self.product_vat_20_701, 80, 96)

        # sale product VAT 5% and 20% / Account 701
        self._sale(False, self.product_vat_5_20_701, 30, 37.5)

        # sale product no VAT / Account 707 with customer
        self._sale(self.partner_agrolait, self.product_no_vat, 1000, 1000)

        # sale product VAT 5% / Account 707 with customer
        self._sale(self.partner_agrolait, self.product_vat_5_707, 210, 220.5)
        # sale product VAT 5% / Account 707 with customer
        self._sale(self.partner_agrolait, self.product_vat_5_707, 70, 73.5)

        # sale product VAT 20% / Account 707 with customer
        self._sale(self.partner_agrolait, self.product_vat_20_707, 160, 192)

        # sale product VAT 20% / Account 701 with customer
        self._sale(self.partner_agrolait, self.product_vat_20_701, 80, 96)

        # sale product VAT 5% and 20% / Account 701 with customer
        self._sale(self.partner_agrolait, self.product_vat_5_20_701, 30, 37.5)

        # sale product no VAT / Account 707 invoiced
        self._sale(
            self.partner_agrolait, self.product_no_vat, 50000, 50000, to_invoice=True
        )

        self._close_session()

        sale_moves = self._get_sale_moves(True)
        self.assertEquals(
            len(sale_moves),
            1,
            "Anonymous PoS orders (or uninvoiced PoS Orders) should generate"
            " a uniq sale move when closing the session",
        )
        sale_move = sale_moves[0]

        # Check Line quantity
        self.assertEquals(
            len(sale_move.line_ids),
            16,
            "Incorrect quantity of lines."
            "Expected : (5 * 2) sale lines + (2 * 2) tax lines "
            "+ (2 * 1) counterpart",
        )

        # Check Customer Line
        line = self._get_move_line(
            sale_move, self.partner_account, [], "counter part line", False
        )
        self.assertEquals(
            line.debit,
            220.5 + 73.5 + 96 + 192 + 37.5 + 10,
            "incorrect Debit value for Counter part line.",
        )
        line = self._get_move_line(
            sale_move,
            self.partner_account,
            [],
            "counter part line",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.debit,
            220.5 + 73.5 + 96 + 192 + 37.5 + 1000,
            "incorrect Debit value for Counter part line.",
        )

        # Check VAT Line (5%)
        line = self._get_move_line(
            sale_move, self.account_vat_5, [], "vat line (vat 5)%", False
        )
        self.assertEquals(
            line.credit, 10.5 + 3.5 + 1.5, "incorrect Credit value for VAT line (5%)."
        )
        self.assertEquals(
            line.tax_line_id.id,
            self.sale_vat_5.id,
            "Vat tax line (5%) doesn't have correct 'Originator tax'",
        )
        line = self._get_move_line(
            sale_move,
            self.account_vat_5,
            [],
            "vat line (vat 5)%",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit, 10.5 + 3.5 + 1.5, "incorrect Credit value for VAT line (5%)."
        )
        self.assertEquals(
            line.tax_line_id.id,
            self.sale_vat_5.id,
            "Vat tax line (5%) doesn't have correct 'Originator tax'",
        )

        # Check VAT Line (20%)
        line = self._get_move_line(
            sale_move, self.account_vat_20, [], "vat line (vat 20%)", False
        )
        self.assertEquals(
            line.credit, 32 + 16 + 6, "incorrect Credit value for VAT line (20%)."
        )
        self.assertEquals(
            line.tax_line_id.id,
            self.sale_vat_20.id,
            "Vat tax line (20%) doesn't have correct 'Originator tax'",
        )
        line = self._get_move_line(
            sale_move,
            self.account_vat_20,
            [],
            "vat line (vat 20%)",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit, 32 + 16 + 6, "incorrect Credit value for VAT line (20%)."
        )
        self.assertEquals(
            line.tax_line_id.id,
            self.sale_vat_20.id,
            "Vat tax line (20%) doesn't have correct 'Originator tax'",
        )

        # Check Income Line 707 (no vat)
        line = self._get_move_line(
            sale_move, self.account_income_707, [], "Sale line 707 (No VAT)", False
        )
        self.assertEquals(
            line.credit, 10, "incorrect Credit value for Income 707 line (No VAT)."
        )
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [],
            "Sale line 707 (No VAT)",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit, 1000, "incorrect Credit value for Income 707 line (No VAT)."
        )

        # Check Income Line 707(5%)
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [self.sale_vat_5.id],
            "Sale line 707 (vat 5%)",
            False,
        )
        self.assertEquals(
            line.credit,
            210.0 + 70.0,
            "incorrect Credit value for Income 707 line (5%).",
        )
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [self.sale_vat_5.id],
            "Sale line 707 (vat 5%)",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit,
            210.0 + 70.0,
            "incorrect Credit value for Income 707 line (5%).",
        )

        # Check Income Line 707(20%)
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [self.sale_vat_20.id],
            "Sale line 707 (vat 20%)",
            False,
        )
        self.assertEquals(
            line.credit, 160, "incorrect Credit value for Income 707 line (20%)."
        )
        line = self._get_move_line(
            sale_move,
            self.account_income_707,
            [self.sale_vat_20.id],
            "Sale line 707 (vat 20%)",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit, 160, "incorrect Credit value for Income 707 line (20%)."
        )

        # Check Income Line 701 (20%)
        line = self._get_move_line(
            sale_move,
            self.account_income_701,
            [self.sale_vat_20.id],
            "Sale line 701 (vat 20%)",
            False,
        )
        self.assertEquals(
            line.credit, 80, "incorrect Credit value for Income 701 line (20%)."
        )
        line = self._get_move_line(
            sale_move,
            self.account_income_701,
            [self.sale_vat_20.id],
            "Sale line 701 (vat 20%)",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit, 80, "incorrect Credit value for Income 701 line (20%)."
        )

        # Check Income Line 701 (5% and 20%)
        line = self._get_move_line(
            sale_move,
            self.account_income_701,
            [self.sale_vat_20.id, self.sale_vat_5.id],
            "Sale line 701 (vat 20%)",
            False,
        )
        self.assertEquals(
            line.credit, 30, "incorrect Credit value for Income 701 line (20%)."
        )
        line = self._get_move_line(
            sale_move,
            self.account_income_701,
            [self.sale_vat_20.id, self.sale_vat_5.id],
            "Sale line 701 (vat 20%)",
            self.partner_agrolait,
        )
        self.assertEquals(
            line.credit, 30, "incorrect Credit value for Income 701 line (20%)."
        )

        # Check the state of the account move
        self.assertEquals(sale_move.state, "posted", "Sale Move should be posted")

    def test_05_empty_sale_order(self):
        company = self.pos_session.config_id.company_id
        company.pos_sale_move_policy = "groupby_account_tax_partner"
        sale_entries_before = len(self._get_sale_moves(False))

        # We make no sales

        self._close_session()

        sale_entries_after = len(self._get_sale_moves(False))
        sale_moves = self._get_sale_moves(True)

        self.assertEquals(
            sale_entries_before + 1,
            sale_entries_after,
            "Closing session with no orders should generate 1 unique sale entry.",
        )

        sale_move = sale_moves[0]

        # Check Line quantity
        self.assertEquals(
            len(sale_move.line_ids),
            0,
            "No move.line should be generated when no orders during pos.session",
        )
