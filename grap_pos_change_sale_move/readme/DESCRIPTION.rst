This module intents to manage correctly sale move lines generated from
point of sale.

By default, with Odoo, account move lines are create by customer, even if
an invoices is not generated, and the date move is the date of the start of
the session. If a session is opened at the end of a year (or a month) and
closed in the next year (or month), it generates account errors (for years)
or analysis errors (for

With this module, when closing a PoS session, you can chose how account
move are created.

Three different aggregation mode are defined.

*Standard Mode*: the default Odoo behaviour is not changed.

*Group by account and tax Mode*:
In each account move

* a 'tax' line is created for each
    * VAT.
* a 'product' line is created for each
    * products accounts
    * VAT
* a unique 'customer' line is created

*Group by account, tax and partner Mode*:
In each account move

* a 'tax' line is created for each
    * VAT.
* a 'product' line is created for each
    * products accounts
    * VAT
    * customer
* a unique 'customer' line is created

This module could be used with ``grap_pos_change_payment_move``.
