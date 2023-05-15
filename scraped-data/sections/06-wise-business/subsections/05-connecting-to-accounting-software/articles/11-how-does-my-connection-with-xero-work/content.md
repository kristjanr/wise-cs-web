# Connecting to accounting software  
## How does my connection with Xero work?  
If you haven’t already, connect your Xero account to your Wise account. Once you’ve connected, you can manage the following from your _Connection settings_:

  *  **Import bills to Wise**

  *  **Automatically record transactions to Xero**

  *  **Bank feeds sync**

  *  **Advanced settings**

    * Sync bill and invoice payments

    * Record other transactions as Expenses

    * Connected accounts




###  **Fees**

This feature is available as part of your Wise Business account at no extra cost, but after August 1, 2023, Xero will apply a 0.1% fee of the transfer value for international transfers and 0.2% fee of transfer value for domestic transfers.

###  **Import bills to Wise**

Turn this on to see your unpaid bills in real time and pay them seamlessly from _Bills_. 

We’ll automatically remove or skip any bills you mark as paid in Xero. Note that this means if you have paid a bill through another provider and haven’t marked it as paid in Xero, it will still be visible in your Bills page on Wise.

This is only available for business in the UK at the moment. 

### **Automatically record transactions to Xero**

Turn this on and when you pay or get paid through Wise, we’ll automatically mark bills and invoices as paid in Xero. Check out our bill payment example below.

###  **Advanced settings**

Easily manage which additional settings you want on or off to suit your business needs:

  *  **Sync bill and invoice payments** Turn this on and we’ll mark bills and invoices as paid in Xero when they are paid through Wise. We’ll only mark invoices as paid if the payment details contain the recipient name, amount, and reference.

  *  **Record other transactions as Expenses** Turn this on to record all Wise transactions that don’t have a bill or invoice as an Expense in Xero. We’ll create separate Bank accounts for you — outgoing transactions will be recorded in ‘Expenses (Wise)’ and incoming transactions will be recorded in ‘Revenue (Wise)’.

  *  **Connected bank accounts** We’ll record your transactions to the Xero bank accounts that you select here. If you skipped this step during setup, we’ll search for a corresponding Wise account before recording a transaction. If we don’t find one, we’ll create an account for you — for example ‘Wise - EUR’. 




### **Example bill payment**

In this example, your bill ‘ABC123’ in the amount of £500 has been paid to ‘Supplier 1’ using your Wise GBP account balance. 

Because you connected your Wise GBP account to your Xero bank account named ‘Wise - GBP’ from your _Advanced settings_, the bill payment transaction gets recorded in that account.

And your ‘ABC123’ bill will be marked as paid. 

### **Why was a new clearing account added? What is this?**

We’ll automatically create these clearing accounts in your Chart of Accounts for the following reasons:

  1.  **‘Expenses (Wise)’** or **‘Revenue (Wise)’** : Depending on the payment method, we’re not always able to retrieve information about the bank account that is funding a payment, for example a non-Wise card payment. If this occurs, the unidentified transaction will be recorded in ‘Expenses (Wise)’ for outgoing transactions, and ‘Revenue (Wise)’ for incoming transactions.

  2. ‘ **Cross currency clearing account (Wise)** ’: To help you keep your books tidy, all transactions that include a currency exchange will be revalued to your base currency. Note that this only applies where neither of the currencies being exchanged are your base currency. We’ll record these transactions in ‘Cross currency clearing account (Wise)’ in two parts. First, a transfer from the source currency to your Xero base currency. Second, a transfer from your Xero base currency to your target currency.




Here’s an example:

Your Xero base currency is GBP and you choose to fund a USD (target) payment with your EUR (source) Wise balance. 

  * We’ll record an EUR to GBP Transfer to ‘Wise-service’ with a Reference: “ _This transfer was reported using a clearing account to allow you to reconcile multiple currencies through your base currency._ ”




  * We’ll then record a GBP to USD Transfer to ‘Payment: [Supplier name]’ with a reference.




###  **How will fees be recorded?**

Any Wise fee will be entered automatically as a separate Expense transaction to ‘Wise-service’ in a Bank Account that we’ll create for you called ‘ **Bank charges (Wise)** ’ including a Reference — you can find this in your Chart of Accounts.

###  **How will cash withdrawals be recorded?**

Any cash withdrawal from one of your Wise accounts will be recorded automatically in an account that we’ll create for you called **‘Petty cash (Wise)’** account — you can find this in your Chart of Accounts.

###  **Why am I seeing new Contacts? Why have you created these?**

A new Contact will automatically be created for any incoming or outgoing transaction where we’re unable to match with one of your existing Contacts. This is usually because you don’t have one saved yet. Matching Contacts allows us to automatically record your transactions with more accuracy.

For example, if you spend your Wise card with ‘Supplier 1’, but we don’t find a ‘Supplier 1’ in your Contacts list, we’ll create a ‘Supplier 1’ Contact for you. This new Contact will be used to identify and record all your future transactions with Supplier 1.