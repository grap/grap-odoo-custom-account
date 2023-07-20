
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/grap/grap-odoo-custom-account/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/grap/grap-odoo-custom-account/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/grap/grap-odoo-custom-account/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/grap/grap-odoo-custom-account/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/grap/grap-odoo-custom-account/branch/12.0/graph/badge.svg)](https://codecov.io/gh/grap/grap-odoo-custom-account)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Custom Account Odoo modules for GRAP

This repository contains Odoo modules developped by the company GRAP for custom accounting needs. They are shared in the hope that it will be useful.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[grap_account_change_invoice_move](grap_account_change_invoice_move/) | 12.0.1.0.2 |  | Remove product from the keys during account moves generation from invoices
[grap_account_export](grap_account_export/) | 12.0.1.0.2 |  | Add a placeholder menu for Accounting Export
[grap_account_export_ebp](grap_account_export_ebp/) | 12.0.2.0.2 |  | GRAP - Export accounting moves to EBP
[grap_account_export_ebp_test](grap_account_export_ebp_test/) | 12.0.1.0.7 |  | GRAP - Export accounting moves to EBP - Test
[grap_account_export_partner_code](grap_account_export_partner_code/) | 12.0.1.0.3 |  | Add an account export code field on partner model
[grap_account_export_partner_code_intercompany_trade_base](grap_account_export_partner_code_intercompany_trade_base/) | 12.0.1.0.2 |  | GRAP - Account Export - Partner Code - Intercompany Trade
[grap_custom_account_invoice_workflow](grap_custom_account_invoice_workflow/) | 12.0.1.0.8 |  | GRAP - Custom Invoice workflow
[grap_custom_account_invoice_workflow_test](grap_custom_account_invoice_workflow_test/) | 12.0.1.0.2 |  | GRAP - Custom Invoice workflow
[grap_custom_account_payment_workflow](grap_custom_account_payment_workflow/) | 12.0.1.0.4 |  | Add Payment Check workflow
[grap_l10n_fr](grap_l10n_fr/) | 12.0.1.1.9 |  | Custom changes of l10n_fr module for GRAP
[grap_pos_change_payment_move](grap_pos_change_payment_move/) | 12.0.1.1.4 |  | Make Bank accounting moves from PoS acceptable for accoutants
[grap_pos_change_sale_move](grap_pos_change_sale_move/) | 12.0.1.0.3 |  | Make Sale accounting moves from PoS acceptable for accoutants
[grap_pos_change_sale_move_test](grap_pos_change_sale_move_test/) | 12.0.1.0.4 |  | Test the module grap_pos_change_sale_move
[grap_pos_reconcile](grap_pos_reconcile/) | 12.0.1.0.4 |  | Reconcile PoS entries

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to GRAP
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

## About GRAP

<p align="center">
   <img src="http://www.grap.coop/wp-content/uploads/2016/11/GRAP.png" width="200"/>
</p>

GRAP, [Groupement Régional Alimentaire de Proximité](http://www.grap.coop) is a
french company which brings together activities that sale food products in the
region Rhône Alpes. We promote organic and local food, social and solidarity
economy and cooperation.

The GRAP IT Team promote Free Software and developp all the Odoo modules under
AGPL-3 Licence.

You can find all these modules here:

* on the [OCA Apps Store](https://odoo-community.org/shop?&search=GRAP)
* on the [Odoo Apps Store](https://www.odoo.com/apps/modules/browse?author=GRAP).
* on [Odoo Code Search](https://odoo-code-search.com/ocs/search?q=author%3AOCA+author%3AGRAP)

You can also take a look on the following repositories:

* [grap-odoo-incubator](https://github.com/grap/grap-odoo-incubator)
* [grap-odoo-business](https://github.com/grap/grap-odoo-business)
* [grap-odoo-business-supplier-invoice](https://github.com/grap/grap-odoo-business-supplier-invoice)
* [odoo-addons-logistics](https://github.com/grap/odoo-addons-logistics)
* [odoo-addons-cae](https://github.com/grap/odoo-addons-cae)
* [odoo-addons-intercompany-trade](https://github.com/grap/odoo-addons-intercompany-trade)
* [odoo-addons-multi-company](https://github.com/grap/odoo-addons-multi-company)
* [odoo-addons-company-wizard](https://github.com/grap/odoo-addons-company-wizard)
