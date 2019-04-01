
from __future__ import absolute_import, unicode_literals
from celery import task
from celery import shared_task
from .models import *
from .consumers import Kiwoom
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from .views import Clock, Day, DatesNum
from PyQt5.QtCore import *
import json
import ast
import cryptocompare
from datetime import timezone, timedelta, datetime, date
import random
import pandas as pd
import requests

class Semaphore:
    sem = False

#need to define multi semaphore


class TaskIdx:
    Max_Task = 0
    taskid = 0


def getCoinList():
    req = requests.get('https://www.cryptocompare.com/api/data/coinlist/').json()
    info = req['Data']
    coinList = pd.DataFrame(info)
    coinList = coinList.transpose()
    coinList.to_csv('coinList.csv')
    return coinList


def MarKetStatus():

    x = MarketStatus.objects.all()
    for k in x:
        k.update_time_setter = k.update_time_setter
        Hour = float(Clock.Clock()[0])
        Min = float(Clock.Clock()[1])
        Hour += Min / 60
        # print(((not(Hour > 15.5)) and (not int(Hour) < 9)))
        if (((not (Hour > 15.5)) and (not int(Hour) < 9)) and not k.is_market_exceptionally_closed):
            k.is_market_opened = True
            k.save()
            return k.is_market_opened
        else:
            k.is_market_opened = False
            k.save()
            return k.is_market_opened


#하루가 지날 때 마다 유저별 손익을 예치금에 반영하고, 0으로 초기화 한다.
def JeongSan():
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


#오버나잇 설정은 오전 9시부터 오후 3시 12분까지 가능합니다.
#오버나잇 자동 판매가 작동하는 시간은 당일 3시12분 이후부터 다음날 오전 6시까지입니다.
# 즉, 그 사이에 오버나잇을 제외한 물량은 모두 판매되어 있어야 합니다
def SellingOut_except_ovn():
    Hour = float(Clock.Clock()[0])
    Min = float(Clock.Clock()[1])
    Hour += Min/60


    OVNFee = 0
    x = MarketStatus.objects.all()
    for k in x:
        OVNFee = float(k.OVNFee)/100

    #print(((not(Hour > 15.5)) and (not int(Hour) < 9)))
    if Hour > 15.2 or Hour < 6:
        print("ovn call")


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

        for x in Holdings.objects.all():
            uobj = x.user_idx
            user_idx = uobj.user_idx
            sobj = x.Share_idx
            sid = sobj.id

            """
                OverNight_Quant = models.IntegerField(default=0)
                OverNight_Rest_Days = models.IntegerField(default=30) #optional to use
                Should_OvN_be_released = models.BooleanField(default=False)
            """
            ovnQ = x.OverNight_Quant
            ovnRest = x.OverNight_Rest_Days
            x.save()
            print(ovnQ, ovnRest)
            #ovnQ > 0 and
            A = True
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

                if "10" in dict_For_This_NotDone_Share:
                    p = abs(int(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1, and Current Price ["10"]
                    print("There is indx 10")
                elif "41" in dict_For_This_NotDone_Share:
                    p = abs(int(dict_For_This_NotDone_Share["41"]))
                else:
                    print("empty price!")
                    continue


                #hisAsset.Realized_Profit -= q*p*OVNFee

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
    elif Hour < 9 and Hour > 7:
        #전 날 ovn 설정 된 물량이 있을 시, ovn 신청 수를 0으로 초기화
        # Jeongsan for users
        JeongSan()
        for x in Holdings.objects.all():
            x.OverNight_Quant = 0
            x.save()

        return

    return

#Profit, Asset
#@task
"""
def JeongSan():
    
        return
"""

#def AssetInspect_and_Modifier(uid):
#    for a in Assets:

def Monitoring_users():

    for x in accessed_user.objects.all():
        A = str(x.accessing_time_now + timedelta(hours=9))
        A = A.split(' ')
        clock = A[1]
        clock = clock.split(':')
        h = clock[0]
        m = clock[1]
        #print(h + ":" + m)
        h = float(h) + (float(m) / 60)

        Hour = float(Clock.Clock()[0])
        Min = float(Clock.Clock()[1])
        Hour += Min / 60

        Init_0 = x.access_time + timedelta(hours=9)
        Init = str(Init_0)
        #print(Init)
        Init = Init.split(' ')
        clock2 = Init[1]
        date_this = Init[0]
        clock2 = clock2.split(':')
        h2 = clock2[0]
        m2 = clock2[1]
        #print(h2 + ":" + m2)
        h2 = float(h2) + (float(m2) / 60)

        date_now = int(DatesNum.Dates())
        date_this = date_this.split('-')
        date_this = date_this[0] + date_this[1] + date_this[2]
        date_this = int(date_this)

        #print(Hour, "Hour")
        #print(h, "h")
        print(Hour - h, "Hour- h")
        #print(h2 - h, "nothing happnening range")
        if h - h2 > 1:
            user_idx = x.user_idx
            if Transaction.objects.filter(user_idx=user_idx):
                transEntities = Transaction.objects.filter(user_idx=user_idx, TransDateTime__gte=Init_0)
                if len(transEntities) == 0:
                    x.behave_type = 2
                    x.save()
                    user_idx.behave_type = 2
                    user_idx.save()
        elif h - h2 > 0.5:
            user_idx = x.user_idx
            if Transaction.objects.filter(user_idx=user_idx):
                transEntities = Transaction.objects.filter(user_idx=user_idx, TransDateTime__gte=Init_0)
                if len(transEntities) == 0:
                    x.behave_type = 1
                    x.save()
                    user_idx.behave_type = 1
                    user_idx.save()
                #datetime.date(y, m, d))
        else:
            user_idx = x.user_idx
            user_idx.behave_type = 0
            user_idx.save()

        if Hour - h > 0.05 or date_now > date_this:
            x.delete()
        return

def SellingOutAll_losscut():

    waittime = 0.5
    for x in Asset.objects.all():
        if x.losscut_left <= 0:
            uobj = x.user_idx
            hisHolding = Holdings.objects.filter(user_idx=uobj)
            for h in hisHolding:
                targetShare = h.Share_idx
                x = RD_Related_To_Shares.objects.get(Share_idx=targetShare)
                x.Should_be_updated_now = True
                waittime += 2
                x.save()
    time.sleep(waittime)
    for x in Asset.objects.all():
        if x.losscut_left <= 0:

            uobj = x.user_idx
            hisHolding = Holdings.objects.filter(user_idx=uobj)
            for h in hisHolding:
                q = h.Holding_Quantities
                sobj = h.Share_idx
                rd_entry = RD_Related_To_Shares.objects.get(Share_idx=sobj)  # RDDictString
                dict_For_This_NotDone_Share = ast.literal_eval(rd_entry.RDDictString)

                p = 0
                if "10" in dict_For_This_NotDone_Share:
                    p = abs(float(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1, and Current Price ["10"]
                    print("There is indx 10")
                elif "41" in dict_For_This_NotDone_Share:
                    p = abs(float(dict_For_This_NotDone_Share["41"]))
                else:
                    print("empty price!")
                    continue

                Share_idx = Entire_Shares.objects.get(id=sobj.id)

                one_Entry = h.user_idx
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
                time.sleep(0.5)


@task()
def JeongSan_Company():
    print("JeongSan Company!")
    Money_I_today = Deposit_Withdraw_Order_Done_List.day_m_i()
    Money_O_today = Deposit_Withdraw_Order_Done_List.day_m_o()

    #print(Money_I_today)

    timestamp = time.time()
    dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
    kmt = dt_utc + timedelta(hours=9)
    kmt = str(kmt)
    kmt = kmt.split(' ')
    today_dates = kmt[0]

    obj = Profit_Stat.objects.all().latest('day')

    this_dates = obj.day  # + timedelta(hours=9)
    this_dates = str(this_dates)
    this_dates = this_dates.split(' ')
    this_dates = this_dates[0]

    print("this_dates: " + this_dates)
    print("today_dates: " + today_dates)

    if this_dates != today_dates:
        #print("pj1!")
        # create Profit_stat
        admin_in_d = Admin_M_IO.day_m_i_admin()
        admin_out_d = Admin_M_IO.day_m_o_admin()
        partner_jeongsan_d = M_P_managementList.day_m_o_partner()
        new_user_d = User_In.day_number_of_signed_in()

        Profit_Stat.objects.create(day_In=Money_I_today, day_Out=Money_O_today, admin_in_d=admin_in_d,
                                   admin_out_d=admin_out_d, partner_jeongsan_d=partner_jeongsan_d,
                                   new_user_d=new_user_d)
        #obj = Profit_Stat.objects.all().latest('day')
        #print(obj.day)
        # update Profit_stat according to all rest of factors

        #obj.admin_in_d = admin_in_d
        #obj.admin_out_d = admin_out_d
        #obj.partner_jeongsan_d = partner_jeongsan_d
        #obj.new_user_d = new_user_d

        partner_list = admins.objects.all().exclude(grant=0)
        print("create")
        for i in partner_list:
            Profit_Stat_Partner.objects.create(admin_idx=i, day_In=admin_in_d, day_Out=admin_out_d)
            # 주의: day_In, Out은 외부에서 입력을 받아야 한다. 계산 효율을 높이기 위함 (한번에 처리)
        #obj.save()
    else:
        print("update")
        #print("pj2!")
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
        #print(partner_list)
        for i in partner_list:
            #print(i)
            if Profit_Stat_Partner.objects.filter(admin_idx=i):
                ps_obj = Profit_Stat_Partner.objects.filter(admin_idx=i).latest('day')
                #print(ps_obj)
                ps_obj.day_In = admin_in_d
                ps_obj.day_Out = admin_out_d
                ps_obj.save()
                #print("done")
            else:
                Profit_Stat_Partner.objects.create(admin_idx=i, day_In=admin_in_d, day_Out=admin_out_d)

        obj.save()


@task()
def Order_Treatment_Alg():

    if Semaphore.sem == True:
        return
    Semaphore.sem = True

    ms = MarketStatus.objects.all().latest('id')
    ms.update_time_setter = 1
    isTest = True#ms.Is_Testing_Buy_Sell
    ms.save()

    print("order")
    fee = 0.001
    x = MarketStatus.objects.all()

    feeB = 0
    feeS = 0

    for k in x:
        feeB = float(k.BasicFeeBuy + k.BuyFee)
        feeS = float(k.BasicFeeSell + k.SellFee)
        feeB = feeB/100
        feeS = feeS/100

    Orders = List_Not_Done.objects.all()
    if not Orders.exists():
        print("There is No Order")
        time.sleep(0.3)
    else:
        for x in Orders:
            TransObj = x.Transaction_idx #From 미체결

            user_obj = x.user_idx
            share_obj = x.Share_idx
            share_id = share_obj.id

            orderType = TransObj.Order_Type
            orderPrice = TransObj.Order_Price
            orderQ = x.Order_Quant

            rd_entry = RD_Related_To_Shares.objects.get(Share_idx=share_obj) #RDDictString
            print("There is Query")
            if rd_entry is None:
               continue
            if rd_entry.RDDictString == "{}":
                continue
            else:
                #proceed Che-gyul
                #Buy
                if orderType == 0:
                    dict_For_This_NotDone_Share = ast.literal_eval(rd_entry.RDDictString)
                    chegPrice = 100
                    chegQuant = 100
                    if "10" in dict_For_This_NotDone_Share:
                        chegPrice = abs(float(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1, and Current Price ["10"]
                        print("There is indx 10")
                    elif "41" in dict_For_This_NotDone_Share:
                        chegPrice = abs(float(dict_For_This_NotDone_Share["41"]))
                    else:
                        print("empty price!")
                        continue
                    if "61" in dict_For_This_NotDone_Share:
                        chegQuant = abs(float(dict_For_This_NotDone_Share["61"]))
                        print("There is indx 61")
                    elif "15" in dict_For_This_NotDone_Share:
                        chegQuant = abs(float(dict_For_This_NotDone_Share["15"]))
                    else:
                        print("empty quant!")
                        continue

                    if orderPrice >= chegPrice:
                        actualChegP = orderPrice
                        actualChegQ = 0
                        #actualChegQ = . . .Advanced Quant Algorithm canbe implemented by later deve version2.
                        #actualChegQ = . . .- orderQ
                        if chegQuant >= orderQ:
                            actualChegQ = orderQ #orderQ
                        else:
                            actualChegQ = chegQuant

                        hisAsset = Asset.objects.get(user_idx=user_obj)
                        totalFee = actualChegQ * actualChegP * feeB

                        # hisAsset.Actual_money_by_now -= totalFee Does not need dut to custom save f
                        hisAsset.Realized_Profit -= totalFee
                        Avail = hisAsset.available_money
                        m_rate = hisAsset.Actual_money_by_now / Avail
                        loan_rate = hisAsset.lended_loan_by_now / Avail
                        # = loan/Actual_money
                        print(hisAsset.used_money)
                        hisAsset.Actual_money_by_now -= m_rate * actualChegQ * actualChegP
                        hisAsset.lended_loan_by_now -= loan_rate * actualChegQ * actualChegP
                        hisAsset.used_money = hisAsset.used_money + actualChegQ * actualChegP
                        hisAsset.save()
                        print(actualChegP)
                        print(hisAsset.used_money)
                        #actualChegQ = chegQuant
                        Transaction.objects.create(
                            user_idx=user_obj,
                            Share_idx=share_obj,
                            Order_Type=0,
                            TreatStatus=0,
                            Order_Quant=orderQ,
                            Order_Price=orderPrice,
                            Trans_Quant=actualChegQ,
                            Trans_Price=actualChegP,
                            Fee_In_Trans=actualChegQ * actualChegP * feeB,
                            Selling_Profit=0,  # = Estimated_Profit in Stock Transactions
                            Realized_Profit=-totalFee,  # Selling_Profit- Fee_In_Trans
                            Deposit_Money=0,
                            Actual_money=hisAsset,
                        )
                        hisHolding = Holdings.objects.filter(user_idx=user_obj, Share_idx=share_id)
                        Current_Prices = chegPrice #dict_For_This_NotDone_Share['10']
                        length = len(hisHolding)
                        if length < 1:
                            print('None!')
                            # 이미 빈 Dict는 상단에서 걸러짐
                            New_Hold = Holdings.objects.create(
                                user_idx=user_obj,
                                Share_idx=share_obj,
                                Holding_Quantities=actualChegQ,
                                Total_Bought_Prices=actualChegQ * actualChegP,
                                Total_Current_Prices=Current_Prices * actualChegQ,
                            )
                            New_Hold.save()
                        else:
                            if length == 1:
                                for a in hisHolding:
                                    hisHolding = a
                                    Current_Prices = chegPrice#dict_For_This_NotDone_Share['10']
                                    hisHolding.Holding_Quantities += actualChegQ
                                    hisHolding.Total_Bought_Prices += actualChegQ * actualChegP
                                    hisHolding.Total_Current_Prices += Current_Prices * actualChegQ
                                    hisHolding.save()
                                    #break

                        QuantLater = x.Order_Quant - actualChegQ
                        if QuantLater <= 0:
                            x.delete()
                        else:
                            x.Order_Quant = QuantLater
                            x.save()
                    else:
                        continue
                #Sell
                elif orderType == 1:
                    dict_For_This_NotDone_Share = ast.literal_eval(rd_entry.RDDictString)
                    chegPrice = 100
                    chegQuant = 100

                    isExt10 = False
                    isExt51 = False
                    if "10" in dict_For_This_NotDone_Share:
                        isExt10 = True
                        print("There is indx 10")
                    if "51" in dict_For_This_NotDone_Share:
                        isExt51 = True
                        chegPrice = abs(float(dict_For_This_NotDone_Share["51"]))

                    if not isExt10 and isExt51:
                        chegPrice = abs(float(dict_For_This_NotDone_Share["51"]))
                    elif not isExt51 and isExt10:
                        chegPrice = abs(float(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1
                    elif isExt51 and isExt10:
                        chegPrice = abs(float(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1
                    if not isExt10 and not isExt51:
                        print("Empty 10, 51 idx rd")
                        continue

                    if "61" in dict_For_This_NotDone_Share:
                        chegQuant = abs(float(dict_For_This_NotDone_Share["71"]))
                        print("There is indx 71")
                    elif "15" in dict_For_This_NotDone_Share:
                        chegQuant = abs(float(dict_For_This_NotDone_Share["15"]))
                    else:
                        print("empty quant!")
                        continue

                    if orderPrice <= chegPrice:
                        actualChegP = orderPrice
                        actualChegQ = 0
                        #actualChegQ = . . .Advanced Quant Algorithm canbe implemented by later deve version2.
                        #actualChegQ = . . .- orderQ
                        if chegQuant >= orderQ:
                            actualChegQ = orderQ #orderQ
                        else:
                            actualChegQ = chegQuant

                        hisAsset = Asset.objects.get(user_idx=user_obj)
                        totalFee = actualChegQ * actualChegP * feeS

                        # hisAsset.Actual_money_by_now -= totalFee Does not need dut to custom save f
                        hisAsset.Realized_Profit -= totalFee
                        #Avail = hisAsset.available_money
                        #m_rate = hisAsset.Actual_money_by_now / Avail
                        #loan_rate = hisAsset.lended_loan_by_now / Avail
                        # = loan/Actual_money
                        hisAsset.Actual_money_by_now += actualChegQ * actualChegP
                        #hisAsset.lended_loan_by_now -= loan_rate * actualChegQ * actualChegP
                        hisAsset.used_money = hisAsset.used_money - actualChegQ * actualChegP

                        hisHolding = Holdings.objects.get(user_idx=user_obj, Share_idx=share_id)
                        #이미 잔고가 있어야 파는 것이 가능
                        #actualChegQ * actualChegP
                        Estimated_Profit = actualChegQ * (actualChegP - hisHolding.Price_Per_Single)

                        Realized_Profit = actualChegQ * (actualChegP - chegPrice)
                        E_R_gap = Estimated_Profit - Realized_Profit
                        hisAsset.Estimated_Profit -= E_R_gap
                        #hisAsset.Estimated_Profit -= Estimated_Profit
                        #hisAsset.Estimated_Profit += Realized_Profit
                        hisAsset.Realized_Profit += Estimated_Profit
                        print("before trans creation-sell")
                        Transaction.objects.create(
                            user_idx=user_obj,
                            Share_idx=share_obj,
                            Order_Type=1,
                            TreatStatus=1,
                            Order_Quant=orderQ,
                            Order_Price=orderPrice,
                            Trans_Quant=actualChegQ,
                            Trans_Price=actualChegP,
                            Fee_In_Trans=actualChegQ * actualChegP * feeS,
                            Selling_Profit=Estimated_Profit,
                            Realized_Profit=Estimated_Profit-totalFee,  # Selling_Profit- Fee_In_Trans
                            Deposit_Money=0,
                            Actual_money=hisAsset,
                        )
                        print("after trans creation-sell")
                        print("before holding trans-sell")
                        Current_Prices = chegPrice#dict_For_This_NotDone_Share['10']
                        hisHolding.Holding_Quantities -= actualChegQ
                        hisHolding.Total_Bought_Prices -= hisHolding.Price_Per_Single * actualChegQ
                        #Current_Prices * actualChegQ
                        hisHolding.Total_Current_Prices -= Current_Prices * actualChegQ
                        print("after holding trans-sell")

                        #holding 청산 절차, 오버나잇 초기화
                        hisHolding.OverNight_Rest_Days = 30
                        if hisHolding.Holding_Quantities <= 0:
                            hisHolding.delete()
                        else:
                            hisHolding.save()
                        QuantLater = x.Order_Quant - actualChegQ
                        if QuantLater <= 0:
                            x.delete()
                        else:
                            x.Order_Quant = QuantLater
                            x.save()
                        hisAsset.save()
                    else:
                        continue

    time.sleep(0.5)
    SellingOutAll_losscut()
    Monitoring_users()

    if isTest:
        pass
    else:
        SellingOut_except_ovn()

    Semaphore.sem = False
    return

@task()
def RD_Modifying():

    MS = MarketStatus.objects.all()
    for ms in MS:
        TaskIdx.Max_Task = ms.Max_Task

    """
    if Semaphore.sem == True:
        return
    Semaphore.sem = True
    """

    if TaskIdx.taskid > TaskIdx.Max_Task-1:
        return
    print("Task " + str(TaskIdx.taskid) + " has been started")
    ThisTaskDutyNum = TaskIdx.taskid
    TaskIdx.taskid += 1
    dates = DatesNum.Dates()

    coininfo = getCoinList()
    # print(A)
    TotalCoinSupplyList = coininfo["TotalCoinSupply"]


    HourN = float(Clock.Clock()[0])
    MinN = float(Clock.Clock()[1])
    Now = HourN + (MinN/60)
    #state = self.dynamicCall("GetConnectState()") #0,1

    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()
    print("API_receive&RD_modified!")
    time.sleep(2)

    BasicFID = "10;11;12;13;16;17;18;15;20"
    # 현재가,전일대비,등락률,누적거래, 시가, 고가, 저가, 거래량(체결수량), 체결시간

    HoggaMado = "41;42;43;44;45;46;47;48;49;"
    QuantMado = "61;62;63;64;65;66;67;68;69;"

    HoggaMaSu = "51;52;53;54;55;56;57;58;59;"
    QuantMaSu = "71;72;73;74;75;76;77;78;79;"
    TotalFid = BasicFID+HoggaMado+QuantMado+HoggaMaSu+QuantMaSu
    # 호가 관련 Fid
    screenNo_this_task = []
    init_screen = {"screen": ThisTaskDutyNum*100, "elemNum": 0}
    screenNo_this_task.append(init_screen)


    # 한 화면당 실시간 종목 수 제한 100종류, 화면수 제한 200
    while True:
        HourN = float(Clock.Clock()[0])
        MinN = float(Clock.Clock()[1])
        Now2 = HourN + (MinN / 60)

        FirstCallSet = []

        # 한 화면당 실시간 종목 수 제한 100종류, 화면수 제한 200
        #정기적으로 재 로그인을 해서 안정성을 늘린다 - 0.3
        if Now2 - Now > 1:
            HourN = float(Clock.Clock()[0])
            MinN = float(Clock.Clock()[1])
            Now = HourN + (MinN / 60)

            kiwoom.comm_connect()
            #break


        share_chart_shuld_be_updated = share_chart.objects.filter(Should_be_updated_now=True,
                                                                  C_load_balance_num=ThisTaskDutyNum)
        if not share_chart_shuld_be_updated:
            pass
        else:
            for x in share_chart_shuld_be_updated:
                scd = x.Share_Code
                cid = x.id
                sct = x.Share_Category
                if sct == 0 or sct == 10:
                    time.sleep(0.2)
                    print(str(ThisTaskDutyNum) + ": DutyNum")
                    Handle_Chart(kiwoom, scd, sct, cid, app, str(dates))
                    print("Treated Chart")

        RDquery = RD_Related_To_Shares.objects.filter(Should_be_updated_now=True, RD_load_balance_num=ThisTaskDutyNum)
        if not RDquery:
            #print("RD is Empty")
            time.sleep(0.3)
        else:

            for x in RDquery:
                scd = x.Share_idx.Share_Code
                sct = x.Share_idx.Share_Category
                if sct != 1:
                    FirstCallSet.append(scd)

            try:
                time.sleep(1.5)
                print(str(ThisTaskDutyNum) + ": DutyNum")
                # Handle_Shares_FirstCall(kiwoom, scd, sct, RD_id, app, TotalFid)
                codes = ""
                trAg = 0
                trUnit = 70
                for e in FirstCallSet:
                    codes += e + ";"
                    trAg += 1
                    if trAg == trUnit:
                        selectedScreen = ""
                        lastElem = {}
                        for i in screenNo_this_task:
                            lastElem = i
                            if i["elemNum"] + trAg <= 90:
                                selectedScreen = str(i["screen"])
                                i["elemNum"] += trAg
                        if selectedScreen == "":
                            screenNo_this_task.append({"screen": lastElem["screen"] + 1, "elemNum": 0})
                            selectedScreen = str((lastElem["screen"] + 1))
                        print("screen No: " + selectedScreen)
                        trAg = 0
                        """
                        while Semaphore.sem:
                            time.sleep(0.1)
                            continue
                        Semaphore.sem = True
                        """
                        Handle_FirstCall(kiwoom, codes, trAg, app, selectedScreen) #Handling Function
                        #Semaphore.sem = False
                        #time.sleep(0.2)
                selectedScreen = ""
                lastElem = {}
                for i in screenNo_this_task:
                    lastElem = i
                    if i["elemNum"] + trAg <= 90:
                        selectedScreen = str(i["screen"])
                        i["elemNum"] += trAg
                if selectedScreen == "":
                    screenNo_this_task.append({"screen": lastElem["screen"] + 1, "elemNum": 0})
                    selectedScreen = str((lastElem["screen"] + 1))
                print("screen No: " + selectedScreen)
                """
                while Semaphore.sem:
                    time.sleep(0.1)
                    continue
                Semaphore.sem = True
                """
                Handle_FirstCall(kiwoom, codes, trAg, app, selectedScreen) #Handling Function
                #Semaphore.sem = False
                time.sleep(0.2)
            except:
                print("handled exception task")
                # Actual Code Below
                # Handle_Shares_OtherCall(kiwoom, scd, sct, RD_id, app)

            for x in RDquery:
                sid = x.Share_idx.id
                print(sid)
                #AHold = Entire_Shares.objects.get(id=sid)
                scd = x.Share_Code
                sct = x.Share_idx.Share_Category
                RD_id = x.id
                # 한 화면당 실시간 종목 수 제한 100종류, 화면수 제한 200
                if sct == 1:
                    print("Coin req")
                    Handle_CryptoCurrency(scd, RD_id, TotalCoinSupplyList[scd])
                    print("Coin done")
                Share_id_num = x.id


    #Semaphore.sem = False
    TaskIdx.taskid -= 1
    print(TaskIdx.taskid, "current task id")
    for i in screenNo_this_task:
        kiwoom.disconnectRealData(str(i["screen"]))
        print("screen " + str(i["screen"]) + "was terminated")
    print(kiwoom.dynamicCall("GetConnectState()"))
    print("Task " + str(TaskIdx.taskid) + " terminated normally")
    return


def Handle_FirstCall(kiwoom, codes, trAg, app, selectedScreen):
    try:
        kiwoom.commKwRqData(codes, 0, trAg, 0, "multi", selectedScreen)
    except:
        print("handled multi request exception_0")
    return
    #print(((not(Hour > 15.5)) and (not int(Hour) < 9)))4




def Handle_CryptoCurrency(scd, RD_id, gapSeed):
    if gapSeed == 'N/A':
        gapSeed = '0'
    gapSeed = int(gapSeed)

    RD_row = RD_Related_To_Shares.objects.get(id=RD_id)
    currentPrice = cryptocompare.get_price(scd, 'USD') #('BTC')
    yesterday = date.today() - timedelta(1)
    #yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y:%m:%d')
    yesterday = yesterday.strftime('%Y:%m:%d')
    yestList = yesterday.split(':')
    y = int(yestList[0])
    m = int(yestList[1])
    d = int(yestList[2])
    yesterdayPrice = cryptocompare.get_historical_price(scd, 'USD', timestamp=datetime(y, m, d))
    currentPrice = currentPrice[scd]['USD']
    yesterdayPrice = yesterdayPrice[scd]['USD']
    hPrice = currentPrice - yesterdayPrice

    excgR = MarketStatus.exchRate()
    hPrice = hPrice*excgR
    currentPrice = currentPrice*excgR
    #initQuant = currentPrice
    #QuantMado = "61;62;63;64;65;66;67;68;69;"
    #QuantMaSu = "71;72;73;74;75;76;77;78;79;"

    q = []
    if gapSeed < 2:
        gapSeed = 2
    for i in range(0, 18):
        rn = random.randrange(0, gapSeed)
        rn = rn/15000000
        q.append("{0:.4f}".format(rn))

    currentPrice = int(currentPrice)
    length = len(str(currentPrice))
    divider = length-5
    if divider < 0:
        divider = 0
    fixer = pow(10, -divider)
    currentPrice = int(fixer*currentPrice)
    temp = currentPrice/fixer
    currentPrice = temp
    dict = {'scd': scd, '10': currentPrice, '15': 1, '11': hPrice, '61': q[0], '62': q[1], '63': q[2], '64': q[3],
            '65': q[4], '66': q[5], '67': q[6], '68': q[7], '69': q[8], '71': q[9], '72': q[10], '73': q[11],
            '74': q[12], '75': q[13], '76': q[14], '77': q[15], '78': q[16], '79': q[17]}

    RD_row.RDDictString = json.dumps(dict)
    RD_row.Should_be_updated_now = False
    RD_row.save()

    return


# @task()
def Handle_Chart(kiwoom, scd, sct, cid, app, dates):
    #dictNew = ast.literal_eval(share_chart.objects.get(id=cid).Chart_Dict)
    #Share_Entity = Entire_Shares.objects.get(Share_Code=scd, Share_Category=sct)
    #C_row = share_chart.objects.get(id=cid, Share_Code=scd)
    # kiwoom.setRealReg("0101", scd, TFid, 0)# Add it on the register - 빼 볼까 다음에는
    print("chart filling")
    kiwoom.cid = cid
    kiwoom.set_chart(scd, dates, 1, "opt10086_req", "opt10086")
    # Transform Code





