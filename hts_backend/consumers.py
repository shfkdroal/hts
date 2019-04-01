# chat/consumers.py
from __future__ import absolute_import
from channels.generic.websocket import *
import json
import asgiref
from .models import *
from .views import DatesNum
import threading
from django.db.models import F, Q
#asgiref.sync.async_to_sync
import sys
from django.utils.encoding import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
#from .kiwoom01 import *
import ast
from django.views.decorators.csrf import *
import random
from django.utils import timezone
#from datetime import timezone, timedelta, datetime, date
#import datetime
from datetime import datetime as dt
#from blockchain import *
"""
app = QApplication(sys.argv)
kiwoom = Kiwoom()
kiwoom.comm_connect()
"""

@python_2_unicode_compatible
class Kiwoom(QAxWidget):


    BasicFID = "10;11;12;13;16;17;18;"
    # 현재가,전일대비,등락률,누적거래, 시가, 고가, 저가

    HoggaMado = "41;42;43;44;45;46;47;48;49;"
    QuantMado = "61;62;63;64;65;66;67;68;69;"

    HoggaMaSu = "51;52;53;54;55;56;57;58;59;"
    QuantMaSu = "71;72;73;74;75;76;77;78;79;"
    TotalFid = BasicFID + HoggaMado + QuantMado + HoggaMaSu + QuantMaSu
    TotalFid = TotalFid.split(";")

    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slot() #only function connects

        self.market_capitalization = ''
        self.rd = {}
        self.data = {}
        self.CurrentPrice = "" #현재가
        self.Sigga = "" #시가
        self.Gogga = "" #고가
        self.Jeogga = "" #저가
        self.JeonIllDaebi = "" #전일대비
        self.ChegQ = "" #예상체결수량
        self.scd = ""
        self.cnt = 0
        self.md1 = ""
        self.md2 = ""
        self.cid = ""

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slot(self):
        self.OnEventConnect.connect(self.event_connect)
        #<-#aint during the EventLoop
        self.OnReceiveTrData.connect(self.receive_trdata) #added - tr setting on kiwoom obj initially
        self.OnReceiveRealData.connect(self.receive_realdata)
        #comm_connect

    #not initially called - is just one of the event trigger
    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.event_connect_loop = QEventLoop()
        #Waint during the EventLoop
        self.event_connect_loop.exec_()

    #rq = "opt10001_req", tr = "opt10001"
    #individual function
    def setter_basic_info(self, code, rq, tr):
        app = QApplication(sys.argv)
        self.scd = code
        #state = self.dynamicCall("GetConnectState()")
        #print(state)
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code) #set input (scd == code)
        # CommRqData -request data for the input
        print('reqGo')
        rqstate = self.dynamicCall("CommRqData(QString, QString, int, QString)", rq, tr, 0,
                                   "0101")
        print(rqstate)        #you can set the number 0 to 2 to use the other method (after the first call with '0'
        #function format, params matching, opt10001_req == RQName

        print('CallDone_rd_wait_1')
        self.event_connect_loop = QEventLoop() #Wait during the EventLoop
        #time.sleep(1)
        self.event_connect_loop.exec_()
        print('reqDone')
    def setter_basic_info_other_call(self, code, rq, tr):
        print("other call for ", code)
        self.scd = code
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rq, tr, 2,
                                   "0202")
        print('CallDone_rd_wait_2')
        self.event_connect_loop = QEventLoop() #Wait during the EventLoop
        self.event_connect_loop.exec_()
        #time.sleep(1.5)
        print('reqDone')

    def setter_getter_outMarket_first(self, code, rq, tr):
        print("other call for ", code)
        self.scd = code
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rq, tr, 0,
                                   "0303")
        print('CallDone_rd_wait_3o')
        self.event_connect_loop = QEventLoop() #Wait during the EventLoop
        self.event_connect_loop.exec_()
        #time.sleep(1.5)
        print('reqDone')

    def setter_getter_outMarket_other(self, code, rq, tr):
        print("other call for ", code)
        self.scd = code
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rq, tr, 2,
                                   "0404")
        print('CallDone_rd_wait_4o')
        self.event_connect_loop = QEventLoop() #Wait during the EventLoop
        self.event_connect_loop.exec_()
        #time.sleep(1.5)
        print('reqDone')

    def set_chart(self, code, dates, flag, rq, tr):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code) #set input (scd == code)
        self.dynamicCall("SetInputValue(QString, QString)", "조회일자", dates) #set input (scd == code)
        self.dynamicCall("SetInputValue(QString, QString)", "표시구분", flag) #set input (scd == code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rq, tr, 0, "0606")
        self.event_connect_loop = QEventLoop() #Wait during the EventLoop
        self.event_connect_loop.exec_()

    def setinput(self, code):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code) #set input (scd == code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0505")
        self.event_connect_loop = QEventLoop() #Wait during the EventLoop
        self.event_connect_loop.exec_()
        #time.sleep(1.5)

    def setRealReg(self, screenNo, codes, fids, realRegType):
        #realRegType should be "0" or "1" (0 in initial setting)
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                         screenNo, codes, fids, realRegType)

    #screenNo = "0101"
    def setRealRemove(self, screenNo, code):

        """
        Real data stopping method
        only stocks that registered by setRealReq, can be stopped by this method.
        :param screenNo: string - screen no
        :param code: string - share code, or ALL keyword can be utilized

        """
        self.dynamicCall("SetRealRemove(QString, QString)", screenNo, code)

    #screenNo = "0101"
    def disconnectRealData(self, screenNo):
        """
        remove all real data request assigned on the screen number. It must be called when exiting the screen
        :param screenNo: string
        """
        self.dynamicCall("DisconnectRealData(QString)", screenNo)

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "optkwfid_req":
            if screen_no == "0707":
                cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", "OPTKWFID", rqname)
                print(cnt)
                for i in range(0, cnt):
                    self.market_capitalization = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                                  "OPTKWFID",
                                                                  rqname, i, "시가총액")
                    code = self.dynamicCall("GetCommData(QString, QString, int, QString)", "OPTKWFID",
                                            rqname, i, "종목코드")
                    code = code.strip()
                    is_Feas = True
                    if float(self.market_capitalization) <= 250:
                        is_Feas = False

                    x = Entire_Shares.objects.get(Share_Code=code)
                    #print(x)
                    x.Is_feasible = is_Feas
                    x.save()

                print(cnt)
            #print("out of tr")
            self.event_connect_loop.exit()
            #print("out of tr2")
            #time.sleep(0.3)
        elif rqname == "opt10001_req":
            if screen_no == "0101":
                self.CurrentPrice = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "현재가")
                self.Sigga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "시가")
                self.Gogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "고가")
                self.Jeogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "저가")
                self.JeonIllDaebi = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, 0, "전일대비")
                self.ChegQ = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                     rqname, 0, "예상체결수량")
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, 0, "종목코드")
                code = code.strip()
                print(code, self.CurrentPrice)
                print("TR_Received!_0101")
                try:
                    print(self.scd, self.CurrentPrice)
                    RD_row = RD_Related_To_Shares.objects.get(Share_Code=code)
                    self.data = ast.literal_eval(RD_row.RDDictString)
                    a = self.CurrentPrice
                    b = self.Sigga
                    c = self.Gogga
                    d = self.Jeogga
                    e = self.JeonIllDaebi
                    f = self.ChegQ

                    print("fk!2")
                    """
                    BasicFID = "10;11;12;13;16;17;18;15;20"
                    # 현재가,전일대비,등락률,누적거래, 시가, 고가, 저가, 거래량(체결수량), 체결시간
                    """
                    # dictNew["CurrentPrice"] = abs(int(a))
                    self.data["10"] = (float(a))
                    # dictNew["Sigga"] = (float(b))
                    self.data["16"] = (float(b))
                    # dictNew["Gogga"] = (float(c))
                    self.data["17"] = (float(c))
                    # dictNew["Jeogga"] = (float(d))
                    self.data["18"] = (float(d))
                    # dictNew["JeonIllDaebi"] = (float(e))
                    self.data["11"] = (float(e))
                    # dictNew["ChegQ"] = (float(f))
                    self.data["15"] = (float(f))

                    # dictNew["10"] = (int(a)) #현재가
                    # dictNew["15"] = dictNew["ChegQ"] #거래량 (체결 수량) - or - 예상체결수량
                    self.data["scd"] = code
                    #self.rd = self.data
                    RD_row.RDDictString = json.dumps(self.data)
                    RD_row.save()
                    print("fk3!")

                except:
                    print("handled exception0- in TR receive f")

            elif screen_no == "0202":
                self.CurrentPrice = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "현재가")
                self.Sigga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "시가")
                self.Gogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "고가")
                self.Jeogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, 0, "저가")
                self.JeonIllDaebi = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, 0, "전일대비")
                self.ChegQ = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                     rqname, 0, "예상체결수량")
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, 0, "종목코드")
                code = code.strip()
                print("TR_Received!_0202")

                try:
                    RD_row = RD_Related_To_Shares.objects.get(Share_Code=code)
                    self.data = ast.literal_eval(RD_row.RDDictString)
                    a = self.CurrentPrice
                    b = self.Sigga
                    c = self.Gogga
                    d = self.Jeogga
                    e = self.JeonIllDaebi
                    f = self.ChegQ

                    print("fk!2")
                    """
                    BasicFID = "10;11;12;13;16;17;18;15;20"
                    # 현재가,전일대비,등락률,누적거래, 시가, 고가, 저가, 거래량(체결수량), 체결시간
                    """
                    # dictNew["CurrentPrice"] = abs(int(a))
                    self.data["10"] = (float(a))
                    # dictNew["Sigga"] = (float(b))
                    self.data["16"] = (float(b))
                    # dictNew["Gogga"] = (float(c))
                    self.data["17"] = (float(c))
                    # dictNew["Jeogga"] = (float(d))
                    self.data["18"] = (float(d))
                    # dictNew["JeonIllDaebi"] = (float(e))
                    self.data["11"] = (float(e))
                    # dictNew["ChegQ"] = (float(f))
                    self.data["15"] = (float(f))

                    # dictNew["10"] = (int(a)) #현재가
                    # dictNew["15"] = dictNew["ChegQ"] #거래량 (체결 수량) - or - 예상체결수량
                    self.data["scd"] = code
                    #self.rd = self.data
                    RD_row.RDDictString = json.dumps(self.data)
                    RD_row.save()
                    print("fk3!")

                except:
                    print("handled exception0- in TR receive f")

            elif screen_no == "0505":
                self.market_capitalization = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                     rqname, 0, "시가총액")
                time.sleep(0.3)

            self.event_connect_loop.exit()
        elif rqname == "opt10004_req":
            if screen_no == "0101":
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, 0, "종목코드")
                code = code.strip()
                RD_row = RD_Related_To_Shares.objects.get(Share_Code=code)
                self.data = ast.literal_eval(RD_row.RDDictString)

                masu = "매수"
                mado = "매도"
                jan = "차선잔량"
                ho = "차선호가"

                for i in range(1, 10):
                    k = 40 + i
                    reqType2 = mado + str(i) + ho
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType2)
                    k = 60 + i
                    reqType1 = mado + str(i) + jan
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType1)
                    k = 70 + i
                    reqType3 = masu + str(i) + jan
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType3)
                    k = 80 + i
                    reqType4 = masu + str(i) + ho
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType4)
                RD_row.RDDictString = json.dumps(self.data)
                RD_row.save()

            elif screen_no == "0202":
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, 0, "종목코드")
                code = code.strip()
                RD_row = RD_Related_To_Shares.objects.get(Share_Code=code)
                self.data = ast.literal_eval(RD_row.RDDictString)

                masu = "매수"
                mado = "매도"
                jan = "차선잔량"
                ho = "차선호가"

                for i in range(1, 10):
                    k = 40 + i
                    reqType2 = mado + str(i) + ho
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType2)
                    k = 60 + i
                    reqType1 = mado + str(i) + jan
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType1)
                    k = 70 + i
                    reqType3 = masu + str(i) + jan
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType3)
                    k = 80 + i
                    reqType4 = masu + str(i) + ho
                    self.data[str(k)] = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                         rqname, 0, reqType4)
                RD_row.RDDictString = json.dumps(self.data)
                RD_row.save()

            self.event_connect_loop.exit()

        #차트를 구성한다
        elif rqname == "opt10086_req":
            if screen_no == "0606":
                cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
                #code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                #                 rqname, 0, "종목코드")
                #code = code.strip()
                #print(code)
                print("filling1")
                chartEnt = share_chart.objects.get(id=self.cid)
                cDict = {} #ast.literal_eval(chartEnt.Chart_Dict)
                for i in range(0, cnt):
                    date = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "날짜")
                    if i==0:
                        chartEnt.StandardDate = date
                    sigga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "시가")
                    gogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "고가")
                    jeogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "저가")
                    jongga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "종가")
                    jeonilbe = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "전일비")
                    dictElem = {"date": int(date), "open": sigga.strip(), "high": gogga.strip(),
                                "low": jeogga.strip(), "close": jongga.strip(),
                                "differ": jeonilbe.strip()}
                    print("filling2")
                    cDict[str(i)] = dictElem
                chartEnt.Chart_Dict = json.dumps(cDict)
                chartEnt.Should_be_updated_now = False
                chartEnt.StandardDate = DatesNum.Dates()
                print("filling4")
                chartEnt.save()
                self.cid = ""
            self.event_connect_loop.exit()

        elif rqname == "multi":

            #print("screen no inside is, " + str(screen_no))
            self.cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
            for i in range(0, self.cnt):
                self.ChegQ = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                              "OPTKWFID",
                                                              rqname, i, "예상체결량")
                self.scd = self.dynamicCall("GetCommData(QString, QString, int, QString)", "OPTKWFID",
                                        rqname, i, "종목코드")
                self.CurrentPrice = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "현재가")
                self.Sigga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "시가")
                self.Gogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "고가")
                self.Jeogga = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                                              rqname, i, "저가")
                self.JeonIllDaebi = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, i, "전일대비")
                self.md1 = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, i, "매도1차호가")
                self.md2 = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode,
                                 rqname, i, "매도2차호가")
                self.scd = self.scd.strip()
                x = RD_Related_To_Shares.objects.get(Share_Code=self.scd)
                rdDict = ast.literal_eval(x.RDDictString)
                rdDict["15"] = abs(float(self.ChegQ))
                rdDict["10"] = float(self.CurrentPrice)
                rdDict["16"] = (float(self.Sigga))
                # dictNew["Gogga"] = (float(c))
                rdDict["17"] = (float(self.Gogga))
                # dictNew["Jeogga"] = (float(d))
                rdDict["18"] = (float(self.Jeogga))
                # dictNew["JeonIllDaebi"] = (float(e))
                rdDict["11"] = (float(self.JeonIllDaebi))
                rdDict["41"] = (float(self.md1))
                rdDict["42"] = (float(self.md2))
                rdDict["scd"] = self.scd
                # self.rd = self.data
                x.RDDictString = json.dumps(rdDict)
                x.Should_be_updated_now = False
                x.save()

            self.event_connect_loop.exit()

            """
            name = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,
                                    0, "종목명")
            volume = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname,
                                      0, "거래량")
            """


        #CommGetData is no longer supported
    def commKwRqData(self, codes, inquiry, codeCount, typeFlag, requestName, screenNo):

        """
        복수종목조회 메서드(관심종목조회 메서드라고도 함).
        이 메서드는 setInputValue() 메서드를 이용하여, 사전에 필요한 값을 지정하지 않는다.
        단지, 메서드의 매개변수에서 직접 종목코드를 지정하여 호출하며,
        데이터 수신은 receiveTrData() 이벤트에서 아래 명시한 항목들을 1회 수신하며,
        이후 receiveRealData() 이벤트를 통해 실시간 데이터를 얻을 수 있다.
        복수종목조회 TR 코드는 OPTKWFID 이며, 요청 성공시 아래 항목들의 정보를 얻을 수 있다.
        종목코드, 종목명, 현재가, 기준가, 전일대비, 전일대비기호, 등락율, 거래량, 거래대금,
        체결량, 체결강도, 전일거래량대비, 매도호가, 매수호가, 매도1~5차호가, 매수1~5차호가,
        상한가, 하한가, 시가, 고가, 저가, 종가, 체결시간, 예상체결가, 예상체결량, 자본금,
        액면가, 시가총액, 주식수, 호가시간, 일자, 우선매도잔량, 우선매수잔량,우선매도건수,
        우선매수건수, 총매도잔량, 총매수잔량, 총매도건수, 총매수건수, 패리티, 기어링, 손익분기,
        잔본지지, ELW행사가, 전환비율, ELW만기일, 미결제약정, 미결제전일대비, 이론가,
        내재변동성, 델타, 감마, 쎄타, 베가, 로
        :param codes: string - 한번에 100종목까지 조회가능하며 종목코드사이에 세미콜론(;)으로 구분.
        :param inquiry: int - api 문서는 bool 타입이지만, int로 처리(0: 조회, 1: 남은 데이터 이어서 조회)
        :param codeCount: int - codes에 지정한 종목의 갯수.
        :param requestName: string
        :param screenNo: string
        :param typeFlag: int - 주식과 선물옵션 구분(0: 주식, 3: 선물옵션), 주의: 매개변수의 위치를 맨 뒤로 이동함.
        :return: list - 중첩 리스트 [[종목코드, 종목명 ... 종목 정보], [종목코드, 종목명 ... 종목 정보]]
        """

        print(codes)
        print(codeCount)

        try:
            self.dynamicCall("CommKwRqData(QString, QBoolean, int, int, QString, QString)",
                                      codes, inquiry, codeCount, typeFlag, requestName, screenNo)
            self.event_connect_loop = QEventLoop()  # Wait during the EventLoop
            print('req go loop1')
            self.event_connect_loop.exec_()
            # receiveTrData() terminate this loop.
            print('out of loop1')
        except:
            print("handled unexpected exception of KWR")

    def receive_realdata(self, code, realType, realData):

        """
        실시간 데이터 수신 이벤트
        실시간 데이터를 수신할 때 마다 호출되며,
        setRealReg() 메서드로 등록한 실시간 데이터도 이 이벤트 메서드에 전달됩니다.
        getCommRealData() 메서드를 이용해서 실시간 데이터를 얻을 수 있습니다.
        :param code: string - 종목코드
        :param realType: string - 실시간 타입(KOA의 실시간 목록 참조)
        :param realData: string - 실시간 데이터 전문
        """
        """
        if realType != "주식호가잔량" or realType != "주식체결":
            print("other real type!")
            return
        """


        #[]
        #print(realData) #첫 시도
        #print(type(realData))
        #print(realType) #주식 호가 잔량
        #print(type(realType))

        codeOrNot = ""
        #if(strRealType == _T("주식체결"))

        if code != "":
            #print("RD nakka! -0")
            self.data['scd'] = code
            codeOrNot = code
        else:
            #print("RD nakka! -1")
            codeOrNot = realType

        if code != "":
            #print("RD nakka! -2")
            codeOrNot = code

        rdrow = RD_Related_To_Shares.objects.get(Share_Code=code)
        self.data = ast.literal_eval(rdrow.RDDictString)
        print("Real data was received! - ", code)
        print(realType)

        if realType == "주식호가잔량":
            #if self.BasicInfoWasReceived == False:
            # 여기서 임의 번호 10, 15, 11등을 호출 해서 확인 해 보자
            print("fk!44")
            try:
                for fid in sorted(RealType.REALTYPE[realType].keys()):
                    #print(fid)
                    value = self.getCommRealData(codeOrNot, fid)
                    #print(fid)
                    #self.data[fid] = value
                    #print(value)
                    if str(fid) in self.data:
                        del(self.data[str(fid)])
                    self.data[str(fid)] = value

                rdrow.RDDictString = json.dumps(self.data)
                rdrow.save()
                #self.event_connect_loop.exit()  # Is it really needed? <- need to see what happens
                # self.rd = self.dynamicCall("GetCommRealData(QString, int)", code, fid)
            except:
                print("handled RD exception")
                pass
        elif realType == "주식체결":

            # 여기서 임의 번호 10, 15, 11등을 호출 해서 확인 해 보자

            try:
                for fid in sorted(RealType.REALTYPE[realType].keys()):
                    #print(fid)
                    value = self.getCommRealData(codeOrNot, fid)
                    #print(fid)
                    #self.data[fid] = value
                    #print(value)
                    if str(fid) in self.data:
                        del(self.data[str(fid)])
                    self.data[str(fid)] = value

                    #debugcode
                    if str(fid) == "10":
                        print(code)
                        print(self.data['scd'])
                        print("SCD ABOVE!". value)
                        print(codeOrNot)

                rdrow.RDDictString = json.dumps(self.data)
                rdrow.save()
                #self.event_connect_loop.exit()  # Is it really needed? <- need to see what happens
                # self.rd = self.dynamicCall("GetCommRealData(QString, int)", code, fid)
            except:
                print("handled RD exception")
                pass
        else:
            pass
        self.event_connect_loop.exit()

            #print("RD nakka! -3") - 원래 여기까지는 통과
        #in sorted(RealType.REALTYPE[realType].keys()):
        """
        for fid in Kiwoom.TotalFid:
            value = self.GetCommRealData(codeOrNot, fid)  # getCommRealData(codeOrNot, fid)
            data[fid] = value  # .append(value)"""

        #

    def getCommRealData(self, code, fid):
        """
        실시간 데이터 획득 메서드
        이 메서드는 반드시 receiveRealData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.
        :param code: string - 종목코드
        :param fid: - 실시간 타입에 포함된 fid
        :return: string - fid에 해당하는 데이터
        """

        value = self.dynamicCall("GetCommRealData(QString, int)", code, fid)

        return value

    def event_connect(self, err_code):
        if err_code == 0:
            print("Kiwoom Login Succeed")
        else:
            print("Kiwoom Connection failed")
        self.event_connect_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        kospi_code_list = code_list.split(';')
        #print(code_list)
        return kospi_code_list


@python_2_unicode_compatible
class RealType(object):

    REALTYPE = {
        '주식시세': {
            10: '현재가',
            11: '전일대비',
            12: '등락율',
            27: '최우선매도호가',
            28: '최우선매수호가',
            13: '누적거래량',
            14: '누적거래대금',
            16: '시가',
            17: '고가',
            18: '저가',
            25: '전일대비기호',
            26: '전일거래량대비',
            29: '거래대금증감',
            30: '거일거래량대비',
            31: '거래회전율',
            32: '거래비용',
            311: '시가총액(억)'
        },
        '주식체결': {
            20: '체결시간(HHMMSS)',
            10: '체결가',
            11: '전일대비',
            12: '등락율',
            27: '최우선매도호가',
            28: '최우선매수호가',
            15: '체결량',
            13: '누적체결량',
            14: '누적거래대금',
            16: '시가',
            17: '고가',
            18: '저가',
            25: '전일대비기호',
            26: '전일거래량대비',
            29: '거래대금증감',
            30: '전일거래량대비',
            31: '거래회전율',
            32: '거래비용',
            228: '체결강도',
            311: '시가총액(억)',
            290: '장구분',
            691: 'KO접근도'
        },

        '주식호가잔량': {
            21: '호가시간',
            41: '매도호가1',
            61: '매도호가수량1',
            81: '매도호가직전대비1',
            51: '매수호가1',
            71: '매수호가수량1',
            91: '매수호가직전대비1',
            42: '매도호가2',
            62: '매도호가수량2',
            82: '매도호가직전대비2',
            52: '매수호가2',
            72: '매수호가수량2',
            92: '매수호가직전대비2',
            43: '매도호가3',
            63: '매도호가수량3',
            83: '매도호가직전대비3',
            53: '매수호가3',
            73: '매수호가수량3',
            93: '매수호가직전대비3',
            44: '매도호가4',
            64: '매도호가수량4',
            84: '매도호가직전대비4',
            54: '매수호가4',
            74: '매수호가수량4',
            94: '매수호가직전대비4',
            45: '매도호가5',
            65: '매도호가수량5',
            85: '매도호가직전대비5',
            55: '매수호가5',
            75: '매수호가수량5',
            95: '매수호가직전대비5',
            46: '매도호가6',
            66: '매도호가수량6',
            86: '매도호가직전대비6',
            56: '매수호가6',
            76: '매수호가수량6',
            96: '매수호가직전대비6',
            47: '매도호가7',
            67: '매도호가수량7',
            87: '매도호가직전대비7',
            57: '매수호가7',
            77: '매수호가수량7',
            97: '매수호가직전대비7',
            48: '매도호가8',
            68: '매도호가수량8',
            88: '매도호가직전대비8',
            58: '매수호가8',
            78: '매수호가수량8',
            98: '매수호가직전대비8',
            49: '매도호가9',
            69: '매도호가수량9',
            89: '매도호가직전대비9',
            59: '매수호가9',
            79: '매수호가수량9',
            99: '매수호가직전대비9',
            50: '매도호가10',
            70: '매도호가수량10',
            90: '매도호가직전대비10',
            60: '매수호가10',
            80: '매수호가수량10',
            100: '매수호가직전대비10',
            121: '매도호가총잔량',
            122: '매도호가총잔량직전대비',
            125: '매수호가총잔량',
            126: '매수호가총잔량직전대비',
            23: '예상체결가',
            24: '예상체결수량',
            128: '순매수잔량(총매수잔량-총매도잔량)',
            129: '매수비율',
            138: '순매도잔량(총매도잔량-총매수잔량)',
            139: '매도비율',
            200: '예상체결가전일종가대비',
            201: '예상체결가전일종가대비등락율',
            238: '예상체결가전일종가대비기호',
            291: '예상체결가',
            292: '예상체결량',
            293: '예상체결가전일대비기호',
            294: '예상체결가전일대비',
            295: '예상체결가전일대비등락율',
            13: '누적거래량',
            299: '전일거래량대비예상체결률',
            215: '장운영구분'
        },

        '장시작시간': {
            215: '장운영구분(0:장시작전, 2:장종료전, 3:장시작, 4,8:장종료, 9:장마감)',
            20: '시간(HHMMSS)',
            214: '장시작예상잔여시간'
        },
    }

"""
@python_2_unicode_compatible
class KiwoomServer(QMainWindow):
    #has only back method - (embedded kiwoom initializer - could be considered)
    #login = False
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()
    #Thre is a way to make view 'CBV'

    def __init__(self):
        super().__init__()
"""


def otherStat_detail():
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
    dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
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
    TransEntities = Transaction.objects.filter((Q(Order_Type=0) | Q(Order_Type=1)) & Q(TransDateTime__year=y) &
                                               Q(TransDateTime__month=m) & Q(TransDateTime__day=d), TreatStatus=-1)
    #Q 구분은 반드시 쉼표에 선행해야 한다 - 장고 문서 참조
    OrderQuantToday = 0
    OrderCapitalsToday = 0
    for x in TransEntities:
        oq = x.Order_Quant
        OrderCapitalsToday += oq
        OrderQuantToday += oq*x.Order_Price

    Access_NUM = accessed_user.objects.count()

    #return user_total_profit, TOTAL_IN_BY_NOW, TOTAL_OUT_BY_NOW, MONEY_HAVE, NewUsersToday,
    # OrderQuantToday, OrderCapitalsToday

    dict = {0: user_total_profit, 1: TOTAL_IN_BY_NOW, 2: TOTAL_OUT_BY_NOW, 3: MONEY_HAVE, 4: NewUsersToday,
            5: OrderQuantToday, 6: OrderCapitalsToday, 7: Access_NUM}
    print(dict)
    return dict

#Example
def today_M_IO():
    if Profit_Stat.objects.all():
        obj = Profit_Stat.objects.all().latest('day')
        mi_today = obj.day_In
        mo_today = obj.day_Out

        dict = {0: mi_today, 1: mo_today}
        print(dict)
        return dict
    else:
        dict = {0: 0, 1: 0}
        return dict

class admin_socket(WebsocketConsumer):

    User_idx_number = 0
    Is_logged_in_Status = 0
    timer = ""

    def connect(self):
        print("admin scoket established!")
        admin_socket.Is_logged_in = 1
        self.accept()

    def disconnect(self, close_code):
        admin_socket.timer.cancel()
        admin_socket.Is_logged_in = 0
        pass

    def receive(self, text_data):

        Num_sign = SignInReq.objects.count()
        Num_loan = Loan_Order_Done.objects.filter(Is_Done=False).count()
        Num_mi = Deposit_Withdraw_Order_Done_List.objects.filter(Order=2, PlusMinus=0, TransactionDependency='').count()
        Num_mo = Deposit_Withdraw_Order_Done_List.objects.filter(Order=3, PlusMinus=0, TransactionDependency='').count()

        MIODict = today_M_IO()
        # dict = {0: mi_today, 1: mo_today}
        DetailStat = otherStat_detail()
        # dict = {0: user_total_profit, 1: TOTAL_IN_BY_NOW, 2: TOTAL_OUT_BY_NOW, 3: MONEY_HAVE, 4: NewUsersToday,
        #       5: OrderQuantToday, 6: OrderCapitalsToday, 7: Access_NUM}

        PSobj = Profit_Stat.objects.all().latest('day')

        EntireDict = {'0_0': PSobj.day_In, '0_1': PSobj.day_Out, '0_2': PSobj.day_Profit, '0_3': PSobj.sonic_d,
                      '0_4': PSobj.admin_in_d, '0_5': PSobj.admin_out_d,
                      '0_6': PSobj.partner_jeongsan_d, '0_7': PSobj.new_user_d,
                      '1_0': PSobj.yesterday_In, '1_1': PSobj.yesterday_Out, '1_2': PSobj.yesterday_Profit,
                      '1_3': PSobj.sonic_y,
                      '1_4': PSobj.admin_in_y, '1_5': PSobj.admin_out_y,
                      '1_6': PSobj.partner_jeongsan_y, '1_7': PSobj.new_user_y,
                      '2_0': PSobj.daybefore_In, '2_1': PSobj.daybefore_Out, '2_2': PSobj.daybefore_Profit,
                      '2_3': PSobj.sonic_db,
                      '2_4': PSobj.admin_in_db, '2_5': PSobj.admin_out_db,
                      '2_6': PSobj.partner_jeongsan_db, '2_7': PSobj.new_user_db,
                      '3_0': PSobj.monthNow_In, '3_1': PSobj.monthNow_Out, '3_2': PSobj.monthNow_Profit,
                      '3_3': PSobj.sonic_m,
                      '3_4': PSobj.admin_in_m, '3_5': PSobj.admin_out_m,
                      '3_6': PSobj.partner_jeongsan_m, '3_7': PSobj.new_user_m,
                      '4_0': PSobj.monthLate_In, '4_1': PSobj.monthLate_Out, '4_2': PSobj.monthLate_Profit,
                      '4_3': PSobj.sonic_ml,
                      '4_4': PSobj.admin_in_ml, '4_5': PSobj.admin_out_ml,
                      '4_6': PSobj.partner_jeongsan_ml, '4_7': PSobj.new_user_ml,
                      '5_0': DetailStat[7], '5_1': DetailStat[4], '5_2': DetailStat[5], '5_3': DetailStat[6],
                      '5_4': DetailStat[0], '5_5': DetailStat[3], '5_6': DetailStat[1], '5_7': DetailStat[2],
                      '6_0': MIODict[0], '6_1': MIODict[1], 'Num_sign': Num_sign, 'Num_loan': Num_loan,
                      'Num_mi': Num_mi, 'Num_mo': Num_mo
                      }


        self.send(text_data=json.dumps(EntireDict))
        print(EntireDict)
        admin_socket.timer = threading.Timer(40, self.receive, args=[text_data])
        #print(admin_socket.Is_logged_in)
        if admin_socket.Is_logged_in == 1:
            admin_socket.timer.start()
        else:
            admin_socket.timer.cancel()
        return



class RealTime_basic_info_list_holdings(WebsocketConsumer):


    Should_Be_Updated_RD_List = []
    Is_logged_in_Status = 0
    User_idx_number = 0
    timer = ""
    #app = QApplication(sys.argv)
    #kiwoom = Kiwoom()
    #kiwoom._create_kiwoom_instance()
    #kiwoom._set_signal_slot()

    #kiwoom.comm_connect()
    #Kiwoom.comm_connect(kiwoom)

    @csrf_exempt
    def connect(self):

        RealTime_basic_info_list_holdings.Is_logged_in = 1
        #Kiwoom.comm_connect(RealTime_basic_info_list_holdings.kiwoom)
        print("connection established!_Holdings")
        print("connection established!_Holdings")
        print(RealTime_basic_info_list_holdings.Is_logged_in)
        print(RealTime_basic_info_list_holdings.Is_logged_in, "===========0")
        self.accept()

    def disconnect(self, close_code):
        RealTime_basic_info_list_holdings.timer.cancel()
        print("disconnected socket") #disconnected가 복수로 호출 되면 아래 코드에서 가벼운 에러가 발생 (이미 AU가
        #삭제 된 뒤이기에.

        #remove info list with this uid
        user_idx_number = RealTime_basic_info_list_holdings.User_idx_number
        if User_In.objects.filter(user_idx=user_idx_number):
            user_idx_obj = User_In.objects.get(user_idx=user_idx_number)
            if accessed_user.objects.filter(user_idx=user_idx_obj):
                AU = accessed_user.objects.get(user_idx=user_idx_obj)
                AU.delete()
        RealTime_basic_info_list_holdings.Is_logged_in = 0

        """
        viewedRD = RD_Related_To_Shares.objects.filter(Supplied_by=user_idx_number)
        for x in viewedRD:
            x.delete()
        """
        #수행 여부도 랜덤으로 결정

        pass

    @csrf_exempt
    def receive(self, text_data):

        print("received")
        """
        app = QApplication(sys.argv)
        kiwoom = Kiwoom()
        kiwoom.comm_connect()
        kiwoom.setter_basic_info("006400")
        """

        text_data_json = json.loads(text_data)
        user_idx_number = int(text_data_json['user_idx'])
        RealTime_basic_info_list_holdings.User_idx_number = user_idx_number
        user_idx_obj = User_In.objects.get(user_idx=user_idx_number)
        is_H = text_data_json['is_H']
        is_H = int(is_H)
        print(RealTime_basic_info_list_holdings.Is_logged_in, "=====!!!")

        if accessed_user.objects.filter(user_idx=user_idx_obj):
            qs = accessed_user.objects.filter(user_idx=user_idx_obj)
            if len(qs) > 1:
                for a in range(1, len(qs)):
                    qs[a].delete()
            entAcc = qs[0]
            timestamp = time.time()
            dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
            kmt = dt_utc + timedelta(hours=9)
            entAcc.accessing_time_now = kmt
            print(kmt)
            entAcc.save()
            pass
        else:
            if RealTime_basic_info_list_holdings.Is_logged_in == 1 and not \
                    accessed_user.objects.filter(user_idx=user_idx_obj):
                RealTime_basic_info_list_holdings.Is_logged_in = 1
                accessed_user.objects.create(user_idx=user_idx_obj)


        if is_H == 1:
            Holdings_Entries = Holdings.objects.filter(user_idx=user_idx_obj)

            ExistList = []
            NoneExistList = []
            # print(Holdings_Entries)
            DictString = ""
            for x in Holdings_Entries:
                # print(x.Share_idx)
                target_share = x.Share_idx
                if RD_Related_To_Shares.objects.filter(Share_idx=target_share):
                    x = RD_Related_To_Shares.objects.get(Share_idx=target_share)
                    x.Should_be_updated_now = True
                    x.save()
                    if x.RDDictString != "{}":
                        DictString += "!"
                        DictString += x.RDDictString

                        dict_For_This_NotDone_Share = ast.literal_eval(x.RDDictString)
                        p = 0

                        if "10" in dict_For_This_NotDone_Share:
                            p = abs(float(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1, and Current Price ["10"]
                            print("There is indx 10")
                            is_Ext_41 = True
                        elif "41" in dict_For_This_NotDone_Share:
                            p = abs(float(dict_For_This_NotDone_Share["41"]))
                        else:
                            print("empty price!")
                            pass
                        sCurrentPrice = p
                        if Holdings.objects.filter(user_idx=user_idx_obj, Share_idx=target_share):
                            print("holding modifying")
                            hisHoldings = Holdings.objects.get(user_idx=user_idx_obj, Share_idx=target_share)
                            hisHoldings.Total_Current_Prices = hisHoldings.Holding_Quantities * sCurrentPrice
                            hisHoldings.save()
                            hisAsset = Asset.objects.get(user_idx=user_idx_obj)
                            hisAsset.save()

                    # ExistList.append(x.Share_idx.id) #can access RD-DB
                else:
                    #RD_load_balance_num = random.randrange(1,7) #1~6
                    MS = MarketStatus.objects.all()
                    RD_load_balance_num = 0
                    for ms in MS:
                        RD_load_balance_num = random.randrange(0, ms.Max_Task)

                    RD_Related_To_Shares.objects.create(Share_idx=target_share,
                                                        RDDictString="{}",
                                                        Supplied_by=user_idx_number,
                                                        RD_load_balance_num=RD_load_balance_num
                                                        )
            self.send(text_data=json.dumps({
                'Share_RD': DictString,
                'integ': -1
            }))
        elif is_H == 0:
            sid_number = int(text_data_json['sid'])  # spk
            print("sid of received share!")
            print(sid_number)
            target_share = Entire_Shares.objects.get(id=sid_number)
            s_name = target_share.Share_Name
            sct = target_share.Share_Category
            print(s_name, 0)
            user_idx_obj = User_In.objects.get(user_idx=user_idx_number)

            if RD_Related_To_Shares.objects.filter(Share_idx=target_share):
                x = RD_Related_To_Shares.objects.get(Share_idx=target_share)
                x.Should_be_updated_now = True
                x.save()
                DictString = x.RDDictString
                if DictString != "{}":
                    # Hold and Real Data, influencing on Asset
                    dict_For_This_NotDone_Share = ast.literal_eval(DictString)

                    p = 0

                    if "10" in dict_For_This_NotDone_Share:
                        p = abs(float(dict_For_This_NotDone_Share["10"]))  # 41 - Mado 1, and Current Price ["10"]
                        print("There is indx 10")
                        is_Ext_41 = True
                    elif "41" in dict_For_This_NotDone_Share:
                        p = abs(float(dict_For_This_NotDone_Share["41"]))
                    else:
                        print("empty price!")
                        pass
                    sCurrentPrice = p


                    integ = 0
                    p41 = 0
                    p10 = 0
                    is_Ext_41 = False
                    is_Ext_10 = False
                    if "41" in dict_For_This_NotDone_Share:
                        p41 = abs(float(dict_For_This_NotDone_Share["41"]))  # 41 - Mado 1, and Current Price ["10"]
                        print("There is indx 41")
                        is_Ext_41 = True
                    if "10" in dict_For_This_NotDone_Share:
                        p10 = abs(float(dict_For_This_NotDone_Share["10"]))
                        print("There is indx 10")
                        is_Ext_10 = True

                    gap = 100
                    if not is_Ext_41 and not is_Ext_10:
                        integ = 0
                    elif not is_Ext_41 and is_Ext_10:
                        integ = 1
                        gap = int(p/100)
                        gap = int(gap/10)
                        gap = gap*10
                    elif is_Ext_41 and not is_Ext_10:
                        integ = 2
                        gap = p/100
                        gap = gap/10
                        gap = gap*10
                    elif is_Ext_41 and is_Ext_10:
                        gap = abs(abs(float(dict_For_This_NotDone_Share["41"])) -
                                  abs(float(dict_For_This_NotDone_Share["42"])))
                        if p41 == p10:
                            integ = 3
                        else:
                            integ = 4
                    #not render current price : 0, 2
                    #render hogga : 3



                    if Holdings.objects.filter(user_idx=user_idx_obj, Share_idx=target_share):
                        print("holding modifying")
                        print(sCurrentPrice)
                        hisHoldings = Holdings.objects.get(user_idx=user_idx_obj, Share_idx=target_share)
                        hisHoldings.Total_Current_Prices = hisHoldings.Holding_Quantities * sCurrentPrice
                        hisHoldings.save()
                        hisAsset = Asset.objects.get(user_idx=user_idx_obj)
                        hisAsset.save()

                    chart = "{}"
                    uptodate = -1
                    if share_chart.objects.filter(Spk=sid_number):
                        chartData = share_chart.objects.get(Spk=sid_number)
                        uptodate = int(not chartData.Should_be_updated_now)
                        # uptodate여야만 차트를 뿌려야 한다
                        chart = chartData.Chart_Dict

                    if sct == 1:
                        sct = 0
                    else:
                        sct = 1 #코인이면 0, 주식이면 1
                    shutdown = 0
                    if user_idx_obj.shut_down == True:
                        shutdown = 1
                    #*hisHoldings.sCurrentPrice
                    gap = int(gap)
                    if gap < 0:
                        gap = -gap
                    elif gap == 0:
                        gap = 1
                    self.send(text_data=json.dumps({
                        'Share_RD': DictString,
                        'Integ': integ,
                        'gap': gap,
                        'chart': chart,
                        'uptodate': uptodate,
                        'sct': sct,
                        'shutdown': shutdown
                    }))
            else:
                MS = MarketStatus.objects.all()
                RD_load_balance_num = 0
                for ms in MS:
                    RD_load_balance_num = random.randrange(0, ms.Max_Task)

                RD_Related_To_Shares.objects.create(Share_idx=target_share,
                                                    RDDictString="{}",
                                                    Supplied_by=user_idx_number,
                                                    RD_load_balance_num=RD_load_balance_num
                                                    )
                self.send(text_data=json.dumps({
                    'Share_RD': "실시간 정보를 불러오는 중입니다",
                    'Integ': -1
                }))

        print("======================1")
        RealTime_basic_info_list_holdings.timer = threading.Timer(4, self.receive, args=[text_data])
        print(RealTime_basic_info_list_holdings.Is_logged_in)
        if RealTime_basic_info_list_holdings.Is_logged_in == 1:
            print("======================2")
            RealTime_basic_info_list_holdings.timer.start()
        else:
            RealTime_basic_info_list_holdings.timer.cancel()


@python_2_unicode_compatible
class KiwoomEventHandler1(SyncConsumer):

    Should_Be_Updated_RD_List = []
    BreakMaker = 0
    #init_rd_set = True

    @python_2_unicode_compatible
    def handleAPIReq(self, event):
        return

        #KiwoomServer.kiwoom.setter_basic_info("006400")


class RealTime_basic_info0(WebsocketConsumer):

    def connect(self):
        print("connection established!_info0")
        print("connection established!_info0")
        self.accept()

    def disconnect(self, close_code):
        #remove info list with this uid
        pass

    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        user_idx_number = text_data_json['user_idx']
        sid_number = int(text_data_json['sid']) #spk
        target_share = Entire_Shares.objects.get(id=sid_number)
        s_name = target_share.Share_Name
        print(s_name)
        user_idx_obj = User_In.objects.get(user_idx=user_idx_number)
        hisHoldings = Holdings.objects.get(user_idx=user_idx_obj, Share_idx=target_share)

        if RD_Related_To_Shares.objects.filter(Share_idx=target_share):
            x=RD_Related_To_Shares.objects.get(Share_idx=target_share)
            DictString = x.RDDictString

            #Hold and Real Data, influencing on Asset
            Dict = ast.literal_eval(DictString)
            sCurrentPrice = Dict["10"]
            hisHoldings.Total_Current_Prices = hisHoldings.Holding_Quantities * sCurrentPrice
            self.send(text_data=json.dumps({
                'Share_RD': DictString
            }))

        else:
            RD_Related_To_Shares.objects.create(Share_idx=target_share,
                                                RDDictString="{}",
                                                Supplied_by=user_idx_number
                                                )
            self.send(text_data=json.dumps({
                'Share_RD': "실시간 정보를 불러오는 중입니다"
            }))


        timer = threading.Timer(5, self.receive, args=[text_data])
        timer.start()



class KiwoomEventReceiver1(WebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        return
        #group send function need group name also as an argument



