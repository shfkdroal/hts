
from __future__ import absolute_import
#from django.template import RequestContext
from django.shortcuts import render, redirect
#from django.http import HttpResponse
#from .forms import *
from .models import *
#from django.db.models import Q
#import json
from passlib.hash import pbkdf2_sha256
import cryptocompare
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import *
import ast
#import datetime
#import time
from django.utils import timezone
#from django.template import r
#from django.core.context_processors import csrf
# Create your views here.
from django.http import JsonResponse
from django.core import serializers
from datetime import timezone, timedelta, date
from datetime import datetime as dt
#from django.conf import settings
#from django.db.models.signals import post_save
#from django.dispatch import receiver
import datetime
#User_Valid = False
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
#from itertools import chain


class Clock:
    @classmethod
    def Clock(cls):
        #timeElemtnets = time.ctime().split(" ")
        #day = timeElemtnets[0]
        #month = timeElemtnets[1]
        #date = timeElemtnets[2]
        #Clock = timeElemtnets[3].split(':')
        # print(Clock)

        Clock = time.strftime("%H %M %S", time.localtime()).split(' ')
        """
        Hour = Clock[0]
        Min = Clock[1]
        Sec = Clock[2]
        """
        return Clock

class Day:
    @classmethod
    def Day(cls):
        timeElemtnets = time.ctime().split(" ")
        day = timeElemtnets[0]
        # print(Clock)
        """
        Hour = Clock[0]
        Min = Clock[1]
        Sec = Clock[2]
        """
        return day

class DatesNum:
    @classmethod
    def Dates(cls):
        totalDates = time.strftime("%Y%m%d", time.localtime())
        return totalDates


@csrf_exempt
def index(request):
    template = 'index.html'
    return render(request, template)


@csrf_exempt
def show_signin_req(request):
    if request.method == 'POST':
        objs = SignInReq.objects.all().order_by('user_idx')
        Searach_query_shares = serializers.serialize("json", objs)
        return JsonResponse(Searach_query_shares, safe=False)
    return

@csrf_exempt
def show_loan_req(request):
    if request.method == 'POST':
        objs = Loan_Order_Done.objects.filter(Is_Done=False).order_by('-Order_Date')
        Searach_query_shares = serializers.serialize("json", objs)
        return JsonResponse(Searach_query_shares, safe=False)
    return

@csrf_exempt
def show_deposit_req(request):
    if request.method == 'POST':
        reqTypeShare_idx = Entire_Shares.objects.get(Share_Category=-1)
        objs = Transaction.objects.filter(Share_idx=reqTypeShare_idx, Order_Type=2, TreatStatus=-1)
        #objs = Deposit_Withdraw_Order_Done_List.objects.filter(Order=2, PlusMinus=0)
        Searach_query_shares = serializers.serialize("json", objs)
        return JsonResponse(Searach_query_shares, safe=False)
    return

@csrf_exempt
def show_width_req(request):
    if request.method == 'POST':
        reqTypeShare_idx = Entire_Shares.objects.get(Share_Category=-1)
        objs = Transaction.objects.filter(Share_idx=reqTypeShare_idx, Order_Type=3, TreatStatus=-1)
        #objs = Deposit_Withdraw_Order_Done_List.objects.filter(Order=3, PlusMinus=0)
        Searach_query_shares = serializers.serialize("json", objs)
        return JsonResponse(Searach_query_shares, safe=False)
    return



@csrf_exempt
def show_signin_appr(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        List = de.get('list') #models.CharField(max_length=50, unique=True) #False

        for i in List:
            object = SignInReq.objects.get(user_idx=i)
            tempObj = User_In.objects.create(
                user_id=object.user_id,
                user_pw=object.user_pw,
                bank_id=object.bank_id,
                user_pn=object.user_pn,
                user_bank_name=object.user_bank_name,
                user_name=object.user_name,
                signin_domain=object.signin_domain
            )
            Asset.objects.create(
                user_idx=tempObj,
                Estimated_Profit=0,
                Realized_Profit=0,
                Total_Profit=0,
                losscut_left=0,
                poured_money=0,
                Actual_money_by_now=0,
                lended_loan_by_now=0,
                used_money=0,
                available_money=0,
            )

        for i in List:
            obj = SignInReq.objects.get(user_idx=i)
            obj.delete()
        #queryset.delete()
    return

@csrf_exempt
def show_loan_appr(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        print(de)
        de = ast.literal_eval(de)
        print(de)
        List = de.get('list') #models.CharField(max_length=50, unique=True) #False

        print(list)

        msObj = MarketStatus.objects.all().latest('id')
        loanFee = msObj.LoanFee
        for i in List:
            object = Loan_Order_Done.objects.get(id=i)
            if object.Is_Done == False:
                timestamp = time.time()
                dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
                kmt = dt_utc + timedelta(hours=9)
                kmt = str(kmt)

                object.Is_Done = True
                object.Done_Date = kmt
                print(kmt)
                """
                loanAppr = Loan_Order_Done.objects.create(user_idx=object.user_idx,
                                                          Stock_Loan_Rate=object.Stock_Loan_Rate,
                                                          Dam_bo_geum=object.Dam_bo_geum,
                                                          Is_Done=True, Done_Date=timezone.now())
                """
                object.save()
                # object.Order_Date = None
                AssetEntry = Asset.objects.get(user_idx=object.user_idx)
                lended_loan_by_now = object.Dam_bo_geum * object.Stock_Loan_Rate
                AssetEntry.lended_loan_by_now += lended_loan_by_now
                AssetEntry.poured_money -= lended_loan_by_now * loanFee / 100
                AssetEntry.Dam_bo_geum += object.Dam_bo_geum
                AssetEntry.save()

    return

@csrf_exempt
def show_deposit_appr(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        List = de.get('list') #models.CharField(max_length=50, unique=True) #False
        for i in List:
            #object_0 = Deposit_Withdraw_Order_Done_List.objects.get(id=i)
            object = Transaction.objects.get(id=i)
            if object.Share_idx.Share_Code == '신청' and object.Order_Type == 2:
                AssetEntry = Asset.objects.get(user_idx=object.user_idx)
                # AssetEntry.poured_money += object.Deposit_Money
                AssetEntry.losscut_left += object.Deposit_Money
                AssetEntry.save()

                order_deposit_obj = Deposit_Withdraw_Order_Done_List.objects.get(Transaction_idx=object)
                order_deposit_obj.TransactionDependency = str(object.id)
                order_deposit_obj.save()

                DepositAppr = Transaction.objects.create(user_idx=object.user_idx,
                                                         Share_idx=Entire_Shares.objects.get(Share_Category=-2),
                                                         TransDateTime=object.TransDateTime,
                                                         Order_Type=object.Order_Type,
                                                         TreatStatus=2, Deposit_Money=object.Deposit_Money,
                                                         Actual_money=object.Actual_money)
                object.Share_idx = Entire_Shares.objects.get(Share_Code='처리 완료')
                object.save()
                # DepositAppr.save()
                DepositAppr_sub = Deposit_Withdraw_Order_Done_List.objects.create(
                    user_idx=object.user_idx,
                    Order_Money_Plus_Minus=object.Deposit_Money,
                    Transaction_idx=DepositAppr, Order=object.Order_Type, PlusMinus=object.Deposit_Money,
                    TransactionDependency=str(object.id)
                )

    return

@csrf_exempt
def show_width_appr(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        List = de.get('list') #models.CharField(max_length=50, unique=True) #False

        for i in List:
            #object_0 = Deposit_Withdraw_Order_Done_List.objects.get(id=i)
            object = Transaction.objects.get(id=i)
            if object.Share_idx.Share_Code == '신청' and object.Order_Type == 3:
                AssetEntry = Asset.objects.get(user_idx=object.user_idx)
                # AssetEntry.poured_money += object.Deposit_Money
                AssetEntry.losscut_left += object.Deposit_Money
                AssetEntry.save()

                order_with_obj = Deposit_Withdraw_Order_Done_List.objects.get(Transaction_idx=object)
                order_with_obj.TransactionDependency = str(object.id)
                order_with_obj.save()

                WithAppr = Transaction.objects.create(user_idx=object.user_idx,
                                                      Share_idx=Entire_Shares.objects.get(Share_Category=-2),
                                                      TransDateTime=object.TransDateTime, Order_Type=object.Order_Type,
                                                      TreatStatus=3, Deposit_Money=object.Deposit_Money,
                                                      Actual_money=object.Actual_money)
                object.Share_idx = Entire_Shares.objects.get(Share_Code='처리 완료')
                object.save()
                # WithAppr.save()
                WithAppr_sub = Deposit_Withdraw_Order_Done_List.objects.create(
                    user_idx=object.user_idx,
                    Order_Money_Plus_Minus=object.Deposit_Money,
                    Transaction_idx=WithAppr, Order=object.Order_Type, PlusMinus=object.Deposit_Money,
                    TransactionDependency=str(object.id)
                )

    return


@csrf_exempt
def create_signin_row(request):

    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_id = de.get('user_id') #models.CharField(max_length=50, unique=True) #False
        user_pw = de.get('user_pw') #models.CharField(max_length=50)
        bank_id = de.get('bank_id') #models.CharField(max_length=100)
        user_pn = de.get('user_pn')
        user_bank_name = de.get('user_bank_name') #models.CharField(max_length=50)
        user_name = de.get('user_name') #models.CharField(max_length=50)

        domain = "-"
        if 'domain' in de:
            domain = de.get('domain')  # models.CharField(max_length=50)
        enc_user_pw = pbkdf2_sha256.encrypt(user_pw, rounds=12000, salt_size=32)

        if SignInReq.objects.filter(user_id=user_id) or User_In.objects.filter(user_id=user_id):
            JsonResponse({"3": "이미 존재하는 아이디 입니다"})
            return

        try:
            SignInReq_row = SignInReq.objects.create(
                user_id=user_id,
                user_pw=enc_user_pw,
                bank_id=bank_id,
                user_pn=user_pn,
                user_bank_name=user_bank_name,
                user_name=user_name,
                signin_domain=domain
            )
            SignInReq_row.save()
            return JsonResponse({"0": "true"})
            #return HttpResponse('true')
        except:
            return JsonResponse({"2": "false"})

        #return render(request, 'index.html', {'form': form})
        #return JsonResponse({"register": "false"})#do something!


"""
global User_Valid
User_Valid = True
global User_Decider
User_Decider = one_Entry.user_idx #get user_idx
token = one_Entry.user_pw
#token.save() #should be deleted when user logged out or exit
#token_json = serializers.serialize("json", token)
"""

@csrf_exempt
def check_login(request):
    if request.method == 'POST':

        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)

        user_id = de.get('user_id') #models.CharField(max_length=50, unique=True) #False
        user_pw = de.get('user_pw') #models.CharField(max_length=50)
        one_Entry = User_In.objects.filter(user_id=user_id)
        one_Entry2 = admins.objects.filter(admin_id=user_id)

        ipTCPadr = MarketStatus.objects.all().latest('id').IpTcpAdr
        if (one_Entry):
            one_Entry = one_Entry[0]
            if (not one_Entry.shut_down):
                if User_In.verify_password(one_Entry, user_pw):
                    return JsonResponse({"user_idx": one_Entry.user_idx, "is_admin": 0, "ipTCPadr": ipTCPadr})
                    # return JsonResponse({0: 'true'}) #redirect to main pg - redirect("")
                else:
                    return JsonResponse({"2": "pw_failed"})  # pw or id was wrong
        elif one_Entry2:
            one_Entry2 = one_Entry2[0]
            if admins.verify_password(one_Entry2, user_pw):
                return JsonResponse({"user_idx": one_Entry2.id, "is_admin": 1, "ipTCPadr": ipTCPadr})
        else:
            return JsonResponse({"2": "false"}) #pw or id was wrong
    else:
        return JsonResponse({"2": "false"})  # pw or id was wrong

@csrf_exempt
def change_pw(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)

        user_id_num = de.get('user_idx')  # models.CharField(max_length=50, unique=True) #False
        newPw = de.get('new_pw')
        user_obj = User_In.objects.get(user_idx=user_id_num)
        user_obj.user_pw = pbkdf2_sha256.encrypt(newPw, rounds=12000, salt_size=32)
        #user_obj.shut_down = True
        user_obj.save()
        return JsonResponse({"1": "shutdown suceed"})  # pw or id was wrong


#user id로 입력을 받는다 (idx가 아님)
@csrf_exempt
def shutdown(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)

        user_id_num = de.get('user_id')  # models.CharField(max_length=50, unique=True) #False
        user_obj = User_In.objects.get(user_id=user_id_num)
        user_obj.shut_down = True
        user_obj.save()
        return JsonResponse({"1": "shutdown suceed"})  # pw or id was wrong

#user id로 입력을 받는다 (idx가 아님)
@csrf_exempt
def shutdown2(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)

        user_id_num = de.get('user_id')  # models.CharField(max_length=50, unique=True) #False
        user_obj = User_In.objects.get(user_id=user_id_num)
        user_obj.shut_down = False
        user_obj.save()
        return JsonResponse({"1": "shutdown2 suceed"})  # pw or id was wrong

@csrf_exempt
def cancell_not_done(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        id_lists_not_done = de.get('list')  # models.CharField(max_length=50, unique=True) #False
        for i in id_lists_not_done:
            not_done_obj = List_Not_Done.objects.get(id=int(i))
            Transaction_idx = not_done_obj.Transaction_idx
            Transaction_idx.OtherMsg = "취소"
            #Transaction_idx.delete()
            not_done_obj.delete()
            Transaction_idx.save()
            #must delete transaction list also
        userEnt = User_In.objects.get(user_idx=user_idx)
        not_done_entities = List_Not_Done.objects.filter(user_idx=userEnt)
        Searach_query_shares = serializers.serialize("json", not_done_entities)
        return JsonResponse(Searach_query_shares, safe=False)

@csrf_exempt
def chart(request):
    if request.method == 'POST':

        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)

        #user_id = de.get('user_id') #models.CharField(max_length=50, unique=True) #False
        sid = int(de.get('spk'))
        sobj = Entire_Shares.objects.get(id=sid)
        sct = sobj.Share_Category
        if sct == 1:
            isExClosed = (MarketStatus.objects)
            usdRate = isExClosed.values()[0]["ExchangeRate_USD"]

            dictD = cryptocompare.get_historical_price_day(sobj.Share_Code, curr='USD')#*usdRate

            for i in dictD["Data"]:
                i["open"] = i["open"]*usdRate
                i["close"] = i["close"]*usdRate
                i["low"] = i["low"] *usdRate
                i["high"] = i["high"]*usdRate
            dictH = cryptocompare.get_historical_price_day(sobj.Share_Code, curr='USD')#*usdRate
            for i in dictH["Data"]:
                i["open"] = i["open"]*usdRate
                i["close"] = i["close"]*usdRate
                i["low"] = i["low"] *usdRate
                i["high"] = i["high"]*usdRate
            dictCharts = {}
            dictCharts['D'] = dictD
            dictCharts['H'] = dictH
            return JsonResponse(dictCharts)
        else:
            Dates = DatesNum.Dates()
            if share_chart.objects.filter(Share_Category=sct, Spk=sid):
                scEnt = share_chart.objects.get(Share_Category=sct, Spk=sid)

                #print(scEnt.StandardDate, "Chart Standard Date")
                #print(Dates, "Now Dates")

                if str(scEnt.StandardDate) == Dates and scEnt.Chart_Dict != "{}":
                    return JsonResponse({"chart": "주식 최신 차트 존재"}) #ast.literal_eval(scEnt.Chart_Dict)
                elif scEnt.StandardDate != Dates or scEnt.Chart_Dict == "{}":
                    scEnt.Should_be_updated_now = True
                    scEnt.save()
                    return JsonResponse({"chart": "차트 업데이트 요청"})
            else:
                share_chart.objects.create(Spk=sid, Share_Category=sct, StandardDate=Dates)
                return JsonResponse({"chart": "주식 차트는 요청 생성"})
                #create
        return


@csrf_exempt
def searh_among_stocks(request):
    #User_Valid = True
    if request.method == 'POST':

        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        isName = de.get('isName')
        sct = de.get('sct') #mandatory input from client

        #scd = de.get('scd')
        #sname = de.get('sname')
        search_name = de.get('search_name')
        # Ff
        #s_Entries = Entire_Shares.objects.filter(Share_Category=sct)
        if isName == "true":
            s_Entries = Entire_Shares.objects.filter(Share_Name__contains=search_name, Share_Category=sct,
                                                     Is_feasible=True)
            Searach_query_shares = serializers.serialize("json", s_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
        elif isName == "false":
            s_Entries = Entire_Shares.objects.filter(Share_Code=search_name, Share_Category=sct,
                                                     Is_feasible=True)
            Searach_query_shares = serializers.serialize("json", s_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
        return JsonResponse({"2": "false"})
    else:
        return JsonResponse({"2": "false"})

@csrf_exempt
def search_among_users(request):
    #User_Valid = True
    if request.method == 'POST':

        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        is_id = bool(de.get('is_id'))
        search_name = de.get('search_name')

        if is_id == True:
            s_Entries = User_In.objects.filter(user_id__contains=search_name)
            Searach_query_shares = serializers.serialize("json", s_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
        elif is_id == False:
            s_Entries = Entire_Shares.objects.filter(user_pn__contains=search_name)
            Searach_query_shares = serializers.serialize("json", s_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
        return JsonResponse({"2": "false"})
    else:
        return JsonResponse({"2": "false"})

@csrf_exempt
def show_domains(request):
    if request.method == 'POST':

        domains = DomainList.objects.all().order_by('dtime')
        Searach_query_shares = serializers.serialize("json", domains)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"2": "false"})


@csrf_exempt
def show_partners(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        ppk = int(de.get('admin_idx'))
        this_admin = admins.objects.get(id=ppk)
        p_list = GrantTreeStructure.objects.filter(admin_idx=this_admin)
        admin_list = []
        for p in p_list:
            dictA = {"admin_id2": "", "admin_pn": "", "admin_bank_name": "", "profit_ratio": 0}
            adminObj = p.admin_refer_idx
            print(adminObj)
            dictA["admin_id2"] = adminObj.admin_id
            dictA["admin_pn"] = adminObj.admin_pn
            dictA["admin_bank_name"] = adminObj.admin_bank_name
            dictA["profit_ratio"] = adminObj.profit_ratio
            admin_list.append(dictA)
        admin_list = json.dumps(admin_list)
        #Searach_query_shares = serializers.serialize("json", admin_list)
        return JsonResponse(admin_list, safe=False)


@csrf_exempt
def show_MarketStatus(request):
    if request.method == 'POST':
        ms = MarketStatus.objects.all()
        Searach_query_shares = serializers.serialize("json", ms)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"2": "failed"})


@csrf_exempt
def modify_MarketStatus(request):
    if request.method == 'POST':
        try:
            de = request.POST.dict()
            de = list(de.keys())[list(de.values()).index('')]
            de = ast.literal_eval(de)

            ppk = int(de.get('admin_idx'))

            adminObj = admins.objects.get(id=ppk)
            grant = adminObj.grant
            if grant != 0:
                return JsonResponse({"msg": "변경 권한이 없습니다"})

            is_market_exceptionally_closed = bool(de.get('is_market_exceptionally_closed'))  # 0, 1
            LossCutRate = float(de.get('LossCutRate'))
            #BasicFeeBuy = float(de.get('BasicFeeBuy'))
            LoanFee = float(de.get('LoanFee'))
            SellFee = float(de.get('SellFee'))
            BuyFee = float(de.get('BuyFee'))
            Max_Task = int(de.get('Max_Task'))
            OVNFee = float(de.get('OVNFee'))
            ExchangeRate_USD = int(de.get('ExchangeRate_USD'))

            ms = MarketStatus.objects.all().latest('id')
            ms.is_market_exceptionally_closed = is_market_exceptionally_closed
            ms.LossCutRate = LossCutRate
            ms.BasicFeeBuy = 0#BasicFeeBuy
            ms.BasicFeeSell = 0#BasicFeeSell
            ms.SellFee = SellFee
            ms.BuyFee = BuyFee
            ms.Max_Task = Max_Task
            ms.OVNFee = OVNFee
            ms.ExchangeRate_USD = ExchangeRate_USD
            ms.LoanFee = LoanFee
            ms.save()

            return JsonResponse({"1": "succeed"})
        except:
            return JsonResponse({"2": "타입을 확인 해 주세요 "
                                       "(최대 프로세스 수, 환율은 자연수, 수수료는 소수형입니다)"})

    else:
        return JsonResponse({"2": "failed"})


@csrf_exempt
def show_Profit_Stat_Partner(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        ppk = int(de.get('ppk'))
        filterVal = de.get('admin_id')
        pg = de.get('pg')

        thiAdmin = admins.objects.get(id=ppk)
        grantToSeeQuery = GrantTreeStructure.objects.filter(admin_idx=thiAdmin)
        #print(grantToSeeQuery)
        grantToSeeList = []
        #print(grantToSeeList)
        for i in grantToSeeQuery:
            grantToSeeList.append(i.admin_refer_idx)
        #print(grantToSeeList)
        if filterVal == "":
            pspList = Profit_Stat_Partner.objects.filter(admin_idx__in=grantToSeeList)
            print(pspList)
            paginator = Paginator(pspList, 10)
            try:
                contacts = paginator.page(pg)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)

            Searach_query_shares = serializers.serialize("json", contacts)
            Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
            return JsonResponse(Searach_query_shares, safe=False)
        else:
            admin_obj = admins.objects.get(admin_id=filterVal)
            pspList = Profit_Stat_Partner.objects.filter(admin_idx=admin_obj, admin_idx__in=grantToSeeList)
            paginator = Paginator(pspList, 10)
            try:
                contacts = paginator.page(pg)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)

            Searach_query_shares = serializers.serialize("json", contacts)
            Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
            return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"2": "failed"})


@csrf_exempt
def admin_in(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        #ppk = int(de.get('admin_idx'))
        user_id = de.get('user_id')
        quantity = float(de.get('q'))
        if quantity == 0:
            return

        user_obj = User_In.objects.get(user_id=user_id)
        asset = Asset.objects.get(user_idx=user_obj)
        asset.poured_money += quantity
        asset.save()
        Admin_M_IO.objects.create(user_idx=user_obj, Order=0, Quantity=quantity)
        return JsonResponse({"msg": "관리자 입금하였습니다"})

@csrf_exempt
def admin_Out(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        #ppk = int(de.get('admin_idx'))
        user_id = de.get('user_id')
        quantity = float(de.get('q'))
        if quantity == 0:
            return

        user_obj = User_In.objects.get(user_id=user_id)
        asset = Asset.objects.get(user_idx=user_obj)
        asset.poured_money -= quantity
        asset.save()
        Admin_M_IO.objects.create(user_idx=user_obj, Order=1, Quantity=quantity)
        return JsonResponse({"msg": "관리자 출금하였습니다"})

@csrf_exempt
def show_M_P_managementList(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        ppk = int(de.get('ppk'))
        filterVal = de.get('admin_id')
        pg = de.get('pg')

        thiAdmin = admins.objects.get(id=ppk)
        grantToSeeQuery = GrantTreeStructure.objects.filter(admin_idx=thiAdmin)
        grantToSeeList = []
        for i in grantToSeeQuery:
            grantToSeeList.append(i.admin_refer_idx)
        if filterVal == "":
            pspList = M_P_managementList.objects.filter(admin_idx__in=grantToSeeList)
            paginator = Paginator(pspList, 10)
            try:
                contacts = paginator.page(pg)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)

            Searach_query_shares = serializers.serialize("json", contacts)
            Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
            return JsonResponse(Searach_query_shares, safe=False)
        else:
            admin_obj = admins.objects.get(admin_id=filterVal)
            pspList = M_P_managementList.objects.filter(admin_idx=admin_obj, admin_idx__in=grantToSeeList)
            paginator = Paginator(pspList, 10)
            try:
                contacts = paginator.page(pg)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)

            Searach_query_shares = serializers.serialize("json", contacts)
            Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
            return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"show_mpm": "failed"})

@csrf_exempt
def mypg_admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        ppk = int(de.get('admin_idx'))
        myAdmin = admins.objects.filter(id=ppk)
        Searach_query_shares = serializers.serialize("json", myAdmin)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"mypg_admin": "failed"})


#개발자 Admin에 추가적인 정산이 가해짐
@csrf_exempt
def jeongsan(request):
    if request.method == 'POST':
        Users = User_In.objects.all()
        for u in Users:
            Asset_of_that_user = Asset.objects.get(user_idx=u)
            Profit.objects.create(
                user_idx=u,
                Total_Estimated_Profit_From_Stocks=Asset_of_that_user.Estimated_Profit,
                Total_Realized_Profit=Asset_of_that_user.Realized_Profit,
                Real_Profit_Today=Asset_of_that_user.Total_Profit,
            )
            # TOTAL_PROFIT_BY_NOW=총손익" - Auto Save
            # Asset_of_that_user.Estimated_Profit = 0
            # Asset_of_that_user.Total_Profit = 0
            Asset_of_that_user.poured_money += Asset_of_that_user.Realized_Profit
            Asset_of_that_user.Realized_Profit = 0
            Asset_of_that_user.save()
        return JsonResponse({"jeongsan": "succeed"})
    else:
        return JsonResponse({"jeongsan": "failed"})


@csrf_exempt
def admin_out_Partner(request):

    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        ppk = int(de.get('admin_idx'))
        user_id = de.get('user_id') #출금을 요청받은 partner의 id (idx가 아니다)
        quantity = float(de.get('q'))

        adminObj = admins.objects.get(id=ppk)
        grant = adminObj.grant
        if grant != 0:
            return JsonResponse({"msg": "출금 권한이 없습니다", "code": 0})
        elif grant == 0:
            partner_obj = admins.objects.get(admin_id=user_id)

            if Profit_Stat_Partner.objects.filter(admin_idx=partner_obj):
                partner_profit_row = Profit_Stat_Partner.objects.filter(admin_idx=partner_obj).latest('day')
                partner_profit_row.partner_out += quantity
                #partner_profit_row.regular_total_jeongsan -= quantity
                partner_profit_row.save()
                return JsonResponse({"msg": "출금 처리 완료", "code": 1})
            else:
                return JsonResponse({"msg": "해당 파트너의 정산 기록이 아직 없습니다", "code": 2})
    return


@csrf_exempt
def JeongSan_Partner(request):
    #파트너 정산. Profit_Stat에 반영, M_P_Managment에 기록
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        ppk = int(de.get('admin_idx'))
        user_id = de.get('user_id') #출금을 요청받은 partner의 id (idx가 아니다)
        i = admins.objects.get(admin_id=user_id)
        p_jeongsan_summation = 0

        adminObj = admins.objects.get(id=ppk)
        grant = adminObj.grant
        if grant != 0:
            return JsonResponse({"msg": "정산 권한이 없습니다"})
        elif grant == 0:
            ps_obj = Profit_Stat_Partner.objects.filter(admin_idx=i).latest('day')
            p_jeongsan = ps_obj.regular_total_jeongsan
            p_jeongsan_summation += p_jeongsan
            M_P_managementList.objects.create(admin_idx=i, jeongsan=p_jeongsan)
            ps_obj.regular_total_jeongsan = 0
            ps_obj.save()

            obj = Profit_Stat.objects.all().latest('day')
            obj.partner_jeongsan_d = p_jeongsan_summation
            obj.save()
            return JsonResponse({"msg": "정산 되었습니다"})
"""
        partner_list = admins.objects.all().exclude(grant=0)
        p_jeongsan_summation = 0
        for i in partner_list:
            ps_obj = Profit_Stat_Partner.objects.filter(admin_idx=i).latest('day')
            p_jeongsan = ps_obj.regular_total_jeongsan
            p_jeongsan_summation += p_jeongsan
            M_P_managementList.objects.create(admin_idx=i, jeongsan=p_jeongsan)
            ps_obj.regular_total_jeongsan = 0
            ps_obj.save()
            # 새 정산 세션을 위한 준비 공사 (완료 - 테스트 필요)
            # Profit_Stat에 반영을 위한 준비 공사 (완료 - 테스트 필요)
        obj = Profit_Stat.objects.all().latest('day')
        obj.partner_jeongsan_d = p_jeongsan_summation
        obj.save()
        return JsonResponse({"jeongsan_p": "succeed"})
    else:
        return JsonResponse({"jeongsan_p": "failed"})
"""

@csrf_exempt
def JeongSan_Company(request):
    if request.method == 'POST':

        Money_I_today = Deposit_Withdraw_Order_Done_List.day_m_i()
        Money_O_today = Deposit_Withdraw_Order_Done_List.day_m_o()

        print(Money_I_today)

        timestamp = time.time()
        dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
        kmt = dt_utc + timedelta(hours=9)
        kmt = str(kmt)
        kmt = kmt.split(' ')
        today_dates = kmt[0]

        obj = Profit_Stat.objects.all().latest('day')

        this_dates = obj.day
        this_dates = str(this_dates)
        this_dates = this_dates.split(' ')
        this_dates = this_dates[0]

        if this_dates != today_dates:
            # create Profit_stat
            Profit_Stat.objects.create(day_In=Money_I_today, day_Out=Money_O_today)
            obj = Profit_Stat.objects.all().latest('day')
            # update Profit_stat according to all rest of factors
            admin_in_d = Admin_M_IO.day_m_i_admin()
            admin_out_d = Admin_M_IO.day_m_o_admin()
            partner_jeongsan_d = M_P_managementList.day_m_o_partner()
            new_user_d = User_In.day_number_of_signed_in()

            obj.admin_in_d = admin_in_d
            obj.admin_out_d = admin_out_d
            obj.partner_jeongsan_d = partner_jeongsan_d
            obj.new_user_d = new_user_d

            partner_list = admins.objects.all().exclude(grant=0)
            for i in partner_list:
                Profit_Stat_Partner.objects.create(admin_idx=i, day_In=admin_in_d, day_Out=admin_out_d)
                # 주의: day_In, Out은 외부에서 입력을 받아야 한다. 계산 효율을 높이기 위함 (한번에 처리)
                #Profit_Stat_Partner를 매일 추가

            obj.save()
        else:
            obj.day_In = Money_I_today
            obj.day_Out = Money_O_today
            # update Profit_stat
            admin_in_d = Admin_M_IO.day_m_i_admin()
            admin_out_d = Admin_M_IO.day_m_o_admin()
            partner_jeongsan_d = M_P_managementList.day_m_o_partner()
            new_user_d = User_In.day_number_of_signed_in()

            obj.admin_in_d = admin_in_d
            obj.admin_out_d = admin_out_d
            obj.partner_jeongsan_d = partner_jeongsan_d
            obj.new_user_d = new_user_d

            partner_list = admins.objects.all().exclude(grant=0)
            for i in partner_list:
                ps_obj = Profit_Stat_Partner.objects.filter(admin_idx=i).latest('day')
                ps_obj.day_In = admin_in_d
                ps_obj.admin_out_d = admin_out_d
                ps_obj.save()

            obj.save()

        return JsonResponse({"jeongsan_c": "succeed"})


@csrf_exempt
def users_list(request):
    if request.method == 'POST':

        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        pg = de.get('pg')

        userDict = {}
        accessed_user_list = []
        accessed_users = accessed_user.objects.all().order_by('-access_time')
        USER_LIST = []
        for i in accessed_users:
            user_idx_obj = i.user_idx
            user_idx = user_idx_obj.user_idx
            hisAsset = Asset.objects.get(user_idx=user_idx_obj)
            total_profit = 0
            profits = Profit.objects.filter(user_idx=user_idx_obj)
            if profits:
                hisProfit = profits.latest('Date_jeong_san')
                total_profit = hisProfit.TOTAL_PROFIT_BY_NOW
            NumOfTransaction = Transaction.objects.filter(user_idx=user_idx_obj).exclude(TreatStatus=-1).count()
            M_in = 0
            M_out = 0
            M_i_num = 0
            loan = 0
            for x in Deposit_Withdraw_Order_Done_List.objects.filter(user_idx=user_idx_obj):
                if x.Order == 2 and x.PlusMinus != 0:
                    M_in += x.PlusMinus
                    M_i_num += 1
                elif x.Order == 3 and x.PlusMinus != 0:
                    M_out -= x.PlusMinus
            for x in Loan_Order_Done.objects.filter(user_idx=user_idx_obj):
                if x.Is_Done:
                    loan += x.Stock_Loan_Rate * x.Dam_bo_geum
            hisHoldings = Holdings.objects.filter(user_idx=user_idx_obj)
            ovn = 0
            for x in hisHoldings:
                if x.OverNight_Quant > 0:
                    ovn += 1
            userDict = {'idx': user_idx, 'is_accessed': 1, 'id': user_idx_obj.user_id,
                                  'actual_m': hisAsset.Actual_money_by_now, 'profit': total_profit,
                                  'num_of_trans': NumOfTransaction, 'M_in': M_in, 'M_out': M_out, 'M_i_num': M_i_num,
                                  'loan': loan, 'ovn': ovn, 'signin_domain': user_idx_obj.signin_domain,
                                  'signin_date': str(user_idx_obj.init_signed_in_date),
                        'shut_down': user_idx_obj.shut_down}
            USER_LIST.append(userDict)
            accessed_user_list.append(user_idx)
        rest_of_users = User_In.objects.all().exclude(user_idx__in=accessed_user_list)


        for i in rest_of_users:
            user_idx_obj = i
            user_idx = i.user_idx
            hisAsset = Asset.objects.get(user_idx=user_idx_obj)
            total_profit = 0
            profits = Profit.objects.filter(user_idx=user_idx_obj)
            if profits:
                hisProfit = profits.latest('Date_jeong_san')
                total_profit = hisProfit.TOTAL_PROFIT_BY_NOW

            NumOfTransaction = Transaction.objects.filter(user_idx=user_idx_obj).exclude(TreatStatus=-1).count()
            M_in = 0
            M_out = 0
            M_i_num = 0
            loan = 0
            for x in Deposit_Withdraw_Order_Done_List.objects.filter(user_idx=user_idx_obj):
                if x.Order == 2 and x.PlusMinus != 0:
                    M_in += x.PlusMinus
                    M_i_num += 1
                elif x.Order == 3 and x.PlusMinus != 0:
                    M_out -= x.PlusMinus
            for x in Loan_Order_Done.objects.filter(user_idx=user_idx_obj):
                if x.Is_Done :
                    loan += x.Stock_Loan_Rate * x.Dam_bo_geum
            hisHoldings = Holdings.objects.filter(user_idx=user_idx_obj)
            ovn = 0
            for x in hisHoldings:
                if x.OverNight_Quant > 0:
                    ovn += 1
            userDict = {'idx': user_idx, 'is_accessed': 0, 'id': user_idx_obj.user_id,
                                  'actual_m': hisAsset.Actual_money_by_now, 'profit': total_profit,
                                  'num_of_trans': NumOfTransaction, 'M_in': M_in, 'M_out': M_out, 'M_i_num': M_i_num,
                                  'loan': loan, 'ovn': ovn, 'signin_domain': user_idx_obj.signin_domain,
                                  'signin_date': str(user_idx_obj.init_signed_in_date),
                        'shut_down': user_idx_obj.shut_down}
            USER_LIST.append(userDict)

        total_users = User_In.objects.all()
        paginator = Paginator(total_users, 10)
        print(USER_LIST)

        """
        try:
            contacts = paginator.page(pg)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        """

        if pg != paginator.num_pages:
            USER_LIST = USER_LIST[(pg-1)*10: (pg-1)*10 + 10]
        elif pg == paginator.num_pages:
            USER_LIST = USER_LIST[(pg-1)*10:]
        #Searach_query_shares = serializers.serialize("json", contacts)
        Searach_query_shares = json.dumps(USER_LIST) + "#" + str(paginator.num_pages)
        return JsonResponse(Searach_query_shares, safe=False)
    return JsonResponse({"users_info": "failed"})

@csrf_exempt
def mypg(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx_num = de.get('user_idx')

        s_Entries = User_In.objects.filter(user_idx=user_idx_num)
        Searach_query_shares = serializers.serialize("json", s_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"mypg": "failed"})

@csrf_exempt
def show_top_kospi(request):
    if request.method == 'POST':
        s_Entries = Top_Kospi.objects.all().order_by('ranking')
        Searach_query_shares = serializers.serialize("json", s_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    return

@csrf_exempt
def show_top_kosdq(request):
    if request.method == 'POST':
        s_Entries = Top_Kosdq.objects.all().order_by('ranking')
        Searach_query_shares = serializers.serialize("json", s_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    return

@csrf_exempt
def show_top_coin(request):
    s_Entries = Top_Coins.objects.all().order_by('ranking')
    Searach_query_shares = serializers.serialize("json", s_Entries)
    return JsonResponse(Searach_query_shares, safe=False)


@csrf_exempt
def set_interest(request):
    if request.method == 'POST':
        print(request)
        de = request.POST.dict()
        print(de)
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx')) #User_Decider  # get current user id
        user_idx = User_In.objects.get(user_idx=user_idx) #foreign k
        #group_name = de.get('g_name')
        gid = int(de.get('g_pk'))
        group_name = Share_Groups_Per_User.objects.get(id=gid)
        #group_name = Share_Groups_Per_User.objects.get(user_idx=user_idx, interest_group=group_name) #foreign k

        spk = int(de.get('spk'))

        """
        sct = de.get('sct')
        scd = de.get('scd')
        sname = de.get('sname')
        """

        sobj = Entire_Shares.objects.get(id=spk)
        # Share_Interest.delete()

        Share_Interest_Add_Obj = Share_Interest.objects.create(
            user_idx=user_idx,
            interest_group=group_name,
            Share_idx=sobj,
            Share_Category=sobj.Share_Category,
            Share_Code=sobj.Share_Code,
            Share_Name=sobj.Share_Name,
        )
        Share_Interest_Add_Obj.save()
        Share_Interest_Entries = Share_Interest.objects.filter(user_idx=user_idx)
        Searach_query_shares = serializers.serialize("json", Share_Interest_Entries)
        return JsonResponse(Searach_query_shares, safe=False) #JsonResponse({"set_interestgroup": "true"})
        #return JsonResponse({"0": "true"})
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def set_interestgroup(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx'))
        group_name = de.get('g_name')

        #user_idx=User_In.objects.get(user_idx=user_idx).user_idx,
        #user_idx=user_idx

        one_Entry = User_In.objects.get(user_idx=user_idx)
        #user_idx = one_Entry.user_idx
        if Share_Groups_Per_User.objects.filter(user_idx=one_Entry, interest_group=group_name):
            return JsonResponse({"dup": "1"})
        else:
            Add_Empty_Share_group = Share_Groups_Per_User.objects.create(
                user_idx=one_Entry,
                interest_group=group_name,
            )
            Add_Empty_Share_group.save()
        Share_Interestgroup_Entries = Share_Groups_Per_User.objects.filter(user_idx=one_Entry)
        #should use 'only' function - serialize function
        #print(Share_Interestgroup_Entries, '<-Entries')
        Searach_query_shares = serializers.serialize("json", Share_Interestgroup_Entries)
        return JsonResponse(Searach_query_shares, safe=False) #JsonResponse({"set_interestgroup": "true"})
        #JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"set_interestgroup": "false"})


@csrf_exempt
def show_interest(request):
        if request.method == 'POST':
            de = request.POST.dict()
            de = list(de.keys())[list(de.values()).index('')]
            de = ast.literal_eval(de)
            user_idx = de.get('user_idx')
            user_idx = User_In.objects.get(user_idx=user_idx)
            interest_group = de.get('g_name')

            group_obj = Share_Groups_Per_User.objects.get(user_idx=user_idx, interest_group=interest_group)
            Share_Interest_Entries = Share_Interest.objects.filter(user_idx=user_idx, interest_group=group_obj)#F
            Searach_query_shares = serializers.serialize("json", Share_Interest_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
        else:
            return JsonResponse({"1": "false"})


@csrf_exempt
def show_interestgroup(request):
        if request.method == 'POST':
            de = request.POST.dict()
            de = list(de.keys())[list(de.values()).index('')]
            de = ast.literal_eval(de)
            user_idx = de.get('user_idx')
            Share_Interest_Entries = Share_Groups_Per_User.objects.filter(user_idx=user_idx)  # F
            Searach_query_shares = serializers.serialize("json", Share_Interest_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
        else:
            return JsonResponse({"1": "false"})

@csrf_exempt
def show_loan(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        user_idx = User_In.objects.get(user_idx=user_idx)
        Share_Interest_Entries = Loan_Order_Done.objects.filter(user_idx=user_idx).order_by('-Order_Date')  # F
        Searach_query_shares = serializers.serialize("json", Share_Interest_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})

@csrf_exempt
def show_loan_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        user_idx = User_In.objects.get(user_idx=user_idx)
        Share_Interest_Entries = Loan_Order_Done.objects.filter(user_idx=user_idx).order_by('-Order_Date')  # F
        Searach_query_shares = serializers.serialize("json", Share_Interest_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})

@csrf_exempt
def unset_interest(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx')) #User_Decider  # get current user id
        user_idx = User_In.objects.get(user_idx=user_idx) #foreign k
        #group_name = de.get('g_name')
        gid = int(de.get('g_pk'))
        #group_name = Share_Groups_Per_User.objects.get(user_idx=user_idx, interest_group=group_name) #foreign k
        group_name = Share_Groups_Per_User.objects.get(id=gid)
        spk = int(de.get('spk'))

        """
        sct = de.get('sct')
        scd = de.get('scd')
        sname = de.get('sname')
        """
        sobj = Entire_Shares.objects.get(id=spk)
        Share_Interest_Delete_Obj = Share_Interest.objects.get(
            user_idx=user_idx,
            interest_group=group_name,
            Share_idx=sobj
        )
        Share_Interest_Delete_Obj.delete()
        Share_Interest_Entries = Share_Interest.objects.filter(user_idx=user_idx)
        Searach_query_shares = serializers.serialize("json", Share_Interest_Entries)
        return JsonResponse(Searach_query_shares, safe=False) #JsonResponse({"set_interestgroup": "true"})
        #return JsonResponse({"del_interest": "true"})
    else:
        return JsonResponse({"del_interest": "false"})


@csrf_exempt
def unset_interest_group(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx'))
        group_name = de.get('g_name')

        #user_idx=User_In.objects.get(user_idx=user_idx).user_idx,
        #user_idx=user_idx

        one_Entry = User_In.objects.get(user_idx=user_idx)
        #user_idx = one_Entry.user_idx
        Del_Empty_Share_group = Share_Groups_Per_User.objects.get(
            user_idx=one_Entry,
            interest_group=group_name,
        )
        Del_Empty_Share_group.delete()
        Share_Interestgroup_Entries = Share_Groups_Per_User.objects.filter(user_idx=one_Entry)
        #should use 'only' function - serialize function
        #print(Share_Interestgroup_Entries, '<-Entries')
        Searach_query_shares = serializers.serialize("json", Share_Interestgroup_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
        #return JsonResponse({"del_interestgroup": "true"})
    else:
        return JsonResponse({"set_interestgroup": "false"})

"""
    path('api/moneyin', moneyin, name='4_moneyin'),
    path('api/moneyout', moneyout, name='4_moneyout'),
    path('api/loan', loan, name='5_loan'),
    path('api/orderBuy', orderBuy, name='6_orderBuy'),
    path('api/orderSell', orderSell, name='7_orderSell'),
    path('api/ovn', ovn, name='8_ovn'),
    
"""
"""
user_idx = models.ForeignKey(
'User_In',
on_delete=models.CASCADE,
)
Share_idx = models.ForeignKey(
'Entire_Shares',
on_delete=models.CASCADE,
)
TransDateTime = models.DateTimeField(auto_created=True, null=True)
Order_Type = models.IntegerField(default=0) #0:byorder, 1:sellorder, 2:deposit order, 3:withdraw order,
TreatStatus = models.IntegerField(default=0) #0:byDone, 1:sellDone, 2:depositDone, 3:withdrawDone,

Order_Quant = models.IntegerField(default=0)
Order_Price = models.IntegerField(default=0)

Trans_Quant = models.IntegerField(default=0)
Trans_Price = models.IntegerField(default=0)

Fee_In_Trans = models.IntegerField(default=0)
Selling_Profit = models.IntegerField(default=0) # = Estimated_Profit in Stock Transactions
Realized_Profit = models.IntegerField(default=0) # Selling_Profit- Fee_In_Trans

Doposit_Money = models.IntegerField(default=0)

#Ref - Actual_money_by_now in 'Asset'
Actual_money = models.ForeignKey(
'Asset',
on_delete=models.CASCADE,
)


"""


############################################PHASE TWO################################################

@csrf_exempt
def moneyin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx'))
        moneyin = float(de.get('moneyin'))


        #user_idx=User_In.objects.get(user_idx=user_idx).user_idx,
        #user_idx=user_idx

        one_Entry = User_In.objects.get(user_idx=user_idx)
        #user_idx = one_Entry.user_idx
        hisAsset = ''

        hisAsset = Asset.objects.get(user_idx=one_Entry)
        money_in_req_Trans = Transaction.objects.create(
            user_idx=one_Entry,
            Share_idx=Entire_Shares.objects.get(Share_Category=-1),
            Order_Type=2,
            Order_Quant=0,
            Order_Price=0,
            Trans_Quant=0,
            Trans_Price=0,
            Fee_In_Trans=0,
            Selling_Profit=0,  # = Estimated_Profit in Stock Transactions
            Realized_Profit=0,  # Selling_Profit- Fee_In_Trans
            Deposit_Money=moneyin,
            Actual_money=hisAsset,
        )
        money_in_req_Trans.save()
        Deposit_Withdraw_Order_Done_List.objects.create(
            user_idx=one_Entry,
            Transaction_idx=money_in_req_Trans,
            Order=2,
            Order_Money_Plus_Minus=moneyin,
            PlusMinus=0,
        )
        money_in_Entries = Deposit_Withdraw_Order_Done_List.objects.filter(user_idx=one_Entry)
        Searach_query_shares = serializers.serialize("json", money_in_Entries)
        return JsonResponse({"Actual_Money": hisAsset.Actual_money_by_now, 'moneyin':moneyin})
        #return JsonResponse({"del_interestgroup": "true"})
    else:
        return JsonResponse({"set_interestgroup": "false"})


@csrf_exempt
def moneyout(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx'))
        moneyout = float(de.get('moneyout'))


        #user_idx=User_In.objects.get(user_idx=user_idx).user_idx,
        #user_idx=user_idx

        one_Entry = User_In.objects.get(user_idx=user_idx)
        #user_idx = one_Entry.user_idx
        hisAsset = ''

        hisAsset = Asset.objects.get(user_idx=one_Entry)
        money_out_req_Trans = Transaction.objects.create(
            user_idx=one_Entry,
            Share_idx=Entire_Shares.objects.get(Share_Category=-1),
            Order_Type=3,
            Order_Quant=0,
            Order_Price=0,
            Trans_Quant=0,
            Trans_Price=0,
            Fee_In_Trans=0,
            Selling_Profit=0,  # = Estimated_Profit in Stock Transactions
            Realized_Profit=0,  # Selling_Profit- Fee_In_Trans
            Deposit_Money=-moneyout,
            Actual_money=hisAsset,
        )
        money_out_req_Trans.save()
        money_out_req = Deposit_Withdraw_Order_Done_List.objects.create(
            user_idx=one_Entry,
            Transaction_idx=money_out_req_Trans,
            Order=3,
            Order_Money_Plus_Minus=-moneyout,
            PlusMinus=0,
        )
        money_out_req.save()
        money_out_Entries = Deposit_Withdraw_Order_Done_List.objects.filter(user_idx=one_Entry)
        Searach_query_shares = serializers.serialize("json", money_out_Entries)
        return JsonResponse({"Actual_Money": hisAsset.Actual_money_by_now, 'moneyout':moneyout})
        #return JsonResponse({"del_interestgroup": "true"})
    else:
        return JsonResponse({"set_interestgroup": "false"})

"""
    Stock_Loan_Rate = models.IntegerField(default=0) #Loan Rate
    Dam_bo_geum = models.IntegerField(default=0)
    #50, 100, 200, 300, 500, 1000, 2000, 3000 : 15%
    #Actual Money by now - 15% of Dam_bo_geum = losscut margin - if the user loose all those margin,
    # the system will sell out all the stocks the user has
    Is_Done = models.BooleanField(default=False) #if it is true, that means the order was treated properly
    Order_Date = models.DateTimeField(auto_created=True, auto_now=True)
    Done_Date = models.DateTimeField(auto_created=True, auto_now=True)
"""

@csrf_exempt
def loan(request):

    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx'))
        Dam_bo_geum = de.get('dam_bo')
        Stock_Loan_Rate = de.get('rate')
        #Done_Date

        one_Entry = User_In.objects.get(user_idx=user_idx)
        #user_idx = one_Entry.user_idx
        hisAsset = Asset.objects.get(user_idx=User_In.objects.get(user_idx=user_idx))
        if hisAsset.Actual_money_by_now < hisAsset.Dam_bo_geum:
            return JsonResponse({"set_loan": "잔고가 부족하여 담보금을 한도를 초과하였습니다"})

        loanReq = Loan_Order_Done.objects.create(
            user_idx=one_Entry,
            Dam_bo_geum=Dam_bo_geum,
            Stock_Loan_Rate=Stock_Loan_Rate,
        )
        #loanReq.save()
        loan_Entries = Loan_Order_Done.objects.filter(user_idx=one_Entry)
        #should use 'only' function - serialize function
        #print(Share_Interestgroup_Entries, '<-Entries')
        Searach_query_shares = serializers.serialize("json", loan_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
        #return JsonResponse({"del_interestgroup": "true"})
    else:
        return JsonResponse({"set_loan": "false"})


@csrf_exempt
def orderBuy(request):

    Hour = float(Clock.Clock()[0])
    Min = float(Clock.Clock()[1])
    Hour += Min/60
    day = Day.Day()

    #print(((not(Hour > 15.5)) and (not int(Hour) < 9)))
    isExClosed = (MarketStatus.objects)

    isExClosed = isExClosed.values()[0]["is_market_exceptionally_closed"]
    isTest = True #isExClosed.values()[0]["Is_Testing_Buy_Sell"]


    #A = True
    #(((not(Hour > 15.3)) and (not int(Hour) < 9) and not isExClosed) and day != 'Sun' and day != 'Sat'):
    if (((not(Hour > 15.3)) and (not int(Hour) < 9) and not isExClosed) and day != 'Sun' and day != 'Sat') or isTest:

        if request.method == 'POST':
            de = request.POST.dict()
            de = list(de.keys())[list(de.values()).index('')]
            de = ast.literal_eval(de)
            user_idx = int(de.get('user_idx'))
            sid = de.get('spk')
            q = float(de.get('q'))
            p = float(de.get('p'))

            # user_idx=User_In.objects.get(user_idx=user_idx).user_idx,
            # user_idx=user_idx

            Share_idx = Entire_Shares.objects.get(id=sid)

            one_Entry = User_In.objects.get(user_idx=user_idx)
            hisAsset = Asset.objects.get(user_idx=one_Entry)

            num_of_his_holdings = Holdings.objects.filter(user_idx=one_Entry).count()
            if num_of_his_holdings >= 10:
                return JsonResponse({"buyorder": "보유 종목은 최대 10종목 까지만 가능 합니다."})

            if hisAsset.available_money >= q * p:
                order = Transaction.objects.create(
                    user_idx=one_Entry,
                    Share_idx=Share_idx,
                    Order_Type=0,
                    Order_Quant=q,
                    Order_Price=p,
                    Trans_Quant=0,
                    Trans_Price=0,
                    Fee_In_Trans=0,
                    Selling_Profit=0,  # = Estimated_Profit in Stock Transactions
                    Realized_Profit=0,  # Selling_Profit- Fee_In_Trans
                    Deposit_Money=0,
                    Actual_money=hisAsset,
                )
                #order.save()
                #send_order_q = OrderQ.objects.create(TransId=order)
                #send_order_q.save()

                List_Not_Done.objects.create(
                    user_idx=one_Entry,
                    Share_idx=Share_idx,
                    Transaction_idx=order,
                    Order_Type=0,
                    Order_Price=p,
                    Order_Quant=q,
                    Is_Cancelled=False,
                )

            else:
                return JsonResponse({"buyorder": "잔고가 부족합니다"})

            time.sleep(1)

            holdings_Entries = Holdings.objects.filter(user_idx=one_Entry)
            # should use 'only' function - serialize function
            # print(Share_Interestgroup_Entries, '<-Entries')
            Searach_query_shares = serializers.serialize("json", holdings_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
            # return JsonResponse({"del_interestgroup": "true"})
        else:
            return JsonResponse({"buyorder": "false"})
    else:
        return JsonResponse({"buyorder": "장 시간이 아닙니다"})


@csrf_exempt
def orderSell(request):
    Hour = float(Clock.Clock()[0])
    Min = float(Clock.Clock()[1])
    Hour += Min/60
    day = Day.Day()

    #print(((not(Hour > 15.5)) and (not int(Hour) < 9)))
    isExClosed = (MarketStatus.objects)
    isExClosed = isExClosed.values()[0]["is_market_exceptionally_closed"]
    isTest = True #isExClosed.values()[0]["Is_Testing_Buy_Sell"]

    #A = True
    #(((not(Hour > 15.3)) and (not int(Hour) < 9) and not isExClosed) and day != 'Sun' and day != 'Sat')
    if (((not(Hour > 15.3)) and (not int(Hour) < 9) and not isExClosed) and day != 'Sun' and day != 'Sat') or isTest:
        if request.method == 'POST':
            de = request.POST.dict()
            de = list(de.keys())[list(de.values()).index('')]
            de = ast.literal_eval(de)

            #for 'pk'

            user_idx = int(de.get('user_idx'))
            sid = de.get('spk')
            q = float(de.get('q'))
            p = float(de.get('p'))

            # user_idx=User_In.objects.get(user_idx=user_idx).user_idx,
            # user_idx=user_idx

            Share_idx = Entire_Shares.objects.get(id=sid)

            one_Entry = User_In.objects.get(user_idx=user_idx)
            hisAsset = Asset.objects.get(user_idx=one_Entry)

            hisHoldings = Holdings.objects.get(user_idx=one_Entry, Share_idx=Share_idx)

            if q <= hisHoldings.Holding_Quantities:
                order = Transaction.objects.create(
                    user_idx=one_Entry,
                    Share_idx=Share_idx,
                    Order_Type=1,
                    Order_Quant=q,
                    Order_Price=p,
                    Trans_Quant=0,
                    Trans_Price=0,
                    Fee_In_Trans=0,
                    Selling_Profit=0,  # = Estimated_Profit in Stock Transactions
                    Realized_Profit=0,  # Selling_Profit- Fee_In_Trans
                    Deposit_Money=0,
                    Actual_money=hisAsset,
                )
                #order.save()
                #send_order_q = OrderQ.objects.create(TransId=order)
                #send_order_q.save()

                List_Not_Done.objects.create(
                    user_idx=one_Entry,
                    Share_idx=Share_idx,
                    Transaction_idx=order,
                    Order_Type=1,
                    Order_Price=p,
                    Order_Quant=q,
                    Is_Cancelled=False,
                )
            else:
                return JsonResponse({"sellorder": "보유 수량이 부족 합니다", "holdQ": hisHoldings.Holding_Quantities})
            time.sleep(1)

            holdings_Entries = Holdings.objects.filter(user_idx=one_Entry)
            # should use 'only' function - serialize function
            # print(Share_Interestgroup_Entries, '<-Entries')
            Searach_query_shares = serializers.serialize("json", holdings_Entries)
            return JsonResponse(Searach_query_shares, safe=False)
            # return JsonResponse({"del_interestgroup": "true"})
        else:
            return JsonResponse({"sellorder": "false"})
    else:
        return JsonResponse({"sellorder": "장 시간이 아닙니다"})


@csrf_exempt
def show_info(request):
    if request.method == 'POST':
        if info.objects.all():
            objs = info.objects.all().order_by('-id')
            Searach_query_shares = serializers.serialize("json", objs)
            return JsonResponse(Searach_query_shares, safe=False)

@csrf_exempt
def show_popup(request):
    if request.method == 'POST':
        if info.objects.all():
            obj = info.objects.filter(is_pop=True).order_by('-id')[0]

            return JsonResponse({"title": obj.title, "contents": obj.contents, "dtime": str(obj.dtime)})
        return
    return

@csrf_exempt
def showTrans_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        pg = de.get('pg')
        user_idx = User_In.objects.get(user_idx=user_idx)

        #CheoriS = Entire_Shares.objects.get(Share_Category=-1)
        #CheoriS2 = Entire_Shares.objects.get(Share_Category=-2)

        TransEntries = Transaction.objects.filter(user_idx=user_idx).exclude(Order_Type=2).exclude(Order_Type=3)  # F
        TransEntries = TransEntries.order_by('-TransDateTime')

        paginator = Paginator(TransEntries, 10)

        try:
            contacts = paginator.page(pg)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        Searach_query_shares = serializers.serialize("json", contacts)
        Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showTrans(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        pg = de.get('pg')
        user_idx = User_In.objects.get(user_idx=user_idx)

        #CheoriS = Entire_Shares.objects.get(Share_Category=-1)
        #CheoriS2 = Entire_Shares.objects.get(Share_Category=-2)

        TransEntries = Transaction.objects.filter(user_idx=user_idx).exclude(Order_Type=2).exclude(Order_Type=3)  # F
        TransEntries = TransEntries.order_by('-TransDateTime')

        paginator = Paginator(TransEntries, 10)

        try:
            contacts = paginator.page(pg)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        Searach_query_shares = serializers.serialize("json", contacts)
        Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showHoldings_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Holding_Entries = Holdings.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Holding_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showHoldings(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Holding_Entries = Holdings.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Holding_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


#회원의 일별 수익 정산 리스트를 반환한다. (Profit 테이블)
@csrf_exempt
def showProfit_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Profit_Entries = Profit.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Profit_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showProfit(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Profit_Entries = Profit.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Profit_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showNot_List_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Not_List_Entries = List_Not_Done.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Not_List_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showNot_List(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Not_List_Entries = List_Not_Done.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Not_List_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showAsset_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Asset_Entries = Asset.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Asset_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def showAsset(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        one_Entity = User_In.objects.get(user_idx=user_idx)
        Asset_Entries = Asset.objects.filter(user_idx=one_Entity)
        Searach_query_shares = serializers.serialize("json", Asset_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def show_M_io_Admin(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        pg = de.get('pg')

        one_Entity = User_In.objects.get(user_idx=user_idx)
        M_io_Entries = Deposit_Withdraw_Order_Done_List.objects.filter(user_idx=one_Entity).order_by('-TransDateTime')

        paginator = Paginator(M_io_Entries, 10)

        try:
            contacts = paginator.page(pg)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        Searach_query_shares = serializers.serialize("json", contacts)
        Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def show_M_io(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = de.get('user_idx')
        pg = de.get('pg')

        one_Entity = User_In.objects.get(user_idx=user_idx)
        M_io_Entries = Deposit_Withdraw_Order_Done_List.objects.filter(user_idx=one_Entity).order_by('-TransDateTime')

        paginator = Paginator(M_io_Entries, 10)

        try:
            contacts = paginator.page(pg)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)

        Searach_query_shares = serializers.serialize("json", contacts)
        Searach_query_shares = Searach_query_shares + "#" + str(paginator.num_pages)
        return JsonResponse(Searach_query_shares, safe=False)
    else:
        return JsonResponse({"1": "false"})


@csrf_exempt
def spk_to_name(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        sid = de.get('spk')

        print(sid)

        Share_Entity = Entire_Shares.objects.get(id=sid)

        sname = Share_Entity.Share_Name
        return JsonResponse({'spk': sid, 'sname': sname })

@csrf_exempt
def scd_to_name(request):
    if request.method == 'POST':
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        sid = de.get('scd')

        print(sid)

        Share_Entity = Entire_Shares.objects.get(Share_Code=sid)

        sname = Share_Entity.Share_Name
        return JsonResponse({'scd': sid, 'sname': sname })


#Sell 때 오버나잇은 모두 해제. 추가 설정 땐 DB의 오버나잇 수량을 이용하여 롤백 후 재계산
@csrf_exempt
def ovn(request):
    if request.method == 'POST':
        Hour = float(Clock.Clock()[0])
        Min = float(Clock.Clock()[1])
        Hour += Min / 60

        #A = False
        #not ((not (Hour > 15.2)) and (not int(Hour) < 9))
        if not ((not (Hour > 15.2)) and (not int(Hour) < 9)):
            return JsonResponse({"holding_ovn": "오버나잇 가능 시간이 아닙니다"})
        de = request.POST.dict()
        de = list(de.keys())[list(de.values()).index('')]
        de = ast.literal_eval(de)
        user_idx = int(de.get('user_idx'))
        sid = int(de.get('spk'))
        #de.get('ovnq')
        #one calling

        Share_Entity = Entire_Shares.objects.get(id=sid)
        one_Entry = User_In.objects.get(user_idx=user_idx)
        ovnq = Holdings.objects.get(user_idx=one_Entry, Share_idx=Share_Entity).Holding_Quantities
        #user_idx = one_Entry.user_idx
        holding_Entity = Holdings.objects.get(user_idx=one_Entry, Share_idx=Share_Entity)
        holding_Entity.OverNight_Quant = ovnq #need some rollback rpoc when applying new ovn
        holding_Entity.OverNight_Rest_Days -= 1
        if holding_Entity.OverNight_Rest_Days < 0:
            return JsonResponse({"holding_ovn": "오버나잇 설정은 연속30회만 가능합니다"})
        holding_Entity.save()
        holding_Entries = Holdings.objects.filter(user_idx=one_Entry)
        #should use 'only' function - serialize function
        #print(Share_Interestgroup_Entries, '<-Entries')
        Searach_query_shares = serializers.serialize("json", holding_Entries)
        return JsonResponse(Searach_query_shares, safe=False)
        #return JsonResponse({"del_interestgroup": "true"})
    else:
        return JsonResponse({"holding_ovn": "false"})
