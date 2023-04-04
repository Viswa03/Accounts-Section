from urllib.request import Request
from bill.serializers import outward_bill_invoice_serializers
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import filters
from rest_framework import filters
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins,generics

from pettycash.models import *
from pettycash.serializers import *
from tools_management.serializers import ToolsPurchaseSerializer23
from .serializers import *
from . models import *
from master.models import *
from datetime import date
from authen .views import Isjwtvalid
from django.db.models import Q
from tools_management.models import *



class bankdetails_entry(APIView):
    def get(self,request,id=None):
        if id:
            gt=Bank_details.objects.get(id=id)
            ser4=bankdetailsSerializer(gt)
            return Response(ser4.data)
        else:
            gt=  Bank_details.objects.all()
            ser4= bankdetailsSerializer(gt,many=True)
            return Response(ser4.data)

    def post(self,request):
        data={}
        jsdata= request.data   
        m= Bank_details( account_no=jsdata['account_no'],account_type=jsdata['account_type'],description=jsdata['des'],tenant_id=request.user.tenant_company.id,ifsc_code=jsdata['ifsc_code'],bank_name=jsdata['bank_name'], branch_name=jsdata['branch_name'])
        m.save()
        return Response({"status":True,"message":"succesfully added"}) 
    def patch(self,request,id=None):
        jsdatas= request.data  
        print(jsdatas)
         
        gt=Bank_details.objects.get(id=id)
       
        ser4=bankdetailsSerializer(gt,data=request.data,partial=True)
        if ser4.is_valid():
            ser4.save()
            return Response({"status":True,"message":"succesfully patched"})
        else:
            return Response({"status":False,"message":ser4.errors})
                
    def delete(self,request,id=None):
        fr= Bank_details.objects.get(id=id)
        if general_ledger.objects.filter(bank_ref_id=id) .exists() or loan_paymentdetails.objects.filter(bank_ref_id=id) .exists() or loan_paymentdetails.objects.filter(bank_i=id) .exists():
             return Response({"status":False,"message":"Sorry can't deleted"})
        else:
           fr.delete()
           return Response({"status":True,"message":"succesfully deleted"})

class generalledg_entry_loanwise(APIView):
    def get(self,request,id=None):
        data=[]
        if id:
            gt=loan_paymentdetails.objects.filter(bank_ref_id=id)
            ser4= bankdetailsSerializer_loan1(gt,many=True)
            qrts=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bank_ref_id=id).aggregate(Sum('amount'))
            pr=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bank_ref_id=id,ln=False).aggregate(Sum('premium_amount'))
            inte=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bank_ref_id=id,ln=False).aggregate(Sum('inte_amount'))
        
            if inte['inte_amount__sum']==None:
                inte['inte_amount__sum']=0
            if pr['premium_amount__sum']==None:
                pr['premium_amount__sum']=0
            if qrts['amount__sum']==None:
                qrts['amount__sum']=0

            m={"Totalloanamount":qrts['amount__sum'],
            'bank':ser4.data,
            "t_premiumamount":pr['premium_amount__sum'],
            "t_int_amount":inte['inte_amount__sum'],
            "t_paid_amount":pr['premium_amount__sum']+inte['inte_amount__sum'],
            "t_balance_amount":qrts['amount__sum']-(pr['premium_amount__sum']+inte['inte_amount__sum'])}
           
            data.append(m)
            
         
            return Response(data)
        else:
            # Bank_details.objects.all()
            # for hr in 
            gt= loan_paymentdetails.objects.all()
            ser4=  bankdetailsSerializer_loan1(gt,many=True)
            qrts=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('amount'))
            pr=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('premium_amount'))
            inte=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('inte_amount'))
          
            print(pr['premium_amount__sum'],'kkkkkkkkkkkkkkkkkkkkkk')
            if inte['inte_amount__sum']==None:
                inte['inte_amount__sum']=0
            if pr['premium_amount__sum']==None:
                pr['premium_amount__sum']=0

            if loan_paymentdetails.objects.all().exists():
                    m={"Totalloanamount":qrts['amount__sum'],
                    'bank':ser4.data,
                    "t_premiumamount":pr['premium_amount__sum'],
                    "t_int_amount":inte['inte_amount__sum'],
                    "t_paid_amount":pr['premium_amount__sum']+inte['inte_amount__sum'],
                    "t_balance_amount":qrts['amount__sum']-(pr['premium_amount__sum']+inte['inte_amount__sum'])}
                
                    data.append(m)
            else:
                m={"Totalloanamount":0,
                "t_premiumamount":0,
                "t_int_amount":0,
                "t_paid_amount":0,
                "t_balance_amount":0}
            
                data.append(m)
            return Response(data)
class generalledg_entry(APIView):
    def get(self,request,id=None):
        if id:
            gt=loan_paymentdetails.objects.get(id=id)
            ser4= bankdetailsSerializer_loan1(gt)
            gt1=Bank_details.objects.get(id=gt.bank_i)
            ser5=bankdetailsSerializer(gt1)
            ser4.data['bank_i']=ser5.data
            return Response(ser4.data)
        else:
            gt= loan_paymentdetails.objects.all()
            ser4=  bankdetailsSerializer_loan1(gt,many=True)
            for i in ser4.data:
                if i['bank_i'] is not None:
                    gt1=Bank_details.objects.get(id=i['bank_i'])
                    ser5=bankdetailsSerializer(gt1)
                    i['bank_i']=ser5.data
            return Response(ser4.data)

    def post(self,request):
        data={}
        js=request.data[0]
        jsdata= request.data[1]  
        def gen_led_entry(notes,payment_amount):
                if general_ledger.objects.filter(cash=True).exists():
                    get=general_ledger.objects.filter(cash=True).last()
                    led=general_ledger(cash=True,description=notes,debit=payment_amount,credit=0,balance=get.balance+payment_amount, paymentcode=get.paymentcode+1)
                    led.save()
                else:
                                  
                    led=general_ledger(cash=True,description=notes,debit=payment_amount,credit=0,balance=payment_amount, paymentcode=1)
                    led.save()
                return()
        def gen_led_entry_bank(b_id,notes,payment_amount):
            if general_ledger.objects.filter(bank=True,bank_ref_id=b_id).exists():
                get=general_ledger.objects.filter(bank=True,bank_ref_id=b_id).last()
                led=general_ledger(bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=get.balance+payment_amount, paymentcode=get.paymentcode+1)
                led.save()
            else:
                                
                led=general_ledger(bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=payment_amount, paymentcode=1)
                led.save()
            return()
       
        
        if js['ln']==True:
             m= loan_paymentdetails(loan=True,ln=True,bank_ref_id=jsdata['bank_ref'],tenant_id=request.user.tenant_company.id,amount=js['loan_amt'],balance_amount=js['loan_amt'],inte_amount=jsdata['inte_amount'],premium_amount=jsdata['premium_amount'])
             m.save()
             Bank_details.objects.filter(id=jsdata['bank_ref']).update(ln=True)
        
        else:
            amount=jsdata['inte_amount']+jsdata['premium_amount']
            notes="loan_payment"
            b_id=jsdata['bank_ref']
            if jsdata['payment_type']==1:
                    gen_led_entry(notes,amount)
            else:
                    gen_led_entry_bank(b_id,notes,amount)
            k=loan_paymentdetails.objects.filter(bank_ref_id=jsdata['bank_ref']).last()
            b=k.balance_amount-(jsdata['premium_amount']+jsdata['inte_amount'])
            if b==0:
                # loan_paymentdetails.objects.filter(bank_ref_id=jsdata['bank_ref']).last().update(close=True)
                m= loan_paymentdetails(loan=True,close=True,bank_i=jsdata['b_id'],balance_amount=b,payment_type=jsdata['payment_type'],inte_amount=jsdata['inte_amount'],premium_amount=jsdata['premium_amount'],bank_ref_id=jsdata['bank_ref'],tenant_id=request.user.tenant_company.id)
                m.save()
                Bank_details.objects.filter(id=jsdata['bank_ref']).update(ln=False,ln_close=True)
                

            else:
               
                if jsdata['loan']==True:    
                    m= loan_paymentdetails(loan=True,ln=True,bank_ref_id=jsdata['bank_ref'],balance_amount=b,premium_amount=jsdata['premium_amount'],tenant_id=request.user.tenant_company.id,inte_amount=jsdata['inte_amount'])
                    m.save()
                        
                else:
                    m= loan_paymentdetails(loan=False,ln=False,bank_i=jsdata['b_id'],balance_amount=b,payment_type=jsdata['payment_type'],inte_amount=jsdata['inte_amount'],premium_amount=jsdata['premium_amount'],bank_ref_id=jsdata['bank_ref'],tenant_id=request.user.tenant_company.id)
                    m.save()
        return Response({"status":True,"message":"succesfully added"}) 
    def patch(self,request,id=None):
        jsdatas= request.data  
        print(jsdatas)
         
        gt=loan_paymentdetails.objects.get(id=id)
       
        ser4= bankdetailsSerializer_loan(gt,data=request.data,partial=True)
        if ser4.is_valid():
            ser4.save()
            return Response({"status":True,"message":"succesfully patched"})
        else:
            return Response({"status":False,"message":ser4.errors})
                
    def delete(self,request,id=None):
        fr= loan_paymentdetails.objects.get(id=id)
        fr.delete()
        return Response({"status":True,"message":"succesfully deleted"})


class salespaymentprocess(generics.GenericAPIView,APIView,mixins.ListModelMixin,mixins.CreateModelMixin):
    serializer_class = salespaymentserializer
    queryset =sales_paymentdetails.objects.all()

    lookup_field = 'id'
    permission_classes=[~Isjwtvalid & IsAuthenticated]


    def post(self, request):

        if request.method == "POST":

            inputdata = request.data
            tenant_id=request.user.tenant_company.id
            def gen_led_entry(notes,payment_amount):
                if general_ledger.objects.filter(cash=True).exists():
                    get=general_ledger.objects.filter(cash=True).last()
                    led=general_ledger(cash=True,description=notes,credit=payment_amount,debit=0,balance=get.balance+payment_amount, paymentcode=get.paymentcode+1)
                    led.save()
                else:
                                  
                    led=general_ledger(cash=True,description=notes,credit=payment_amount,debit=0,balance=payment_amount, paymentcode=1)
                    led.save()
                return(led.id)
            def gen_led_entry_bank(b_id,notes,payment_amount):
                if general_ledger.objects.filter(bank=True,bank_ref_id=b_id).exists():
                    get=general_ledger.objects.filter(bank=True,bank_ref_id=b_id).last()
                    led=general_ledger(bank=True,description=notes,bank_ref_id=b_id,credit=payment_amount,debit=0,balance=get.balance+payment_amount, paymentcode=get.paymentcode+1)
                    led.save()
                else:
                                  
                    led=general_ledger(bank=True,description=notes,bank_ref_id=b_id,credit=payment_amount,debit=0,balance=payment_amount, paymentcode=1)
                    led.save()
                return(led.id)
            for i in inputdata:
                notes=i['Notes']
                payment_amount = float(i['payment_amount'])
                sales_type = i['sales_type']
                company_id = i['companycode']
                payment_date = i['payment_date']
                companycode = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = company_id)

                saleinvref_sets = i['saleinvref_set']

                if sales_type == 1:

                    debit_type = i['debit_type']
                    debit_refno = i['debit_refno']
                    debit_refdate = i['debit_refdate']

                    if len(saleinvref_sets) != 0:

                        value = []

                        for x in saleinvref_sets:

                            value.append(x['refinvamount'])

                        if sum(value) == payment_amount:

                            datas = sales_paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, sales_type = sales_type, billrefered = True, unreferenced_payment = 0, semirefrenced = False,payment_date = payment_date)

                        else:

                            datas = sales_paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, sales_type = sales_type, billrefered = True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)

                    else:

                        datas = sales_paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)

                elif sales_type == 2:

                    payment_refdate = i['payment_refdate']
                    payment_refno = i['payment_refno']
                    
                    cash = i['cash']
                    cheque= i["cheque"]
                    bank = i["bank"]
                    b_id=i['bank_id']

                    if len(saleinvref_sets) != 0:

                        value = []

                        for x in saleinvref_sets:

                            value.append(x['refinvamount'])

                        if sum(value) == payment_amount:

                            if cash == True:
                                k=gen_led_entry(notes,payment_amount)
                                datas = sales_paymentdetails( general_le_id=k,cash = True, notes=notes,payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                
                            elif cheque == True:

                                close = i['close']
                               
                                if close == True:
                                        k=gen_led_entry_bank(b_id,notes,payment_amount)
                                        datas = sales_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                        
                                else:
                                    k=gen_led_entry_bank(b_id,notes,payment_amount)

                                    datas = sales_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                    
                            elif bank == True:
                                k=gen_led_entry_bank(b_id,notes,payment_amount)


                                datas = sales_paymentdetails(general_le_id=k,bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                
                        else:

                            if cash == True:
                                k=gen_led_entry(notes,payment_amount)

                                datas = sales_paymentdetails(general_le_id=k,cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                
                            elif cheque == True:

                                close = i['close']
                                b_id=i['bank_id']

                                if close == True:
                                        k=gen_led_entry_bank(b_id,notes,payment_amount)

                                        datas = sales_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                        
                                else:
                                    k= gen_led_entry_bank(b_id,notes,payment_amount)
    
                                    datas = sales_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                   
                            elif bank == True:
                                k= gen_led_entry_bank(b_id,notes,payment_amount)

                                datas = sales_paymentdetails(general_le_id=k,bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                               
                    elif len(saleinvref_sets) == 0:

                        if cash == True:
                            k=gen_led_entry(notes,payment_amount)

                            datas = sales_paymentdetails(general_le_id=k,cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                            
                        elif cheque == True:

                            close = i['close']
                            b_id=i['bank_id']
                            if close == True:
                                    k=gen_led_entry_bank(b_id,notes,payment_amount)

                                    datas = sales_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                                    
                            else:
                                k=gen_led_entry_bank(b_id,notes,payment_amount)

                                datas = sales_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                                
                        elif bank == True:
                            k=gen_led_entry_bank(b_id,notes,payment_amount)

                            datas = sales_paymentdetails(general_le_id=k,bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                            
                datas.save()

                xt = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode=companycode).exists()

                if xt == True:
                    m = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode=companycode).last()

                    if m.totalbalance_amount == 0:

                        data = balancedetails(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount,totalpaymentamount=m.totalpaymentamount + payment_amount,totalbalance_amount=(0-payment_amount),totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data.save()

                    elif m.totalbalance_amount < 0:
                        z = 0
                        z = float(float(payment_amount) + float(m.totalpaymentamount))
                        zy = float(float(m.totalbalance_amount) - float(payment_amount))

                        data1 = balancedetails(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount, totalpaymentamount=z, totalbalance_amount=zy,totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data1.save()

                    elif m.totalbalance_amount > 0:

                        z = 0
                        z = float(float(payment_amount) + float(m.totalpaymentamount))
                        zy = float(float(m.totalbalance_amount) - float(payment_amount))

                        data1 = balancedetails(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount, totalpaymentamount=z, totalbalance_amount=zy,totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data1.save()

                else:

                    data = balancedetails(payment_code=1,payment_details=datas, companycode=companycode, invamount=0,payment=payment_amount, totalpaymentamount=payment_amount,totalbalance_amount=(0 - payment_amount), totalinvoiceamount=0,tenant_id=tenant_id, date = payment_date)

                    data.save()

                serializer = SalesPaymentdetailsSerializer(request.data)
                balanceamount=payment_amount
                datares={}

                if len(saleinvref_sets) !=0:

                    if serializer.is_valid:

                        # zx = 0
                        for j in saleinvref_sets:

                            # zx=zx+1

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']
                                balanceamount = balanceamount - refinvamount

                                data = saleinvref(refernce=datas, tenant_id=tenant_id,refinvno_id=refinvno, refinvamount=refinvamount)

                                data.save()

                                mt = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id=refinvno)

                                x = mt.invamount
                                xy = mt.ref_payment

                                if x == 0:

                                    datares["message"]="Payment already exists for this "
                                else:

                                    z = x - refinvamount
                                    ref_payment = xy + refinvamount

                                    balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id=refinvno).update(invamount=z,ref_payment=ref_payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']
                                balanceamount = balanceamount - refinvamount

                                data = saleinvref(refernce = datas, tenant_id = tenant_id, refinvno_id = refinvno, refinvamount = refinvamount)

                                data.save()

                                mt = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode = companycode).first()

                                x = mt.invamount
                                xy = mt.ref_payment

                                if x == 0:

                                    datares["message"]="Payment already exists for this"

                                else:

                                    z = x - refinvamount
                                    ref_payment = xy + refinvamount

                                    balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode = companycode, invoice_details_id = None, payment_details_id = None)

                                    balance_update_filter.update(invamount=z,ref_payment=ref_payment)

                        datares['message'] = 'Success'

                    else:

                        return Response(datares)

        return Response(True)
class overallpayment(APIView):
    def get(self,request):
        k=[]
        data=[]
        g1=general_ledger.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(cash=True).last()
        g2=general_ledger.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(petty_cash=True).last()
        g3=general_ledger.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(petty_cash=True).last()
          
        m1={
        "cash_in_hand":g1.balance,
        "petty_cash_inhand":g2.balance,}
        data.append(m1)
      
        return Response(data)
class payments_aggregate(APIView):
    def get(self,request):
        data=[]
        k=[]
        h5=outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('grand_total'))
        h=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=2).aggregate(Sum('payment_amount'))
        h1=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(cash=True).aggregate(Sum('payment_amount'))
        h2=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bank=True).aggregate(Sum('payment_amount'))
        h3=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(cheque=True).aggregate(Sum('payment_amount'))
        v=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('payment_amount'))
        v1=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(cash=True).aggregate(Sum('payment_amount'))
        v2=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bank=True).aggregate(Sum('payment_amount'))
        v3=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(cheque=True).aggregate(Sum('payment_amount'))
        v5=ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('subtotal'))
        
        # g=general_ledger.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bank=True).aggregate(Sum('payment_amount'))
        # g=general_ledger.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(cash=True).aggregate(Sum('payment_amount'))
        # qrts=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('amount'))
        # pr=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('premium_amount'))
        # inte=loan_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(Sum('inte_amount'))
        
        if sales_paymentdetails.objects.all().exists():
            if outward_bill_invoice.objects.all().exists():
                  
                m1={"t_sales_amount":h['payment_amount__sum'],
                "t_sales_cash":h1['payment_amount__sum'],
                "t_sales_bank":h2['payment_amount__sum'],
                "t_sales_cheque":h3['payment_amount__sum'],"t_sales_invoice":h5['grand_total__sum']}
                data.append(m1)
            else:
                 
               
                m1={"t_sales_amount":h['payment_amount__sum'],
                "t_sales_cash":h1['payment_amount__sum'],
                "t_sales_bank":h2['payment_amount__sum'],
                "t_sales_cheque":h3['payment_amount__sum'],
                 "t_sales_invoice":0}
                
            
                data.append(m1)
        else:
             m1={"t_sales_amount":0,
                "t_sales_cash":0,
                "t_sales_bank":0,
                "t_sales_cheque":0,
                  "t_sales_invoice":0}
             data.append(m1)
        if purchase_paymentdetails.objects.all().exists():
            if ToolsPurchase_Invoice.objects.all().exists():
                m2={"t_purchase_amount":v['payment_amount__sum'],
                "t_purchase_cash":v1['payment_amount__sum'],
                "t_purchase_bank":v2['payment_amount__sum'],
                "t_purchase_cheque":v3['payment_amount__sum'],"t_purchase_invoice":v5['subtotal__sum']}
                data.append(m2)
            else:
                m2={"t_purchase_amount":v['payment_amount__sum'],
                "t_purchase_cash":v1['payment_amount__sum'],
                "t_purchase_bank":v2['payment_amount__sum'],
                "t_purchase_cheque":v3['payment_amount__sum'],"t_purchase_invoice":0}
                data.append(m2)


        else:
             m2={"t_purchase_amount":0,
                "t_purchase_cash":0,
                "t_purchase_bank":0,
                "t_purchase_cheque":0,
                "t_purchase_invoice":0}
             data.append(m2)
        
       

        k.append(data)
        return Response(data)
class salespaymentall_aggr(APIView):
    def get(self,request):
        details = outward_bill_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all()
        list1 = []
        y1=[]
        y=[]
        z=[]
        z1=[]
        serializer = outward_bill_invoice_serializers(details,many=True)
        a = serializer.data
      
        if  outward_bill_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all().exists():
            final_total1= outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(total_amount=Sum('t_amount'),grand_total=Sum('grand_total'),t_sgst=Sum('t_sgst'),t_cgst=Sum('t_cgst'),t_igst=Sum('t_igst'))
            
            
            total_amount = final_total1['total_amount']
            grand_total = final_total1['grand_total']
            t_sgst = final_total1['t_sgst']
            t_cgst = final_total1['t_cgst']
            t_igst = final_total1['t_igst']


            if total_amount == None:
                total_amount = 0
            if grand_total == None:
                grand_total = 0
            if t_sgst == None:
                t_sgst = 0
            if t_cgst == None:
                t_cgst = 0
            if t_igst == None:
                t_igst = 0

            datalists={
                    "total_amount":round(float(total_amount),2),
                    "grand_total":round(float(grand_total),2),
                    "t_sgst": round(float(t_sgst),2),
                    "t_cgst": round(float(t_cgst),2),
                    "t_igst": round(float(t_igst),2)
                }
            y1.append(datalists)
            y1.append(a)
        else:
            datalists={
                    "total_amount":0,
                    "grand_total":0,
                    "t_sgst": 0,
                    "t_cgst": 0,
                    "t_igst": 0
                }
            y1.append(datalists)
            y1.append(a)
        h=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=2).aggregate(Sum('payment_amount'))
        
        k= sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=2)
        if sales_paymentdetails.objects.all().exists():
           m1={"t_sales_payment_received":h['payment_amount__sum']}
           y1.append(m1)
        else:
            m1={"t_sales_payment_received":0}
            y1.append(m1)
        serializers =salespaymentdetserializer(k,many=True)
        b5=serializers.data
        y1.append(b5)
        h13=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=1).aggregate(Sum('payment_amount'))
        
        k13= sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=1)
        if sales_paymentdetails.objects.all().exists():
           m13={"t_salesdebit_payment_received":h['payment_amount__sum']}
           y1.append(m13)
        else:
            m1={"t_salesdebit_payment_received":0}
            y1.append(m13)
        serializers =salespaymentdetserializer(k13,many=True)
        b13=serializers.data
        y1.append(b13)
        list1.append(y1)
        if ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,
        stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all().exists():
            final_total1=ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(total_amount=Sum('amount'),g_total=Sum('subtotal'),total_cgst=Sum('cgst'),total_sgst=Sum('sgst'),total_igst=Sum('igst'))

                
            total_amount = final_total1['total_amount']
            grand_total = final_total1['g_total']
            t_sgst = final_total1['total_sgst']
            t_cgst = final_total1['total_cgst']
            t_igst = final_total1['total_igst']


            if total_amount == None:
                total_amount = 0
            if grand_total == None:
                grand_total = 0
            if t_sgst == None:
                t_sgst = 0
            if t_cgst == None:
                t_cgst = 0
            if t_igst == None:
                t_igst = 0

            datalist={
                "total_amount":round(float(total_amount),2),
                "g_total":round(float(grand_total),2),
                "total_sgst": round(float(t_sgst),2),
                "total_cgst": round(float(t_cgst),2),
                "total_igst": round(float(t_igst),2)
            }
            y.append(datalist)
            purchase_details = ToolsPurchase_Invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all()

            purchase_serializer = ToolsPurchaseSerializer23(purchase_details, many= True)
            c=purchase_serializer.data
            y.append(c)
         
        else:
            
            datalist={
                "total_amount":0,
                "g_total":0,
                "total_sgst": 0,
                "total_cgst": 0,
                "total_igst":0
            }
            y.append(datalist)
            purchase_details = ToolsPurchase_Invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all()

            purchase_serializer = ToolsPurchaseSerializer23(purchase_details, many= True)
            c=purchase_serializer.data
            y.append(c)
        
        h1=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=2).aggregate(Sum('payment_amount'))
        
        k= purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=2)
        if purchase_paymentdetails.objects.all().exists():
           m11={"t_purchase_payment_received":h1['payment_amount__sum']}
           y.append(m11)
        else:
            m1={"t_purchase_payment_received":0}
            y.append(m11)

        serializers =purchasepaymentserializer(k,many=True)
        b1=serializers.data
        y.append(b1)
        list1.append(y)
        h5=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(debit=True).aggregate(Sum('voucher_amount'))
        h4=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(credit=True).aggregate(Sum('voucher_amount'))
        

        h7=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(with_gst=True).aggregate(Sum('voucher_amount'))
        h8=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(with_gst=False).aggregate(Sum('voucher_amount'))
        h6=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(with_gst=True).aggregate(Sum('gst_amt'))
        
        if pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all().exists():

        
         
        

            d={"total_expenses":h5['voucher_amount__sum'],
            "total_credit":h4['voucher_amount__sum'],
            "total_without_gst":h8['voucher_amount__sum'],
            "total_with_gst":h7['voucher_amount__sum'],
            "total_gst":h6['gst_amt__sum'],}
            z.append(d)
            
            data= pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all()

            serializer = pettycashdserializer(data, many=True)
            z.append(serializer.data)
        else:
            d={"total_expenses":0,
                "total_credit":0,
                "total_without_gst":0,
                "total_with_gst":0,
                "total_gst":0}
            z.append(d)     
            data= pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all()

            serializer = pettycashdserializer(data, many=True)
            z.append(serializer.data)
        list1.append(z)
        if depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all().exists():
            final_total1= depit_note_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).aggregate(total_amount=Sum('t_amount'),grand_total=Sum('grand_total'),t_sgst=Sum('t_sgst'),t_cgst=Sum('t_cgst'),t_igst=Sum('t_igst'))
            
            
            total_amount = final_total1['total_amount']
            grand_total = final_total1['grand_total']
            t_sgst = final_total1['t_sgst']
            t_cgst = final_total1['t_cgst']
            t_igst = final_total1['t_igst']


            if total_amount == None:
                total_amount = 0
            if grand_total == None:
                grand_total = 0
            if t_sgst == None:
                t_sgst = 0
            if t_cgst == None:
                t_cgst = 0
            if t_igst == None:
                t_igst = 0

            datalists={
                    "total_amount":round(float(total_amount),2),
                    "grand_total":round(float(grand_total),2),
                    "t_sgst": round(float(t_sgst),2),
                    "t_cgst": round(float(t_cgst),2),
                    "t_igst": round(float(t_igst),2)
                }
            z1.append(datalists)
            data= depit_note_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all()

            serializer =Depit_Note_Serializer_GetByID(data, many=True)
            z1.append(serializer.data)
          
        else:
            datalists={
                    "total_amount":0,
                    "grand_total":0,
                    "t_sgst": 0,
                    "t_cgst": 0,
                    "t_igst": 0
                }
            data= depit_note_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all()

            serializer =Depit_Note_Serializer_GetByID(data, many=True)
            z1.append(serializer.data)
            z1.append(datalists)
         
        h=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=1).aggregate(Sum('payment_amount'))
        
        k= purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=1)
        if purchase_paymentdetails.objects.all().exists():
           m1={"t_payment_received":h['payment_amount__sum']}
           z1.append(m1)
        else:
            m1={"t_payment_received":0}
            z1.append(m1)
        serializers =purchasepaymentserializer(k,many=True)
        b6=serializers.data
        z1.append(b6)
        list1.append(z1)
        return Response(list1)
class salespaymentall_aggr_daybook(APIView):
    def post(self,request):
        startdate=request.data['from_date']
        enddate=request.data['to_date']
        details = outward_bill_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).all()
        list1 = []
        y1=[]
        y=[]
        z=[]
        z1=[]
        serializer = outward_bill_invoice_serializers(details,many=True)
        a = serializer.data
      
        if  outward_bill_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).all().exists():
            final_total1= outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).aggregate(total_amount=Sum('t_amount'),grand_total=Sum('grand_total'),t_sgst=Sum('t_sgst'),t_cgst=Sum('t_cgst'),t_igst=Sum('t_igst'))
            
            
            total_amount = final_total1['total_amount']
            grand_total = final_total1['grand_total']
            t_sgst = final_total1['t_sgst']
            t_cgst = final_total1['t_cgst']
            t_igst = final_total1['t_igst']


            if total_amount == None:
                total_amount = 0
            if grand_total == None:
                grand_total = 0
            if t_sgst == None:
                t_sgst = 0
            if t_cgst == None:
                t_cgst = 0
            if t_igst == None:
                t_igst = 0

            datalists={
                    "total_amount":round(float(total_amount),2),
                    "grand_total":round(float(grand_total),2),
                    "t_sgst": round(float(t_sgst),2),
                    "t_cgst": round(float(t_cgst),2),
                    "t_igst": round(float(t_igst),2)
                }
            y1.append(datalists)
            y1.append(a)
        else:
            datalists={
                    "total_amount":0,
                    "grand_total":0,
                    "t_sgst": 0,
                    "t_cgst": 0,
                    "t_igst": 0
                }
            y1.append(datalists)
            y1.append(a)
        h=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=2).filter(financial_period__range=[startdate, enddate]).aggregate(Sum('payment_amount'))
        
        k= sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=2)
        if sales_paymentdetails.objects.all().exists():
           m1={"t_sales_payment_received":h['payment_amount__sum']}
           y1.append(m1)
        else:
            m1={"t_sales_payment_received":0}
            y1.append(m1)
        serializers =salespaymentdetserializer(k,many=True)
        b5=serializers.data
        y1.append(b5)
        h13=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=1).filter(financial_period__range=[startdate, enddate]).aggregate(Sum('payment_amount'))
        
        k13= sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(sales_type=1).filter(financial_period__range=[startdate, enddate])
        if sales_paymentdetails.objects.all().exists():
           m13={"t_salesdebit_payment_received":h['payment_amount__sum']}
           y1.append(m13)
        else:
            m1={"t_salesdebit_payment_received":0}
            y1.append(m13)
        serializers =salespaymentdetserializer(k13,many=True)
        b13=serializers.data
        y1.append(b13)
        list1.append(y1)
        if ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,
        stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all().exists():
            final_total1=ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).aggregate(total_amount=Sum('amount'),g_total=Sum('subtotal'),total_cgst=Sum('cgst'),total_sgst=Sum('sgst'),total_igst=Sum('igst'))

                
            total_amount = final_total1['total_amount']
            grand_total = final_total1['g_total']
            t_sgst = final_total1['total_sgst']
            t_cgst = final_total1['total_cgst']
            t_igst = final_total1['total_igst']


            if total_amount == None:
                total_amount = 0
            if grand_total == None:
                grand_total = 0
            if t_sgst == None:
                t_sgst = 0
            if t_cgst == None:
                t_cgst = 0
            if t_igst == None:
                t_igst = 0

            datalist={
                "total_amount":round(float(total_amount),2),
                "g_total":round(float(grand_total),2),
                "total_sgst": round(float(t_sgst),2),
                "total_cgst": round(float(t_cgst),2),
                "total_igst": round(float(t_igst),2)
            }
            y.append(datalist)
            purchase_details = ToolsPurchase_Invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).all()

            purchase_serializer = ToolsPurchaseSerializer23(purchase_details, many= True)
            c=purchase_serializer.data
            y.append(c)
         
        else:
            
            datalist={
                "total_amount":0,
                "g_total":0,
                "total_sgst": 0,
                "total_cgst": 0,
                "total_igst":0
            }
            y.append(datalist)
            purchase_details = ToolsPurchase_Invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).all()

            purchase_serializer = ToolsPurchaseSerializer23(purchase_details, many= True)
            c=purchase_serializer.data
            y.append(c)
        
        h1=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=2).filter(financial_period__range=[startdate, enddate]).aggregate(Sum('payment_amount'))
        
        k= purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=2).filter(financial_period__range=[startdate, enddate])
        if purchase_paymentdetails.objects.all().exists():
           m11={"t_purchase_payment_received":h1['payment_amount__sum']}
           y.append(m11)
        else:
            m1={"t_purchase_payment_received":0}
            y.append(m11)

        serializers =purchasepaymentserializer(k,many=True)
        b1=serializers.data
        y.append(b1)
        list1.append(y)
        h5=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(debit=True).filter(financial_period__range=[startdate, enddate]).aggregate(Sum('voucher_amount'))
        h4=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).filter(credit=True).aggregate(Sum('voucher_amount'))
        

        h7=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).filter(with_gst=True).aggregate(Sum('voucher_amount'))
        h8=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).filter(with_gst=False).aggregate(Sum('voucher_amount'))
        h6=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).filter(with_gst=True).aggregate(Sum('gst_amt'))
        
        if pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all().exists():

        
         
        

            d={"total_expenses":h5['voucher_amount__sum'],
            "total_credit":h4['voucher_amount__sum'],
            "total_without_gst":h8['voucher_amount__sum'],
            "total_with_gst":h7['voucher_amount__sum'],
            "total_gst":h6['gst_amt__sum'],}
            z.append(d)
            
            data= pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all()

            serializer = pettycashdserializer(data, many=True)
            z.append(serializer.data)
        else:
            d={"total_expenses":0,
                "total_credit":0,
                "total_without_gst":0,
                "total_with_gst":0,
                "total_gst":0}
            z.append(d)     
            data= pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all().filter(financial_period__range=[startdate, enddate])

            serializer = pettycashdserializer(data, many=True)
            z.append(serializer.data)
        list1.append(z)
        if depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all().exists():
            final_total1= depit_note_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).aggregate(total_amount=Sum('t_amount'),grand_total=Sum('grand_total'),t_sgst=Sum('t_sgst'),t_cgst=Sum('t_cgst'),t_igst=Sum('t_igst'))
            
            
            total_amount = final_total1['total_amount']
            grand_total = final_total1['grand_total']
            t_sgst = final_total1['t_sgst']
            t_cgst = final_total1['t_cgst']
            t_igst = final_total1['t_igst']


            if total_amount == None:
                total_amount = 0
            if grand_total == None:
                grand_total = 0
            if t_sgst == None:
                t_sgst = 0
            if t_cgst == None:
                t_cgst = 0
            if t_igst == None:
                t_igst = 0

            datalists={
                    "total_amount":round(float(total_amount),2),
                    "grand_total":round(float(grand_total),2),
                    "t_sgst": round(float(t_sgst),2),
                    "t_cgst": round(float(t_cgst),2),
                    "t_igst": round(float(t_igst),2)
                }
            z1.append(datalists)
            data= depit_note_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all().filter(financial_period__range=[startdate, enddate])

            serializer =Depit_Note_Serializer_GetByID(data, many=True)
            z1.append(serializer.data)
          
        else:
            datalists={
                    "total_amount":0,
                    "grand_total":0,
                    "t_sgst": 0,
                    "t_cgst": 0,
                    "t_igst": 0
                }
            data= depit_note_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                                stdate=request.headers['sdate'],
                                                                                lstdate=request.headers['ldate']).all().filter(financial_period__range=[startdate, enddate])

            serializer =Depit_Note_Serializer_GetByID(data, many=True)
            z1.append(serializer.data)
            z1.append(datalists)
         
        h=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(financial_period__range=[startdate, enddate]).filter(purchase_type=1).aggregate(Sum('payment_amount'))
        
        k= purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purchase_type=1).filter(financial_period__range=[startdate, enddate])
        if purchase_paymentdetails.objects.all().exists():
           m1={"t_payment_received":h['payment_amount__sum']}
           z1.append(m1)
        else:
            m1={"t_payment_received":0}
            z1.append(m1)
        serializers =purchasepaymentserializer(k,many=True)
        b6=serializers.data
        z1.append(b6)
        list1.append(z1)
        return Response(list1)

class salesprintpayment(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id=None):
        if id:
            queryset = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

            serializers =salespaymentdetserializer(queryset)
          
            return Response(serializers.data)
        else:
            queryset = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializers =salespaymentdetserializer(queryset, many=True)
          
            return Response(serializers.data)

class daybookre(APIView):
    pass
class salesdeletepayment(generics.GenericAPIView,mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):

    serializer_class = salespaymentdetserializer
    queryset = sales_paymentdetails.objects.all()
    lookup_field = 'id'

    # permission_classes=[~Isjwtvalid & IsAuthenticated]
    # def get(self, request, id=None):

    #     if id:
    #         queryset = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id=id)

    #         serializers =salespaymentdetserializer(queryset,many=True)
    #         resdata = []

    #         for poo in serializers.data:
    #             resdata.append({
    #                 'payment_details':poo,
    #                 'invoice_reff':[]
    #             })
    #             index = len(resdata)-1

    #             f=saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce=poo['id'])

    #             for i in f:

    #                 if i.refinvno == None:

    #                     m=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id=None, payment_details_id = None, companycode_id = poo['companycode_id']).first()

    #                     resdata[index]['invoice_reff'].append({
    #                         'total_amt_invoice':m.totalinvoiceamount,
    #                         'payment_amt_per_invo':m.totalpaymentamount,
    #                         'invo': "Company Opening Balance"
    #                     })

    #                 else:

    #                     m=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id=i.refinvno)

    #                     resdata[index]['invoice_reff'].append({
    #                         'total_amt_invoice':m.invoice_details.grand_total,
    #                         'payment_amt_per_invo':m.payment,
    #                         'invo':m.invoice_details.invno
    #                     })

    #         res = json.dumps(resdata)
    #         return Response(resdata)

    #     else:

    #         return self.list(request)

    # def delete(self, request, id):
    #     return self.destroy(request, id=id)
    

    def get(self, request, id):

        if id:

            payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id=id)

            serializer = salespaymentdetserializer(payment)

            a = serializer.data
            print(a,'llllllllllllll')
            for x in a['invrefs']:

                if x['refinvno'] != None:

                    balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = x['refinvno']['id'])

                    balance_serializer = balancedetailsserilaizer15(balance_get)

                    x['refinvno'] = balance_serializer.data

                elif x['refinvno'] == None:

                    balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = a['companycode']['id']).first()

                    balance_serializer = balancedetailsserilaizer15(balance_get)

                    x['company_opening_balance'] = balance_serializer.data

            return Response(a)

        else:

            payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer =salespaymentdetserializer(payment)

            return Response(serializer.data)
    def delete(self, request, id=None):
        # if id:
        #     payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id=id)

        #     serializer = salespaymentdetserializer(payment)

        #     a = serializer.data

        #     balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = payment.id)
            
        #     balance_get.delete()
        #     if saleinvref.objects.filter(refernce_id=payment.id).exists():

        #         k=saleinvref.objects.filter(refernce_id=payment.id)
        #         k.delete()

        #     payment.delete()
        
        sales_payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        ref_check = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

        if ref_check == True:

            k=saleinvref.objects.filter(refernce_id=sales_payment.id)
            for ke in k:
                m=balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ke.refinvno_id,companycode_id = sales_payment.companycode_id)
                balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ke.refinvno_id,companycode_id = sales_payment.companycode_id).update(ref_payment=m.ref_payment-ke.refinvamount,invamount=m.invamount+ke.refinvamount)
            k.delete()
            reduced_payment = sales_payment.payment_amount

            balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)
            balance_get.delete()
            balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

            

            sales_payment.delete()
        else:

        
            reduced_payment = sales_payment.payment_amount

            balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

            balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

            balance_get.delete()

            sales_payment.delete()
        return Response({"status":True,"message":"succesfully deleted"})

    



class saleswisebalance(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    

    # serializer_class = salespaybalanceserializer
    # queryset = salespaymentbalance.objects.all()

    # lookup_field = 'id'
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request):
        return self.list(request)

    def post(self, request):
        data={}
        indata=request.data
        # print(indata,'ppppppp')
        # print(request.data)
     
        companycode =indata['company_id']
        # print(companycode)
        amount = indata['amount']
        tenant_id=request.user.tenant_company.id
        # print(amount,'pppppppppp')

        # print(ft)
        datas = salesinvoicedetails(company_id=companycode, t_amount=amount,tenant_id =tenant_id)
        ft=salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(invno=datas.invno).exists()
        # update for sales have to create invoice amount match check
        if ft == True:
            print('already exist')

        else:
            datas.save()
            # print(amount)
            xt=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(companycode=companycode).exists()
            # print('..........................................')
            # print(xt)
            if xt == True:
                            getlastdata = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                              stdate=request.headers['sdate'],
                                                                              lstdate=request.headers['ldate']).filter(
                                companycode=companycode).last()
                            # print(getlastdata,'oooooooooooooooo')
                            # print(getlastdata.id,'555555555555555555555555')
                            z = 0
                            za=0
                            z = float(float(amount) + float(getlastdata.totalinvoiceamount))
                            za= float(float(amount) + float(getlastdata.totalbalance_amount))
                            ttdata=balancedetails(payment_code=getlastdata.payment_code+1,invoice_details=datas,invamount=float(amount),companycode=companycode,payment=0,
                                                totalbalance_amount=float(za),totalinvoiceamount=float(z),tenant_id=tenant_id,totalpaymentamount=getlastdata.totalpaymentamount)
                
                            ttdata.save()  
                            # print(ttdata)

            else:
                firstdata=balancedetails(payment_code=1,invoice_details=datas,invamount=float(amount),companycode=companycode,payment=0,
                                                 totalbalance_amount=float(amount),totalinvoiceamount=float(amount),tenant_id=tenant_id,totalpaymentamount=0)
                  
                firstdata.save()      

             

        return Response('succesfully saved')
class saleswisebalanceedit(APIView):
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def post(self,request):
        data={}
        indata=request.data
        # print(indata,'ppppppp')
        # print(request.data)
        
        companycode =indata['companyid']
        amount = indata['amount']
        tenant_id=request.user.tenant_company.id
        # print(amount,'pppppppppp')

        ger=salesinvoicedetails(company_id=companycode ,tenant_id=tenant_id ,t_amount=amount)
        ft=salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(invno=ger.invno).exists()
        # print(ft)
        getid=salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(invno=ger.invno)
        # print(getid.id,'.................................')                                                          
        salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(invno=ger.invno).update(t_amount=amount)
    
        # print(amount)
        xt=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(invoice_details_id=getid.id)
        # print(xt,'pppppppppppppppppppppppppppppppppppp')   
        ge=0
        le=0
        ge=xt.payment_code
        le=ge+1
        # print(xt.payment)
        # print(ge,'999999999999999999999999999999999')
        if ge==1:

            balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(invoice_details_id=getid.id).update(invamount=float(amount),totalbalance_amount=float(amount),totalinvoiceamount=float(amount))
        else:
              
                getlastdata = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(payment_code=int(ge-1),companycode=companycode)
                                                             
                # print(getlastdata,'oooooooooooooooo')
                # print(getlastdata.id,'555555555555555555555555')
             
               
                z = 0
                za=0
                z = float(float(amount) + float(getlastdata.totalinvoiceamount))
                za= float(float(amount) + float(getlastdata.totalbalance_amount))
                balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(payment_code=ge,companycode=companycode).update(invamount=float(amount),totalbalance_amount=float(za),totalinvoiceamount=float(z))
                # print(za,'1111111111111111111111111111')
                zb=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(companycode=companycode).last()  

                fe=zb.payment_code-le
                # (# print(fe))
                xe= range(fe+1)
                for k in xe:
                    ke=0
                    ke=le
                    # print(le,'99999999999999999999999999999')
                    zd=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(companycode=companycode,payment_code=le-1)
                    zc=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(companycode=companycode,payment_code=le)                                          
                    zcx=salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).filter(id=zc.invoice_details_id).exists()
                    if zcx:

                        zl = 0
                        zm=0
                        zcy=salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(id=zc.invoice_details_id)
                        zl = float(float(zcy.invamount) + float(zd.totalinvoiceamount))
                        zm= float(zd.totalbalance_amount) +float(zc.invamount) -float(zc.payment)
                        balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(companycode=companycode,payment_code=le).update(invamount=zcy.invamount,totalbalance_amount=float(zm),totalinvoiceamount=float(zl))
                        le=le+1 
                    else:
                        zl = 0
                        zm=0
                        zcb=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(companycode=companycode,payment_code=le)
                        zl = float(float(zc.invamount) + float(zd.totalinvoiceamount))
                        zm= float(zd.totalbalance_amount) +float(zc.invamount) -float(zc.payment)
                        zax=saleinvref.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(refernce_id=zcb.payment_details_id)
                        saleinvref.current_financialyear(id=request.user.tenant_company.id,
                                                                    stdate=request.headers['sdate'],
                                                                    lstdate=request.headers['ldate']).get(refernce_id=zcb.payment_details_id)                                         
                        balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(companycode=companycode,payment_code=le).update(totalbalance_amount=float(zm),totalinvoiceamount=float(zl))
                        le=le+1 
            
                      
                        
        return Response('succesfully saved')
class salesoverallbalance(generics.GenericAPIView, APIView, mixins.ListModelMixin):
    # serializer = salespaybalanceserializer
    # queryset = salespaymentbalance.objects.all()

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self, request):


    
            a = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).aggregate(Sum('payment_amount'))

            return Response(a)

class salesaggrgate(generics.ListAPIView):  # Just an assumption here
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    serializer_class=salespaymentdetserializer
    queryset=sales_paymentdetails.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cash', 'cheque', 'bank', 'payment_refno_type', 'payment_refno', 'bankdetails_r',  'payment_amount',
    'companycode', 'payment_refdate', 'payment_date', 'billrefered', 'financial_period' ]
    def get(self, request, *args, **kwargs):
        result=[]
        response = super().get(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        total_payment = queryset.aggregate(total_payment=Sum('payment_amount'))

  
        result.append(response.data)
        result.append(total_payment)
        # print(result)
        return Response(result)
class purchaseaggregate(generics.ListAPIView):  # Just an assumption here
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    serializer_class=purchasepaymentserializer
    queryset=purchase_paymentdetails.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cash', 'cheque', 'bank', 'payment_refno_type', 'payment_refno', 'bankdetails_r',  'payment_amount',
    'companycode', 'payment_refdate', 'payment_date','billrefered', 'financial_period' ]
    def get(self, request, *args, **kwargs):
        result=[]
        response = super().get(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())
        total_payment = queryset.aggregate(total_payment=Sum('payment_amount'))

  
        result.append(response.data)
        result.append(total_payment)
        # print(result)
        return Response(result)
class purchasebalance(generics.GenericAPIView, APIView, mixins.ListModelMixin):
    # serializer = salespaybalanceserializer
    # queryset = salespaymentbalance.objects.all()

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self, request):


    
            a = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).aggregate(Sum('payment_amount'))
            return Response(a)

class invwisbalance(generics.GenericAPIView, APIView, mixins.ListModelMixin,mixins.UpdateModelMixin,mixins.CreateModelMixin):
    serializer_class = salespaymentserializer
    queryset = sales_paymentdetails.objects.all()

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request):
        return self.list(request)

    def post(self, request):
        imt=0
        fmt=0
        ift=0
        n = 0
        amt=0
        ab = 0
        inputdata = request.data
        response = request.data
        for r in inputdata:
            for i in response:
                ccode = i['companycode']
                ino = i['invno']
                ft=r['refinvno']
                code=r['companycode']

                resp = list(map(int, str(ft)))
                z = len(resp)
                # print("the perenfernece list",z)
                fmt = float(i['invamount'])
                imt = imt + fmt
                if ccode == code:
                    if ino == resp[ab]:
                        ab = ab + 1
                        ino = i['invno']
                        amounts = float(i['invamount'])
                        n=r['payment_amount']
                        # print("invoice payment ",n)
                        # print("invoice number ",ino)
                        # print("invoice amount ",amounts)
                        amt = float(amounts - n)
                        # print("balance amount",ino,amt)
                    else:
                        ino = i['invno']
                        amounts = float(i['invamount'])
                        n = r['payment_amount']
                        # print("invoice payment ", n)
                        # print("invoice number ", ino)
                        # print("invoice amount ", amounts)
                        bmt = float(amounts + (amt))
                        # print("balance amount", ino, bmt)
                     #  paymentbalance.objects.filter(invno=ino).update(payment_amount=n, balance_amount=amt)
                #else:








            # print('total invoice amount:', imt)
            # print('Total payment:',ift)

        return Response("success")

class customerbalance(generics.GenericAPIView, APIView, mixins.ListModelMixin):
    # serializer_class = salespaybalanceserializer
    # queryset = salespaymentbalance.objects.all()

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request):
        return self.list(request)

    def post(self, request):
        toatl_invamount=0
        total_payamount=0
        i = request.data[0]

        ccode = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = i['companycode'])
        # print(ccode)
        salesinvoice_number = i['invno']
        e = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all().filter(refinvno=salesinvoice_number)
        invamount= float(i['subtotal'])
        response = request.data[1]
        for m in response:
            payment_amount=m['payment_amount']
            companycode = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = m['companycode'])

            if ccode==companycode:
                    # print(salesinvoice_number)
                    # print(invamount)
                    # print(payment_amount)
                    x=saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all()
                    sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(invno=salesinvoice_number).update(payment_amount=payment_amount,balance_amount= 0,total_invamount=toatl_invamount,total_payamount=payment_amount)


        return Response("success")




class delpayment(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    serializer_class = salespaymentserializer
    queryset = sales_paymentdetails.objects.all()
    lookup_field = 'id'
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def delete(self, request, id):
        return self.destroy(request, id=id)
class salespayment(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    serializer_class = paymentserializer
    queryset = balancedetails.objects.all()

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self, request):

      lm=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companyid=id)

      return lm
class purchasepaymentprocessenter(generics.GenericAPIView,APIView,mixins.ListModelMixin,mixins.CreateModelMixin):
    serializer_class = purchasepaymentserializer
    queryset =purchase_paymentdetails.objects.all()
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def post(self, request):

            response=request.data

            # print(response)
            for m in response:
                ccode = m['companycode']
                tenant_id = request.user.tenant_company.id
                # print(ccode)
                sinvno = m['invno']
                amount = float(m['subtotal'])

                ft = purchaseinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                          stdate=request.headers['sdate'],
                                                                          lstdate=request.headers['ldate']).filter(
                    invno=sinvno).exists()
                # print(ft)
                datas = purchaseinvoicedetails(companycode=ccode, amount=float(amount), invno=sinvno,tenant_id=tenant_id)
                if ft == True:
                    print('already exist')

                else:
                    datas.save()
                    # print(amount)
                    xt = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                          stdate=request.headers['sdate'],
                                                                          lstdate=request.headers['ldate']).filter(
                        companycode=ccode).exists()
                    # print('..........................................')
                    # print(xt)
                    if xt == True:
                        hm = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                              stdate=request.headers['sdate'],
                                                                              lstdate=request.headers['ldate']).filter(
                            companycode=ccode)
                        for i in hm:
                            # print(i.id)
                            z = 0
                            z = amount + i.totalinvoiceamount
                            zy = amount + i.totalbalance_amount
                        data1 = purchase_statement(invoice_details=datas, companycode=ccode, invamount=amount,
                                                   payment=0, totalinvoiceamount=z, totalbalance_amount=zy,
                                                   totalpaymentamount=i.totalpaymentamount, tenant_id=tenant_id)
                        data1.save()
                    else:
                        data = purchase_statement(invoice_details=datas, companycode=ccode, totalinvoiceamount=amount,
                                                  invamount=amount, payment=0, totalbalance_amount=amount,
                                                  totalpaymentamount=0, tenant_id=tenant_id)
                        data.save()
            return Response(True)




class purchasepaymentprocess(generics.GenericAPIView,APIView,mixins.ListModelMixin,mixins.CreateModelMixin):
    serializer_class = purchasepaymentserializer
    queryset = purchase_paymentdetails.objects.all()

    lookup_field = 'id'
    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def post(self, request):

        if request.method == "POST":

            inputdata = request.data
            tenant_id=request.user.tenant_company.id
            def gen_led_entry(notes,payment_amount):
                if general_ledger.objects.filter(cash=True).exists():
                    get=general_ledger.objects.filter(cash=True).last()
                    led=general_ledger(cash=True,description=notes,debit=payment_amount,credit=0,balance=get.balance-payment_amount, paymentcode=get.paymentcode+1)
                    led.save()
                else:
                                  
                    led=general_ledger(cash=True,description=notes,debit=payment_amount,credit=0,balance=payment_amount, paymentcode=1)
                    led.save()
                return(led.id)
            def gen_led_entry_bank(b_id,notes,payment_amount):
                if general_ledger.objects.filter(bank=True,bank_ref_id=b_id).exists():
                    get=general_ledger.objects.filter(bank=True,bank_ref_id=b_id).last()
                    led=general_ledger(bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=get.balance-payment_amount, paymentcode=get.paymentcode+1)
                    led.save()
                else:
                                  
                    led=general_ledger(bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=payment_amount, paymentcode=1)
                    led.save()
                return(led.id)
            for i in inputdata:

                payment_amount = float(i['payment_amount'])
                purchase_type = i['purchase_type']
                company_id = i['companycode']
                payment_date = i['payment_date']
                companycode = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = company_id)

                saleinvref_sets = i['saleinvref_set']

                if purchase_type == 1:

                    debit_type = i['debit_type']
                    debit_refno = i['debit_refno']
                    debit_refdate = i['debit_refdate']

                    if len(saleinvref_sets) != 0:

                        value = []

                        for x in saleinvref_sets:

                            value.append(x['refinvamount'])

                        if sum(value) == payment_amount:

                            datas = purchase_paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, purchase_type = purchase_type, billrefered = True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)

                        else:

                            datas = purchase_paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, purchase_type = purchase_type, billrefered = True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)

                    else:

                        datas = purchase_paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, purchase_type = purchase_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)

                elif purchase_type == 2:

                    payment_refdate = i['payment_refdate']
                    payment_refno = i['payment_refno']
                    notes=i['Notes']

                    cash = i['cash']
                    cheque= i["cheque"]
                    bank = i["bank"]
                    b_id=i['bank_id']

                    if len(saleinvref_sets) != 0:

                        value = []

                        for x in saleinvref_sets:

                            value.append(x['refinvamount'])

                        if sum(value) == payment_amount:

                            if cash == True:
                                k=gen_led_entry(notes,payment_amount)

                                datas = purchase_paymentdetails(general_le_id=k,cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, purchase_type = purchase_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                
                            elif cheque == True:

                                close = i['close']

                                if close == True:
                                        k=gen_led_entry_bank(b_id,notes,payment_amount)

                                        datas = purchase_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, purchase_type = purchase_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                        
                                else:
                                    k=gen_led_entry_bank(b_id,notes,payment_amount)

                                    datas = purchase_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, purchase_type = purchase_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                    
                            elif bank == True:
                                k=gen_led_entry_bank(b_id,notes,payment_amount)

                                datas = purchase_paymentdetails(general_le_id=k,bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, purchase_type = purchase_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)
                                
                        else:

                            if cash == True:
                                k=gen_led_entry(notes,payment_amount)

                                datas = purchase_paymentdetails(general_le_id=k,cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, purchase_type = purchase_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                
                            elif cheque == True:

                                close = i['close']

                                if close == True:
                                        k=gen_led_entry_bank(b_id,notes,payment_amount)

                                        datas = purchase_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, purchase_type = purchase_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                        
                                else:
                                    k=gen_led_entry_bank(b_id,notes,payment_amount)

                                    datas = purchase_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, purchase_type = purchase_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                    
                            elif bank == True:
                                k=gen_led_entry_bank(b_id,notes,payment_amount)

                                datas = purchase_paymentdetails(general_le_id=k,bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, purchase_type = purchase_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)
                                
                    elif len(saleinvref_sets) == 0:

                        if cash == True:
                            k=gen_led_entry(notes,payment_amount)

                            datas = purchase_paymentdetails(general_le_id=k,cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, purchase_type = purchase_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                            
                        elif cheque == True:

                            close = i['close']

                            if close == True:
                                    k=gen_led_entry_bank(b_id,notes,payment_amount)

                                    datas = purchase_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, purchase_type = purchase_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                                   
                            else:
                                k=gen_led_entry_bank(b_id,notes,payment_amount)
                                datas = purchase_paymentdetails(general_le_id=k,cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, purchase_type = purchase_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False,payment_date = payment_date)
                             
                        elif bank == True:
                            k=gen_led_entry_bank(b_id,notes,payment_amount)

                            datas = purchase_paymentdetails(general_le_id=k,bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, purchase_type = purchase_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)
                            
                datas.save()

                xt = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode=companycode).exists()

                if xt == True:
                    m = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode=companycode).last()

                    if m.totalbalance_amount == 0:

                        data = purchase_statement(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount,totalpaymentamount=m.totalpaymentamount + payment_amount,totalbalance_amount=(0-payment_amount),totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data.save()

                    elif m.totalbalance_amount < 0:
                        z = 0
                        z = float(float(payment_amount) + float(m.totalpaymentamount))
                        zy = float(float(m.totalbalance_amount) - float(payment_amount))

                        data1 = purchase_statement(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount, totalpaymentamount=z, totalbalance_amount=zy,totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data1.save()

                    elif m.totalbalance_amount > 0:

                        z = 0
                        z = float(float(payment_amount) + float(m.totalpaymentamount))
                        zy = float(float(m.totalbalance_amount) - float(payment_amount))

                        data1 = purchase_statement(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount, totalpaymentamount=z, totalbalance_amount=zy,totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data1.save()

                else:

                    data = purchase_statement(payment_code=1,payment_details=datas, companycode=companycode, invamount=0,payment=payment_amount, totalpaymentamount=payment_amount,totalbalance_amount=(0 - payment_amount), totalinvoiceamount=0,tenant_id=tenant_id, date = payment_date)

                    data.save()

                serializer = purchasepaymentserializer2(request.data)
                balanceamount=payment_amount
                datares={}

                if len(saleinvref_sets) !=0:

                    if serializer.is_valid:

                        # zx = 0
                        for j in saleinvref_sets:

                            # zx=zx+1

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']
                                balanceamount = balanceamount - refinvamount

                                data = purchaseinvref(refernce=datas, tenant_id=tenant_id,refinvno_id=refinvno, refinvamount=refinvamount)

                                data.save()

                                mt = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id=refinvno)

                                x = mt.invamount
                                xy = mt.ref_payment

                                if x == 0:

                                    datares["message"]="Payment already exists for this "
                                else:

                                    z = x - refinvamount
                                    ref_payment = xy + refinvamount

                                    purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id=refinvno).update(invamount=z,ref_payment=ref_payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']
                                balanceamount = balanceamount - refinvamount

                                data = purchaseinvref(refernce = datas, tenant_id = tenant_id, refinvno_id = refinvno, refinvamount = refinvamount)

                                data.save()

                                mt = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode = companycode).first()

                                x = mt.invamount
                                xy = mt.ref_payment

                                if x == 0:

                                    datares["message"]="Payment already exists for this"

                                else:

                                    z = x - refinvamount
                                    ref_payment = xy + refinvamount

                                    balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode = companycode, invoice_details_id = None, payment_details_id = None)

                                    balance_update_filter.update(invamount=z,ref_payment=ref_payment)

                        datares['message'] = 'Success'

                    else:

                        return Response(datares)

        return Response(True)


class purchaseprintpayment(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request):
        
        queryset = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

        serializers = purchasepaymentserializer(queryset, many=True)
        return Response(serializers.data)

    


class purchasedeletepayment(APIView):

    def get(self, request, id):

        if id:

            payment = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id=id)

            serializer = purchasepaymentserializer(payment)

            a = serializer.data

            for x in a['invrefs']:

                if x['refinvno'] != None:

                    balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = x['refinvno']['id'])

                    balance_serializer = purchaseserilaizers17(balance_get)

                    x['refinvno'] = balance_serializer.data

                elif x['refinvno'] == None:

                    balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = a['companycode']['id']).first()

                    balance_serializer = purchaseserilaizers17(balance_get)

                    x['company_opening_balance'] = balance_serializer.data

            return Response(a)

        else:

            payment = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer = purchasepaymentserializer(payment)

            return Response(serializer.data)

    def delete(self, request, id):

        sales_payment = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        ref_check = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

        if ref_check == True:

            k=purchaseinvref.objects.filter(refernce_id=sales_payment.id)
            for ke in k:
                m=balance_get =purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ke.refinvno_id,companycode_id = sales_payment.companycode_id)
                purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ke.refinvno_id,companycode_id = sales_payment.companycode_id).update(ref_payment=m.ref_payment-ke.refinvamount,invamount=m.invamount+ke.refinvamount)
            k.delete()
            reduced_payment = sales_payment.payment_amount

            balance_get =purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

            balance_get.delete()
            balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)
            
            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update =purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)


            sales_payment.delete()
          
            return Response({"status":True,"message":"succesfully deleted"})

        else:

            reduced_payment = sales_payment.payment_amount

            balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

            balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

            balance_get.delete()

            sales_payment.delete()

            return Response({"status":True,"message":"succesfully deleted"})

class GstReports(APIView):

    # permission_classes=[~Isjwtvalid & IsAuthenticated]

    def post(self, request):

        datas=[]
        x=[]
        x1=[]
        y1=[]
        k=[]
        l=[]
        y=[]
        z=[]

        startdate = request.data['fromdate']
        enddate = request.data['todate']

        purchase_data = ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purdate__range=[startdate, enddate]).exists()

        if purchase_data == True:

            purchase = ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purdate__range=[startdate, enddate])

            all_purchase_total =ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purdate__range=[startdate, enddate]).aggregate(total_amount=Sum('amount'),grand_total=Sum('subtotal'),total_cgst=Sum('cgst'),total_sgst=Sum('sgst'),total_igst=Sum('igst'))

            purchase_total_amount = all_purchase_total['total_amount']
            purchase_grand_total = all_purchase_total['grand_total']
            purchase_total_cgst = all_purchase_total['total_cgst']
            purchase_total_sgst = all_purchase_total['total_sgst']
            purchase_total_igst = all_purchase_total['total_igst']

            if purchase_total_amount == None:
                purchase_total_amount = 0

            if purchase_grand_total == None:
                purchase_grand_total = 0

            if purchase_total_cgst == None:
                purchase_total_cgst = 0

            if purchase_total_sgst == None:
                purchase_total_sgst = 0

            if purchase_total_igst == None:
                purchase_total_igst = 0

            for i in purchase:

                company=CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id=i.companycode_id)
                serializer = CompanyDetailsSerializer(company)
            
                datalist={ "purchase_inv_amount":i.amount,
                "purchase_inv_number":i.invno,
                "purchase_inv_date":i.financial_period,
                "purchase_inv_igst":i.igst,
                "purchase_inv_cgst":i.cgst,
                "purchase_inv_sgst":i.sgst,
                "purchase_grand_total":i.subtotal,
                "purchase_company_id":serializer.data}
                x.append(datalist)

            company_ids = []

            for q in purchase:

                if q.companycode_id in company_ids:

                    pass
                    
                else:

                    company_ids.append(q.companycode_id)

            for n in company_ids:

                final_total1=ToolsPurchase_Invoice.objects.current_financialyear(id=request.user.tenant_company.id,
                stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(purdate__range=[startdate, enddate], companycode=n).aggregate(total_amount=Sum('amount'),g_total=Sum('subtotal'),total_cgst=Sum('cgst'),total_sgst=Sum('sgst'),total_igst=Sum('igst'))

                company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = n)
                company_serializer = CompanyDetailsSerializer(company)

                total_amount = final_total1['total_amount']
                grand_total = final_total1['g_total']
                t_sgst = final_total1['total_sgst']
                t_cgst = final_total1['total_cgst']
                t_igst = final_total1['total_igst']


                if total_amount == None:
                    total_amount = 0
                if grand_total == None:
                    grand_total = 0
                if t_sgst == None:
                    t_sgst = 0
                if t_cgst == None:
                    t_cgst = 0
                if t_igst == None:
                    t_igst = 0

                datalist={
                "purchase_company_id":company_serializer.data,
                "purchase_final_total":{
                    "total_amount":round(float(total_amount),2),
                    "g_total":round(float(grand_total),2),
                    "total_sgst": round(float(t_sgst),2),
                    "total_cgst": round(float(t_cgst),2),
                    "total_igst": round(float(t_igst),2)
                }}
                y.append(datalist)

            p_t_amt = purchase_total_amount
            p_g_total = purchase_grand_total
            p_g_cgst = purchase_total_cgst
            p_g_sgst = purchase_total_sgst
            p_g_igst = purchase_total_igst

            z.append({

                "total_amount": round(float(purchase_total_amount),2),
                "g_total": round(float(purchase_grand_total),2),
                "total_cgst": round(float(purchase_total_cgst),2),
                "total_sgst": round(float(purchase_total_sgst),2),
                "total_igst": round(float(purchase_total_igst),2)
            })

            z.append(x)
            z.append(y)

        elif purchase_data == False:

            z.append({

                "total_amount": 0,
                "g_total": 0,
                "total_cgst": 0,
                "total_sgst": 0,
                "total_igst": 0
            })

            z.append(x)
            z.append(y)

        bill_invoice_data = outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bill_date__range=[startdate, enddate]).exists()

        if bill_invoice_data == True:

            invoices = outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bill_date__range=[startdate, enddate]).filter(is_deleted = False)

            final_totals= outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bill_date__range=[startdate, enddate]).aggregate(total_amount=Sum('t_amount'),grand_total=Sum('grand_total'),t_cgst=Sum('t_cgst'),t_sgst=Sum('t_sgst'),t_igst=Sum('t_igst'))

            final_total_amount = final_totals['total_amount']
            final_grand_total = final_totals['grand_total']
            final_t_cgst = final_totals['t_cgst']
            final_t_sgst = final_totals['t_sgst']
            final_t_igst = final_totals['t_igst']

            if final_total_amount == None:
                final_total_amount = 0

            if final_grand_total == None:
                final_grand_total = 0

            if final_t_cgst == None:
                final_t_cgst = 0

            if final_t_sgst == None:
                final_t_sgst = 0

            if final_t_igst == None:
                final_t_igst = 0

            for i in invoices:

                company=CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id=i.company_id_id)
                serializer = CompanyDetailsSerializer(company)

            
                datalists={ "sales_inv_amount":i.t_amount,
                "sales_inv_number":i.invno,
                "sales_inv_date":i.financial_period,
                "sales_inv_igst":i.t_igst,
                "sales_inv_cgst":i.t_cgst,
                "sales_inv_sgst":i.t_sgst,
                "sales_grand_total":i.grand_total,
                "sales_company_id":serializer.data}
                x1.append(datalists)
        
            company_ids = []

            for q in invoices:

                if q.company_id_id in company_ids:

                    pass
                    
                else:

                    company_ids.append(q.company_id_id)
            
            for n in company_ids:

                final_total1= outward_bill_invoice.objects.current_financialyear(id=request.user.tenant_company.id,
                stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(bill_date__range=[startdate, enddate], company_id=n).aggregate(total_amount=Sum('t_amount'),grand_total=Sum('grand_total'),t_sgst=Sum('t_sgst'),t_cgst=Sum('t_cgst'),t_igst=Sum('t_igst'))

                company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = n)
                company_serializer = CompanyDetailsSerializer(company)

                total_amount = final_total1['total_amount']
                grand_total = final_total1['grand_total']
                t_sgst = final_total1['t_sgst']
                t_cgst = final_total1['t_cgst']
                t_igst = final_total1['t_igst']


                if total_amount == None:
                    total_amount = 0
                if grand_total == None:
                    grand_total = 0
                if t_sgst == None:
                    t_sgst = 0
                if t_cgst == None:
                    t_cgst = 0
                if t_igst == None:
                    t_igst = 0

                datalists={
                    "sales_company_code":company_serializer.data,
                    "sales_final_total":{
                        "total_amount":round(float(total_amount),2),
                        "grand_total":round(float(grand_total),2),
                        "t_sgst": round(float(t_sgst),2),
                        "t_cgst": round(float(t_cgst),2),
                        "t_igst": round(float(t_igst),2)
                    }}
                y1.append(datalists)
                
            
            s_t_amt = final_total_amount
            s_g_total = final_grand_total
            sales_g_cgst = final_t_cgst
            sales_g_sgst = final_t_sgst
            sales_g_igst = final_t_igst

            l.append({
                "total_amount": round(float(final_total_amount), 2),
                "grand_total": round(float(final_grand_total), 2),
                "t_cgst": round(float(final_t_cgst), 2),
                "t_sgst": round(float(final_t_sgst), 2),
                "t_igst": round(float(final_t_igst), 2)
            })
            l.append(x1)
            l.append(y1)

        elif bill_invoice_data == False:

            l.append({
                "total_amount": 0,
                "grand_total": 0,
                "t_cgst": 0,
                "t_sgst": 0,
                "t_igst": 0
            })
            l.append(x1)
            l.append(y1)

        if purchase_data == True and bill_invoice_data == True:
            t_amt= p_t_amt - s_t_amt
            g_total= p_g_total - s_g_total
            g_cgst=p_g_cgst-sales_g_cgst
            g_sgst= p_g_sgst- sales_g_sgst
            g_igst=p_g_igst-sales_g_igst
            datatm={ "t_amt":round(float(t_amt),2),
            "g_total":round(float(g_total),2),
            "g_cgst":round(float(g_cgst),2),
            "g_sgst":round(float(g_sgst),2),
            "g_igst":round(float(g_igst),2)}
            k.append(datatm)

            datas.append(l)
            datas.append(z)
            datas.append(k)

        elif purchase_data == True and bill_invoice_data == False:

            t_amt= p_t_amt
            g_total= p_g_total
            g_cgst=p_g_cgst
            g_sgst= p_g_sgst
            g_igst=p_g_igst
            datatm={ "t_amt":round(float(t_amt),2),
            "g_total":round(float(g_total),2),
            "g_cgst":round(float(g_cgst),2),
            "g_sgst":round(float(g_sgst),2),
            "g_igst":round(float(g_igst),2)}
            k.append(datatm)

            datas.append(l)
            datas.append(z)
            datas.append(k)

        elif purchase_data == False and bill_invoice_data == True:

            t_amt= s_t_amt
            g_total= s_g_total
            g_cgst=sales_g_cgst
            g_sgst= sales_g_sgst
            g_igst=sales_g_igst
            datatm={ "t_amt":round(float(t_amt),2),
            "g_total":round(float(g_total),2),
            "g_cgst":round(float(g_cgst),2),
            "g_sgst":round(float(g_sgst),2),
            "g_igst":round(float(g_igst),2)}
            k.append(datatm)

            datas.append(l)
            datas.append(z)
            datas.append(k)

        elif purchase_data == False and bill_invoice_data == False:

            t_amt= 0
            g_total= 0
            g_cgst=0
            g_sgst= 0
            g_igst=0
            datatm={ "t_amt":round(float(t_amt),2),
            "g_total":round(float(g_total),2),
            "g_cgst":round(float(g_cgst),2),
            "g_sgst":round(float(g_sgst),2),
            "g_igst":round(float(g_igst),2)}
            k.append(datatm)

            datas.append(l)
            datas.append(z)
            datas.append(k)


        h7=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(with_gst=True).aggregate(Sum('voucher_amount'))
        h8=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'], lstdate=request.headers['ldate']).filter(with_gst=True).aggregate(Sum('gst_amt'))
        list1 = []
        list3=[]
        if pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(with_gst=True).exists():

            d={
                "total_expenses":h7['voucher_amount__sum'],
                "total_gst_amount":h8['gst_amt__sum'],
                "total":h7['voucher_amount__sum']+h8['gst_amt__sum']}
            list1.append(d)
  
            k=pettycash.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                            stdate=request.headers['sdate'],
                                                                            lstdate=request.headers['ldate']).filter(with_gst=True)
            k1= voucherdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                      lstdate=request.headers['ldate']).filter(expenses__with_gst=True)
            jh=0 
            for xc in k1:
                if jh==xc.id:
                    print('lll')
                    jh=xc.id
                else:
                    m=voucherdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                            stdate=request.headers['sdate'],
                                                                            lstdate=request.headers['ldate']).get(id=xc.id)
                    serializers = voucherserializer(m) 
                    jh=xc.id
                
                    list2=serializers.data
                    list1.append(list2)
            datas.append(list1)
        return Response(datas)
class salesrefupdate(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    # serializer_class = salespaybalanceserializer
    # queryset = salespaymentbalance.objects.all()
    lookup_field = 'id'

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id = None):

        if id:

            sales = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'], lstdate=request.headers['ldate']).get(id=id)

            serializer = salespaymentserializer(sales)

            return Response(serializer.data)

        else: 

            sales = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'], lstdate=request.headers['ldate']).all()

            serializer = salespaymentserializer(sales, many = True)

            return Response(serializer.data)



    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def patch(self,request,id):
        inputdata = request.data
        # print(inputdata)
        for i in inputdata:
            # paymentid=i['paymentid']

            saleinvref_sets = i['saleinvref_set']

            # refinvno = i['refinvno']
            ft=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(id=id).exists()

            if ft == True:
                datas=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(id=id)

                companycode=datas.companycode
                ht = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(refernce=id).exists()
                if ht == True:
                    for j in saleinvref_sets:

                        tenant_id=request.user.tenant_company.id
                        refinvamount = j['refinvamount']
                        refid=j['refernce']
                        gt = salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(invno=datas.invno)  
                        saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(id=refid).update(refernce=datas, refinvno=datas.invno, refinvamount=refinvamount,tenant_id=tenant_id,invoice_details=gt)
                        
                        mt = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(invoice_details_id=datas.id)
                        gt = salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(invno=datas.invno) 
                        x = gt.invamount
                        # y = mt.invno
                        xy = mt.payment
                    

                        z = x - refinvamount
                        payment = xy+refinvamount
                        balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(invoice_details_id=datas.id).update(
                                 invamount=z,ref_payment=payment,payment_details=datas)
                    sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(id=id).update(billrefered=True)
                   
                      
                else:
                   for j in saleinvref_sets:

                        tenant_id=request.user.tenant_company.id
                        refinvamount = j['refinvamount']
                        gt = salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(invno=datas.invno)  
                        data = saleinvref(refernce=datas, refinvno=datas.invno, refinvamount=refinvamount,tenant_id=tenant_id,invoice_details=gt)
                        data.save()
                        mt = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(invoice_details_id=datas.id)
                                                                       
                        # print (mt)
                        # print('++++++++++++++++++++++++++++++++++++')
                        x=0
                        x = mt.invamount
                        # print(x,'ppppppppp')
                        xy=0
                        xy = mt.ref_payment
                        if x == 0:
                            return Response(str(
                               datas.invno) + '' + 'This invoice amount already paid....enter this amount for another invoice')
                        else:

                            z = x - refinvamount
                            payment = xy+refinvamount
                            balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(invoice_details_id=datas.id).update(
                                 invamount=z,ref_payment=payment,payment_details=datas)
                   sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(id=id).update(billrefered=True)
        return Response(True)
class purchasewisebalance(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    # serializer_class = purchasepaymentserilaizer
    # queryset = purchasepaymentbalance.objects.all()
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request):
     #  a = dynamic_link("sales/allinvprint")
      # response = requests.get(a).json()
      # return Response(response)
       return self.list(request)


    def post(self, request):
          
            response = request.data
            # print(response)
            # response = requests.get('http://127.0.0.1:8000/sales/invoice/all/').json()
            # print(response)
            for m in response :
                company_id = m['companycode']
                companycode = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = company_id)
                tenant_id=request.user.tenant_company.id
                # print(companycode)
                sinvno = m['invno']
                amount = float(m['subtotal'])


                ft = purchaseinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(invno=sinvno).exists()
                # print(ft)
                datas = purchaseinvoicedetails(companycode=companycode, subtotal=amount, invno=sinvno,tenant_id=tenant_id)
                # serializer = salespaybalanceserializer(request.data)
                # update for sales have to create invoice amount match check
                if ft == True:
                    return Response('Invoice number already exist')

                else:
                    datas.save()
                    # print(amount)
                    xt=purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=companycode).exists()
                    # print('..........................................')
                    # print(xt)
                    if xt ==True:
                             hm= purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=companycode)
                             for i in hm:
                                 # print(i.id)
                                 z=0
                                 z=amount+i.totalinvoiceamount
                                 zy=amount+i.totalbalance_amount
                             data1=purchase_statement(invoice_details=datas,companycode=companycode,invamount=amount,payment=0,totalinvoiceamount=z,totalbalance_amount=zy,totalpaymentamount=0,tenant_id=tenant_id)
                             data1.save()
                    else:
                        data = purchase_statement(invoice_details=datas,companycode=companycode, totalinvoiceamount=amount, invamount=amount,payment=0,totalbalance_amount=amount,totalpaymentamount=0,tenant_id=tenant_id)
                        data.save()


            return Response('succesfully saved')

class purchasebalancedetails(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    serializer_class = purchaseserilaizer
    queryset = purchase_statement.objects.all()
    lookup_field = 'id'
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self, request, id=None):
        if id:
            queryset = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                             lstdate=request.headers['ldate']).filter(companycode=id).exclude(invamount=0)
            serializers = purchaseserilaizer(queryset, many=True)
            return Response(serializers.data)
        else:

            queryset = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all()

            serializers =balancedetailsserilaizer(queryset, many=True)
            return Response(serializers.data)
class purchaserefupdate(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    serializer_class = purchaseserilaizer
    queryset = purchase_statement.objects.all()
    lookup_field = 'id'

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def patch(self,request,id):
        inputdata = request.data
        # print(inputdata)
        for i in inputdata:
            # companycode = i['companycode']
            # paymentid=i['paymentid']

            purchaseinvref_sets = i['purchaseinvref_set']

            # refinvno = i['refinvno']
            ft=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(id=id).exists()

            if ft == True:
               datas=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(id=id)
               # print (datas)
               ht = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(refernce=id).exists()
               if ht == True:
                   print('already exist')
               else:
                   for j in purchaseinvref_sets:
                        # print(purchaseinvref_sets)
                        # print('@@@@@@@@@@@@@@@@@@@@@')
                        # print(j)
                        tenant_id=request.user.tenant_company.id
                        refinvno = j['refinvno']
                        refinvamount = j['refinvamount']
                        data = purchaseinvref(refernce=datas, refinvno=refinvno, refinvamount=refinvamount,tenant_id=tenant_id)
                        data.save()
                        # print(request.user.tenant_company.id)
                        mt = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).get(invoice_details__invno=refinvno)
                        # print (mt)
                        # print('++++++++++++++++++++++++++++++++++++')
                        # print(mt.payment,'oo')
                        x = mt.invamount
                        # y = mt.invno
                        xy = mt.payment
                        # print(xy)
                        if x == 0:
                            return Response(str(
                                refinvno) + '' + 'This invoice amount already paid....enter this amount for another invoice')
                        else:

                            z = x - refinvamount
                            payment = xy+refinvamount
                            purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(invoice_details__invno=refinvno).update(
                                 invamount=z, payment=payment)
                            return Response(str(
                                refinvno) + '' + 'saved')
                   purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(id=id).update(billrefered=True)
                

        return Response(True)

class salesinvoicebalancedetails(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):
    serializer_class =  balancedetailsserilaizer
    queryset = balancedetails.objects.all()
    lookup_field = 'id'
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self, request, id=None):
        if id:
            queryset = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                             lstdate=request.headers['ldate']).filter(companycode=id)
            # serializers = balancedetailsserilaizer(queryset, many=True)
            serializers = paymentserializers(queryset, many=True)
            return Response(serializers.data)
        else:

            queryset = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all()

            serializers =balancedetailsserilaizer(queryset, many=True)
            return Response(serializers.data)

class purchaseinvoicebalancedetails(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    serializer_class =  purchaseserilaizer
    queryset = purchase_statement.objects.all()
    lookup_field = 'id'
    def get(self, request, id=None):
        if id:
            queryset = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                             lstdate=request.headers['ldate']).filter(companycode=id)
            serializers = purchaseserilaizer(queryset, many=True)
            return Response(serializers.data)
        else:

            queryset =purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all()

            serializers =purchaseserilaizer(queryset, many=True)
            return Response(serializers.data)

   
# class 
#     fromDate = self.request.query_params.get('fromDate',None)
#     toDate = self.request.query_params.get('toDate',None)
#     response  = yourModel.objects.filter(date__gte=fromDate,date__lte=toDate)
#     return response
   
  

class debitnoteentry(APIView):
      permission_classes=[~Isjwtvalid & IsAuthenticated]
      def post(self,request):
        data=request.data
        # print(request.data)
        for i in data:
            zy=0
            debitamount=i['c']
            debitno=i['debitno']
            cmyid = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = i['company_id'])
            tenant_id=request.user.tenant_company.id
            aa=balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=cmyid).last()
            zy=aa.totalbalance_amount-debitamount
            data1=balancedetails( payment_code= aa.payment_code+1,debitnote_amount=debitamount,companycode=cmyid,debinoterefno=debitno,totalinvoiceamount=aa.totalinvoiceamount,totalbalance_amount=zy,totalpaymentamount=aa.totalpaymentamount,tenant_id=tenant_id)
            data1.save()      
        return Response(True)  
class debitnoteentrypurchase(APIView):
      permission_classes=[~Isjwtvalid & IsAuthenticated]
      def post(self,request):
        data=request.data
        for i in data:
            zy=0
            debitamount=i['debitamount']
            debitno=i['debitno']
            cmyid = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = i['company_id'])
            tenant_id=request.user.tenant_company.id
            aa=purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=cmyid).last()
            
            zy=aa.totalbalance_amount - float(debitamount)
            data1=purchase_statement( payment_code= aa.payment_code+1,debitnote_amount=debitamount,companycode=cmyid,debinoterefno=debitno,totalinvoiceamount=aa.totalinvoiceamount,totalbalance_amount=zy,totalpaymentamount=aa.totalpaymentamount,tenant_id=tenant_id)
            data1.save()      
        return Response(True)  

class sales_payment_report_sheet(APIView):
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request):
        a = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all()
        ser = balancedetailsreportserilaizers(a,many=True)
        return Response(ser.data)

class purchasebillpayment_reports(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self, request):
            queryset =purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).all()

            serializers =purchaseserilaizer(queryset, many=True)
            return Response(serializers.data)


class yearopeningview(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request,id=None):

      
        datas={}
        data=request.data
        for k in data:
            # print(k['id'],'llllllllllllllll')
            ger=purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=k['id']).exists()
            if ger:
                stocks=purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=k['id']).last()
                lst_date=stocks.financial_period
                # print(lst_date)
               
                gets=purchase_statement(companycode=stocks.companycode , payment_code=stocks.payment_code+1  , tenant_id=request.user.tenant_company.id , totalbalance_amount =stocks.totalbalance_amount ,  totalinvoiceamount=stocks.totalinvoiceamount , totalpaymentamount=stocks.totalpaymentamount)
                gets.save()
            else:
                    datas['error']='not matching fields'
            datas['message']="done"
        return Response(datas)




class ledger_Openingqty(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    def get(self,request,id=None):

      
        datas={}
        

        fere=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(cash=True).exists()

        if fere==False:
            final_total3=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(bank=True).aggregate(Sum('payment_amount'))
            final_total4=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(bank=True).aggregate(Sum('payment_amount'))
            # print(final_total3,'0000000000')
            # print(final_total4,'000000000000dsddddddddd')

            final_total5=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(cheque=True).aggregate(Sum('payment_amount'))
            final_total6=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(cheque=True).aggregate(Sum('payment_amount'))
            # print(final_total5,'0000000000')
            # print(final_total6,'000000000000dsddddddddd')

        
            total_amount3 = float(final_total3['payment_amount__sum'])+float(final_total5['payment_amount__sum'])
            total_amount4= float(final_total4['payment_amount__sum'])+float(final_total6['payment_amount__sum'])
            fin=total_amount3-total_amount4
            # print(fin,'ooooooo')
            ope=general_ledger(opening_bank_balance=fin,bank=True)
            ope.save()
        else:
            final_total1=sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(cash=True).aggregate(Sum('payment_amount'))
            final_total2=purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(cash=True).aggregate(Sum('payment_amount'))
            # print(final_total1,'0000000000')
            # print(final_total2,'000000000000dsddddddddd')

        
            total_amount1 = float(final_total1['payment_amount__sum'])
            total_amount2= float(final_total2['payment_amount__sum'])
            # print(total_amount1)
            # print(total_amount2)
            fin=float(total_amount1-total_amount2)
            # print(fin,'ooooooo')
            ope=general_ledger(opening_cash_balance=fin,cash=True)
            ope.save()

        datas['message']="done"
        return Response(datas)


class sales_statement_Openingqty(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request,id=None):

        
        datas={}
        data=request.data
        for k in data:
            ger= balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=k['id']).exists()
            if ger:
                stocks= balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=k['id']).last()
                lst_date=stocks.financial_period
                # print(lst_date)
   
                gets= balancedetails(companycode=stocks.companycode , payment_code=stocks.payment_code  , tenant_id=request.user.tenant_company.id , totalbalance_amount =stocks.totalbalance_amount ,  totalinvoiceamount=stocks.totalinvoiceamount , totalpaymentamount=stocks.totalpaymentamount)
                gets.save()
            else:
                    datas['error']='not matching fields'
            datas['message']="done"
        return Response(datas)


class companytoSalesPayment(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id = None):

        if id:

            company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = id)

            serializer = CompanyToSales(company)

            return Response(serializer.data)

        else:

            company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).all()

            serializer = CompanyToSales(company,many=True)

            return Response(serializer.data)

class companytoPurchasePayment(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id = None):

        if id:

            company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = id)

            serializer =  CompanyToPurchase(company)


            return Response(serializer.data)

        else:

            company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).filter(cancel=False,type=2)

            serializer =  CompanyToPurchase(company, many = True)

            return Response(serializer.data)


class ledgerview(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request,id=None):

        if id :

            queryset=general_ledger.objects.get(id=id)
            ser= ledgerserializer(queryset)

            return Response(ser.data)

        else:

            queryset1=general_ledger.objects.all()
            ser1= ledgerserializer(queryset1 ,many=True)

            return Response(ser1.data)

    def post(self,request):
        m=request.data
        cash=m['cash']
        bank=m['bank']
        notes=m['notes']
        payment_amount=m['amount']
        trf=m['bank_transfer']
        tenant_id=request.user.tenant_company.id

        if cash==True:
            b_id=m['bank_ref']
            if general_ledger.objects.filter(cash=True).exists():
                if general_ledger.objects.filter(bank_ref_id=b_id).exists():
                    get=general_ledger.objects.filter(bank_ref_id=b_id).last()
                    led=general_ledger(tenant_id=tenant_id,bank=True,description=notes,debit=0,bank_ref_id=b_id,credit=payment_amount,balance=get.balance+payment_amount, paymentcode=int(get.paymentcode)+1)
                    led.save()
                    get1=general_ledger.objects.filter(cash=True).last()
                    led1=general_ledger(tenant_id=tenant_id,cash=True,description=notes,debit=payment_amount,credit=0,balance=get1.balance-payment_amount, paymentcode=int(get.paymentcode)+1)
                    led1.save()
                else:
                    
                    led=general_ledger(tenant_id=tenant_id,bank=True,description=notes,debit=0,bank_ref_id=b_id,credit=payment_amount,balance=payment_amount, paymentcode=1)
                    led.save()
                    get1=general_ledger.objects.filter(cash=True).last()
                    led1=general_ledger(tenant_id=tenant_id,cash=True,description=notes,debit=payment_amount,credit=0,balance=get1.balance-payment_amount, paymentcode=int(get1.paymentcode)+1)
                    led1.save()
            else:
                                
                led=general_ledger(tenant_id=tenant_id,cash=True,description=notes,debit=payment_amount,credit=payment_amount,balance=payment_amount, paymentcode=1)
                led.save()
                
        elif bank==True:
            b_id=m['bank_ref']
            if general_ledger.objects.filter(bank_ref_id=b_id).exists():
                if general_ledger.objects.filter(bank_ref_id=b_id).exists():
                    get=general_ledger.objects.filter(bank_ref_id=b_id).last()
                    print(b_id,'kkkkkkkkkkkkkkkkkkkkkkkkkk')
                    led=general_ledger(tenant_id=tenant_id,bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=get.balance-payment_amount, paymentcode=int(get.paymentcode)+1)
                    led.save()
                    get1=general_ledger.objects.filter(cash=True).last()
                    led1=general_ledger(tenant_id=tenant_id,cash=True,description=notes,debit=0,credit=payment_amount,balance=get1.balance+payment_amount, paymentcode=int(get1.paymentcode)+1)
                    led1.save()
                else:
                    led=general_ledger(tenant_id=tenant_id,bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=get.balance-payment_amount, paymentcode=1)
                    led.save()
                    get1=general_ledger.objects.filter(cash=True).last()
                    led1=general_ledger(tenant_id=tenant_id,cash=True,description=notes,debit=0,credit=payment_amount,balance=get1.balance+payment_amount, paymentcode=int(get1.paymentcode)+1)
                    led1.save()
            else:
                                
                led=general_ledger(tenant_id=tenant_id,bank=True,cash=True,description=notes,debit=payment_amount,credit=0,balance=payment_amount, paymentcode=1)
                led.save()
        elif trf==True:
            b_id=m['bank_ref_from']
            b_id1=m['bank_ref_to']
            if general_ledger.objects.filter(bank=True,bank_ref_id=b_id).exists():
                get=general_ledger.objects.filter(bank=True,bank_ref_id=b_id).last()
                print(get.paymentcode,'lllllllll')
                led=general_ledger(tenant_id=tenant_id,bank=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=0,balance=get.balance-payment_amount, paymentcode=int(get.paymentcode)+1)
                led.save()
                get1=general_ledger.objects.filter(bank=True,bank_ref_id=b_id1).last()
                print(get.paymentcode,'lllllllll')
                led1=general_ledger(tenant_id=tenant_id,bank=True,description=notes,bank_ref_id=b_id1,debit=0,credit=payment_amount,balance=get1.balance+payment_amount, paymentcode=int(get1.paymentcode)+1)
                led1.save()
            else:
                                
                led=general_ledger(tenant_id=tenant_id,bank=True,cash=True,description=notes,bank_ref_id=b_id,debit=payment_amount,credit=payment_amount,balance=payment_amount, paymentcode=1)
                led.save()

        return Response({"status":True,"message":"successfully added"})

class ledgerview_t(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request,id=None):

        if id :

            queryset=general_ledger.objects.filter(bank_ref_id=id)
            ser= ledgerserializer1(queryset,many=True)

            return Response(ser.data)

        else:

            queryset1=general_ledger.objects.all()
            ser1= ledgerserializer1(queryset1 ,many=True)

            return Response(ser1.data)

    def post(self,request):
        m=request.data
    
        notes=m['notes']
        voucher_amount=m['amount']
        credit=m['credit']
        tenant_id=request.user.tenant_company.id
        if credit==True:

            if general_ledger.objects.filter(petty_cash=True).exists():


                ki=general_ledger.objects.filter(petty_cash=True).last()
                ldata=general_ledger(tenant_id=tenant_id,petty_cash=True,credit=voucher_amount,debit=0,paymentcode=ki.paymentcode+1,balance=ki.balance+voucher_amount)
                ldata.save()
                if general_ledger.objects.filter(cash=True).exists():
                    ki2=general_ledger.objects.filter(cash=True).last()
                    ldata1=general_ledger(tenant_id=tenant_id,cash=True,credit=0,debit=voucher_amount,paymentcode=ki2.paymentcode+1,balance=ki2.balance-voucher_amount)
                    ldata1.save()
                else:
                    data=general_ledger(tenant_id=tenant_id,cash=True,credit=0,debit=voucher_amount,paymentcode=1,balance=voucher_amount)
                    data.save()
            else:
                ldata=general_ledger(tenant_id=tenant_id,petty_cash=True,credit=voucher_amount,debit=0,paymentcode=1,balance=voucher_amount)
                ldata.save()
                
        else:
           
            if general_ledger.objects.filter(petty_cash=True).exists():
                ki=general_ledger.objects.filter(petty_cash=True).last()
                print(ki,'kkkkk')
                ldata=general_ledger(tenant_id=tenant_id,petty_cash=True,credit=0,debit=voucher_amount,paymentcode=ki.paymentcode+1,balance=ki.balance-voucher_amount)
                ldata.save()
                if general_ledger.objects.filter(cash=True).exists():
                    ki2=general_ledger.objects.filter(cash=True).last()
                    ldata1=general_ledger(tenant_id=tenant_id,cash=True,credit=voucher_amount,debit=0,paymentcode=ki2.paymentcode+1,balance=ki2.balance+voucher_amount)
                    ldata1.save()
                else:
                    ldata=general_ledger(tenant_id=tenant_id,cash=True,credit=voucher_amount,debit=0,paymentcode=1,balance=voucher_amount)
                    ldata.save()
            else:
                ldata=general_ledger(tenant_id=tenant_id,petty_cash=True,credit=0,debit=voucher_amount,paymentcode=1,balance=voucher_amount)
                ldata.save()
        return Response({"status":True,"message":"successfully added"})

class purchase_statement_Openingqty_yr(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request, type = None):

        if type == 1:

            balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(year_opening = True)

        elif type == 0:

            balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(year_opening = False)

        else:

            balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

        serializer = purchaseserilaizer2(balance, many=True)

        return Response(serializer.data)

    def post(self,request):

      
        datas={}
        data=request.data
        for i in data:

            to_date = date.today() 
         
            cos_id=i['companycode']
            get_id=CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id=cos_id)
            gets=purchase_statement(companycode=get_id , payment_code=1  , tenant_id=request.user.tenant_company.id , invamount = i['totalbalance_amount'], ref_payment = 0, totalbalance_amount =i['totalbalance_amount'] ,  totalinvoiceamount=i['totalinvoiceamount'] , totalpaymentamount=i['totalpaymentamount'], year_opening = i['year_opening'], date = to_date)
            gets.save()
         
        datas['message']="done"
        return Response(datas)


class sales_statement_Openingqty_yr(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request, type = None):

        if type == 1:

            balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(year_opening = True)

        elif type == 0:

            balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(year_opening = False)

        else:

            balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

        serializer=balancedetailsreportserilaizers2(balance,many=True)
        return Response(serializer.data)


    def post(self,request,id=None):

        
        datas={}
        data=request.data
        for i in data:

            to_date = date.today() 
               
            cos_id=i['companycode']
            get_id=CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id=cos_id)
            gets= balancedetails(companycode=get_id , payment_code=1  , tenant_id=request.user.tenant_company.id , invamount = i['totalbalance_amount'], ref_payment = 0, totalbalance_amount =i['totalbalance_amount'] ,  totalinvoiceamount=i['totalinvoiceamount'], totalpaymentamount=i['totalpaymentamount'], year_opening = i['year_opening'], date = to_date)
            gets.save()
           
            datas['message']="done"
        return Response(datas)

class vendor_statement_Openingqty_yr(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request, type = None):

        if type == 1:

            balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(year_opening = True)

        elif type == 0:

            balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(year_opening = False)

        else:

            balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

        serializer=Vendor_Balance_Serializer2(balance,many=True)
        return Response(serializer.data)


    def post(self,request):

        
        datas={}
        data=request.data
        for i in data:

            to_date = date.today() 
               
            cos_id=i['companycode']
            get_id=CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id=cos_id)
            gets= Vendor_Balancedetails(companycode=get_id, payment_code=1, tenant_id=request.user.tenant_company.id, invamount = i['totalbalance_amount'], ref_payment = 0, totalbalance_amount =i['totalbalance_amount'],  totalinvoiceamount=i['totalinvoiceamount'], totalpaymentamount=i['totalpaymentamount'], year_opening = i['year_opening'], date = to_date)
            gets.save()
           
            datas['message']="done"
        return Response(datas)


class PurcahseOpeningGetPatch(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id):

        balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, year_opening = True, invoice_details_id = None, payment_details_id = None)

        serializer = purchaseserilaizer2(balance, many=True)

        return Response(serializer.data)

    def patch(self, request, id):

        data = {}

        # ADD FRONT END VALIDATIONS FOR TOTAL BALANCE AMOUNT

        company_balances = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, year_opening = True, invoice_details_id = None, payment_details_id = None)

        for x in company_balances:

            company_opening = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            company_opening_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

            old_balance_amount = company_opening.totalbalance_amount
            old_invoice_amount = company_opening.totalinvoiceamount
            old_payment_amount = company_opening.totalpaymentamount

            serializer = purchaseserilaizers17(company_opening, data=request.data, partial = True)

            if serializer.is_valid():

                serializer.save()

                amount = request.data

                if old_balance_amount < amount['totalbalance_amount']:

                    extra = amount['totalbalance_amount'] - old_balance_amount

                    company_opening_filter.update(invamount = company_opening.invamount + extra)

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalbalance_amount = t.totalbalance_amount + extra)

                elif old_invoice_amount < amount['totalinvoiceamount']:

                    extra = amount['totalinvoiceamount'] + old_balance_amount

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalinvoiceamount = t.totalinvoiceamount + extra)

                elif old_payment_amount < amount['totalpaymentamount']:

                    extra = amount['totalpaymentamount'] + old_balance_amount

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalpaymentamount = t.totalpaymentamount + extra)

                elif old_balance_amount > amount['totalbalance_amount']:

                    extra = amount['totalbalance_amount'] - old_balance_amount

                    company_opening_filter.update(invamount = company_opening.invamount - extra)

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalbalance_amount = t.totalbalance_amount - extra)

                elif old_invoice_amount > amount['totalinvoiceamount']:

                    extra = amount['totalinvoiceamount'] - old_balance_amount

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalinvoiceamount = t.totalinvoiceamount - extra)

                elif old_payment_amount > amount['totalpaymentamount']:

                    extra = amount['totalpaymentamount'] - old_balance_amount

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalpaymentamount = t.totalpaymentamount + extra)

                data['status'] = True
                data['success'] = "patch"

            else:

                data['status'] = False
                data['error'] = serializer.errors

        return Response(data)

class SalesOpeningGetPatch(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id):

        balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, year_opening = True, invoice_details_id = None, payment_details_id = None)

        serializer = paymentserializers(balance, many=True)

        return Response(serializer.data)

    def patch(self, request, id):

        data = {}

        # ADD FRONT END VALIDATIONS FOR TOTAL BALANCE AMOUNT

        company_balances = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, year_opening = True, invoice_details_id = None, payment_details_id = None)

        for x in company_balances:

            company_opening = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            company_opening_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

            old_balance_amount = company_opening.totalbalance_amount
            old_invoice_amount = company_opening.totalinvoiceamount
            old_payment_amount = company_opening.totalpaymentamount

            serializer = balancedetailsserilaizers17(company_opening, data=request.data, partial = True)

            if serializer.is_valid():

                serializer.save()

                amount = request.data

                if old_balance_amount < amount['totalbalance_amount']:

                    extra = amount['totalbalance_amount'] - old_balance_amount

                    company_opening_filter.update(invamount = company_opening.invamount + extra)

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalbalance_amount = t.totalbalance_amount + extra)

                elif old_invoice_amount < amount['totalinvoiceamount']:

                    extra = amount['totalinvoiceamount'] + old_balance_amount

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalinvoiceamount = t.totalinvoiceamount + extra)

                elif old_payment_amount < amount['totalpaymentamount']:

                    extra = amount['totalpaymentamount'] + old_balance_amount

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalpaymentamount = t.totalpaymentamount + extra)

                elif old_balance_amount > amount['totalbalance_amount']:

                    extra = amount['totalbalance_amount'] - old_balance_amount

                    company_opening_filter.update(invamount = company_opening.invamount - extra)

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalbalance_amount = t.totalbalance_amount - extra)

                elif old_invoice_amount > amount['totalinvoiceamount']:

                    extra = amount['totalinvoiceamount'] - old_balance_amount

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalinvoiceamount = t.totalinvoiceamount - extra)

                elif old_payment_amount > amount['totalpaymentamount']:

                    extra = amount['totalpaymentamount'] - old_balance_amount

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalpaymentamount = t.totalpaymentamount + extra)

                data['status'] = True
                data['success'] = "Patch"
            else:
                data['status'] = False
                data['error'] = serializer.errors


        return Response(data)


class VendorOpeningGetPatch(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id):

        balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, year_opening = True, invoice_details_id = None, payment_details_id = None)

        serializer = Vendor_Balance_Serializer2(balance, many=True)

        return Response(serializer.data)

    def patch(self, request, id):

        data={}

        # ADD FRONT END VALIDATIONS FOR TOTAL BALANCE AMOUNT

        company_balances = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, year_opening = True, invoice_details_id = None, payment_details_id = None)
        print('1222')
        print(id)
        for x in company_balances:

            print('1')
            company_opening = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            company_opening_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

            old_balance_amount = company_opening.totalbalance_amount
            old_invoice_amount = company_opening.totalinvoiceamount
            old_payment_amount = company_opening.totalpaymentamount

            serializer = Vendor_Balance_Serializer(company_opening, data=request.data, partial = True)

            if serializer.is_valid():
                print('2')
                serializer.save()

                amount = request.data

                if old_balance_amount < amount['totalbalance_amount']:

                    extra = amount['totalbalance_amount'] - old_balance_amount

                    company_opening_filter.update(invamount = company_opening.invamount + extra)

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalbalance_amount = t.totalbalance_amount + extra)

                elif old_invoice_amount < amount['totalinvoiceamount']:

                    extra = amount['totalinvoiceamount'] + old_balance_amount

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalinvoiceamount = t.totalinvoiceamount + extra)

                elif old_payment_amount < amount['totalpaymentamount']:

                    extra = amount['totalpaymentamount'] + old_balance_amount

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalpaymentamount = t.totalpaymentamount + extra)

                elif old_balance_amount > amount['totalbalance_amount']:

                    extra = amount['totalbalance_amount'] - old_balance_amount

                    company_opening_filter.update(invamount = company_opening.invamount - extra)

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalbalance_amount = t.totalbalance_amount - extra)

                elif old_invoice_amount > amount['totalinvoiceamount']:

                    extra = amount['totalinvoiceamount'] - old_balance_amount

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalinvoiceamount = t.totalinvoiceamount - extra)

                elif old_payment_amount > amount['totalpaymentamount']:

                    extra = amount['totalpaymentamount'] - old_balance_amount

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

                    for t in balance_details_filter:

                        if t.payment_code > company_opening.payment_code:

                            balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = t.id)

                            balance_filter.update(totalpaymentamount = t.totalpaymentamount + extra)

                data['status'] = True
                data['Patch'] =  "success"
            else:
                print(serializer.data)
                data['status'] = False
                data['error'] =  serializer.errors


        return Response(data)


class purchase_statement_Openingqty(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self,request,id=None):

      
        datas={}
        data=request.data
        for k in data:
            # print(k['id'],'llllllllllllllll')
            ger=purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=k['id']).exists()
            start_dates=request.headers['sdate']
            end_dates=request.headers['ldate']
            if ger:
                stocks=purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,
                                                                         stdate=request.headers['sdate'],
                                                                         lstdate=request.headers['ldate']).filter(companycode=k['id']).last()
                lst_date=stocks.financial_period
                # print(lst_date)
                # wer=purchase_statement_opening(invno=stocks.invoice_details , companycode=stocks.companycode , payment_code=stocks.payment_code , invamount=stocks.invamount ,totalbalance_amount=stocks.totalbalance_amount , tenant_id=request.user.tenant_company.id, debitnote_amount=stocks.debitnote_amount , closed_date=lst_date ,closing_payment=stocks.payment , closing_invamount = stocks.invamount , closing_totalbalance_amount=stocks.totalbalance_amount , closing_debitnote_amount=stocks.debitnote_amount ,  opening_date= start_dates , payment=stocks.payment, ending_date=end_dates)
                # wer.save()
               
                gets=purchase_statement(companycode=stocks.companycode , payment_code=stocks.payment_code+1  , tenant_id=request.user.tenant_company.id , totalbalance_amount =stocks.totalbalance_amount ,  totalinvoiceamount=stocks.totalinvoiceamount , totalpaymentamount=stocks.totalpaymentamount)
                gets.save()
            else:
                    datas['error']='not matching fields'
            datas['message']="done"
        return Response(datas)


class paymentreports_sales(generics.ListAPIView,APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]
    serializer_class=balancedetailsserilaizers
    queryset=balancedetails.objects.all()
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['companycode']
    filterset_fields = ['companycode',]



class paymentreports_purchase(generics.ListAPIView,APIView):
    permission_classes=[~Isjwtvalid & IsAuthenticated]
    serializer_class=purchaseserilaizers
    queryset=purchase_statement.objects.all()
    
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['companycode']
    filterset_fields = ['companycode',]


class CompanySalesPendingBalance(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val']) 

            elif(t['key'] == 'financial_period'):

                q_objects |= Q(financial_period=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = balancedetails.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects)

        return response

    def post(self, request,*args,**kwargs):

        list = []

        sales_amount = []
        paid_amount = []
        pending_amount = []

        queryset = self.custom_filter(request)

        comapny_ids = []

        for x in queryset:

            if x.companycode_id in comapny_ids:

                pass

            else:
            
                comapny_ids.append(x.companycode_id)

                dict = {

                }
                
                company_balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = x.companycode_id).last()

                company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = x.companycode_id)

                serializer = companyserializer(company)


                dict['CompanyDetails'] = serializer.data
                dict['sales_amount'] = company_balance.totalinvoiceamount
                dict['paid_amount'] = company_balance.totalpaymentamount
                dict['pending_amount'] = company_balance.totalbalance_amount

                sales_amount.append(company_balance.totalinvoiceamount)
                paid_amount.append(company_balance.totalpaymentamount)
                pending_amount.append(company_balance.totalbalance_amount)


                list.append(dict)

        dict1 = {
            "total_sales_amount": sum(sales_amount),
            "total_received_amount": sum(paid_amount),
            "total_pending_amount": sum(pending_amount)
        }

        list.append(dict1)

        print(list)

        return Response(list)


class InvoicewiseSalesBalance(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'company_id_id'):

                q_objects |= Q(company_id_id=t['val']) 

            elif(t['key'] == 'invoice_details_id'):

                q_objects |= Q(id=t['val'])

            elif(t['key'] == 'bill_date'):

                q_objects |= Q(bill_date=t['val'])
            
            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = salesinvoicedetails.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects)

        return response

    def post(self, request,*args,**kwargs):

        list = []

        queryset = self.custom_filter(request)

        balance_details = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).all()

        total_grandtotal = []
        total_ref_payment = []

        for x in queryset:

            dict = {}

            bill = salesinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            serializer = salesserializer1(bill)

            sales_references = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(refinvno_id = x.id)

            total_grandtotal.append(bill.grand_total)

            for y in balance_details:

                if x.id == y.invoice_details_id:

                    dict['invoice_details'] = serializer.data
                    dict['invoice_amount'] = bill.grand_total

                    dict['paid_amount'] = y.ref_payment

                    total_ref_payment.append(y.ref_payment)

                    pending_amount = bill.grand_total - y.ref_payment

                    dict['pending_amount'] = pending_amount

                    today = date.today()

                    a = str(today)

                    b = a.split("-")

                    inward_date = str(x.financial_period)

                    c = inward_date.split("-")

                    d1 = date(int(b[0]), int(b[1]), int(b[2]))

                    d2 = date(int(c[0]), int(c[1]), int(c[2]))

                    delta = d1 - d2

                    dict['current_date'] = a
                    dict['inward_date'] = x.financial_period
                    dict['difference_days'] = delta.days

                    reference = []

                    for a in sales_references:

                        sales_reference = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = a.id)

                        serializer = salesinvrefreportserializer(sales_reference)

                        reference.append(serializer.data)

                    dict['reference_history'] = reference
                    
                    list.append(dict)

        a = sum(total_grandtotal)
        b = sum(total_ref_payment)

        c = a - b

        dict2 = {
            "total_invoice_amount": a,
            "total_paid_amount": b,
            "total_balance_amount": c
        }

        list.append(dict2)

        return Response(list)


class SalesPaymentBalanceDetails(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]


    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val']) 

            elif(t['key'] == 'invoice_details_id'):

                q_objects |= Q(invoice_details_id=t['val'])

            elif(t['key'] == 'financial_period'):

                q_objects |= Q(financial_period=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = balancedetails.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects).order_by('date')

        return response

    def post(self, request,*args,**kwargs):

        list = []

        tot_amount = []

        tot_balance = []

        tot_payment = []

        queryset = self.custom_filter(request)

        for x in queryset:

            details_check = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id , year_opening = False).exists()

            if details_check == True:

                details = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id , year_opening = False)

                tot_amount.append(details.totalinvoiceamount)

                tot_balance.append(details.totalbalance_amount)

                tot_payment.append(details.totalpaymentamount)

                serializer = balancedetailsreportserilaizers(details)

                list.append(serializer.data)

            else:

                tot_amount.append(0)

                tot_balance.append(0)

                tot_payment.append(0)

        a = {
            "total_invoiceamount":sum(tot_amount),
            "total_balanceamount":sum(tot_balance),
            "total_paymentamount":sum(tot_payment)
        }
        list.append(a)

        return Response(list)



class CompanyPurchasePendingBalance(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val']) 

            elif(t['key'] == 'financial_period'):

                q_objects |= Q(financial_period=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = purchase_statement.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects)

        return response


    def post(self, request,*args,**kwargs):

        list = []

        purchase_amount = []
        paid_amount = []
        pending_amount = []

        queryset = self.custom_filter(request)

        comapny_ids = []

        for x in queryset:

            if x.companycode_id in comapny_ids:

                pass

            else:
            
                comapny_ids.append(x.companycode_id)

                dict = {

                }
                
                company_balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = x.companycode_id).last()

                company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = x.companycode_id)

                serializer = companyserializer(company)


                dict['CompanyDetails'] = serializer.data
                dict['purchase_amount'] = company_balance.totalinvoiceamount
                dict['paid_amount'] = company_balance.totalpaymentamount
                dict['pending_amount'] = company_balance.totalbalance_amount

                purchase_amount.append(company_balance.totalinvoiceamount)
                paid_amount.append(company_balance.totalpaymentamount)
                pending_amount.append(company_balance.totalbalance_amount)


                list.append(dict)

        dict1 = {
            "total_sales_amount": sum(purchase_amount),
            "total_received_amount": sum(paid_amount),
            "total_pending_amount": sum(pending_amount)
        }

        list.append(dict1)

        return Response(list)


class InvoicewisePurchaseBalance(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val']) 

            elif(t['key'] == 'invoice_details_id'):

                q_objects |= Q(id=t['val'])

            elif(t['key'] == 'date'):

                q_objects |= Q(purdate=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(purdate__range=[t['val'], t['val2']])

        response = purchaseinvoicedetails.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects)

        return response


    def post(self, request,*args,**kwargs):

        list = []

        queryset = self.custom_filter(request)

        purchase_details = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).all()

        for x in queryset:

            dict = {}

            bill = purchaseinvoicedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            serializer = PurchaseSerializer(bill)

            purchase_references = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(refinvno_id = x.id)

            for y in purchase_details:

                if x.id == y.invoice_details_id:

                    dict['invoice_details'] = serializer.data
                    dict['invoice_amount'] = bill.subtotal

                    dict['paid_amount'] = round(float(y.ref_payment),2)

                    pending_amount = bill.subtotal - y.ref_payment

                    dict['pending_amount'] = pending_amount

                    
                    today = date.today()

                    a = str(today)

                    b = a.split("-")

                    inward_date = str(x.financial_period)

                    c = inward_date.split("-")

                    d1 = date(int(b[0]), int(b[1]), int(b[2]))

                    d2 = date(int(c[0]), int(c[1]), int(c[2]))

                    delta = d1 - d2

                    dict['current_date'] = a
                    dict['inward_date'] = x.financial_period
                    dict['difference_days'] = delta.days

                    reference = []

                    for a in purchase_references:

                        purchase_reference = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = a.id)

                        serializer = purcahseinvrefserializer2(purchase_reference)

                        reference.append(serializer.data)

                    dict['reference_history'] = reference
                    
                    list.append(dict)

        return Response(list)


class PurchasePaymentBalanceDetails(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val']) 

            elif(t['key'] == 'invoice_details_id'):

                q_objects |= Q(invoice_details_id=t['val'])

            elif(t['key'] == 'date'):

                q_objects |= Q(financial_period=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = purchase_statement.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects).order_by('date')

        return response


    def post(self, request,*args,**kwargs):

        list = []
        total_invoice = []
        total_balance = []
        total_payment = []

        queryset = self.custom_filter(request)

        for x in queryset:

            details_check = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id , year_opening = False).exists()

            if details_check == True:

                details = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id , year_opening = False)

                serializer = purchaseserilaizers2(details)

                total_invoice.append(details.totalinvoiceamount)

                total_balance.append(details.totalbalance_amount)

                total_payment.append(details.totalpaymentamount)

                list.append(serializer.data)

            else:

                total_invoice.append(0)

                total_balance.append(0)

                total_payment.append(0)

        a = {
            "total_invoiceamount":round(float(sum(total_invoice)),2),
            "total_balanceamount":round(float(sum(total_balance)),2),
            "total_paymentamount":round(float(sum(total_payment)),2)
        }
        list.append(a)

        return Response(list)


class SalesPaymentUpdate(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id):

        queryset = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        serializer = salespaymentdetserializer(queryset)

        return Response(serializer.data)

    def patch(self, request, id):

        sales_payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        tenant_id = request.user.tenant_company.id

        old_payment = sales_payment.payment_amount

        balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = id)

        balance_details_filter.update(date = request.data['payment_date'])

        serializer = SalesPaymentdetailsSerializer(sales_payment, data=request.data, partial = True)

        if serializer.is_valid():

            serializer.save()

            sales_payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

            new_payment = sales_payment.payment_amount

            if old_payment == new_payment:

                pass

            elif old_payment > new_payment:

                reduced_payment = old_payment - new_payment

                ref_check = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

                if ref_check == True:

                    ref_filter = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id)

                    ref_amount_list = []

                    for b in ref_filter:

                        ref_amount_list.append(b.refinvamount)

                    ref_amount = sum(ref_amount_list)

                    if new_payment >= ref_amount:

                        balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                        balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                        balance_filter.update(payment = new_payment)

                        balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                        for y in balance_update_filter:

                            if y.payment_code >= balance_get.payment_code:

                                balance_payment_update = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                                balance_payment_update.update(totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

                        sale_payment_update = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                        if new_payment == ref_amount:

                            sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = False)

                        else:

                            sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = True)

                    elif new_payment < ref_amount:

                        return Response({'status': False, 'error': 'Entered amount is lesser than the referenced amount of this payment. First delete the required reference to reduce this payment amount'})

                else:

                    balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                    balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                    balance_filter.update(payment = new_payment)

                    balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                    for y in balance_update_filter:

                        if y.payment_code >= balance_get.payment_code:

                            balance_payment_update = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                            balance_payment_update.update(totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

                    sale_payment_update = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                    sale_payment_update.update(billrefered = False, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = False)

            elif old_payment < new_payment:

                increased_payment = new_payment - old_payment

                balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                balance_filter.update(payment = new_payment)

                balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                for y in balance_update_filter:

                    if y.payment_code >= balance_get.payment_code:

                        balance_payment_update = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                        balance_payment_update.update(totalpaymentamount = y.totalpaymentamount + increased_payment,totalbalance_amount = y.totalbalance_amount - increased_payment)

                sale_payment_update = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                if old_payment == sales_payment.unreferenced_payment:

                    sale_payment_update.update(billrefered = False, unreferenced_payment = sales_payment.unreferenced_payment + increased_payment, semirefrenced = False)

                else:

                    sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment + increased_payment, semirefrenced = True)

            return Response({'status': True, 'error' : "Data Saved"})

        else:

            return Response({'status': False, 'error' : serializer.errors})

    def delete(self, request, id):

        sales_payment = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        ref_check = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

        if ref_check == True:

            print('11')

            return Response({'status': False, 'error': "Delete the required references to delete this payment amount"})

        else:

            print('22')
            reduced_payment = sales_payment.payment_amount

            balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

            balance_update_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

            balance_get.delete()

            sales_payment.delete()

            return Response("Deleted")


class PurchasePaymentUpdate(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id):

        queryset = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        serializer = purchasepaymentserializer(queryset)

        return Response(serializer.data)

    def patch(self, request, id):

        sales_payment = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        tenant_id = request.user.tenant_company.id

        old_payment = sales_payment.payment_amount

        balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = id)

        balance_details_filter.update(date = request.data['payment_date'])

        serializer = PurchasePaymentdetailsSerializer(sales_payment, data=request.data, partial = True)

        if serializer.is_valid():

            serializer.save()

            sales_payment = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

            new_payment = sales_payment.payment_amount

            if old_payment == new_payment:

                pass

            elif old_payment > new_payment:

                reduced_payment = old_payment - new_payment

                ref_check = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

                if ref_check == True:

                    ref_filter = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id)

                    ref_amount_list = []

                    for b in ref_filter:

                        ref_amount_list.append(b.refinvamount)

                    ref_amount = sum(ref_amount_list)

                    if new_payment >= ref_amount:

                        balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                        balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                        balance_filter.update(payment = new_payment)

                        balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                        for y in balance_update_filter:

                            if y.payment_code >= balance_get.payment_code:

                                balance_payment_update = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                                balance_payment_update.update(totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

                        sale_payment_update = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                        if new_payment == ref_amount:

                            sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = False)

                        else:

                            sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = True)

                    elif new_payment < ref_amount:

                        return Response({'status': False, 'error': 'Entered amount is lesser than the referenced amount of this payment. First delete the required reference to reduce this payment amount'})

                else:

                    balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                    balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                    balance_filter.update(payment = new_payment)

                    balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                    for y in balance_update_filter:

                        if y.payment_code >= balance_get.payment_code:

                            balance_payment_update = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                            balance_payment_update.update(totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

                    sale_payment_update = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                    sale_payment_update.update(billrefered = False, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = False)

            elif old_payment < new_payment:

                increased_payment = new_payment - old_payment

                balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                balance_filter.update(payment = new_payment)

                balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                for y in balance_update_filter:

                    if y.payment_code >= balance_get.payment_code:

                        balance_payment_update = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                        balance_payment_update.update(totalpaymentamount = y.totalpaymentamount + increased_payment,totalbalance_amount = y.totalbalance_amount - increased_payment)

                sale_payment_update = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                if old_payment == sales_payment.unreferenced_payment:

                    sale_payment_update.update(billrefered = False, unreferenced_payment = sales_payment.unreferenced_payment + increased_payment, semirefrenced = False)

                else:

                    sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment + increased_payment, semirefrenced = True)

            return Response({'status': True, 'error' : "Data Saved"})

        else:

            return Response({'status': False, 'error' : serializer.errors})

    def delete(self, request, id):

        sales_payment = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        ref_check = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

        if ref_check == True:

            return Response({'status': False, 'error': "Delete the required references to delete this payment amount"})

        else:

            reduced_payment = sales_payment.payment_amount

            balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

            balance_update_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

            balance_get.delete()

            sales_payment.delete()

            return Response("Deleted")


class VendorPaymentDetails(APIView):

    def get(self, request, id = None):

        if id:

            queryset = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

            serializer = Vendor_Payments_Serializer2(queryset)

            return Response(serializer.data)

        else:

            queryset = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer = Vendor_Payments_Serializer2(queryset, many=True)

            return Response(serializer.data)

    def post(self, request):

        if request.method == "POST":

            inputdata = request.data
            tenant_id=request.user.tenant_company.id

            for i in inputdata:

                payment_amount = float(i['payment_amount'])
                sales_type = i['sales_type']
                company_id = i['companycode']
                payment_date = i['payment_date']
                companycode = CompanyDetails.objects.current_tenant(id = request.user.tenant_company.id).get(id = company_id)

                saleinvref_sets = i['saleinvref_set']

                if sales_type == 1:

                    debit_type = i['debit_type']
                    debit_refno = i['debit_refno']
                    debit_refdate = i['debit_refdate']

                    if len(saleinvref_sets) != 0:

                        value = []

                        for x in saleinvref_sets:

                            value.append(x['refinvamount'])

                        if sum(value) == payment_amount:

                            datas = Vendor_Paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, sales_type = sales_type, billrefered = True, unreferenced_payment = 0, semirefrenced = False,payment_date = payment_date)

                        else:

                            datas = Vendor_Paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, sales_type = sales_type, billrefered = True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value),payment_date = payment_date)

                    else:

                        datas = Vendor_Paymentdetails(debit_refno = debit_refno, payment_amount = payment_amount, debit_refdate = debit_refdate, tenant_id = tenant_id, debit_type = debit_type, companycode = companycode, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False,payment_date = payment_date)

                elif sales_type == 2:

                    payment_refdate = i['payment_refdate']
                    payment_refno = i['payment_refno']

                    cash = i['cash']
                    cheque= i["cheque"]
                    bank = i["bank"]

                    if len(saleinvref_sets) != 0:

                        value = []

                        for x in saleinvref_sets:

                            value.append(x['refinvamount'])

                        a = sum(value)

                        if a == payment_amount:

                            if cash == True:

                                datas = Vendor_Paymentdetails(cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)

                            elif cheque == True:

                                close = i['close']

                                if close == True:

                                        datas = Vendor_Paymentdetails(cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)

                                else:

                                    datas = Vendor_Paymentdetails(cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False, payment_date = payment_date)

                            elif bank == True:

                                datas = Vendor_Paymentdetails(bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, sales_type = sales_type, billrefered=True, unreferenced_payment = 0, semirefrenced = False,payment_date = payment_date)

                        else:

                            if cash == True:

                                datas = Vendor_Paymentdetails(cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)

                            elif cheque == True:

                                close = i['close']

                                if close == True:

                                        datas = Vendor_Paymentdetails(cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)

                                else:

                                    datas = Vendor_Paymentdetails(cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)

                            elif bank == True:

                                datas = Vendor_Paymentdetails(bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, sales_type = sales_type, billrefered=True, semirefrenced = True, unreferenced_payment = payment_amount - sum(value), payment_date = payment_date)

                    elif len(saleinvref_sets) == 0:

                        if cash == True:

                            datas = Vendor_Paymentdetails(cash = True, payment_refdate = payment_refdate, tenant_id = tenant_id, payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)

                        elif cheque == True:

                            close = i['close']

                            if close == True:

                                    datas = Vendor_Paymentdetails(cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode, payment_refdate = payment_refdate, close = close, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)

                            else:

                                datas = Vendor_Paymentdetails(cheque = True, tenant_id = tenant_id,payment_amount = payment_amount, payment_refno = payment_refno, companycode = companycode,payment_refdate = payment_refdate, close = close, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)

                        elif bank == True:

                            datas = Vendor_Paymentdetails(bank=True, tenant_id=tenant_id,payment_amount=payment_amount, payment_refno=payment_refno,companycode=companycode,payment_refdate=payment_refdate, sales_type = sales_type, unreferenced_payment = payment_amount, billrefered = False, semirefrenced = False, payment_date = payment_date)

                datas.save()

                xt = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode=companycode).exists()

                if xt == True:
                    m = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode=companycode).last()

                    if m.totalbalance_amount == 0:

                        data = Vendor_Balancedetails(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount,totalpaymentamount=m.totalpaymentamount + payment_amount,totalbalance_amount=(0-payment_amount),totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data.save()

                    elif m.totalbalance_amount < 0:
                        z = 0
                        z = float(float(payment_amount) + float(m.totalpaymentamount))
                        zy = float(float(m.totalbalance_amount) - float(payment_amount))

                        data1 = Vendor_Balancedetails(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount, totalpaymentamount=z, totalbalance_amount=zy,totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data1.save()

                    elif m.totalbalance_amount > 0:

                        z = 0
                        z = float(float(payment_amount) + float(m.totalpaymentamount))
                        zy = float(float(m.totalbalance_amount) - float(payment_amount))

                        data1 = Vendor_Balancedetails(payment_code=m.payment_code+1,payment_details=datas,companycode=companycode,invamount=0,payment=payment_amount, totalpaymentamount=z, totalbalance_amount=zy,totalinvoiceamount=m.totalinvoiceamount,tenant_id=tenant_id, date = payment_date)

                        data1.save()

                else:

                    data = Vendor_Balancedetails(payment_code=1,payment_details=datas, companycode=companycode, invamount=0,payment=payment_amount, totalpaymentamount=payment_amount,totalbalance_amount=(0 - payment_amount), totalinvoiceamount=0,tenant_id=tenant_id, date = payment_date)

                    data.save()

                serializer = Vendor_Payments_Serializer(request.data)
                balanceamount=payment_amount
                datares={}

                if len(saleinvref_sets) !=0:

                    if serializer.is_valid:

                        for j in saleinvref_sets:

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']
                                balanceamount = balanceamount - refinvamount

                                data = Vendor_Saleinvref(refernce=datas, tenant_id=tenant_id,refinvno_id=refinvno, refinvamount=refinvamount)

                                data.save()

                                mt = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id=refinvno)

                                x = mt.invamount
                                xy = mt.ref_payment

                                if x == 0:

                                    datares["message"]="Payment already exists for this "
                                else:

                                    z = x - refinvamount
                                    ref_payment = xy + refinvamount

                                    Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id=refinvno).update(invamount=z,ref_payment=ref_payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']
                                balanceamount = balanceamount - refinvamount

                                data = Vendor_Saleinvref(refernce = datas, tenant_id = tenant_id, refinvno_id = refinvno, refinvamount = refinvamount)

                                data.save()

                                mt = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode = companycode).first()

                                x = mt.invamount
                                xy = mt.ref_payment

                                if x == 0:

                                    datares["message"]="Payment already exists for this"

                                else:

                                    z = x - refinvamount
                                    ref_payment = xy + refinvamount

                                    balance_update_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode = companycode, invoice_details_id = None, payment_details_id = None)

                                    balance_update_filter.update(invamount=z,ref_payment=ref_payment)

                        datares['status'] = True
                        datares['message'] = 'Vendor Payment SuccessFully Paid.'


                    else:

                        datares['status'] = False
                        datares['message'] = 'Vendor Payment Reference Error.'
                        datares['error'] = serializer.errors


        return Response(datares)

    def patch(self, request, id):

        sales_payment = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        tenant_id = request.user.tenant_company.id

        old_payment = sales_payment.payment_amount

        serializer = Vendor_Payments_Serializer(sales_payment, data=request.data, partial = True)

        if serializer.is_valid():

            serializer.save()

            sales_payment = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

            new_payment = sales_payment.payment_amount

            if old_payment == new_payment:

                pass

            elif old_payment > new_payment:

                reduced_payment = old_payment - new_payment

                ref_check = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

                if ref_check == True:

                    ref_filter = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id)

                    ref_amount_list = []

                    for b in ref_filter:

                        ref_amount_list.append(b.refinvamount)

                    ref_amount = sum(ref_amount_list)

                    if new_payment >= ref_amount:

                        balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                        balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                        balance_filter.update(payment = new_payment)

                        balance_update_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                        for y in balance_update_filter:

                            if y.payment_code >= balance_get.payment_code:

                                balance_payment_update = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                                balance_payment_update.update(totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

                        sale_payment_update = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                        if new_payment == ref_amount:

                            sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = False)

                        else:

                            sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = True)

                    elif new_payment < ref_amount:

                        return Response({'status': False, 'error': 'Entered amount is lesser than the referenced amount of this payment. First delete the required reference to reduce this payment amount'})

                else:

                    balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                    balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                    balance_filter.update(payment = new_payment)

                    balance_update_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                    for y in balance_update_filter:

                        if y.payment_code >= balance_get.payment_code:

                            balance_payment_update = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                            balance_payment_update.update(totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

                    sale_payment_update = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                    sale_payment_update.update(billrefered = False, unreferenced_payment = sales_payment.unreferenced_payment - reduced_payment, semirefrenced = False)

            elif old_payment < new_payment:

                increased_payment = new_payment - old_payment

                balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(payment_details_id = sales_payment.id)

                balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

                balance_filter.update(payment = new_payment)

                balance_update_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

                for y in balance_update_filter:

                    if y.payment_code >= balance_get.payment_code:

                        balance_payment_update = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                        balance_payment_update.update(totalpaymentamount = y.totalpaymentamount + increased_payment,totalbalance_amount = y.totalbalance_amount - increased_payment)

                sale_payment_update = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id)

                if old_payment == sales_payment.unreferenced_payment:

                    sale_payment_update.update(billrefered = False, unreferenced_payment = sales_payment.unreferenced_payment + increased_payment, semirefrenced = False)

                else:

                    sale_payment_update.update(billrefered = True, unreferenced_payment = sales_payment.unreferenced_payment + increased_payment, semirefrenced = True)

            return Response({'status': True, 'message' : "Vendor Payment Updated Successfully"})

        else:

            return Response({'status': False, 'message' : "Vendor Payment Data Some Error." ,'error' : serializer.errors})

    def delete(self, request, id):

        sales_payment = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

        ref_check = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

        if ref_check == True:

            return Response({'status': False, 'message': "Delete the required references to delete this payment amount"})

        else:

            reduced_payment = sales_payment.payment_amount

            balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(payment_details_id = sales_payment.id)

            balance_update_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = sales_payment.companycode_id)

            for y in balance_update_filter:

                if y.payment_code > balance_get.payment_code:

                    balance_payment_update = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = y.id)

                    balance_payment_update.update(payment_code = y.payment_code - 1, totalpaymentamount = y.totalpaymentamount - reduced_payment, totalbalance_amount = y.totalbalance_amount + reduced_payment)

            balance_get.delete()

            sales_payment.delete()

            return Response({'status': True, 'message': "Vendor Payments Deleted Successfully."})


class VendorCompanyPendingBalance(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val'])

            elif(t['key'] == 'financial_period'):

                q_objects |= Q(financial_period=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = balancedetails.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects)

        return response

    def post(self, request,*args,**kwargs):

        list = []

        sales_amount = []
        paid_amount = []
        pending_amount = []

        queryset = self.custom_filter(request)

        comapny_ids = []

        for x in queryset:

            if x.companycode_id in comapny_ids:

                pass

            else:

                comapny_ids.append(x.companycode_id)

                dict = {

                }

                company_balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = x.companycode_id).last()

                company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = x.companycode_id)

                serializer = companyserializer(company)


                dict['CompanyDetails'] = serializer.data
                dict['sales_amount'] = company_balance.totalinvoiceamount
                dict['paid_amount'] = company_balance.totalpaymentamount
                dict['pending_amount'] = company_balance.totalbalance_amount

                sales_amount.append(company_balance.totalinvoiceamount)
                paid_amount.append(company_balance.totalpaymentamount)
                pending_amount.append(company_balance.totalbalance_amount)


                list.append(dict)

        dict1 = {
            "total_sales_amount": sum(sales_amount),
            "total_received_amount": sum(paid_amount),
            "total_pending_amount": sum(pending_amount)
        }

        list.append(dict1)

        return Response(list)


class InvoicewiseVendorBalance(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'company_id_id'):

                q_objects |= Q(company_id_id=t['val'])

            elif(t['key'] == 'invoice_details_id'):

                q_objects |= Q(id=t['val'])

            elif(t['key'] == 'bill_date'):

                q_objects |= Q(bill_date=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = Joborder_Bill.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects)

        return response

    def post(self, request,*args,**kwargs):

        list = []

        queryset = self.custom_filter(request)

        balance_details = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).all()

        total_grandtotal = []
        total_ref_payment = []

        for x in queryset:

            dict = {}

            bill = Joborder_Bill.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            serializer = Joborder_Serializer2(bill)

            sales_references = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).filter(refinvno_id = x.id)

            total_grandtotal.append(bill.grand_total)

            for y in balance_details:

                if x.id == y.invoice_details_id:

                    dict['invoice_details'] = serializer.data
                    dict['invoice_amount'] = bill.grand_total

                    dict['paid_amount'] = y.ref_payment

                    total_ref_payment.append(y.ref_payment)

                    pending_amount = bill.grand_total - y.ref_payment

                    dict['pending_amount'] = pending_amount

                    today = date.today()

                    a = str(today)

                    b = a.split("-")

                    inward_date = str(x.financial_period)

                    c = inward_date.split("-")

                    d1 = date(int(b[0]), int(b[1]), int(b[2]))

                    d2 = date(int(c[0]), int(c[1]), int(c[2]))

                    delta = d1 - d2

                    dict['current_date'] = a
                    dict['inward_date'] = x.financial_period
                    dict['difference_days'] = delta.days

                    reference = []

                    for a in sales_references:

                        sales_reference = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = a.id)

                        serializer = Vendor_Reference_Serializer2(sales_reference)

                        reference.append(serializer.data)

                    dict['reference_history'] = reference

                    list.append(dict)

        a = sum(total_grandtotal)
        b = sum(total_ref_payment)

        c = a - b

        dict2 = {
            "total_invoice_amount": a,
            "total_paid_amount": b,
            "total_balance_amount": c
        }

        list.append(dict2)

        return Response(list)


class VendorPaymentBalanceDetails(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]


    def custom_filter(self,requestval):

        q_objects = Q()

        for t in requestval.data:

            if(t['key'] == 'companycode_id'):

                q_objects |= Q(companycode_id=t['val'])

            elif(t['key'] == 'invoice_details_id'):

                q_objects |= Q(invoice_details_id=t['val'])

            elif(t['key'] == 'financial_period'):

                q_objects |= Q(financial_period=t['val'])

            elif(t['key'] == 'start_date') and (t['key2'] == 'end_date'):

                q_objects = Q(financial_period__range=[t['val'], t['val2']])

        response = Vendor_Balancedetails.objects.current_financialyear(id=requestval.user.tenant_company.id,stdate = requestval.headers['sdate'],lstdate=requestval.headers['ldate']).filter(q_objects).order_by('date')

        return response

    def post(self, request,*args,**kwargs):

        list = []
        dict = {}
        debit = []
        payment = []

        queryset = self.custom_filter(request)

        for x in queryset:

            details = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate = request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

            serializer = Vendor_Balance_Serializer2(details)

            # if details.payment_details != None:

                # if details.payment_details.sales_type == 1:

                #     debit.append(details.payment_details.payment_amount)

                # elif details.payment_details.sales_type == 2:

                #     payment.append(details.payment_details.payment_amount)

            list.append(serializer.data)

        # total_debit = sum(debit)
        # total_payment = sum(payment)

        # dict['total_debit'] = total_debit
        # dict['total_payment'] = total_payment
        # list.append(dict)

        return Response(list)


class VendorCompanyPaymentGet(APIView):

    permission_classes=[~Isjwtvalid & IsAuthenticated]

    def get(self, request, id = None):

        if id:

            company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).get(id = id)

            serializer = CompanyToVendor(company)

            return Response(serializer.data)

        else:

            company = CompanyDetails.objects.current_tenant(id=request.user.tenant_company.id).filter(cancel=False)

            serializer = CompanyToVendor(company, many = True)

            return Response(serializer.data)


class VendorPaymentGetByID(APIView):

    def get(self, request, id=None):

        if id:

            payment = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id=id)

            serializer = Vendor_Payments_Serializer2(payment)

            a = serializer.data

            for x in a['vendor_invrefs']:

                if x['refinvno'] != None:

                    balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = x['refinvno']['id'])

                    balance_serializer = Vendor_Balance_Serializer(balance_get)

                    x['refinvno']['balance_details'] = balance_serializer.data

                elif x['refinvno'] == None:

                    balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = a['companycode']['id']).first()

                    balance_serializer = Vendor_Balance_Serializer(balance_get)

                    x['company_opening_balance'] = balance_serializer.data

            return Response(a)

        else:

            payment = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer = Vendor_Payments_Serializer2(payment, many = True)

            return Response(serializer.data)


class SalesRefUpdate(APIView):

    def get(self, request, id):

        if id:

            sales_ref = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id)

            serializer = salesinvrefreportserializer(sales_ref, many = True)

            return Response(serializer.data)

        else:

            sales_ref = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer = salesinvrefreportserializer(sales_ref, many=True)

            return Response(serializer.data)

    def patch(self, request, id = None):

        print(request.data)

        ref_data = request.data

        for x in ref_data:

            if x['new'] == True:

                saleinvref_sets = x['salesinvref_set']

                payments_check = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).exists()

                if payments_check == True:

                    datas = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                    reference_check = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

                    refinvamount_list = []

                    if reference_check == False:

                        print("Here QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")

                        for j in saleinvref_sets:

                            tenant_id = request.user.tenant_company.id

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_data = saleinvref(refernce = datas, refinvno_id = refinvno, refinvamount = refinvamount,tenant_id = tenant_id)

                                reference_data.save()

                                payment_balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = refinvno)

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invoice_details_id= refinvno).update(invamount = invoice_amount, ref_payment = payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_data = saleinvref(refernce = datas, refinvno_id = None, refinvamount = refinvamount,tenant_id = tenant_id)

                                reference_data.save()

                                payment_balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = datas.companycode_id, invoice_details_id = None, payment_details_id = None)

                                for n in payment_balance_filter:

                                    payment_balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = n.id)

                                    invoice_amount = payment_balance.invamount - refinvamount
                                    payment = payment_balance.ref_payment + refinvamount

                                    balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id = n.id).update(invamount = invoice_amount, ref_payment = payment)

                        if datas.unreferenced_payment == sum(refinvamount_list):

                            sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True,semirefrenced = False, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list))

                        else:

                            sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list), semirefrenced = True)

                    else:

                        print("There WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")

                        for j in saleinvref_sets:

                            tenant_id=request.user.tenant_company.id

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_filter_check = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = refinvno).exists()

                                if reference_filter_check == True:

                                    print("invoice reference exists")

                                    reference_filter = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = refinvno)

                                    for x in reference_filter:

                                        data_filter = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                                        data_get = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

                                        data_filter.update(refinvamount = data_get.refinvamount + refinvamount)

                                else:

                                    print("reference filter not found")

                                    reference_data = saleinvref(refernce = datas, refinvno_id = refinvno, refinvamount = refinvamount,tenant_id = tenant_id)

                                    reference_data.save()

                                payment_balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = refinvno)

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invoice_details_id= refinvno).update(invamount = invoice_amount, ref_payment = payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_filter_check = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = None).exists()

                                if reference_filter_check == True:

                                    print("invoice reference exists")

                                    reference_filter = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = None)

                                    for x in reference_filter:

                                        data_filter = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                                        data_get = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

                                        data_filter.update(refinvamount = data_get.refinvamount + refinvamount)

                                else:

                                    print("reference filter not found")

                                    reference_data = saleinvref(refernce = datas, refinvno_id = None, refinvamount = refinvamount,tenant_id = tenant_id)

                                    reference_data.save()

                                payment_balance = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = datas.companycode_id).first()

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id= payment_balance.id).update(invamount = invoice_amount, ref_payment = payment)

                            if datas.unreferenced_payment == sum(refinvamount_list):

                                print("Here")

                                sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, semirefrenced = False, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list))

                            else:

                                print("there")

                                sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list), semirefrenced = True)

                else:

                    return Response("Matching Payment Details Does Not Exists")

            elif x['patch'] == True:

                print("IN PATCH")

                datas = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                ref_get = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                old_amount = ref_get.refinvamount

                serializer = salesinvrefserializer2(ref_get, data = x, partial = True)

                if serializer.is_valid():

                    serializer.save()

                    ref_get = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                    new_amount = ref_get.refinvamount

                    if new_amount > old_amount:

                        extra_amount = new_amount - old_amount

                        if ref_get.refinvno_id != None:

                            balance_details_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                            balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                        elif ref_get.refinvno_id == None:

                            balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                            for g in balance_details_filter:

                                balance_details_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                        balance_details_filter.update(invamount = balance_details_get.invamount - extra_amount, ref_payment = balance_details_get.ref_payment + extra_amount)

                        payments_get = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        payments_filter = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                        payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment - extra_amount)

                        payments_get2 = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        if payments_get2.unreferenced_payment == 0:

                            payments_filter.update(semirefrenced = False)

                        else:

                            payments_filter.update(semirefrenced = True)

                    elif new_amount < old_amount:

                        extra_amount = old_amount - new_amount

                        if ref_get.refinvno_id != None:

                            balance_details_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                            balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                        elif ref_get.refinvno_id == None:

                            balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                            for g in balance_details_filter:

                                balance_details_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                        balance_details_filter.update(invamount = balance_details_get.invamount + extra_amount, ref_payment = balance_details_get.ref_payment - extra_amount)

                        payments_get = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        payments_filter = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                        payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment + extra_amount)

                        payments_get2 = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        if payments_get2.unreferenced_payment == payments_get2.payment_amount:

                            payments_filter.update(semirefrenced = False, billrefered = False)

                        else:

                            payments_filter.update(billrefered = True, semirefrenced = True)

                else:

                    return Response({'status': False, 'error': serializer.errors})

            elif x['delete'] == True:

                datas = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                ref_get = saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                if ref_get.refinvno_id != None:

                    balance_details_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                elif ref_get.refinvno_id == None:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                    for g in balance_details_filter:

                        balance_details_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                balance_details_filter.update(invamount = balance_details_get.invamount + ref_get.refinvamount, ref_payment = balance_details_get.ref_payment - ref_get.refinvamount)

                payments_get = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                payments_filter = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment + ref_get.refinvamount)

                payments_get2 = sales_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                if payments_get2.unreferenced_payment == payments_get2.payment_amount:

                    payments_filter.update(semirefrenced = False, billrefered = False)

                else:

                    payments_filter.update(billrefered = True, semirefrenced = True)

                ref_get.delete()

        return Response({'status': True, 'patch': 'Data Updated successfully'})


class PurchaseRefUpdate(APIView):

    def get(self, request, id):

        if id:

            sales_ref = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id)

            serializer = purcahseinvrefserializer2(sales_ref, many = True)

            return Response(serializer.data)

        else:

            sales_ref = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer = purcahseinvrefserializer2(sales_ref, many=True)

            return Response(serializer.data)

    def patch(self, request, id = None):

        ref_data = request.data

        for x in ref_data:

            if x['new'] == True:

                saleinvref_sets = x['salesinvref_set']

                payments_check = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).exists()

                if payments_check == True:

                    datas = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                    reference_check = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

                    refinvamount_list = []

                    if reference_check == False:

                        for j in saleinvref_sets:

                            tenant_id = request.user.tenant_company.id

                            if j['refinvno'] != None and j['year_opening'] == False:

                                print('Here')

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_data = purchaseinvref(refernce = datas, refinvno_id = refinvno, refinvamount = refinvamount,tenant_id = tenant_id)

                                reference_data.save()

                                payment_balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = refinvno)

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                purchase_statement.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invoice_details_id= refinvno).update(invamount = invoice_amount, ref_payment = payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_data = purchaseinvref(refernce = datas, refinvno_id = None, refinvamount = refinvamount,tenant_id = tenant_id)

                                reference_data.save()

                                payment_balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = datas.companycode_id, invoice_details_id = None, payment_details_id = None)

                                for n in payment_balance_filter:

                                    payment_balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = n.id)

                                    invoice_amount = payment_balance.invamount - refinvamount
                                    payment = payment_balance.ref_payment + refinvamount

                                    purchase_statement.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id = n.id).update(invamount = invoice_amount, ref_payment = payment)

                        if datas.unreferenced_payment == sum(refinvamount_list):

                            purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True,semirefrenced = False, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list))

                        else:

                            purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list), semirefrenced = True)

                    else:

                        for j in saleinvref_sets:

                            tenant_id=request.user.tenant_company.id

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_filter_check = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = refinvno).exists()

                                if reference_filter_check == True:

                                    print("invoice reference exists")

                                    reference_filter = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = refinvno)

                                    for x in reference_filter:

                                        data_filter = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                                        data_get = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

                                        data_filter.update(refinvamount = data_get.refinvamount + refinvamount)

                                else:

                                    print("reference filter not found")

                                    reference_data = purchaseinvref(refernce = datas, refinvno_id = refinvno, refinvamount = refinvamount,tenant_id = tenant_id)

                                    reference_data.save()

                                payment_balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = refinvno)

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                purchase_statement.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invoice_details_id= refinvno).update(invamount = invoice_amount, ref_payment = payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_filter_check = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = None).exists()

                                if reference_filter_check == True:

                                    print("invoice reference exists")

                                    reference_filter = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = None)

                                    for x in reference_filter:

                                        data_filter = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                                        data_get = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

                                        data_filter.update(refinvamount = data_get.refinvamount + refinvamount)

                                else:

                                    print("reference filter not found")

                                    reference_data = purchaseinvref(refernce = datas, refinvno_id = None, refinvamount = refinvamount,tenant_id = tenant_id)

                                    reference_data.save()

                                payment_balance = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = datas.companycode_id).first()

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                purchase_statement.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id= payment_balance.id).update(invamount = invoice_amount, ref_payment = payment)


                            if datas.unreferenced_payment == sum(refinvamount_list):

                                print("Here")

                                purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, semirefrenced = False, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list))

                            else:

                                print("there")

                                purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list), semirefrenced = True)

                else:

                    return Response("Matching Payment Details Does Not Exists")

            elif x['patch'] == True:

                datas = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                ref_get = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                old_amount = ref_get.refinvamount

                serializer = salesinvrefserializer2(ref_get, data = x, partial = True)

                if serializer.is_valid():

                    serializer.save()

                    ref_get = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                    new_amount = ref_get.refinvamount

                    if new_amount > old_amount:

                        extra_amount = new_amount - old_amount

                        if ref_get.refinvno_id != None:

                            balance_details_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                            balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                        elif ref_get.refinvno_id == None:

                            balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                            for g in balance_details_filter:

                                balance_details_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                        balance_details_filter.update(invamount = balance_details_get.invamount - extra_amount, ref_payment = balance_details_get.ref_payment + extra_amount)

                        payments_get = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        payments_filter = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                        payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment - extra_amount)

                        payments_get2 = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        if payments_get2.unreferenced_payment == 0:

                            payments_filter.update(semirefrenced = False)

                        else:

                            payments_filter.update(semirefrenced = True)

                    elif new_amount < old_amount:

                        extra_amount = old_amount - new_amount

                        if ref_get.refinvno_id != None:

                            balance_details_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                            balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                        elif ref_get.refinvno_id == None:

                            balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                            for g in balance_details_filter:

                                balance_details_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                        balance_details_filter.update(invamount = balance_details_get.invamount + extra_amount, ref_payment = balance_details_get.ref_payment - extra_amount)

                        payments_get = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        payments_filter = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                        payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment + extra_amount)

                        payments_get2 = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        if payments_get2.unreferenced_payment == payments_get2.payment_amount:

                            payments_filter.update(semirefrenced = False, billrefered = False)

                        else:

                            payments_filter.update(billrefered = True, semirefrenced = True)

                else:

                    return Response({'status': False, 'error': serializer.errors})

            elif x['delete'] == True:

                datas = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                ref_get = purchaseinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                if ref_get.refinvno_id != None:

                    balance_details_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                elif ref_get.refinvno_id == None:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                    for g in balance_details_filter:

                        balance_details_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                balance_details_filter.update(invamount = balance_details_get.invamount + ref_get.refinvamount, ref_payment = balance_details_get.ref_payment - ref_get.refinvamount)

                payments_get = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                payments_filter = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment + ref_get.refinvamount)

                payments_get2 = purchase_paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                if payments_get2.unreferenced_payment == payments_get2.payment_amount:

                    payments_filter.update(semirefrenced = False, billrefered = False)

                else:

                    payments_filter.update(billrefered = True, semirefrenced = True)

                ref_get.delete()

        return Response({'status': True, 'patch': 'Data Updated successfully'})


class VendorRefUpdate(APIView):

    def get(self, request, id):

        if id:

            sales_ref = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id)

            serializer = Vendor_Reference_Serializer2(sales_ref, many = True)

            return Response(serializer.data)

        else:

            sales_ref = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).all()

            serializer = Vendor_Reference_Serializer2(sales_ref, many=True)

            return Response(serializer.data)

    def patch(self, request, id = None):

        print('KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')

        ref_data = request.data

        print(ref_data, 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')

        for x in ref_data:

            if x['new'] == True:

                saleinvref_sets = x['salesinvref_set']

                payments_check = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).exists()

                if payments_check == True:

                    datas = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                    reference_check = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id).exists()

                    refinvamount_list = []

                    if reference_check == False:

                        for j in saleinvref_sets:

                            tenant_id = request.user.tenant_company.id

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_data = Vendor_Saleinvref(refernce = datas, refinvno_id = refinvno, refinvamount = refinvamount,tenant_id = tenant_id)

                                reference_data.save()

                                payment_balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = refinvno)

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                Vendor_Balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invoice_details_id= refinvno).update(invamount = invoice_amount, ref_payment = payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_data = Vendor_Saleinvref(refernce = datas, refinvno_id = None, refinvamount = refinvamount,tenant_id = tenant_id)

                                reference_data.save()

                                payment_balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = datas.companycode_id, invoice_details_id = None, payment_details_id = None)

                                for n in payment_balance_filter:

                                    payment_balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = n.id)

                                    invoice_amount = payment_balance.invamount - refinvamount
                                    payment = payment_balance.ref_payment + refinvamount

                                    Vendor_Balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id = n.id).update(invamount = invoice_amount, ref_payment = payment)

                        if datas.unreferenced_payment == sum(refinvamount_list):

                            Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True,semirefrenced = False, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list))

                        else:

                            Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list), semirefrenced = True)

                    else:

                        for j in saleinvref_sets:

                            tenant_id=request.user.tenant_company.id

                            if j['refinvno'] != None and j['year_opening'] == False:

                                refinvno = j['refinvno']
                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_filter_check = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = refinvno).exists()

                                if reference_filter_check == True:

                                    print("invoice reference exists")

                                    reference_filter = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = refinvno)

                                    for x in reference_filter:

                                        data_filter = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                                        data_get = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

                                        data_filter.update(refinvamount = data_get.refinvamount + refinvamount)

                                else:

                                    print("reference filter not found")

                                    reference_data = Vendor_Saleinvref(refernce = datas, refinvno_id = refinvno, refinvamount = refinvamount,tenant_id = tenant_id)

                                    reference_data.save()

                                payment_balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = refinvno)

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                Vendor_Balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invoice_details_id= refinvno).update(invamount = invoice_amount, ref_payment = payment)

                            elif j['refinvno'] == None and j['year_opening'] == True:

                                refinvamount = j['refinvamount']

                                refinvamount_list.append(refinvamount)

                                reference_filter_check = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = None).exists()

                                if reference_filter_check == True:

                                    print("invoice reference exists")

                                    reference_filter = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(refernce_id = id, refinvno_id = None)

                                    for x in reference_filter:

                                        data_filter = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                                        data_get = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x.id)

                                        data_filter.update(refinvamount = data_get.refinvamount + refinvamount)

                                else:

                                    print("reference filter not found")

                                    reference_data = Vendor_Saleinvref(refernce = datas, refinvno_id = None, refinvamount = refinvamount,tenant_id = tenant_id)

                                    reference_data.save()

                                payment_balance = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = datas.companycode_id).first()

                                invoice_amount = payment_balance.invamount - refinvamount
                                payment = payment_balance.ref_payment + refinvamount

                                Vendor_Balancedetails.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id= payment_balance.id).update(invamount = invoice_amount, ref_payment = payment)

                            if datas.unreferenced_payment == sum(refinvamount_list):

                                print("Here")

                                Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, semirefrenced = False, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list))

                            else:

                                print("there")

                                Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = id).update(billrefered = True, unreferenced_payment = datas.unreferenced_payment - sum(refinvamount_list), semirefrenced = True)

                else:

                    return Response("Matching Payment Details Does Not Exists")

            elif x['patch'] == True:

                datas = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                ref_get = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                old_amount = ref_get.refinvamount

                serializer = salesinvrefserializer2(ref_get, data = x, partial = True)

                if serializer.is_valid():

                    serializer.save()

                    ref_get = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                    new_amount = ref_get.refinvamount

                    if new_amount > old_amount:

                        extra_amount = new_amount - old_amount

                        if ref_get.refinvno_id != None:

                            balance_details_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                            balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                        elif ref_get.refinvno_id == None:

                            balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                            for g in balance_details_filter:

                                balance_details_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                        balance_details_filter.update(invamount = balance_details_get.invamount - extra_amount, ref_payment = balance_details_get.ref_payment + extra_amount)

                        payments_get = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        payments_filter = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                        payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment - extra_amount)

                        payments_get2 = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        if payments_get2.unreferenced_payment == 0:

                            payments_filter.update(semirefrenced = False)

                        else:

                            payments_filter.update(semirefrenced = True)

                    elif new_amount < old_amount:

                        extra_amount = old_amount - new_amount

                        if ref_get.refinvno_id != None:

                            balance_details_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                            balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                        elif ref_get.refinvno_id == None:

                            balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                            for g in balance_details_filter:

                                balance_details_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                        balance_details_filter.update(invamount = balance_details_get.invamount + extra_amount, ref_payment = balance_details_get.ref_payment - extra_amount)

                        payments_get = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        payments_filter = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                        payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment + extra_amount)

                        payments_get2 = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                        if payments_get2.unreferenced_payment == payments_get2.payment_amount:

                            payments_filter.update(semirefrenced = False, billrefered = False)

                        else:

                            payments_filter.update(billrefered = True, semirefrenced = True)

                else:

                    return Response({'status': False, 'error': serializer.errors})

            elif x['delete'] == True:

                print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")

                datas = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = id)

                ref_get = Vendor_Saleinvref.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = x['id'])

                if ref_get.refinvno_id != None:

                    print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')

                    balance_details_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(invoice_details_id = ref_get.refinvno_id)

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = ref_get.refinvno_id)

                elif ref_get.refinvno_id == None:

                    print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(invoice_details_id = None, payment_details_id = None, companycode_id = datas.companycode_id)

                    for g in balance_details_filter:

                        balance_details_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = g.id)

                balance_details_filter.update(invamount = balance_details_get.invamount + ref_get.refinvamount, ref_payment = balance_details_get.ref_payment - ref_get.refinvamount)

                payments_get = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                payments_filter = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = ref_get.refernce_id)

                payments_filter.update(unreferenced_payment = payments_get.unreferenced_payment + ref_get.refinvamount)

                payments_get2 = Vendor_Paymentdetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).get(id = ref_get.refernce_id)

                print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')

                if payments_get2.unreferenced_payment == payments_get2.payment_amount:

                    payments_filter.update(semirefrenced = False, billrefered = False)

                else:

                    payments_filter.update(billrefered = True, semirefrenced = True)

                print('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')

                ref_get.delete()

        return Response({'status': True, 'patch': 'Data Updated successfully'})


class SalesCompanyYearOpeningUpdate(APIView):

    def updateData(self, request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id):

        if old_balance > balance_amount:

            new_balance = old_balance - balance_amount

            balance_data_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalbalance_amount = x.totalbalance_amount - new_balance)

        elif old_balance < balance_amount:

            new_balance = balance_amount - old_balance

            balance_data_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalbalance_amount = x.totalbalance_amount + new_balance)


        if old_invoice > invoice_amount:

            new_balance = old_invoice - invoice_amount

            balance_data_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalinvoiceamount = x.totalinvoiceamount - new_balance)

        elif old_invoice < invoice_amount:

            new_balance = invoice_amount - old_invoice

            balance_data_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalinvoiceamount = x.totalinvoiceamount + new_balance)


        if old_payment > payment_amount:

            new_balance = old_payment - payment_amount

            balance_data_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalpaymentamount = x.totalpaymentamount - new_balance)

        elif old_payment < payment_amount:

            new_balance = payment_amount - old_payment

            balance_data_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalpaymentamount = x.totalpaymentamount + new_balance)


    def get(self, request, id):

        balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id).first()

        serializer = balancedetailsserilaizer15(balance_get)

        return Response(serializer.data)

    
    def patch(self, request, id = None):

        data = request.data

        balance_get = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id).first()

        old_balance = balance_get.totalbalance_amount
        old_invoice = balance_get.totalinvoiceamount
        old_payment = balance_get.totalpaymentamount

        serializer = balancedetailsserilaizer15(balance_get, data = data, partial = True)

        balance_amount = data['totalbalance_amount']
        invoice_amount = data['totalinvoiceamount']
        payment_amount = data['totalpaymentamount']

        if serializer.is_valid():

            if (balance_amount + payment_amount) <= invoice_amount:

                if balance_get.ref_payment == 0:

                    serializer.save()

                    balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, invoice_details_id = None, payment_details_id = None)

                    balance_filter.update(invamount = balance_amount)

                    self.updateData(request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id)

                    return Response({'status': True, "Message": 'Data Updated'})

                elif balance_get.ref_payment > 0:

                    if balance_amount >= balance_get.ref_payment:

                        serializer.save()

                        balance_filter = balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, invoice_details_id = None, payment_details_id = None)

                        balance_filter.update(invamount = balance_amount - balance_get.ref_payment)

                        self.updateData(request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id)

                        return Response({'status': True, "Message": 'Data Updated'})

                    elif balance_amount < balance_get.ref_payment:

                        return Response({'status': False, 'error': "You can't reduce the balance amount lesserthan referenced amount, please delete references to reduce balance amount"})

            else:

                return Response({'status': False, 'error': 'The (balance amount + payment amount) must be lesserthan or equal to invoice amount'})

        else:

            return Response({'status': False, 'error': serializer.errors})


class PurchaseCompanyYearOpeningUpdate(APIView):
    
    def updateData(self, request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id):

        if old_balance > balance_amount:

            new_balance = old_balance - balance_amount

            balance_data_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalbalance_amount = x.totalbalance_amount - new_balance)

        elif old_balance < balance_amount:

            new_balance = balance_amount - old_balance

            balance_data_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalbalance_amount = x.totalbalance_amount + new_balance)


        if old_invoice > invoice_amount:

            new_balance = old_invoice - invoice_amount

            balance_data_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalinvoiceamount = x.totalinvoiceamount - new_balance)

        elif old_invoice < invoice_amount:

            new_balance = invoice_amount - old_invoice

            balance_data_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalinvoiceamount = x.totalinvoiceamount + new_balance)


        if old_payment > payment_amount:

            new_balance = old_payment - payment_amount

            balance_data_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalpaymentamount = x.totalpaymentamount - new_balance)

        elif old_payment < payment_amount:

            new_balance = payment_amount - old_payment

            balance_data_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalpaymentamount = x.totalpaymentamount + new_balance)


    def get(self, request, id):

        balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id).first()
        
        serializer = purchaseserilaizers17(balance_get)

        return Response(serializer.data)

    
    def patch(self, request, id = None):

        data = request.data

        balance_get = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id).first()

        old_balance = balance_get.totalbalance_amount
        old_invoice = balance_get.totalinvoiceamount
        old_payment = balance_get.totalpaymentamount

        serializer = purchaseserilaizers17(balance_get, data = data, partial = True)

        balance_amount = data['totalbalance_amount']
        invoice_amount = data['totalinvoiceamount']
        payment_amount = data['totalpaymentamount']

        if serializer.is_valid():

            if (balance_amount + payment_amount) <= invoice_amount:

                if balance_get.ref_payment == 0:

                    serializer.save()

                    balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, invoice_details_id = None, payment_details_id = None)

                    balance_filter.update(invamount = balance_amount)

                    self.updateData(request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id)

                    return Response({'status': True, "Message": 'Data Updated'})

                elif balance_get.ref_payment > 0:

                    if balance_amount >= balance_get.ref_payment:

                        serializer.save()

                        balance_filter = purchase_statement.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, invoice_details_id = None, payment_details_id = None)

                        balance_filter.update(invamount = balance_amount - balance_get.ref_payment)

                        self.updateData(request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id)

                        return Response({'status': True, "Message": 'Data Updated'})

                    elif balance_amount < balance_get.ref_payment:

                        return Response({'status': False, 'error': "You can't reduce the balance amount lesserthan referenced amount, please delete references to reduce balance amount"})

            else:

                return Response({'status': False, 'error': 'The (balance amount + payment amount) must be lesserthan or equal to invoice amount'})

        else:

            return Response({'status': False, 'error': serializer.errors})


class VendorCompanyYearOpeningUpdate(APIView):

    def updateData(self, request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id):

        print("inside the function")

        if old_balance > balance_amount:

            print("old balance greaterthan new balance")

            new_balance = old_balance - balance_amount

            print(new_balance, "the new balance")

            balance_data_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            print(balance_data_filter)

            for x in balance_data_filter:

                print("inside the loop")

                if x.payment_code > 1:

                    print("inside the iff")

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalbalance_amount = x.totalbalance_amount - new_balance)

        elif old_balance < balance_amount:

            new_balance = balance_amount - old_balance

            balance_data_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalbalance_amount = x.totalbalance_amount + new_balance)


        if old_invoice > invoice_amount:

            new_balance = old_invoice - invoice_amount

            balance_data_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalinvoiceamount = x.totalinvoiceamount - new_balance)

        elif old_invoice < invoice_amount:

            new_balance = invoice_amount - old_invoice

            balance_data_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalinvoiceamount = x.totalinvoiceamount + new_balance)


        if old_payment > payment_amount:

            new_balance = old_payment - payment_amount

            balance_data_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalpaymentamount = x.totalpaymentamount - new_balance)

        elif old_payment < payment_amount:

            new_balance = payment_amount - old_payment

            balance_data_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id)

            for x in balance_data_filter:

                if x.payment_code > 1:

                    balance_details_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(id = x.id)

                    balance_details_filter.update(totalpaymentamount = x.totalpaymentamount + new_balance)


    def get(self, request, id):

        balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id).first()

        serializer = Vendor_Balance_Serializer(balance_get)

        return Response(serializer.data)

    
    def patch(self, request, id = None):

        data = request.data

        balance_get = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id).first()

        print(balance_get.invamount, "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")

        old_balance = balance_get.totalbalance_amount
        old_invoice = balance_get.totalinvoiceamount
        old_payment = balance_get.totalpaymentamount

        serializer = Vendor_Balance_Serializer(balance_get, data = data, partial = True)

        balance_amount = data['totalbalance_amount']
        invoice_amount = data['totalinvoiceamount']
        payment_amount = data['totalpaymentamount']

        if serializer.is_valid():

            if (balance_amount + payment_amount) <= invoice_amount:

                if balance_get.ref_payment == 0:


                    print("Ref payment ==== 0")

                    serializer.save()

                    balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, invoice_details_id = None, payment_details_id = None)

                    balance_filter.update(invamount = balance_amount)

                    self.updateData(request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id)

                    return Response({'status': True, "Message": 'Data Updated'})

                elif balance_get.ref_payment > 0:

                    print("Ref payment not equal to 0")

                    if balance_amount >= balance_get.ref_payment:

                        print("Valid condition")

                        serializer.save()

                        balance_filter = Vendor_Balancedetails.objects.current_financialyear(id=request.user.tenant_company.id,stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(companycode_id = id, invoice_details_id = None, payment_details_id = None)

                        balance_filter.update(invamount = balance_amount - balance_get.ref_payment)

                        self.updateData(request, old_balance, old_invoice, old_payment, balance_amount, invoice_amount, payment_amount, id)

                        return Response({'status': True, "Message": 'Data Updated'})

                    elif balance_amount < balance_get.ref_payment:

                        print("Invalid condition")

                        return Response({'status': False, 'error': "You can't reduce the balance amount lesserthan referenced amount, please delete references to reduce balance amount"})

            else:

                return Response({'status': False, 'error': 'The (balance amount + payment amount) must be lesserthan or equal to invoice amount'})

        else:

            return Response({'status': False, 'error': serializer.errors})



class apigetway_plreports(APIView):

    def stock_get(self,request):
        pass
    def post(self, request, *args, **kwargs):
        datas=[]
        x=[]
        x1=[]
        y1=[]
        k=[]
        l=[]
        y=[]
        z=[]
        za=[]
        startdate = request.data['fromdate']
        enddate = request.data['todate']
        details= purchaseinvoicedetails.objects.current_financialyear(id=request.headers['tenant-id'],
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(financial_period__gte=startdate, financial_period__lt=enddate)

        final_total=purchaseinvoicedetails.objects.current_financialyear(id=request.headers['tenant-id'],
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(financial_period__gte=startdate, financial_period__lt=enddate).aggregate(total_amount=Sum('amount'),g_total=Sum('subtotal'),total_cgst=Sum('cgst'),total_sgst=Sum('sgst'),total_igst=Sum('igst'))

        details1=details
        deta=details
        for i in details:

            resdata=company_details.objects.get(id=i.companycode_id)
            serializer = companyserializer(resdata)
        
            datalist={ "purchase_inv_amount":i.amount,
            "purchase_inv_number":i.invno,
            "purchase_inv_date":i.financial_period,
            "purchase_inv_igst":i.igst,
            "purchase_inv_cgst":i.cgst,
            "purchase_inv_sgst":i.sgst,
            "purchase_grand_total":i.subtotal,
            "company_id":serializer.data}
            x.append(datalist)
       
        md=[]
     
        for j in details:
        
            
            deta=[]
            
            for i in details1:
           
                if j.companycode == i.companycode:
                    
                 
                    datalist={ "purchase_inv_amount":i.amount,
                    "purchase_inv_number":i.invno,
                    "purchase_inv_date":i.financial_period,
                    "purchase_inv_igst":i.igst,
                    "purchase_inv_cgst":i.cgst,
                    "purchase_inv_sgst":i.sgst,
                    "purchase_grand_total":i.subtotal,
                    "purchase_company_id":i.companycode}
                    # y.append(datalist)
                    xy={"purchase_company_id":serializer.data}
                    md.append(xy)
                else:
                  
                  
                    deta.append(i)
           
          
            details1=deta
        
        temp = []
        res = dict()
        for m in md:
            for key, val in m.items():
                if val not in temp:
                    temp.append(val)
                    res[key] = val
        
     
        for n in temp:
            print(n["id"],"lkjhgfdsa")
            final_total1=purchaseinvoicedetails.objects.current_financialyear(id=request.headers['tenant-id'],
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(financial_period__gte=startdate,companycode=n["id"],
            financial_period__lt=enddate).aggregate(total_amount=Sum('amount'),g_total=Sum('subtotal'),total_cgst=Sum('cgst'),total_sgst=Sum('sgst'),total_igst=Sum('igst'))
            datalist={
            "purchase_company_id":n,
            "purchase_final_total":final_total1}
            y.append(datalist)

        kl=[]
        detailss= salesinvoicedetails.objects.current_financialyear(id=request.headers['tenant-id'],
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(financial_period__gte=startdate, financial_period__lt=enddate)





        final_totals= salesinvoicedetails.objects.current_financialyear(id=request.headers['tenant-id'],
                                                                        stdate=request.headers['sdate'],
                                                                        lstdate=request.headers['ldate']).filter(financial_period__gte=startdate, financial_period__lt=enddate).aggregate(total_amount=Sum('amount'),subtotal=Sum('subtotal'),cgst=Sum('cgst'),sgst=Sum('sgst'),igst=Sum('igst'))
   
        details1=detailss
        deta=detailss
        for i in detailss:
            print(i.companycode_id,">>>>>>>>")
            # resdata=company_details.objects.get(id=i.companycode_id)
            # serializer = companyserializer(resdata)
        
            datalists={ "sales_inv_amount":i.amount,
            "sales_inv_number":i.invno,
            "sales_inv_date":i.financial_period,
            "sales_inv_igst":i.igst,
            "sales_inv_cgst":i.cgst,
            "sales_inv_sgst":i.sgst,
            "sales_grand_total":i.subtotal,
            "sales_company_id":serializer.data}
            x1.append(datalists)

        kl.append(x1)
        mds=[]
     
        for j in detailss:
            
            deta=[]
            for i in details1:
        
                if j.companycode == i.companycode:
                    
                    xy1={"sales_company_code":j.companycode_id}
                    mds.append(xy1)
                else:
                  
                    deta.append(i)
           
            print(deta)
            details1=deta
            print(details1)
        kl.append(details1)
        temp = []
        res = dict()
        for m in md:
            for key, val in m.items():
                if val not in temp:
                    temp.append(val)
                    res[key] = val
        
        for n in temp:
            print(n,'<<<<')
            final_total1= salesinvoicedetails.objects.current_financialyear(id=request.headers['tenant-id'],
            stdate=request.headers['sdate'],lstdate=request.headers['ldate']).filter(financial_period__gte=startdate,companycode=n['id'],
            financial_period__lt=enddate).aggregate(total_amount=Sum('amount'),subtotal=Sum('subtotal'),sgst=Sum('sgst'),cgst=Sum('cgst'),igst=Sum('igst'))
            datalists={
                "sales_company_code":n,
                "sales_final_total":final_total1}
            y1.append(datalists)
            kl.append(y1)
        s_t_amt=i.amount
        s_g_total=i.subtotal
        sales_g_cgst=i.cgst
        sales_g_sgst=i.sgst
        sales_g_igst=i.igst

        p_t_amt=i.amount
        p_g_total=i.subtotal
        p_g_cgst=i.cgst
        p_g_sgst=i.sgst
        p_g_igst=i.igst

        z.append(final_total)

        z.append(x)
        z.append(y)

        t_amt= p_t_amt - s_t_amt
        g_total= p_g_total - s_g_total
        g_cgst=p_g_cgst-sales_g_cgst
        g_sgst= p_g_sgst- sales_g_sgst
        g_igst=p_g_igst-sales_g_igst
        datatm={ "t_amt":t_amt,
        "g_total":g_total,
        "g_cgst":g_cgst,
        "g_sgst":g_sgst,
        "g_igst":g_igst}
        k.append(datatm)

        l.append(final_totals)
        l.append(x1)
        l.append(y1)
        datas.append(l)
        datas.append(z)
        datas.append(k)
        # datas.append(kl)
        return Response(datas)












class debit_note_view(APIView):

    def DebitNumber(self, request):

        last_without_number = depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).order_by('id').last()
        

        if not last_without_number:

            return "DN1001"

        else:

            running_number = last_without_number.running_numbers + 1

            return "DN" + str(running_number)
    
    def DebitRunningNumber(self, request):

        last_without_running_number = depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).order_by('id').last()
        
        if not last_without_running_number:

            return 1001

        else:

            running_number = last_without_running_number.running_numbers + 1

            return running_number

    def get(self,request, id=None):

        if id:

            debit = depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).get(id = id)

            debit_details = Depit_Note_Serializer_GetByID(debit).data

            materials_filter = depit_note_materials.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(depit_details = id)

            materials_data = []

            for x in materials_filter:

                material = Depit_Note_Material_Serializer(x).data

                tool_price = ToolsPrice.objects.current_tenant(id = request.user.tenant_company.id).get(tool_id = material['tool']['id'], company_id = debit.company_id)

                material['tool']['tool_price'] = Tools_Price_Serializer(tool_price).data

                materials_data.append(material)

            debit_details['materials'] = materials_data

            return Response(debit_details)

        else:

            debit = depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).all()

            serializer = Depit_Note_Material_Serializer_Get(debit, many=True)

            return Response(serializer.data)

    def post(self,request):

        details = request.data[0]
        tenant_id = request.user.tenant_company.id
        serializer = Depit_Note_Serializer(data=details)

        if serializer.is_valid():

            debit_details = serializer.save(tenant_id=tenant_id,company_id=details['company_id'], invno = self.DebitNumber(request), running_numbers = self.DebitRunningNumber(request))

            materials = request.data[1]

            for dc in materials:

                without_dc = dc['without_details']

                without_details = ToolsWithout_Details.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).get(id = without_dc)

                without_material = ToolsWithout_Materials.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(without_details_id = without_details.id)

                Without_reference = without_ref(tenant_id = tenant_id, without_details_id= without_details.id , depit_details_id = debit_details.id)

                Without_reference.save()

                for mat in without_material:

                    tool = Tools.objects.current_tenant(id = request.user.tenant_company.id).get(id = mat.tool_id)

                    tool_price = ToolsPrice.objects.current_tenant(id = request.user.tenant_company.id).get(tool_id = tool.id, company_id = without_details.company.id)

                    price = tool_price.price
                    qty = mat.qty
                    amount = round(float(price * qty))

                    sgstper = tool_price.SGST
                    igstper = tool_price.IGST
                    cgstper = tool_price.CGST

                    sgst = (amount * (sgstper / 100))
                    igst = (amount * (igstper / 100))
                    cgst = (amount * (cgstper / 100))
                    tgst = (sgst + igst + cgst)
                    subtotal = amount + tgst

                    debit_materials = depit_note_materials(amount = amount, subtotal = subtotal, cgst = cgst, igst = igst, sgst = sgst, cgstper = cgstper, sgstper = sgstper, igstper = igstper, qty = qty, price = price, depit_details_id = debit_details.id, tenant_id = tenant_id, without_materials_id = mat.id, tool_id = mat.tool_id)

                    debit_materials.save()

                    ToolsWithout_Details.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id = without_details.id).update(is_debit=True)

            ft = depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(invno=debit_details.invno).exists()

            if ft == True:

                bill_inv = debit_details.id
                subtotal_bill=[]
                amount_bill=[]
                sgst_bill = []
                cgst_bill = []
                igst_bill = []

                agg = depit_note_materials.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(depit_details_id = bill_inv)
                for details in agg:
                    subtotal_bill.append(details.subtotal)
                    amount_bill.append(details.amount)
                    sgst_bill.append(details.sgst)
                    cgst_bill.append(details.cgst)
                    igst_bill.append(details.igst)

                df3= depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id = bill_inv)

                df3.update(grand_total=round(sum(subtotal_bill),2),t_amount=round(sum(amount_bill),2),t_sgst = round(sum(sgst_bill),2),t_cgst=round(sum(cgst_bill),2),t_igst = round(sum(igst_bill),2))

            return Response({'status': True, 'message': "Data Saved"})
          
        else:
            
            return Response({'status': False, 'message': "Some error in data", 'error': serializer.errors})

    def delete(self,request,id):

        debit_invoice = depit_note_invoice.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).get(id=id)

        debit_materials = depit_note_materials.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(depit_details_id = id)

        for x in debit_materials:

            x.delete()

        without_references = without_ref.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(depit_details_id=id)

        for y in without_references:

            without_dcs = ToolsWithout_Details.objects.current_financialyear(id = request.user.tenant_company.id, stdate = request.headers['sdate'], lstdate = request.headers['ldate']).filter(id = y.without_details_id)

            without_dcs.update(is_debit=False)

            y.delete()

        debit_invoice.delete()
    
        return Response({'status': True, 'Message': 'Data Deleted'})



