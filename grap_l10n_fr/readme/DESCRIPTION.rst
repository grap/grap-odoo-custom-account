This module extends the functionality of french Accounting module
to make easy the creation of taxes and accounts for GRAP.

**``account.tax.template`` Model**

* Add a new field ``active``

**``account.tax.template`` Datas**

* Rename ``name`` : TVA <achat/vente> <xx%> basé sur prix <HT/TTC>
* Rename ``code`` : TVA-<HA/VT>-xx.x-<HT/TTC>
* Disable VAT with 8,5% rate (via the active field)

**``account.account.template`` Model**

* Add a new field ``active``

**``account.account.template`` Datas**

* Create specific accounts
* Disable somes accounts. (via the active field)
* rename or change type of some accounts

**``account.chart.template`` Model**

* do not initialize ``account_sale_tax_id`` and ``purchase_sale_tax_id``
  when installing new chart of account

**``account.chart.template`` Data**

* Set ``digit_codes`` (No. of Digits to use for account code)
  to 3. (instead of 6)

**``account.tax.code.template`` Datas**

* Add a new field ``active``
* Add EBP code

**``account.fiscal.position.template`` Model**

* Add a new field ``active``

**``account.fiscal.position.template`` Datas**

* Rename existing Fiscal Positition Templates
* Create 'Non Assujetti' Fiscal Positition Template
* Disable 'Hors UE + DOM-TOM' Fiscal Position (via the active field)

**``account.fiscal.position.tax.template`` Model**

* Add a new field ``active``

**``account.fiscal.position.tax.template`` Datas**

* Disable VAT with 8,5% rate (via the active field)
