from django.db import models
from master .views import *
from django.db import models
import datetime
from master.models import *
from tools_management.models import *
# exposed_request=''


# def DebitNoteBill():

#     lastreportnumber = depit_note_invoice.objects.current_financialyear(id = int(exposed_request.user.tenant_company.id),stdate=exposed_request.headers['sdate'],lstdate=exposed_request.headers['ldate']).order_by('id').last()

#     debit_prefix = YearOpeningNumbers.objects.current_financialyear(id = int(exposed_request.user.tenant_company.id),stdate=exposed_request.headers['sdate'],lstdate=exposed_request.headers['ldate']).last()

#     if not lastreportnumber :

#         if debit_prefix.start_debit_note_bill_prefix == None:

#             return "DNB" + debit_prefix.start__debit_note_bill_no
#         else:
            
#             return debit_prefix.start_debit_note_bill_prefix + debit_prefix.start_debit_note_bill_no

#     else:
#         report_no = lastreportnumber.running_numbers
#         newreportno_int=report_no +1
#         if debit_prefix.start_debit_note_bill_prefix == None:

#             prefix = 'DNB'
            
#         else:

#             prefix = debit_prefix.start_debit_note_bill_prefix
            
#         new_number = prefix + str(newreportno_int)
#         return new_number

# def DebitNote_RunningNumber():

#     lastreportnumber = depit_note_invoice.objects.current_financialyear(id = int(exposed_request.user.tenant_company.id),stdate=exposed_request.headers['sdate'],lstdate=exposed_request.headers['ldate']).order_by('id').last()

#     dc_prefix = YearOpeningNumbers.objects.current_financialyear(id = int(exposed_request.user.tenant_company.id),stdate=exposed_request.headers['sdate'],lstdate=exposed_request.headers['ldate']).last()

#     if not lastreportnumber :
#         return int(dc_prefix.start_debit_note_bill_no)
#     report_no = lastreportnumber.running_numbers
#     newreportno_int=report_no +1
#     return newreportno_int




class FinancialQuerySet(models.QuerySet):
    def current_financialyear(self, id, stdate, lstdate):
        cdatec = datetime.datetime.now()
        if (stdate == '' or lstdate == ''):
            if(cdatec.month <= 3):
                current_finyear_start = datetime.datetime(cdatec.year-1, 4, 1)
                current_finyear_end = datetime.datetime(cdatec.year, 3, 31)
            else:
                current_finyear_start = datetime.datetime(cdatec.year, 4, 1)
                current_finyear_end = datetime.datetime(cdatec.year + 1, 3, 31)
        else:
            current_finyear_start = stdate
            current_finyear_end = lstdate

        return self.filter(financial_period__gte=current_finyear_start, financial_period__lte=current_finyear_end,
                           tenant_id=id)

class TenantQuerySet(models.QuerySet):
    def current_tenant(self, id,stdate='',lstdate=''):
        return self.filter(tenant_id=id)


class Bank_details(models.Model):
    account_no = models.CharField(null=True, max_length=1024)
    class type_choices(models.IntegerChoices):
        SB = 1
        CA = 2
        Loan = 3
    account_type=models.IntegerField(choices=type_choices.choices, default=1)
    ifsc_code = models.CharField(null=True, max_length=1024)
    bank_name = models.CharField(null=True, max_length=1024)
    branch_name = models.CharField(null=True, max_length=1024)
    tenant_id=models.PositiveIntegerField(null=True,blank=True)
    description = models.TextField(null=True)
    cancel = models.BooleanField(default=False, null=True)
    ln=models.BooleanField(default=False)
    ln_close=models.BooleanField(default=False)
    financial_period = models.DateField(auto_now=True)
    objects = TenantQuerySet.as_manager()   

class loan_paymentdetails(models.Model):
    class type_choices(models.IntegerChoices):
        cash = 1
        bank = 2
   
    payment_type = models.IntegerField(choices=type_choices.choices, default=1)
    close = models.BooleanField(default=False)
    bank_ref=models.ForeignKey(Bank_details,related_name='Ba_details',null=True,on_delete=models.CASCADE)
    bank_i=models.PositiveIntegerField(null=True,blank=True)
    payment_refno = models.CharField(max_length=60,default=None, null=True)
    premium_amount = models.FloatField(default=0)
    loan=models.BooleanField(default=False)
    inte_amount= models.FloatField(default=0)
    balance_amount= models.FloatField(default=0)
    ln=models.BooleanField(default=False)
   
    amount=models.FloatField(default=0,null=True)
    payment_refdate=models.DateField(default=None,null=True,blank=True)
    payment_date=models.DateField(auto_now=False, auto_now_add=False, null=True)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    notes=models.TextField(blank=True,null=True)
    objects = FinancialQuerySet.as_manager()


    def __str__(self):
        return str(self.premium_amount)

payment_ref=[(1,'cashref'),(2,'chequeno'),(3,'bankrefno')]

class general_ledger(models.Model):
    
    credit=models.FloatField(default=0,null=True,blank=True)
    bank_ref=models.ForeignKey(Bank_details,related_name='B_details',null=True,on_delete=models.CASCADE)
    debit=models.FloatField(default=0,null=True,blank=True)
    balance=models.FloatField(default=0,null=True,blank=True)
    paymentcode=models.PositiveIntegerField(null=True,blank=True)
    opening=models.BooleanField(default=False)
    description=models.TextField(blank=True,null=True)
    cash = models.BooleanField(default=False)
    petty_cash= models.BooleanField(default=False)
    bank = models.BooleanField(default=False)
    financial_period = models.DateField(auto_now=True)
    objects = FinancialQuerySet.as_manager()
    tenant_id = models.IntegerField()
   


    def __str__(self):
        return str(self.credit)


class sales_paymentdetails(models.Model):
    class sales_type_choices(models.IntegerChoices):
        debitnote = 1
        normalpayment = 2

    class debit_type_choices(models.IntegerChoices):
        tds = 1
        esipf = 2
        material_rejection = 3

    sales_type = models.IntegerField(choices=sales_type_choices.choices, default=1)
    debit_type = models.IntegerField(choices=debit_type_choices.choices, null=True)
    cash = models.BooleanField(default=False)
    cheque = models.BooleanField(default=False)
    bank = models.BooleanField(default=False)
    close = models.BooleanField(null=True)
    bank_payment = models.BooleanField(null=True)
    payment_refno_type = models.CharField(max_length=50,choices=payment_ref,default=1)
    payment_refno = models.CharField(max_length=60,default=None, null=True)
    debit_refno = models.CharField(max_length=60,default=None, null=True)
    payment_amount = models.FloatField(default=0,null=True)
    general_le = models.ForeignKey(general_ledger,related_name='ldetails',null=True,on_delete=models.CASCADE,blank=True)
    companycode = models.ForeignKey(CompanyDetails,related_name='sales_payment_details',null=True,on_delete=models.CASCADE)
    payment_refdate=models.DateField(default=None,null=True,blank=True)
    debit_refdate=models.DateField(default=None,null=True,blank=True)
    payment_date=models.DateField(auto_now=False, auto_now_add=False, null=True)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    notes=models.TextField(blank=True,null=True)
    billrefered=models.BooleanField(default=False)
    semirefrenced=models.BooleanField(default=False)
    unreferenced_payment = models.FloatField(default=0)
    objects = FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.payment_amount = round(float(self.payment_amount),2)
        self.unreferenced_payment = round(float(self.unreferenced_payment),2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.payment_amount = round(float(self.payment_amount),2)
        self.unreferenced_payment = round(float(self.unreferenced_payment),2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.companycode)


class saleinvref(models.Model):
    refernce = models.ForeignKey(sales_paymentdetails, related_name= 'invrefs', on_delete=models.CASCADE)
    refinvno = models.ForeignKey(outward_bill_invoice, related_name='sales_payment_details', on_delete=models.CASCADE, null=True)
    refinvamount=models.FloatField(default=0)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    objects = FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.refinvamount = round(float(self.refinvamount),2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.refinvamount = round(float(self.refinvamount),2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.refinvno)


class balancedetails(models.Model):
    payment_details = models.ForeignKey(sales_paymentdetails, null=True, blank=True, related_name='paymentdetail',on_delete=models.CASCADE)
    invoice_details = models.ForeignKey(outward_bill_invoice, null=True, blank=True, related_name='salesdetails',on_delete=models.CASCADE)
    payment_code=models.PositiveIntegerField(null=True,blank=True)
    companycode = models.ForeignKey(CompanyDetails,related_name="balance_details",null=True,on_delete=models.CASCADE)
    invamount = models.FloatField(default=0, null=True, blank=True) #grand total
    ref_payment = models.FloatField(default=0, null=True, blank=True) 
    payment = models.FloatField(default=0, null=True, blank=True)
    date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    debitnote_amount = models.FloatField(default=0, null=True, blank=True)
    debinoterefno=models.IntegerField(default=0, null=True, blank=True)
    totalbalance_amount = models.FloatField(default=0, null=True, blank=True)
    totalinvoiceamount = models.FloatField(default=0, null=True, blank=True)
    totalpaymentamount = models.FloatField(default=0, null=True, blank=True)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    year_opening = models.BooleanField(default=False)
    objects = FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.invamount = round(float(self.invamount),2)
        self.ref_payment = round(float(self.ref_payment),2)
        self.payment = round(float(self.payment),2)
        self.debitnote_amount = round(float(self.debitnote_amount),2)
        self.totalbalance_amount = round(float(self.totalbalance_amount),2)
        self.totalinvoiceamount = round(float(self.totalinvoiceamount),2)
        self.totalpaymentamount = round(float(self.totalpaymentamount),2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.invamount = round(float(self.invamount),2)
        self.ref_payment = round(float(self.ref_payment),2)
        self.payment = round(float(self.payment),2)
        self.debitnote_amount = round(float(self.debitnote_amount),2)
        self.totalbalance_amount = round(float(self.totalbalance_amount),2)
        self.totalinvoiceamount = round(float(self.totalinvoiceamount),2)
        self.totalpaymentamount = round(float(self.totalpaymentamount),2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.invamount)


class purchase_paymentdetails(models.Model):

    class sales_type_choices(models.IntegerChoices):
        debitnote = 1
        normalpayment = 2

    class debit_type_choices(models.IntegerChoices):
        material_rejection = 1
        material_return = 2
        shortage = 3

    purchase_type = models.IntegerField(choices=sales_type_choices.choices, default=1)
    debit_type = models.IntegerField(choices=debit_type_choices.choices, null=True)
    cash = models.BooleanField(default=False)
    cheque = models.BooleanField(default=False)
    close = models.BooleanField(null=True)
    bank = models.BooleanField(default=False)
    payment_refno_type = models.CharField(max_length=50,choices=payment_ref,default=1)
    payment_refno = models.CharField(max_length=60,default=None,null=True)
    debit_refno = models.CharField(max_length=60,default=None, null=True)
    debit_refdate=models.DateField(default=None,null=True,blank=True)
    payment_amount = models.FloatField(null=True, default=0)
    general_le = models.ForeignKey(general_ledger,related_name='p_details',null=True,on_delete=models.CASCADE,blank=True)
    companycode = models.ForeignKey(CompanyDetails,null=True,on_delete=models.CASCADE)
    payment_refdate=models.DateField(default=None,null=True,blank=True)
    payment_date=models.DateField(auto_now=False, auto_now_add=False, null=True)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    billrefered=models.BooleanField(default=False)
    semirefrenced=models.BooleanField(default=False)
    unreferenced_payment = models.FloatField(default=0)
    objects =FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.payment_amount = round(float(self.payment_amount),2)
        self.unreferenced_payment = round(float(self.unreferenced_payment),2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.payment_amount = round(float(self.payment_amount),2)
        self.unreferenced_payment = round(float(self.unreferenced_payment),2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.companycode)


class purchaseinvref(models.Model):
    refernce = models.ForeignKey(purchase_paymentdetails, related_name= 'invrefs', on_delete=models.CASCADE)
    refinvno = models.ForeignKey(ToolsPurchase_Invoice, related_name='purchase_payment', on_delete=models.CASCADE, null=True)
    refinvamount=models.FloatField(default=0)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    objects = FinancialQuerySet.as_manager()
    
    def save(self, *args, **kwargs):
        self.refinvamount = round(float(self.refinvamount),2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.refinvamount = round(float(self.refinvamount),2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.refinvno)


class purchase_statement(models.Model):
    payment_details = models.ForeignKey(purchase_paymentdetails, null=True, blank=True, related_name='purpaymentdetail',
                                        on_delete=models.CASCADE)
    invoice_details = models.ForeignKey(ToolsPurchase_Invoice, null=True, blank=True, related_name='purdetails',on_delete=models.CASCADE)
    companycode = models.ForeignKey(CompanyDetails,related_name='purchase_balance_details',null=True,on_delete=models.CASCADE)
    payment_code=models.PositiveIntegerField(null=True,blank=True)
    invamount = models.FloatField(default=0, null=True, blank=True)
    ref_payment = models.FloatField(default=0, null=True, blank=True) 
    payment = models.FloatField(default=0, null=True, blank=True)
    date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    totalbalance_amount = models.FloatField(default=0, null=True, blank=True)
    totalinvoiceamount = models.FloatField(default=0, null=True, blank=True)
    totalpaymentamount = models.FloatField(default=0, null=True, blank=True)
    debitnote_amount = models.FloatField(default=0, null=True, blank=True)
    debinoterefno=models.IntegerField(null=True)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    year_opening = models.BooleanField(default=False)
    objects = FinancialQuerySet.as_manager()

    # def save(self, *args, **kwargs):
    #     self.invamount = round(float(self.invamount),2)
    #     self.payment = round(float(self.payment),2)
    #     self.debitnote_amount = round(float(self.debitnote_amount),2)
    #     self.totalbalance_amount = round(float(self.totalbalance_amount),2)
    #     self.totalinvoiceamount = round(float(self.totalinvoiceamount),2)
    #     self.totalpaymentamount = round(float(self.totalpaymentamount),2)
    #     super().save(*args, **kwargs)

    # def update(self, *args, **kwargs):
    #     self.invamount = round(float(self.invamount),2)
    #     self.payment = round(float(self.payment),2)
    #     self.debitnote_amount = round(float(self.debitnote_amount),2)
    #     self.totalbalance_amount = round(float(self.totalbalance_amount),2)
    #     self.totalinvoiceamount = round(float(self.totalinvoiceamount),2)
    #     self.totalpaymentamount = round(float(self.totalpaymentamount),2)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return str(self.payment)


class Vendor_Paymentdetails(models.Model):
    class sales_type_choices(models.IntegerChoices):
        debitnote = 1
        normalpayment = 2

    class debit_type_choices(models.IntegerChoices):
        tds = 1
        esipf = 2
        material_rejection = 3

    sales_type = models.IntegerField(choices=sales_type_choices.choices, default=1)
    debit_type = models.IntegerField(choices=debit_type_choices.choices, null=True)
    cash = models.BooleanField(default=False)
    cheque = models.BooleanField(default=False)
    bank = models.BooleanField(default=False)
    close = models.BooleanField(null=True)
    bank_payment = models.BooleanField(null=True)
    payment_refno_type = models.CharField(max_length=50,choices=payment_ref,default=1)
    payment_refno = models.CharField(max_length=60,default=None, null=True)
    debit_refno = models.CharField(max_length=60,default=None, null=True)
    payment_amount = models.FloatField(default=0,null=True)
    companycode = models.ForeignKey(CompanyDetails,related_name='vendor_payment_details',null=True,on_delete=models.CASCADE)
    payment_refdate=models.DateField(default=None,null=True,blank=True)
    debit_refdate=models.DateField(default=None,null=True,blank=True)
    payment_date=models.DateField(auto_now=False, auto_now_add=False, null=True)
    financial_period = models.DateField(auto_now=True)
    tenant_id = models.IntegerField()
    billrefered=models.BooleanField(default=False)
    semirefrenced=models.BooleanField(default=False)
    unreferenced_payment = models.FloatField(default=0)
    objects = FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.payment_amount = round(float(self.payment_amount),2)
        self.unreferenced_payment = round(float(self.unreferenced_payment),2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.payment_amount = round(float(self.payment_amount),2)
        self.unreferenced_payment = round(float(self.unreferenced_payment),2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.companycode)


class depit_note_invoice(models.Model):
    
    tenant_id = models.PositiveIntegerField(null=True)
    company = models.ForeignKey(CompanyDetails,null=True,on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(ShippingAddress,on_delete=models.CASCADE, null=True)
    invno = models.CharField(max_length=100,null=True)
    bill_date = models.DateField(auto_now=True, null=True)
    vc_no_f = models.ForeignKey(VehicleDetails, null=True, on_delete=models.CASCADE)
    financial_period = models.DateField(auto_now=True)
    t_discount = models.FloatField(default=0,null=True)
    t_amount = models.FloatField(default=0, null=True)
    t_sgst = models.FloatField(default=0,null=True)
    t_cgst = models.FloatField(default=0,null=True)
    t_igst = models.FloatField(default=0,null=True)
    t_ot = models.FloatField(default=0, null=True)
    grand_total = models.FloatField(default=0,null=True)
    year_opening=models.BooleanField(default=False, null=True)
    is_deleted=models.BooleanField(default=False, null=True)
    bill_to_dc =models.BooleanField(default=False, null = True)
    note = models.TextField(null=True)
    refno = models.CharField(max_length=200, null=True)
    running_numbers = models.IntegerField(null=True)
    objects=FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        
        self.t_amount = round(float(self.t_amount), 2)
        self.t_discount = round(float(self.t_discount), 2)
        self.t_sgst = round(float(self.t_sgst), 2)
        self.t_cgst = round(float(self.t_cgst), 2)
        self.t_igst = round(float(self.t_igst), 2)
        self.t_ot = round(float(self.t_ot), 2)
        self.grand_total = round(float(self.grand_total))
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        
        self.sgstper = round(float(self.sgstper), 2)
        self.cgstper = round(float(self.cgstper), 2)
        self.igstper = round(float(self.igstper), 2)
        self.amount = round(float(self.amount), 2)
        self.t_discount = round(float(self.t_discount), 2)
        self.t_sgst = round(float(self.t_sgst), 2)
        self.t_cgst = round(float(self.t_cgst), 2)
        self.t_igst = round(float(self.t_igst), 2)
        self.t_ot = round(float(self.t_ot), 2)
        self.grand_total = round(float(self.grand_total))
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
    

class depit_note_materials(models.Model):

    tenant_id = models.PositiveIntegerField(null=True)
    depit_details = models.ForeignKey(depit_note_invoice, related_name='materials',on_delete=models.CASCADE,null=True)
    tool = models.ForeignKey(Tools, related_name='tool_data',on_delete=models.CASCADE,null=True)
    without_materials = models.ForeignKey(ToolsWithout_Materials, related_name = 'without_material_reference', on_delete=models.CASCADE,null = True)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0) 
    sgstper = models.FloatField(default=0)
    cgstper = models.FloatField(default=0)
    igstper = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
    cgst = models.FloatField(default=0)
    igst = models.FloatField(default=0)
    amount = models.FloatField(default = 0)
    subtotal = models.FloatField(default=0)
    discount = models.FloatField(null=True,blank=True,default=0)
    ot = models.FloatField(null=True,blank=True,default=0)
    financial_period = models.DateField(auto_now=True)
    objects = FinancialQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.qty = round(float(self.qty), 2)
        self.price = round(float(self.price), 2)
        self.discount = round(float(self.discount), 2)
        self.amount = round(float(self.amount), 2)
        self.sgst = round(float(self.sgst), 2)
        self.cgst = round(float(self.cgst), 2)
        self.igst = round(float(self.igst), 2)
        self.sgstper = round(float(self.sgstper), 2)
        self.cgstper = round(float(self.cgstper), 2)
        self.igstper = round(float(self.igstper), 2)
        self.subtotal = round(float(self.subtotal), 2)
        self.ot = round(float(self.ot), 2)
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.qty = round(float(self.qty), 2)
        self.price = round(float(self.price), 2)
        self.discount = round(float(self.discount), 2)
        self.amount = round(float(self.amount), 2)
        self.sgst = round(float(self.sgst), 2)
        self.cgst = round(float(self.cgst), 2)
        self.igst = round(float(self.igst), 2)
        self.sgstper = round(float(self.sgstper), 2)
        self.cgstper = round(float(self.cgstper), 2)
        self.igstper = round(float(self.igstper), 2)
        self.subtotal = round(float(self.subtotal), 2)
        self.ot = round(float(self.ot), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.depit_details)


class without_ref(models.Model):

    tenant_id = models.PositiveIntegerField(null=True)
    without_details = models.ForeignKey(ToolsWithout_Details,related_name="without_ref", on_delete= models.CASCADE)
    depit_details = models.ForeignKey(depit_note_invoice,related_name="depit_ref", on_delete= models.CASCADE)
    financial_period = models.DateField(auto_now=True)
    objects = FinancialQuerySet.as_manager()



