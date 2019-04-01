from __future__ import absolute_import
from django.contrib import admin
from .models import *
from .consumers import *
import cryptocompare
from .views import *
from django.utils import timezone
# Register your models here.
from django.db.models import Q
#from datetime import timezone, timedelta, datetime, date
import pandas as pd
import requests
from datetime import datetime as dt

#회원 가입 요청 테이블에서 선택된 항의 회원가입 요청을 처리한다 (회원가입 요청 테이블에서 해당 행을 제거하고
#회원목록에 회원 정보를 생성한다)
def Allow_Signin(modeladmin, request, queryset):
    for object in queryset:
        tempObj = User_In.objects.create(
            user_idx=object.user_idx,
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

    queryset.delete()
Allow_Signin.short_description = "회원 가입을 수락"

#코인들의 정보를 담고 있는 리스트를 반환하는 함수.
def getCoinList():
    req = requests.get('https://www.cryptocompare.com/api/data/coinlist/').json()
    info = req['Data']
    coinList = pd.DataFrame(info)
    coinList = coinList.transpose()
    coinList.to_csv('coinList.csv')
    return coinList

def Coins_Init(modeladmin, request, queryset):

    A = getCoinList()
    CoinNameList = A['CoinName']

    coins = cryptocompare.get_coin_list(format=True)
    print(coins)
    for x in coins:
        if Entire_Shares.objects.filter(Share_Code=x, Share_Category=1):
            coin = Entire_Shares.objects.get(Share_Code=x, Share_Category=1)
            coin.Share_Name = CoinNameList[x]
            coin.save()
        else:
            Entire_Shares.objects.create(
                Share_Code=x,
                Share_Category=1,
                Share_Name=x,
                Is_feasible=True
            )
#해당 액션 함수에 한글 설명을 부여한다 ("코인 종목들을 받아옵니다")
Coins_Init.short_description = "코인 종목들을 받아옵니다"

def Share_Init_Kospi(modeladmin, request, queryset):

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    #id = Entire_Shares.objects.get(Share_Code='211900', Share_Category).id
    #Kospilist = Entire_Shares.objects.filter(Share_Category=0) #, id__gt=id
    #print(kiwoom.get_code_list_by_market(["0"])[0])
    kospi_code_list = kiwoom.get_code_list_by_market(["0"])
    kospi_code_name_list = []
    #is_feasible = True

    #k = KiwoomServer.kiwoom

    #app = QApplication(sys.argv)

    for x in kospi_code_list:
        if Entire_Shares.objects.filter(Share_Code=x, Share_Category=0):
            name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            entr = Entire_Shares.objects.get(Share_Code=x, Share_Name=name)
            entr.delete()
            Entire_Shares.objects.create(Share_Category=0, Share_Code=x, Share_Name=name)
            print(x, ' : ', name)
            time.sleep(0.2)
        else:
            name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            Entire_Shares.objects.create(Share_Category=0, Share_Code=x, Share_Name=name)
            print(x, ' : ', name)
            time.sleep(0.2)
Share_Init_Kospi.short_description = "코스피 종목 받아오기"


def Share_Init_Kosdaq(modeladmin, request, queryset):

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    kosdaq_code_list = kiwoom.get_code_list_by_market(["10"])
    kosdaq_code_name_list = []

    for x in kosdaq_code_list:
        if Entire_Shares.objects.filter(Share_Code=x, Share_Category=10):
            name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            entr = Entire_Shares.objects.get(Share_Code=x, Share_Name=name)
            entr.delete()
            Entire_Shares.objects.create(Share_Category=10, Share_Code=x, Share_Name=name)
            print(x, ' : ', name)
            time.sleep(0.2)
        else:
            name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            Entire_Shares.objects.create(Share_Category=10, Share_Code=x, Share_Name=name)
            print(x, ' : ', name)
            time.sleep(0.2)
        #kosdaq_code_name_list.append(x + ' : ' + name)
        #time.sleep(0.2)
        #print(x, ' : ', name)

Share_Init_Kosdaq.short_description = "코스닥 종목 받아오기"


#오버나잇 신청을 제외한 물량을 반대 매도 주문한다. 해당 함수는 개발자 페이지에서 실행 가능한 수동 함수이며,
#동일한 함수가 tasks.py에서 주기적으로 실행되고 있다. (자세한 주석은 tasks.py 참조)
def SellingOut_except_ovn(modeladmin, request, queryset):
    Hour = float(Clock.Clock()[0])
    Min = float(Clock.Clock()[1])
    Hour += Min/60


    OVNFee = 0
    x = MarketStatus.objects.all()
    for k in x:
        OVNFee = float(k.OVNFee)/100



    #print(((not(Hour > 15.5)) and (not int(Hour) < 9)))
    A = True
    #Hour > 15.2 or Hour < 6
    if A:
        uobj = x.user_idx
        hisHolding = Holdings.objects.filter(user_idx=uobj)
        time_wait = 2
        for h in hisHolding:
            if h.Holding_Quantities - h.OverNight_Quant > 0:
                targetShare = h.Share_idx
                x = RD_Related_To_Shares.objects.get(Share_idx=targetShare)
                x.Should_be_updated_now = True
                x.save()
                time_wait += 0.5
        time.sleep(time_wait)

        print("ovn call")
        for x in Holdings.objects.all():
            uobj = x.user_idx
            user_idx = uobj.user_idx
            sobj = x.Share_idx
            sid = sobj.id
            ovnQ = x.OverNight_Quant
            ovnRest = x.OverNight_Rest_Days
            x.save()
            print(ovnQ, ovnRest)
            print(ovnQ, ovnRest)
            #ovnQ > 0 and
            if A:
                Share_idx = Entire_Shares.objects.get(id=sid)

                one_Entry = User_In.objects.get(user_idx=user_idx)
                hisAsset = Asset.objects.get(user_idx=one_Entry)

                q = x.Holding_Quantities
                if ovnQ > 0 and ovnRest >= 0:
                    q = q - ovnQ
                    if q == 0:
                        return
                    ovnRest -= 1
                    hisAsset.Realized_Profit -= ovnQ * x.Price_Per_Single * OVNFee #오버나잇 수수료 적용.
                    # 실잔금에서 차감
                    hisAsset.save()
                elif ovnQ == 0:
                    ovnRest = 30
                rd_entry = RD_Related_To_Shares.objects.get(Share_idx=sobj)  # RDDictString
                dict_For_This_NotDone_Share = ast.literal_eval(rd_entry.RDDictString)

                p = 0
                #시장 가격을 얻어온다.
                if "10" in dict_For_This_NotDone_Share:
                    p = abs(int(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1, and Current Price ["10"]
                    print("There is indx 10")
                elif "41" in dict_For_This_NotDone_Share:
                    p = abs(int(dict_For_This_NotDone_Share["41"]))
                else:
                    print("empty price!")
                    continue

                #매도 주문 내역을 생성하고 미체결 목록을 생성 한다.
                hisHoldings = Holdings.objects.get(user_idx=one_Entry, Share_idx=Share_idx)
                print("selling our standby")
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
                    print("order created")
                    # order.save()
                    # send_order_q = OrderQ.objects.create(TransId=order)
                    # send_order_q.save()

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
                return

    return
SellingOut_except_ovn.short_description = "오버나잇 신청을 제외한 물량을 반대 매도 주문합니다"

#모든 유저의 잔고를 시장가 매도합니다. (사용 전에 공지할 것)
def SellingOut(modeladmin, request, queryset):

    for x in Holdings.objects.all():
        x.OverNight_Quant = 0
        x.save()
    SellingOut_except_ovn()
    #모든 잔고의 오버나잇 신청 수량을 0으로 초기화 한다음, 오버나잇 제외 물량 매도 함수를 호출
    return
SellingOut.short_description = "모든 유저의 잔고를 반대매매 합니다"

def Share_Init_feas(modeladmin, request, queryset):

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    #id = Entire_Shares.objects.get(Share_Code='211900', Share_Category).id
    Kospilist = Entire_Shares.objects.filter(Share_Category=0) #, id__gt=id
    #print(kiwoom.get_code_list_by_market(["0"])[0])
    #kospi_code_list = kiwoom.get_code_list_by_market(["10"])
    #kospi_code_name_list = []
    #is_feasible = True

    #k = KiwoomServer.kiwoom

    #app = QApplication(sys.argv)

    for x in Kospilist:

        #name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
        #kospi_code_name_list.append(x + ' : ' + name)
        #time.sleep(0.2)
        print(x.Share_Code, ' : ', x.Share_Name)
        if is_the_stock_feasible_sichong(x.Share_Code, kiwoom) == True:
            x.Is_feasible = True
            x.save()
        else:
            x.Is_feasible =False
            x.save()

    for x in Kospilist:
        if (not x.Is_feasible) and (x.Share_Category >= 0):
            x.delete()

Share_Init_feas.short_description = "코스피 종목 매수 가능 여부 심사_시총"


"""
        if x.Share_Code == "900140":
            st = 1

        if st == 0:
            continue

"""

def Share_Init_feas4(modeladmin, request, queryset):

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    #id = Entire_Shares.objects.get(Share_Code='211900', Share_Category).id
    Kospilist = Entire_Shares.objects.filter(Share_Category=0) #, id__gt=id

    for x in Kospilist:
        #name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
        #kospi_code_name_list.append(x + ' : ' + name)
        #time.sleep(0.2)
        print(x.Share_Code, ' : ', x.Share_Name)
        if is_the_stock_feasible_gamri(x.Share_Code, kiwoom) == True:
            x.Is_feasible = True
            x.save()
        else:
            x.Is_feasible = False
            x.save()
    for x in Kospilist:
        if (not x.Is_feasible) and (x.Share_Category >= 0):
            x.delete()
Share_Init_feas4.short_description = "코스피 종목 매수 가능 여부 심사_감리"


def Share_Init_feas2(modeladmin, request, queryset):

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    #id = Entire_Shares.objects.get(Share_Code='211900', Share_Category).id
    KosQlist = Entire_Shares.objects.filter(Share_Category=10) #, id__gt=id

    #st = 0
    codes = ""
    cnt = 0
    for x in KosQlist:
       # if x.Share_Code == "950110":
        #    st = 1

        #if st == 0:
         #   continue

        #print(x.Share_Code, ' : ', x.Share_Name)
        codes += x.Share_Code + ";"
        cnt += 1
        if cnt == 60:
            the_stock_feasible_sichong(codes, kiwoom, cnt)
            #kiwoom.disconnectRealData("0707") # 한 화면당 실시간 종목 수 제한 100종류, 화면수 제한 200
            print(codes)
            cnt = 0
            codes = ""
        """
        print(x.Share_Code, ' : ', x.Share_Name)
        if is_the_stock_feasible_sichong(x.Share_Code, kiwoom) == True:
            x.Is_feasible = True
            x.save()
        else:
            x.Is_feasible=False
            x.save()
        """
    the_stock_feasible_sichong(codes, kiwoom, cnt)
    #kiwoom.disconnectRealData("0707")

    print("task over!")

    for x in KosQlist:
        if (not x.Is_feasible) and (x.Share_Category >= 0):
            x.delete()
Share_Init_feas2.short_description = "코스닥 종목 매수 가능 여부 심사_시총"


def Share_Init_feas3(modeladmin, request, queryset):

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    #id = Entire_Shares.objects.get(Share_Code='211900', Share_Category).id
    KosQlist = Entire_Shares.objects.filter(Share_Category=10) #, id__gt=id
    #print(kiwoom.get_code_list_by_market(["0"])[0])
    #kospi_code_list = kiwoom.get_code_list_by_market(["10"])
    #kospi_code_name_list = []
    #is_feasible = True

    #k = KiwoomServer.kiwoom

    #app = QApplication(sys.argv)

    for x in KosQlist:
        #name = kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
        #kospi_code_name_list.append(x + ' : ' + name)
        #time.sleep(0.2)
        print(x.Share_Code, ' : ', x.Share_Name)
        if is_the_stock_feasible_gamri(x.Share_Code, kiwoom) == True:
            x.Is_feasible= True
            x.save()
        else:
            x.Is_feasible=False
            x.save()
    for x in KosQlist:
        if (not x.Is_feasible) and (x.Share_Category >= 0):
            x.delete()
Share_Init_feas3.short_description = "코스닥 종목 매수 가능 여부 심사_감리"


#지금은 사용되지 않는 코드 (디버깅용)
def See_RD(modeladmin, request, queryset):

    BasicFID = "10;11;12;13;16;17;18;"
    # 현재가,전일대비,등락률,누적거래, 시가, 고가, 저가

    HoggaMado = "41;42;43;44;45;46;47;48;49;"
    QuantMado = "61;62;63;64;65;66;67;68;69;"

    HoggaMaSu = "52;52;53;54;55;56;57;58;59;"
    QuantMaSu = "71;72;73;74;75;76;77;78;79;"
    TotalFid = BasicFID+HoggaMado+QuantMado+HoggaMaSu+QuantMaSu

    #kiwoom.setRealReg("0101", "006400", "10", 0)

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    #print(kiwoom.rd)
    kiwoom.setter_basic_info("006400")
    print(kiwoom.rd)
    time.sleep(2)
    #print(kiwoom.rd)
    time.sleep(2)
    kiwoom.setRealReg("0101", "005930", TotalFid, 0)
    kiwoom.setRealRemove("0101", "005930")
    print(kiwoom.rd)
    time.sleep(2)

#선택된 신청내역에서 입금 신청 내역을 찾아 처리 판정합니다 (처리 될 경우 고객의 자산에 예치금이 들어온다)
def DepositApprove(modeladmin, request, queryset):

    for object in queryset:
        if object.Share_idx.Share_Code == '신청' and object.Order_Type == 2:
            AssetEntry = Asset.objects.get(user_idx=object.user_idx)
            #AssetEntry.poured_money += object.Deposit_Money
            AssetEntry.losscut_left += object.Deposit_Money
            AssetEntry.save()

            order_deposit_obj = Deposit_Withdraw_Order_Done_List.objects.get(Transaction_idx=object)
            order_deposit_obj.TransactionDependency = str(object.id)
            order_deposit_obj.save()

            DepositAppr = Transaction.objects.create(user_idx=object.user_idx,
                                                     Share_idx=Entire_Shares.objects.get(Share_Category=-2),
                                                     TransDateTime=object.TransDateTime, Order_Type=object.Order_Type,
                                                     TreatStatus=2, Deposit_Money=object.Deposit_Money,
                                                     Actual_money=object.Actual_money)
            object.Share_idx = Entire_Shares.objects.get(Share_Code='처리 완료')
            object.save()
            #DepositAppr.save()
            DepositAppr_sub = Deposit_Withdraw_Order_Done_List.objects.create(
                user_idx=object.user_idx,
                Order_Money_Plus_Minus=object.Deposit_Money,
                Transaction_idx=DepositAppr, Order=object.Order_Type, PlusMinus=object.Deposit_Money,
                TransactionDependency=str(object.id)
            )
            #DepositAppr_sub.save()
DepositApprove.short_description = "입금을 처리 판정 합니다"


#선택된 신청내역에서 츨금 신청 내역을 찾아 처리 판정합니다 (처리 될 경우 고객의 자산에 예치금이 빠진다)
def WithdrApprove(modeladmin, request, queryset):
    for object in queryset:
        if object.Share_idx.Share_Code == '신청' and object.Order_Type == 3:
            AssetEntry = Asset.objects.get(user_idx=object.user_idx)
            #AssetEntry.poured_money += object.Deposit_Money
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
            #WithAppr.save()
            WithAppr_sub = Deposit_Withdraw_Order_Done_List.objects.create(
                user_idx=object.user_idx,
                Order_Money_Plus_Minus=object.Deposit_Money,
                Transaction_idx=WithAppr, Order=object.Order_Type, PlusMinus=object.Deposit_Money,
                TransactionDependency=str(object.id)
            )
            #DepositAppr_sub.save()
WithdrApprove.short_description = "출금을 처리 판정 합니다"

#대출 신청 내역에 선택된 항목들중 대출 신청을 찾아 처리한다. (대출이 처리 될 경우 회원 자산에 대출금이 들어온다)
def loanProve(modeladmin, request, queryset):

    msObj = MarketStatus.objects.all().latest('id')
    loanFee = msObj.LoanFee
    for object in queryset:
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
            #object.Order_Date = None
            AssetEntry = Asset.objects.get(user_idx=object.user_idx)
            lended_loan_by_now = object.Dam_bo_geum * object.Stock_Loan_Rate
            AssetEntry.lended_loan_by_now += lended_loan_by_now
            AssetEntry.poured_money -= lended_loan_by_now*loanFee/100
            AssetEntry.Dam_bo_geum += object.Dam_bo_geum
            AssetEntry.save()


loanProve.short_description = "대출을 처리 판정 합니다"

#회원별 수익을 정산하고 당일 실현손익과 실잔금을 초기화 하며, 오버나잇 신청 수를 0으로 초기화 합니다.
def JeongSan(modeladmin, request, queryset):
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
        #Asset_of_that_user.Estimated_Profit = 0
        #Asset_of_that_user.Total_Profit = 0
        Asset_of_that_user.poured_money += Asset_of_that_user.Realized_Profit
        Asset_of_that_user.Realized_Profit = 0
        Asset_of_that_user.save()

    # 전 날 ovn 설정 된 물량이 있을 시, ovn 신청 수를 0으로 초기화
    for x in Holdings.objects.all():
        x.OverNight_Quant = 0
        x.save()
    return

JeongSan.short_description = "금일 유저별 손익을 정산합니다"

#회사의 통계를 정산합니다. 이 함수는 수동 함수로, 평상시에도 자동으로 수행 되고 있음. tasks.py의 동일한 함수 설명 참조
def JeongSan_Company(modeladmin, request, queryset):

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
        #create Profit_stat
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
            #주의: day_In, Out은 외부에서 입력을 받아야 한다. 계산 효율을 높이기 위함 (한번에 처리)

        obj.save()
    else:
        obj.day_In = Money_I_today
        obj.day_Out = Money_O_today
        #update Profit_stat
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
    return
JeongSan_Company.short_description = "회사 정산을 시행합니다"

#should alway execute jeongsan_company first
#consumers.py의 관리자 소캣에서 동일한 함수가 자동으로 호출됨. 자세한 설명은 해당 소캣을 참조
def today_M_IO(modeladmin, request, queryset):
    obj = Profit_Stat.objects.all().latest('day')
    mi_today = obj.day_In
    mo_today = obj.day_Out

    dict = {0: mi_today, 1: mo_today}
    print(dict)
    return dict
today_M_IO.short_description = "금일 지금까지의 입출금 액수를 산정합니다"

#should alway execute jeongsan_company first
#consumers.py의 관리자 소캣에서 동일한 함수가 자동으로 호출됨. 자세한 설명은 해당 소캣을 참조
def otherStat_detail(modeladmin, request, queryset):
    obj0 = Profit_Stat.objects.all().latest('day')

    user_total_profit = 0
    TOTAL_IN_BY_NOW = obj0.TOTAL_IN_BY_NOW
    TOTAL_OUT_BY_NOW = obj0.TOTAL_OUT_BY_NOW
    MONEY_HAVE = TOTAL_IN_BY_NOW - TOTAL_OUT_BY_NOW
    assets = Asset.objects.all()
    profStats = Profit_Stat.objects.all()
    for x in assets:
        user_total_profit = x.Total_Profit

    NewUsersToday = obj0.new_user_d
    AccessNow = accessed_user.objects.count()

    timestamp = time.time()
    dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
    kmt = dt_utc + timedelta(hours=9)
    # 여기서부터 day를 추출해서 하면 오류의 여지가 줄어든다
    today = kmt - timedelta(days=1)
    today = str(today)
    today = today.split(' ')
    today = today[0]
    today = today.split('-')
    y = today[0]
    m = today[1]
    d = today[2]
    TransEntities = Transaction.objects.filter((Q(Order_Type=0) | Q(Order_Type=1)) & Q(TransDateTime__year=y)
                                     & Q(TransDateTime__month=m) & Q(TransDateTime__day=d), TreatStatus=-1)
    #Q 구분은 반드시 쉼표에 선행해야 한다 - 장고 문서 참조
    OrderQuantToday = 0
    OrderCapitalsToday = 0
    for x in TransEntities:
        oq = x.Order_Quant
        OrderCapitalsToday += oq
        OrderQuantToday += oq*x.Order_Price

    #return user_total_profit, TOTAL_IN_BY_NOW, TOTAL_OUT_BY_NOW, MONEY_HAVE, NewUsersToday,
    # OrderQuantToday, OrderCapitalsToday

    dict = {0: user_total_profit, 1: TOTAL_IN_BY_NOW, 2: TOTAL_OUT_BY_NOW, 3: MONEY_HAVE, 4: NewUsersToday,
            5: OrderQuantToday, 6: OrderCapitalsToday}
    #print(dict)
    return dict
otherStat_detail.short_description = "세부 통계를 산정합니다"


#아래의 JeongSan_Partner 함수는 회사 정산과 다른 주기를 따른다 (주 단위로 계산)
#또한 자동이 아닌 수동으로 한다.
#반드시 JeongSan_Comp 이후에 수행 되어야 한다 (그렇지 않은 겅우 예외사항이 생길 수 있음)
#should alway execute jeongsan_company first

#파트너 정산이다. 매일 기록되는 파트너 정산은 회사 정산 내에서 함꼐 호출되나,
# 정기적으로 시행되는 (1주일 혹은 1달에 한 번) 파트너 정산은 이와 같이 수동으로 시행된다. 이 함수는 views.py에도
# 존재하여, 개발자 페이지 뿐 아니라 관리자 페이지에서도 호출 가능하다.
def JeongSan_Partner(modeladmin, request, queryset):
    #파트너 정산. Profit_Stat에 반영, M_P_Managment에 기록
    partner_list = admins.objects.all().exclude(grant=0)
    p_jeongsan_summation = 0
    #매일의 파트너 정산 기록인 Profit_Stat_Partner에 접근하여 결산을 한다.
    for i in partner_list:
        ps_obj = Profit_Stat_Partner.objects.filter(admin_idx=i).latest('day')
        p_jeongsan = ps_obj.regular_total_jeongsan
        p_jeongsan_summation += p_jeongsan
        M_P_managementList.objects.create(admin_idx=i, jeongsan=p_jeongsan)
        ps_obj.regular_total_jeongsan = 0
        ps_obj.save()
    obj = Profit_Stat.objects.all().latest('day')
    obj.partner_jeongsan_d = p_jeongsan_summation
    obj.save()
    return
JeongSan_Partner.short_description = "파트너 정산을 시행합니다"


#지금은 사용되지 않는 함수
def ini_Called_State(modeladmin, request, queryset):
    for q in queryset:
        q.Is_Called_Second = False
        q.save()
    return
ini_Called_State.short_description = "호출 상태를 초기화 합니다"


#필요한 모든 테이블과 테이블 항목이 개발자 페이지에 나타나도록 하였다.
class adminsAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'bank_id', 'admin_pn', 'admin_bank_name', 'admin_name', 'profit_ratio', 'grant')

class ProfitAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'Total_Estimated_Profit_From_Stocks', 'Total_Realized_Profit', 'Real_Profit_Today',
                     'TOTAL_PROFIT_BY_NOW')

class Profit_StatAdmin(admin.ModelAdmin):
    list_display = ('day', 'day_In', 'day_Out', 'day_Profit', 'yesterday', 'yesterday_In', 'yesterday_Out',
                    'yesterday_Profit', 'monthNow', 'monthNow_In', 'monthNow_Out', 'monthNow_Profit', 'sonic_m',
                    'monthLate',
                    'monthLate_In', 'monthLate_Out', 'monthLate_Profit', 'TOTAL_IN_BY_NOW')

#회원가입 요청. 해당 테이블로 들어가면, 회원가입 승인 함수를 호출 할 수 있다.
class SignInReqAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'user_id', 'user_pw', 'bank_id', 'user_pn', 'user_bank_name', 'user_name',
                    'signin_domain')
    actions = [Allow_Signin]

class Profit_Stat_PartnerAdmin(admin.ModelAdmin):
    list_display = ('admin_idx', 'admin_id', 'day', 'day_In', 'day_Out', 'users_total_yest', 'users_total_today', 'profit_ratio',
                    'sonic', 'partner_out', 'jeongsan_today', 'regular_total_jeongsan')

class Top_KospiAdmin(admin.ModelAdmin):
    list_display = ('id', 'Share_Category', 'Share_Code', 'Share_Name', 'Is_feasible', 'spk', 'ranking')

class Top_CoinsAdmin(admin.ModelAdmin):
    list_display = ('id', 'Share_Category', 'Share_Code', 'Share_Name', 'Is_feasible', 'spk', 'ranking')

class Top_KosdqAdmin(admin.ModelAdmin):
    list_display = ('id', 'Share_Category', 'Share_Code', 'Share_Name', 'Is_feasible', 'spk', 'ranking')

class accessed_userAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'access_time', 'accessing_time_now', 'behave_type')

class User_InAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'user_id', 'user_pw', 'bank_id', 'user_pn', 'user_bank_name', 'user_name',
                    'init_signed_in_date', 'signin_domain', 'shut_down')


class Activity_LogAdmin(admin.ModelAdmin):
    list_display = ('log_idx', 'user_idx', 'uname', 'User_Activity', 'Market_Activity',
                    'System_Activity', 'Admin_Activity')

class infoAdmin(admin.ModelAdmin):
    list_display = ('dtime', 'title', 'contents', 'is_pop')

#전 종목 테이블. 종목 코드 혹은 이름으로 검색 열람이 가능하다.
class Entire_SharesAdmin(admin.ModelAdmin):
    list_display = ('id', 'Share_Category', 'Share_Code', 'Share_Name', 'Is_feasible')
    search_fields = ('Share_Code', 'Share_Name')


class Share_Groups_Per_UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_idx', 'interest_group')


class Share_InterestAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'interest_group', 'Share_idx', 'Share_Category', 'Share_Code', 'Share_Name')

#시장 상태 테이블. 아래에 등록된 함수들을 호출 가능하다.
class MarketStatusAdmin(admin.ModelAdmin):
    list_display = ('current_DayTime', 'current_Time', 'is_market_opened', 'is_market_exceptionally_closed'
                    , 'LossCutRate', 'Max_Task', 'BuyFee', 'OVNFee', 'ExchangeRate_USD',
                    'LoanFee', 'IpTcpAdr', 'Is_Testing_Buy_Sell')
    actions = [Share_Init_feas, Share_Init_feas2, Share_Init_feas3, Share_Init_feas4, Coins_Init, JeongSan
               , Share_Init_Kospi, Share_Init_Kosdaq, SellingOut_except_ovn, otherStat_detail,
               today_M_IO, JeongSan_Company, SellingOut]
    #Needs JeongSan, Overnight release ,etc actions more

class Admin_M_IOAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'dtime_jeongsan', 'Order', 'Quantity')

class RD_Related_To_SharesAdmin(admin.ModelAdmin):
    list_display = ('Share_idx', 'Share_Code', 'RDDictString', 'RD_load_balance_num',
                    'Should_be_updated_now', 'Supplied_by')

class HoldingsAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'Share_idx', 'Share_Name', 'Holding_Quantities', 'Price_Per_Single',
                    'Total_Bought_Prices',
                    'Total_Current_Prices', 'Estimated_Profit_In_This_Stock', 'OverNight_Quant', 'OverNight_Rest_Days',
                    'Should_OvN_be_released')

#거래 내역 함수. 입,출금 허락 함수를 호출 가능하다.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_idx', 'Share_idx', 'TransDateTime', 'Order_Type', 'TreatStatus',
                    'Order_Quant', 'Order_Price', 'Trans_Quant', 'Trans_Price',
                    'Fee_In_Trans', 'Selling_Profit', 'Realized_Profit', 'Deposit_Money', 'Actual_money', 'OtherMsg')
    actions = [DepositApprove, WithdrApprove]

class List_Not_DoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_idx', 'Share_idx', 'Transaction_idx', 'Order_Type', 'Order_Price',
                    'Order_Quant', 'Is_Cancelled')


class share_chartAdmin(admin.ModelAdmin):
    list_display = ('Share_Code', 'Chart_Dict', 'StandardDate', 'Should_be_updated_now')

class Deposit_Withdraw_Order_Done_ListAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'Transaction_idx', 'Order', 'TransDateTime', 'Order_Money_Plus_Minus',
                    'MoneyBefore', 'PlusMinus',
                    'MoneyNow', 'TransactionDependency')

#대출 테이블. 대출 승낙 함수 호출이 가능하다.
class Loan_Order_DoneAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'Stock_Loan_Rate', 'Dam_bo_geum', 'Is_Done', 'Order_Date', 'Done_Date')
    actions = [loanProve]

class AssetAdmin(admin.ModelAdmin):
    list_display = ('user_idx', 'Estimated_Profit', 'poured_money', 'Actual_money_by_now', 'Realized_Profit'
                    , 'Total_Profit', 'losscut_left', 'lended_loan_by_now', 'used_money', 'available_money')

class M_P_managementListAdmin(admin.ModelAdmin):
    list_display = ('admin_idx','admin_id', 'dtime_jeongsan', 'jeongsan')

class DomainListAdmin(admin.ModelAdmin):
    list_display = ('domain', 'status', 'dtime', 'admin_id')

class GrantTreeStructureAdmin(admin.ModelAdmin):
    list_display = ('admin_id1', 'admin_id2')


#아래는 회사의 감리와 시총을 기준으로 거래 적합 여부를 판단하는데 도움을 주는 함수들이다.
def is_the_stock_feasible_sichong(cd, kiwoom):

    kiwoom.setinput(cd) #request, tr
    print(kiwoom.market_capitalization)
    market_cap = float(kiwoom.market_capitalization)
    time.sleep(0.2)
    if market_cap <= 250:
        return False
    else:
        return True

def the_stock_feasible_sichong(codes, kiwoom, cnt):

    #print("fuck")
    kiwoom.commKwRqData(codes, 0, cnt, 0, "optkwfid_req", "0707")

def is_the_stock_feasible_gamri(cd, kiwoom):

    is_normal_str = kiwoom.dynamicCall("GetMasterConstruction(QString)", cd)
    #print(is_normal_str, ' : ', market_cap)
    time.sleep(0.2)
    if is_normal_str == '정상':
        return True
    else:
        return False


def is_the_stock_feasible(cd, kiwoom):

    is_feasible = True
    is_feasible = is_the_stock_feasible_gamri(cd, kiwoom)
    if is_feasible == False:
        return False
    else:
        return is_the_stock_feasible_sichong(cd, kiwoom)

def filter_feasible_stocks(startIdx, list, kiwoom):

    filtered_stocks = []
    list = list[startIdx:]
    for x in list:
        print(x)
        lookup_cd = x.split(' : ')[0]
        lookup_name = x.split(' : ')[1]
        if is_the_stock_feasible(lookup_cd, kiwoom):
            filtered_stocks.append(lookup_cd + ' : ' + lookup_name)
    return filtered_stocks


def stock_list_to_db_raw(scd_p, sname_p, sct_p):

    scd = scd_p
    sname = sname_p
    sct = sct_p
    is_feasible = True
    print(sct, ":", scd_p, ":", sname_p)
    print(type(sct), ":", type(scd_p), ":", type(sname_p))
    Share_Add_Obj = Entire_Shares.objects.create(
        Share_Category=sct,
        Share_Code=scd,
        Share_Name=sname,
    )
    #is_feasible=is_feasible, invalid keyword argument in this function?

    Share_Add_Obj.save()
    return


admin.site.register(User_In, User_InAdmin)
admin.site.register(Activity_Log, Activity_LogAdmin)

admin.site.register(SignInReq, SignInReqAdmin)

admin.site.register(MarketStatus, MarketStatusAdmin)
admin.site.register(Entire_Shares, Entire_SharesAdmin)
admin.site.register(Share_Groups_Per_User, Share_Groups_Per_UserAdmin)
admin.site.register(Share_Interest, Share_InterestAdmin)
admin.site.register(RD_Related_To_Shares, RD_Related_To_SharesAdmin)
admin.site.register(Holdings, HoldingsAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Deposit_Withdraw_Order_Done_List, Deposit_Withdraw_Order_Done_ListAdmin)
admin.site.register(Loan_Order_Done, Loan_Order_DoneAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(List_Not_Done, List_Not_DoneAdmin)
admin.site.register(Top_Coins, Top_CoinsAdmin)
admin.site.register(Top_Kospi, Top_KospiAdmin)
admin.site.register(Top_Kosdq, Top_KosdqAdmin)
admin.site.register(accessed_user, accessed_userAdmin)
admin.site.register(share_chart, share_chartAdmin)

admin.site.register(Profit_Stat, Profit_StatAdmin)
admin.site.register(Profit_Stat_Partner, Profit_Stat_PartnerAdmin)
admin.site.register(Profit, ProfitAdmin)

admin.site.register(M_P_managementList, M_P_managementListAdmin)
admin.site.register(DomainList, DomainListAdmin)
admin.site.register(admins, adminsAdmin)

admin.site.register(info, infoAdmin)
admin.site.register(GrantTreeStructure, GrantTreeStructureAdmin)
admin.site.register(Admin_M_IO, Admin_M_IOAdmin)