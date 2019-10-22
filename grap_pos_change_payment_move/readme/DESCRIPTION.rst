this module intents to manage correctly payment move lines generated from
point of sale.

By default, with Odoo, an account move is create by payment, that generates
a lot of useless account moves for an accountant.

With this module, when closing a PoS session, a single account move is created
for each combination of:

* journal
* pos order partner (*)
* account (counterpart account)

(*) : Note that if a pos order is associated to a partner, without an invoice,
the partner is ignored, reducing more, moves quantity.

This module could be used with ``grap_pos_change_sale_move``.

**Important Note**

Once installed, closing a PoS session will not generate ``account.payment``
anymore.
