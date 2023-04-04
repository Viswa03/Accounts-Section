from bill.serializers import *
from rest_framework import serializers
from master.serializers import *
from tools_management.serializers import ToolsPurchaseSerializer
from .models import *



class ledgerserializer(serializers.ModelSerializer):
    class Meta:
        model = general_ledger
        fields = '__all__'




class salesinvrefserializer(serializers.ModelSerializer):
    class Meta :
        model = saleinvref
        fields= ['refinvno', 'refinvamount',  ]

class salesinvrefserializer3(serializers.ModelSerializer):
    refinvno=outward_bill_invoice_serializer()
  
    
    class Meta :
        model = saleinvref
        fields= '__all__'


class salespaymentserializer(serializers.ModelSerializer):

    saleinvref_set = salesinvrefserializer(many=True,read_only=True)

    class Meta :
        model = sales_paymentdetails
        fields= '__all__'


class purcahseinvrefserializer(serializers.ModelSerializer):


    class Meta :
        model = purchaseinvref
        fields='__all__'

class purcahseinvrefserializer1(serializers.ModelSerializer):
    refinvno=ToolsPurchaseSerializer()

    class Meta :
        model = purchaseinvref
        fields='__all__'
class purchasepaymentserializer(serializers.ModelSerializer):
    invrefs= purcahseinvrefserializer1(many=True)
    companycode=CompanyDetailsSerializer()
    class Meta:
        model =purchase_paymentdetails
        fields = '__all__'

class balancedetailsserilaizer(serializers.ModelSerializer):



    class Meta :
        model = balancedetails
        fields= '__all__'


class salespaymentdetserializer(serializers.ModelSerializer):
   
    invrefs=salesinvrefserializer3(many=True,read_only=True)
    companycode=CompanyDetailsSerializer()
    class Meta :
        model = sales_paymentdetails
        fields= '__all__'


class paymentserializer(serializers.ModelSerializer):

    class Meta:
        model = sales_paymentdetails
        fields = ['companycode', 'payment_amount', 'payment_date']


class reportserializer(serializers.ModelSerializer):
 
    class Meta:
        model = sales_paymentdetails
        fields = ['companycode', 'payment_amount', 'payment_date']


class purchaseserilaizer2(serializers.ModelSerializer):

    payment_details=purchasepaymentserializer()
    companycode = CompanyDetailsSerializer()
 
    class Meta :
        model = purchase_statement
        fields= '__all__'


class paymentserializers(serializers.ModelSerializer):

 
    class Meta :
        model = balancedetails
        fields= '__all__'

class purchaseserilaizers(serializers.ModelSerializer):


    class Meta :
        model = purchase_statement
        fields= '__all__'

class balancedetailsserilaizers(serializers.ModelSerializer):

    class Meta :
        model = balancedetails
        fields= '__all__'


class salespaymentdetailsreportserializer(serializers.ModelSerializer):
  
    class Meta :
        model = sales_paymentdetails
        fields= '__all__'

class salesinvrefreportserializer(serializers.ModelSerializer):
    refernce = salespaymentdetailsreportserializer()
    class Meta :
        model = saleinvref
        fields= '__all__'


class balancedetailsreportserilaizers2(serializers.ModelSerializer):

    payment_details = salespaymentdetailsreportserializer()
    companycode=CompanyDetailsSerializer()
    # payment_code = masterproductserializer(read_only=True)
    class Meta :
        model = balancedetails
        fields= '__all__'


# class purcahseinvrefserializer(serializers.ModelSerializer):

#     refinvno = PurchaseSerializer()

#     class Meta :
#         model = purchaseinvref
#         fields='__all__'


class purchasepaymentserializer2(serializers.ModelSerializer):
    invrefs= purcahseinvrefserializer(many=True,read_only=True)

    class Meta:
        model =purchase_paymentdetails
        fields = '__all__'

class balancedetailsserilaizer15(serializers.ModelSerializer):
    invoice_details=outward_bill_invoice_serializer()
    class Meta :
        model = balancedetails
        fields= '__all__'

class salespaymentdetserializer(serializers.ModelSerializer):
   
    invrefs=salesinvrefserializer3(many=True,read_only=True)
    companycode=CompanyDetailsSerializer()

    class Meta :
        model = sales_paymentdetails
        fields= '__all__'


class paymentserializer(serializers.ModelSerializer):
    class Meta:
        model = sales_paymentdetails
        fields = ['companycode', 'payment_amount', 'payment_date']

class reportserializer(serializers.ModelSerializer):


    class Meta:
        model = sales_paymentdetails
        fields = ['companycode', 'payment_amount', 'payment_date']

class purchaseserilaizer(serializers.ModelSerializer):
   
    payment_details=purchasepaymentserializer()
    class Meta :
        model = purchase_statement
        fields= '__all__'

class paymentserializers(serializers.ModelSerializer):

    class Meta :
        model = balancedetails
        fields= '__all__'

class purchaseserilaizers17(serializers.ModelSerializer):
    invoice_details =ToolsPurchaseSerializer()
    class Meta :
        model = purchase_statement
        fields= '__all__'

class balancedetailsserilaizers17(serializers.ModelSerializer):
   
    class Meta :
        model = balancedetails
        fields= '__all__'

class purchaseserilaizers5(serializers.ModelSerializer):

    invoice_details = ToolsPurchaseSerializer()

    class Meta :
        model = purchase_statement
        fields= '__all__'

class CompanyToPurchase(serializers.ModelSerializer):

    purchase_balance_details = purchaseserilaizers5(many = True)

    class Meta:

        model = CompanyDetails
        fields = '__all__'
class salespaymentdetailsreportserializer(serializers.ModelSerializer):
    class Meta :
        model = sales_paymentdetails
        fields= '__all__'

class salesinvrefreportserializer(serializers.ModelSerializer):
    refernce = salespaymentdetailsreportserializer()
    class Meta :
        model = saleinvref
        fields= '__all__'

class balancedetailsreportserilaizers(serializers.ModelSerializer):
  
    payment_details = salespaymentdetailsreportserializer()

    class Meta :
        model = balancedetails
        fields= '__all__'


class balancedetailsSerializer2(serializers.ModelSerializer):



    class Meta :
        model = balancedetails
        fields= '__all__'


class balancedetailsSerializer2(serializers.ModelSerializer):

    invoice_details = outward_bill_invoice_serializers()

    class Meta :
        model = balancedetails
        fields= '__all__'

class CompanyToSales(serializers.ModelSerializer):

    balance_details = balancedetailsSerializer2(many = True)

    class Meta:

        model = CompanyDetails
        fields = '__all__'

class purchaseserilaizers5(serializers.ModelSerializer):

    

    class Meta :
        model = purchase_statement
        fields= '__all__'


class purchasepaymentserializer2(serializers.ModelSerializer):

    class Meta:
        model =purchase_paymentdetails
        fields = '__all__'


class purcahseinvrefserializer2(serializers.ModelSerializer):

    refernce = purchasepaymentserializer2()
    class Meta :
        model = purchaseinvref
        fields='__all__'


class purchaseserilaizers2(serializers.ModelSerializer):

    payment_details = purchasepaymentserializer2()


    class Meta :
        model = purchase_statement
        fields= '__all__'


class SalesPaymentdetailsSerializer(serializers.ModelSerializer):
    
    class Meta :
        model = sales_paymentdetails
        fields= '__all__'


class PurchasePaymentdetailsSerializer(serializers.ModelSerializer):
    
    class Meta :
        model = purchase_paymentdetails
        fields= '__all__'

class Vendor_Payments_Serializer(serializers.ModelSerializer):

    class Meta:

        model = Vendor_Paymentdetails
        fields = '__all__'


# class Vendor_Balance_Serializer(serializers.ModelSerializer):

#     class Meta:

#         model = Vendor_Balancedetails
#         fields = '__all__'


# class Vendor_Reference_Serializer(serializers.ModelSerializer):



#     class Meta:

#         model = Vendor_Saleinvref
#         fields = '__all__'


# class Vendor_Balance_Serializer2(serializers.ModelSerializer):


#     class Meta:

#         model = Vendor_Balancedetails
#         fields = '__all__'





class salesinvrefserializer2(serializers.ModelSerializer):
    class Meta :
        model = saleinvref
        fields= '__all__'



# class Vendor_Reference_Serializer2(serializers.ModelSerializer):

#     refernce = Vendor_Payments_Serializer()

#     class Meta:

#         model = Vendor_Saleinvref
#         fields = '__all__'


class bankdetailsSerializer(serializers.ModelSerializer):
    
    class Meta :
        model = Bank_details
        fields= '__all__'

class bankdetailsSerializer_loan(serializers.ModelSerializer):
  
    class Meta :
        model = loan_paymentdetails
        fields= '__all__'


class bankdetailsSerializer1(serializers.ModelSerializer):
   
    class Meta :
        model = Bank_details
        fields= '__all__'

class bankdetailsSerializer_loan1(serializers.ModelSerializer):
    bank_ref=bankdetailsSerializer()
    class Meta :
        model = loan_paymentdetails
        fields= '__all__'




class Depit_Note_Material_Serializer(serializers.ModelSerializer):

    tool = ToolsSerializer()

    class Meta:

        model = depit_note_materials
        fields = '__all__'


class Depit_Note_Material_Serializer_Get(serializers.ModelSerializer):

    company = CompanyDetailsSerializer()
    materials = Depit_Note_Material_Serializer(many=True)

    class Meta:

        model = depit_note_invoice
        fields = '__all__'


class Depit_Note_Serializer(serializers.ModelSerializer):

    class Meta:

        model = depit_note_invoice
        fields = '__all__'

class Depit_Note_Serializer_GetByID(serializers.ModelSerializer):

    company = CompanyDetailsSerializer()

    class Meta:

        model = depit_note_invoice
        fields = '__all__'

class ledgerserializer1(serializers.ModelSerializer):

    ldetails= salespaymentdetserializer(many=True)
    bank_ref=bankdetailsSerializer1()
    p_details=purchasepaymentserializer(many=True)
    class Meta:
        model = general_ledger
        fields = '__all__'