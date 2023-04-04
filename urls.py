from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [




    path('bank/details/',views. bankdetails_entry.as_view()),
    path('bank/details/<int:id>/',views. bankdetails_entry.as_view()),
    path('loan/details/',views.generalledg_entry.as_view()),
    path('loan/details/<int:id>/',views.generalledg_entry.as_view()),
    path('cash/',views. overallpayment.as_view()),
    path('ln/details/<int:id>/',views.generalledg_entry_loanwise.as_view()),
    path('payment/sum/',views.  payments_aggregate.as_view()),
    path('sales/overall/',views.  salespaymentall_aggr.as_view()), 
    path('daybook/',views.  salespaymentall_aggr_daybook.as_view()), 
    path('ln/details/all/',views.generalledg_entry_loanwise.as_view()),
    path('salespayment/',views.salespaymentprocess.as_view()), #post salespayment
    path('salespayment/all/',views.salesprintpayment.as_view()),#get sales all
    path('salespayment/all/<int:id>/',views.salesdeletepayment.as_view()), #delete payment sales
    path('sales/paymentforinvoice/<int:id>/',views.salesrefupdate.as_view()), #refupdate
    path('purchaseinvoice/',views.purchasewisebalance.as_view()),#purchaseget
    path('salesbalance/',views.customerbalance.as_view()),
    path('sales/balance/list/<int:id>/',views.salesinvoicebalancedetails.as_view()),
    path('purchase/balance/list/<int:id>/', views.purchaseinvoicebalancedetails.as_view()),
    
    path('purchasepayment/',views.purchasepaymentprocess.as_view()),
    path('purchasepayment/all/',views.purchaseprintpayment.as_view()),#getall
    path('purchasepayment/all/<int:id>/',views.purchasedeletepayment.as_view()),#deletepayment
    path('salesbe/',views.salespayment.as_view()),
    path('purchase/balance/<int:id>/', views.purchasebalancedetails.as_view()),#invoice balance based on companyid
    path('purchase/paymentforinvoice/<int:id>/',views.purchaserefupdate.as_view()), #refupdate
    path('purchase/enter/', views.purchasepaymentprocessenter.as_view()),

    path('report/sales/',views.paymentreports_sales.as_view()),
    path('report/purchase/',views.paymentreports_purchase.as_view()),
    path('sales/total/',views.salesoverallbalance.as_view()),
    path('purchase/total/',views.purchasebalance.as_view()),

   path('sales/sum/',views.salesaggrgate.as_view(),name='sale'),
   path('purchase/sum/',views.purchaseaggregate.as_view(),name='sale'),
   
  path('debit/payment/',views.debitnoteentry.as_view(),name='sale'),
  path('debit/payment/purchase/',views.debitnoteentrypurchase.as_view(),name='sale'),


  ### report sales 
  path('report/sales/payment/all/',views.sales_payment_report_sheet.as_view()),
  path('report/purchase/payment/all/',views.purchasebillpayment_reports.as_view()),

  path('company/sales/payment/',views.companytoSalesPayment.as_view()),
  path('company/sales/payment/<int:id>/',views.companytoSalesPayment.as_view()),
  path('gst/reports/',views.GstReports.as_view()),
  path('company/purchase/payment/',views.companytoPurchasePayment.as_view()),
  path('company/purchase/payment/<int:id>/',views.companytoPurchasePayment.as_view()),

  path('cash/opening/',views.ledger_Openingqty.as_view()),
  path('sales/statement/opening/',views.sales_statement_Openingqty.as_view()),
  path('yr/purchase/statement/opening/',views.purchase_statement_Openingqty_yr.as_view()),
  path('yr/purchase/statement/opening/<int:type>/',views.purchase_statement_Openingqty_yr.as_view()),
  path('yr/sales/statement/opening/',views.sales_statement_Openingqty_yr.as_view()),
  path('yr/sales/statement/opening/<int:type>/',views.sales_statement_Openingqty_yr.as_view()),
  path('yr/vendor/statement/opening/',views.vendor_statement_Openingqty_yr.as_view()),
  path('yr/vendor/statement/opening/<int:type>/',views.vendor_statement_Openingqty_yr.as_view()),
  path('purchase/statement/opening/',views.purchase_statement_Openingqty.as_view()),
  path('ledger/',views.ledgerview.as_view()), 
  path('ledger/pettycash/',views.ledgerview_t.as_view()), 
  path('ledger/<int:id>/',views.ledgerview.as_view()),
  path('bank/ledger/<int:id>/',views.ledgerview_t.as_view()),
  path('bank/ledger/',views.ledgerview.as_view()),
  path('company/sales/balance/details/report/',views.CompanySalesPendingBalance.as_view()),
  path('invoicewise/sales/balance/report/',views.InvoicewiseSalesBalance.as_view()),
  path('sales/payment/balance/details/report/',views.SalesPaymentBalanceDetails.as_view()),

  path('company/purchase/balance/details/report/',views.CompanyPurchasePendingBalance.as_view()),
  path('invoicewise/purchase/balance/report/',views.InvoicewisePurchaseBalance.as_view()),
  path('purchase/payment/balance/details/report/',views.PurchasePaymentBalanceDetails.as_view()),

  path('sales/payment/update/<int:id>/',views.SalesPaymentUpdate.as_view()),
  path('purchase/payment/update/<int:id>/',views.PurchasePaymentUpdate.as_view()),



  path('vendor/payments/',views.VendorPaymentDetails.as_view()),
  path('vendor/payments/<int:id>/',views.VendorPaymentDetails.as_view()),


  path('vendor/payments/get/',views.VendorPaymentGetByID.as_view()),
  path('vendor/payments/get/<int:id>/',views.VendorPaymentGetByID.as_view()),


  path('vendor/company/balance/details/report/',views.VendorCompanyPendingBalance.as_view()),
  path('invoicewise/vendor/balance/report/',views.InvoicewiseVendorBalance.as_view()),
  path('vendor/payment/balance/details/report/',views.VendorPaymentBalanceDetails.as_view()),



  path('vendor/company/payment/',views.VendorCompanyPaymentGet.as_view()),
  path('vendor/company/payment/<int:id>/',views.VendorCompanyPaymentGet.as_view()),

  
  path('company/wise/purchase/opening/<int:id>/',views.PurcahseOpeningGetPatch.as_view()),
  path('company/wise/sales/opening/<int:id>/',views.SalesOpeningGetPatch.as_view()),
  path('vendor/company/opening/<int:id>/',views.VendorOpeningGetPatch.as_view()),

  
  path('sales/reference/update/<int:id>/',views.SalesRefUpdate.as_view()),
  path('purchase/reference/update/<int:id>/',views.PurchaseRefUpdate.as_view()),
  path('vendor/reference/update/<int:id>/',views.VendorRefUpdate.as_view()),

  path('sales/company/year/opening/update/<int:id>/',views.SalesCompanyYearOpeningUpdate.as_view()),
  path('purchase/company/year/opening/update/<int:id>/',views.PurchaseCompanyYearOpeningUpdate.as_view()),
  path('vendor/company/year/opening/update/<int:id>/',views.VendorCompanyYearOpeningUpdate.as_view()),

  path('debit/',views.debit_note_view.as_view()),
  path('debit/<int:id>/',views.debit_note_view.as_view()),

]