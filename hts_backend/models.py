from __future__ import absolute_import
from __future__ import unicode_literals  # python 2.x support
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from passlib.hash import pbkdf2_sha256
from django.contrib.auth.models import User
import sys
from django.utils.encoding import *
import random
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from django.utils.translation import ugettext_lazy as _
from datetime import timezone, timedelta, datetime
import time
import django.utils
from datetime import datetime as dt
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

#시장의 여러 파라미터를 통제하는 곳이다. 각 파라미터의 의미를 아래에 기술한다.
@python_2_unicode_compatible
class MarketStatus(models.Model):
    current_DayTime = models.DateTimeField(auto_created=True, auto_now=True)
    current_Time = models.TimeField(auto_created=True, auto_now=True)
    update_time_setter = models.IntegerField()
    #update_time_setter : MarketStatus의 current_DayTime, currentTime을 업데이트하는데 사용된다.
    # 이 값을 업데이트 한 뒤 행을 저장하면, 자동으로 시간이 현재 시간이 된다.
    is_market_opened = models.BooleanField(default=False)
    is_market_exceptionally_closed = models.BooleanField(default=False)
    LossCutRate = models.FloatField(default=0.15)
    #로스컷 비중이다. 0.15인 경우, 담보금의 0.15배를 실잔금에서 제외한 금액이 로스컷 여유금이 된다.
    BasicFeeBuy = models.FloatField(default=0)
    BasicFeeSell = models.FloatField(default=0)
    #BasicFeeBuy, BasicFeeSell은 더이상 사용되지 않는다.
    SellFee = models.FloatField(default=0.03)
    #매도 수수료이다. 0.03은 0.03퍼센트임을 의미한다.
    BuyFee = models.FloatField(default=0.03)
    #매수 수수료이다.
    Max_Task = models.IntegerField(default=1)
    #최대 프로세스 수를 설정할 수 있다. 이 수가 n인 경우, 백그라운드 태스크의 멀티프로세스가 n개 생성되며,
    # 안정적인 운영을 위해 n개의 키움 계정이 필요하다

    OVNFee = models.FloatField(default=0.01)
    #오버나잇 수수료이다.
    LoanFee = models.FloatField(default=0.02)
    #대출 수수료이다.
    ExchangeRate_USD = models.IntegerField(default=1070)
    IpTcpAdr = models.CharField(max_length=200, default="192.168.35.60:8000")
    #공인 IP주소와 포트 정보를 담고 있으며, 이 값 또한 개발자 관리 페이지에서 수정 가능하다.
    # 이 값이 현재 서버의 값과 일치해야 소캣 연결을 정상적으로 할 수 있다.
    Is_Testing_Buy_Sell = models.BooleanField(default=False)
    #이 값이 참인 경우, 테스트 모드가 실행된다. 테스트모드시, 모든 시간이 '장중'으로 간주되어 종목의 거래가 가능해지고,
    #오버나잇 기능이 Off되어, 사자마자 파는 일이 없어지게 된다. (오버나잇 기능 활성화시, 장외시간때는 오버나잇 설정이
    #안 된 물량의 경우 모두 자동 매도되게 된다.

    current_DayTime.verbose_name = "현재 일시"
    current_Time.verbose_name = "현재 시간"
    is_market_opened.verbose_name = "장상태" #이 값이 참일 경우 장중 시간이며, 아닌 경우 장외시간이다.
    is_market_exceptionally_closed.verbose_name = "예외적 폐장 여부" #이 값을 참으로 설정하면, 시간과 무관하게 폐장된다.
    ExchangeRate_USD.verbose_name = "달러 환율"
    Is_Testing_Buy_Sell.verbose_name = "테스트 모드 여부 - 장시간 제한 해제, 오버나잇 잠금"

    @classmethod
    def exchRate(cls):
        obj = MarketStatus.objects.all().latest('id')
        return obj.ExchangeRate_USD

    class Meta:
        verbose_name = '시장상태' #MarketStatus의 한글 이름이다. 관리자 페이지에서 나오는 이름이다.


#회원가입 요청이 잠시 머무는 테이블이다. 회원가입 요청이 이곳에 저장되어 관리자의 승인을 기다리고, 승인시에 삭제된다.
#승인된 회원은 회원 리스트를 담고 있는 User_In 테이블로 이동하게 된다.
@python_2_unicode_compatible
class SignInReq(models.Model):
    user_idx = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, unique=True)
    user_pw = models.CharField(max_length=500)
    bank_id = models.CharField(max_length=100)
    user_pn = models.CharField(max_length=100, null=True)
    user_bank_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)

    signin_domain = models.CharField(max_length=300, null=True)

    user_id.verbose_name = "회원 ID"
    user_pn.verbose_name = "연락처"
    user_bank_name.verbose_name = "계좌번호"
    user_name.verbose_name = "회원명"
    signin_domain.verbose_name = "요청 도메인"
    #필요시, 회원가입을 요청한 도메인을 이곳에 담을 수 있다. 해당 행위는 프론트앤드단에서 시행되어야 한다.
    class Meta:
        verbose_name = '회원가입 요청'


#회원들의 명단과 정보를 저장 해 둔다. 양식은 회원가입 요청과 같다.
@python_2_unicode_compatible
class User_In(models.Model):
    user_idx = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, unique=True)
    user_pw = models.CharField(max_length=500)
    bank_id = models.CharField(max_length=100)
    user_pn = models.CharField(max_length=100, null=True)
    user_bank_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    init_signed_in_date = models.DateTimeField(auto_now_add=True)
    shut_down = models.BooleanField(default=False)

    signin_domain = models.CharField(max_length=300, null=True)

    behave_type = models.IntegerField(default=0)
    #is_accessed = models.BooleanField(default=False)

    user_id.verbose_name = "회원 ID"
    user_pn.verbose_name = "연락처"
    user_bank_name.verbose_name = "계좌번호"
    user_name.verbose_name = "회원명"
    init_signed_in_date.verbose_name = "가입일시"
    shut_down.verbose_name = "차단여부"
    signin_domain.verbose_name = "요청 도메인"

    #이 함수는 클래스 함수로서, 당일 회원 가입 한 회원의 수를 반환한다.
    @classmethod
    def day_number_of_signed_in(cls):
        timestamp = time.time()
        dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
        kmt = dt_utc + timedelta(hours=9)
        kmt = str(kmt)
        kmt = kmt.split(' ')
        today_dates = kmt[0]
        #today_dates에는 당일 날짜(연도-달-일)이 스트링 형태로 담겨져 있다.
        #  장고 파이썬상에서 날짜를 얻는 방법은 장고 공식 문서를 참조할 것.

        si = User_In.objects.all()
        summation_of_signed_in_today = 0
        if si:
            for x in si:
                this_dates = x.init_signed_in_date
                this_dates = str(this_dates)
                this_dates = this_dates.split(' ')
                this_dates = this_dates[0]
                if this_dates == today_dates:
                    summation_of_signed_in_today += 1
            return summation_of_signed_in_today
        else:
            return 0


    #로그인시 회원의 비밀번호가 올바른지 판단하는 함수. pbkdf2_sha256 라이브러리에 이미 속해있다.
    # 회원의 비밀번호는 회원 가입 시에 이미 passlib 함수로 인해 복호화 되는데,
    # 로그인시에 이 복호화 된 스트링의 원본 비밀번호와 입력받은 비밀번호를 비교하여, 옳은 경우 True를 반환한다.
    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.user_pw)

    class Meta:
        verbose_name = '회원목록'


#현재 접속중인 회원의 정보를 담는 곳이다. 특정 회원이 로그인하면 해당 회원에 관한 행이 추가되고, 로그아웃 시 삭제된다
class accessed_user(models.Model):
    #해당 회원 객체를 참조한다
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    #해당 회원의 자산을 참조한다
    user_asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
    )
    #해당 회원의 첫 접속일시
    access_time = models.DateTimeField(auto_now_add=True)
    #해당 회원의 현재 일시를 보여준다 (접속중에 특정 주기로 업데이트된다)
    accessing_time_now = models.DateTimeField(auto_now=True)
    #access_time ~ accessing_time_now 동안 거래 횟수가 없으면 behave_type을 '비정상'으로 설정한다. 아래 설명 참조
    #0 normal, 1 abnormal, 2 extremely abnormal . . . etc
    behave_type = models.IntegerField(default=0)

    #해당 Table의 행이 저장되거나 업데이트 될 때 자동으로 행 할 행동을 이렇게 정의할 수 있다. 아래 함수의 경우 그 행동은
    #다음과 같다. [ 행이 저장되기 전에, 해당 객체에서 회원의 자산을 불러와 저장한다.
    # 즉, 해당 객체의 회원 자산이 실제와 일치하도록 한다. ]
    def save(self, *args, **kwargs):
        self.user_asset = Asset.objects.get(user_idx=self.user_idx)
        # Run default save() method
        super(accessed_user, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '접속중인 회원'



#로그 기록을 담을 수 있는 테이블. 현재까지는 사용 되지 않는다.
@python_2_unicode_compatible
class Activity_Log(models.Model):
    log_idx = models.AutoField(primary_key=True)
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    uname = models.CharField(max_length=200, default='a')
    log_time = models.DateTimeField(auto_created=True, null=True)
    User_Activity = models.CharField(max_length=200)
    Market_Activity = models.CharField(max_length=200)
    System_Activity = models.CharField(max_length=200)
    Admin_Activity = models.CharField(max_length=200)

    user_idx.verbose_name = "회원색인"
    uname.verbose_name = "회원이름"
    log_time.verbose_name = "발생일시"
    User_Activity.verbose_name = "회원 활동"
    Market_Activity.verbose_name = "시장 활동"
    System_Activity.verbose_name = "시스템 활동"
    Admin_Activity.verbose_name = "관리자 활동"

    def save(self, *args, **kwargs):
        self.uname = self.user_idx.user_name
        # Run default save() method
        super(Activity_Log, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '회원, 시스템, 관리자 활동로그'


"""전 종목 (코스피, 코스닥, 코인) 목록을 담는 테이블. 유저(User_In) 테이블, 거래 내역(Transaction) 테이블과 함께 
충추적인 역활을 하는 테이블. """
@python_2_unicode_compatible
class Entire_Shares(models.Model):
    Share_Category = models.IntegerField()
    Share_Code = models.CharField(max_length=100)
    Share_Name = models.CharField(max_length=100)
    # current price, soaring_tumbling_rate, sell_prices, buy_prices api
    Is_feasible = models.BooleanField(default=True)

    Share_Category.verbose_name = "종목구분(0:코스피, 1:코인, 10:코스닥)"
    Share_Code.verbose_name = "종목 코드"
    Share_Name.verbose_name = "종목 이름"
    Is_feasible.verbose_name = "매매 가능 여부"

    class Meta:
        unique_together = (('Share_Category', 'Share_Code'),)
        verbose_name = '전체 종목 리스트'


#코스피 상위 종목들을 정리 해 놓는 테이블. 입력은 관리자 화면에서 수동으로 이루어지며, 전 종목 테이블과 같은 양식을 가짐
@python_2_unicode_compatible
class Top_Kospi(models.Model):
    Share_Category = models.IntegerField(default=0)
    Share_Code = models.CharField(max_length=100, default="a")
    Share_Name = models.CharField(max_length=100)
    # current price, soaring_tumbling_rate, sell_prices, buy_prices api
    Is_feasible = models.BooleanField(default=True)
    spk = models.IntegerField(default=0)
    ranking = models.IntegerField(default=0)

    Share_Category.verbose_name = "종목구분(0:코스피, 1:코인, 10:코스닥)"
    Share_Code.verbose_name = "종목 코드"
    Share_Name.verbose_name = "종목 이름"
    Is_feasible.verbose_name = "매매 가능 여부"

    def save(self, *args, **kwargs):
        shareEntry = Entire_Shares.objects.get(Share_Category=self.Share_Category, Share_Name=self.Share_Name)
        self.spk = shareEntry.id
        self.Share_Code = shareEntry.Share_Code
        # Run default save() method
        super(Top_Kospi, self).save(*args, **kwargs)

#코스닥 상위 종목들을 정리 해 놓는 테이블. 입력은 관리자 화면에서 수동으로 이루어지며, 전 종목 테이블과 같은 양식을 가짐
@python_2_unicode_compatible
class Top_Kosdq(models.Model):
    Share_Category = models.IntegerField(default=10)
    Share_Code = models.CharField(max_length=100, default="a")
    Share_Name = models.CharField(max_length=100)
    # current price, soaring_tumbling_rate, sell_prices, buy_prices api
    Is_feasible = models.BooleanField(default=True)
    spk = models.IntegerField(default=0)
    ranking = models.IntegerField(default=0)

    Share_Category.verbose_name = "종목구분(0:코스피, 1:코인, 10:코스닥)"
    Share_Code.verbose_name = "종목 코드"
    Share_Name.verbose_name = "종목 이름"
    Is_feasible.verbose_name = "매매 가능 여부"

    def save(self, *args, **kwargs):
        shareEntry = Entire_Shares.objects.get(Share_Category=self.Share_Category, Share_Name=self.Share_Name)
        self.spk = shareEntry.id
        self.Share_Code = shareEntry.Share_Code
        # Run default save() method
        super(Top_Kosdq, self).save(*args, **kwargs)

#코인 상위 종목들을 정리 해 놓는 테이블. 입력은 관리자 화면에서 수동으로 이루어지며, 전 종목 테이블과 같은 양식을 가짐
@python_2_unicode_compatible
class Top_Coins(models.Model):
    Share_Category = models.IntegerField(default=1)
    Share_Code = models.CharField(max_length=100, default="a")
    Share_Name = models.CharField(max_length=100, default="a")
    # current price, soaring_tumbling_rate, sell_prices, buy_prices api
    Is_feasible = models.BooleanField(default=True)
    spk = models.IntegerField(default=0)
    ranking = models.IntegerField(default=0)

    Share_Category.verbose_name = "종목구분(0:코스피, 1:코인, 10:코스닥)"
    Share_Code.verbose_name = "종목 코드"
    Share_Name.verbose_name = "종목 이름"
    Is_feasible.verbose_name = "매매 가능 여부"


    def save(self, *args, **kwargs):
        shareEntry = Entire_Shares.objects.get(Share_Category=1, Share_Code=self.Share_Code)
        self.spk = shareEntry.id
        self.Share_Name = shareEntry.Share_Name
        # Run default save() method
        super(Top_Coins, self).save(*args, **kwargs)


#주식 차트의 정보를 담아 두고 공유하는 테이블. 코스피, 코스닥의 차트 정보를 관리한다.
@python_2_unicode_compatible
class share_chart(models.Model):
    #종목의 정수 인덱스를 담아두고 이용한다.
    Spk = models.IntegerField(default=0)
    #종목의 실제 시장에서의 코드를 담고 활용한다.
    Share_Code = models.CharField(default="a", max_length=20)
    #종목의 코스닥/코스피 구분
    Share_Category = models.IntegerField(default=0)
    #Chart_Dict에 차트를 저장한다. 이는 하나의 커다란 딕셔너리를 스트링으로 변환 한 뒤, 저장하는 방식을 따른다.
    Chart_Dict = models.TextField(default="{}")
    #기준일 (현재 차트 작성일)을 기록한다. (ex : 20180330) 만일 차트가 최신이 아니고 and 유저로부터 조회 요청을 받으면
    #그 아래의 Should_be_updated_now를 참으로 바꾼다.
    StandardDate = models.IntegerField(default=0)
    Should_be_updated_now = models.BooleanField(default=True)

    #난수를 부여받는 값. 로드 밸런서로서, 멀티 프로세스가 각기 자신의 로드밸런스 넘버에 해당하는 작업을 하도록 한다.
    #즉, 해당 난수의 범위는 0 ~ 최대 멀티프로세스 수 -1 이다.
    C_load_balance_num = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        #종목 코드를 자동으로 찾아서 설정한다.
        shareEntry = Entire_Shares.objects.get(id=self.Spk)
        self.Share_Code = shareEntry.Share_Code
        #아래 코드는 관리자에 의해 설정된 최대 프로세스 수를 기반으로 로드밸런서를 설정하는 자동 저장 코드이다.
        MS = MarketStatus.objects.all()
        load_balance_num = 0
        for ms in MS:
            load_balance_num = random.randrange(0, ms.Max_Task)
        self.C_load_balance_num = load_balance_num
        # Run default save() method
        super(share_chart, self).save(*args, **kwargs)

#관심 그룹 테이블이다. 모든 회원은 관심그룹과, 해당 관심그룹에 속한 관심종목들을 가질 수 있다.
#관심 그룹은 비어있을 수 있다.
@python_2_unicode_compatible
class Share_Groups_Per_User(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    interest_group = models.CharField(max_length=100, null=False)

    user_idx.verbose_name = "회원색인"
    interest_group.verbose_name = "관심 그룹 명"
    class Meta:
        unique_together = (('user_idx', 'interest_group'),)
        verbose_name = '관심 그룹 목록'

#관심 그룹에 속한 관심종목을 담는 테이블이다 (따라서 관심 그룹을 외래키로 가진다)
@python_2_unicode_compatible
class Share_Interest(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    interest_group = models.ForeignKey(
        'Share_Groups_Per_User',
        on_delete=models.CASCADE,
    )
    Share_idx = models.ForeignKey(
        'Entire_Shares',
        on_delete=models.CASCADE,
    )
    Share_Category = models.IntegerField()
    Share_Code = models.CharField(max_length=100)
    Share_Name = models.CharField(max_length=100)

    user_idx.verbose_name = "회원색인"
    interest_group.verbose_name = "관심 그룹 명"

    Share_idx.verbose_name = "종목 색인"
    Share_Category.verbose_name = "종목 구분"
    Share_Code.verbose_name = "종목 코드"
    Share_Name.verbose_name = "종목 이름"

    class Meta:
        unique_together = (('user_idx', 'interest_group', 'Share_idx'),)
        verbose_name = '회원별 관심 그룹, 관심 종목'


##################################################################################################################

#PHASE TWO - ASSETS, HOLDINGS, TRANSACTION, DEPOSIT_WITHDRAW(ORDERS AND TREATS), LIST_NOT_DONE, PROFITS,
# LOANS(ORDER AND TREATS)

##################################################################################################################

#회원별로 회원의 자산 정보를 정리하는 테이블. 이중 금일 실현손익과 총손익은 매일 예치금으로 반영되고 0으로 초기화되며,
#평가손익은 오버나잇 물량을 제외하고 모두 초기화된다 (오버나잇 물량을 제외하고 반대매도 되기 때문에)
@python_2_unicode_compatible
class Asset(models.Model):
    #Asset_idx -it would use default Primary Key
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    Estimated_Profit = models.BigIntegerField(default=0)
    Realized_Profit = models.BigIntegerField(default=0)
    Total_Profit = models.BigIntegerField(default=0)
    losscut_left = models.BigIntegerField(default=0)

    poured_money = models.BigIntegerField(default=0)

    Actual_money_by_now = models.BigIntegerField(default=0)

    lended_loan_by_now = models.BigIntegerField(default=0)
    used_money = models.BigIntegerField(default=0)
    available_money = models.BigIntegerField(default=0)
    #대출 담보금이다. 대출을 여러번 하면 그만큼 담보금이 합산되고 가중된다
    # (대출시 담보금과 대출비율을 유저가 결정 할 수 있다.)
    Dam_bo_geum = models.BigIntegerField(default=0)

    user_idx.verbose_name = "회원색인"
    Estimated_Profit.verbose_name = "금일 평가손익"

    Realized_Profit.verbose_name = "금일 실현손익"
    Total_Profit.verbose_name = "금일 총손익"
    losscut_left.verbose_name = "로스컷 여유금"
    poured_money.verbose_name = "예치금"
    Actual_money_by_now.verbose_name = "실잔금"
    lended_loan_by_now.verbose_name = "대출금"
    used_money.verbose_name = "사용증거금"
    available_money.verbose_name = "이용가능금"

    def save(self, *args, **kwargs):
        hisHoldings = Holdings.objects.filter(user_idx=self.user_idx)
        sumOfEstiProfit = 0
        #회원 잔고 (회원들이 가진 주식)을 기반으로 회원들의 평가 손익을 계산하여 반영
        for x in hisHoldings:
            sumOfEstiProfit += x.Estimated_Profit_In_This_Stock
        self.Estimated_Profit = sumOfEstiProfit

        #평가손익과 실현손익 합으로 총 손익과 현재 실잔금을 계산. 이용가능금은 대출금과 실잔금의 합에서
        # 사용된 금액을 제한 것.
        self.Total_Profit = self.Realized_Profit + self.Estimated_Profit
        self.Actual_money_by_now = self.poured_money + self.Total_Profit #self.poured_money : Ye-Chi-Geum
        self.available_money = self.lended_loan_by_now + self.Actual_money_by_now - self.used_money

        #관리자가 설정한 로스컷 비율을 기반으로 로스컷 잔여금을 계산.
        lossRate = 0
        x = MarketStatus.objects.all()
        for k in x:
            lossRate = k.LossCutRate

        self.losscut_left = self.Actual_money_by_now - lossRate*self.Dam_bo_geum
        # Run default save() method
        super(Asset, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '회원 자산'


#공지사항을 담는 테이블이다. 팝업 공지사항으로 하고 싶은 경우 팝업 여부를 참으로 설정한다.
@python_2_unicode_compatible
class info(models.Model):
    dtime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=250, default='내용을 입력 하세요')
    contents = models.TextField(default="내용을 입력 하세요")
    is_pop = models.BooleanField(default=False)

    is_pop.verbose_name = "팝업 여부"

    class Meta:
        verbose_name = '공지사항'

#회원들이 보유한 주식 정보를 담는 테이블. '어떤 종목'을 '얼마에' '어느 수량만큼' 샀으며, 지금 가격은 얼마인지 저장.
@python_2_unicode_compatible
class Holdings(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    Share_idx = models.ForeignKey(
        'Entire_Shares',
        on_delete=models.CASCADE,
    )
    Share_Name = models.CharField(max_length=100, null=True, default='a')
    Holding_Quantities = models.FloatField(default=0)
    Price_Per_Single = models.FloatField(default=0) #checked

    Total_Bought_Prices = models.FloatField(default=0)
    Total_Current_Prices = models.FloatField(default=0)
    Estimated_Profit_In_This_Stock = models.FloatField(default=0) #checked

    #또한 오버나잇에 대한 정보도 담고 있다. 해당 종목에 대해 오버나잇 신청 수량과, 연속으로 앞으로 몇 번 신청 가능한지
    #담고 있다.
    OverNight_Quant = models.FloatField(default=0)
    OverNight_Rest_Days = models.IntegerField(default=30)

    #지금은 사용되지 않는 값이다. 별개의 함수로 OverNight_Quant를 0으로 설정함으로서 해당 변수의 기능을 대체한다.
    Should_OvN_be_released = models.BooleanField(default=False)


    Share_Name.verbose_name = "종목명"
    Holding_Quantities.verbose_name = "보유수량"
    Price_Per_Single.verbose_name = "평단가"

    Total_Bought_Prices.verbose_name = "총매입액"
    Total_Current_Prices.verbose_name = "현재자산"
    Estimated_Profit_In_This_Stock.verbose_name = "평가손익"

    OverNight_Quant.verbose_name = "오버나잇 신청 수량"
    OverNight_Rest_Days.verbose_name = "오버나잇 남은 연속 횟수 (최대 30회)"
    Should_OvN_be_released.verbose_name = "오버나잇 예외적 해제 여부"

    def save(self, *args, **kwargs):
        #종목 이름과 해당 종목서 평가손익, 평단가를 자동으로 계산
        self.Share_Name = self.Share_idx.Share_Name
        self.Estimated_Profit_In_This_Stock = self.Total_Current_Prices - self.Total_Bought_Prices
        self.Price_Per_Single = float(self.Total_Bought_Prices/self.Holding_Quantities)

        super(Holdings, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '회원별 잔고 목록'


#거래 내역을 담는 중추 테이블. 해당 테이블에 입,출금, 매수,매도의 주문과 체결 정보가 모두 담긴다 (단, 대출은 별도)
@python_2_unicode_compatible
class Transaction(models.Model):
    #Transaction Idx - it would use default Primary Key
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    Share_idx = models.ForeignKey(
        'Entire_Shares',
        on_delete=models.CASCADE,
    )
    Share_Name = models.CharField(max_length=100, default='-')
    user_id = models.CharField(max_length=50, default="-")
    TransDateTime = models.DateTimeField(auto_created=True, auto_now=True, null=True)
    #주문 타입이다. 입금신청, 출금신청, 매수주문, 매도주문으로 구성된다.
    Order_Type = models.IntegerField(default=-1) #0:buyorder, 1:sellorder, 2:deposit order, 3:withdraw order,
    #체결 타입이다. 평상시엔 -1이다가 위의 주문이 체결 될 경우 다음 값들을 지닌 채로 하나의 행이 새로 생성된다.
    TreatStatus = models.IntegerField(default=-1) #0:buyDone, 1:sellDone, 2:depositDone, 3:withdrawDone,

    Order_Quant = models.FloatField(default=0)
    Order_Price = models.FloatField(default=0)

    Trans_Quant = models.FloatField(default=0)
    Trans_Price = models.FloatField(default=0)

    Fee_In_Trans = models.FloatField(default=0)

    #종목의 매도 때만 사용되는 특성 값.
    Selling_Profit = models.FloatField(default=0) # Estimated_Profit in Stock Transactions
    Realized_Profit = models.FloatField(default=0) # Selling_Profit- Fee_In_Trans

    #입출금때만 사용되는 특성 값.
    Deposit_Money = models.IntegerField(default=0)

    #Ref - Actual_money_by_now in 'Asset'
    Actual_money = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
    )
    OtherMsg = models.CharField(max_length=100, default=' ')

    user_idx.verbose_name = "회원 색인"
    Share_idx.verbose_name = "종목 색인"
    TransDateTime.verbose_name = "거래 일시"
    Order_Type.verbose_name = "주문 타입 (0-매수,1-매도,2-입금,3-출금)"
    TreatStatus.verbose_name = "처리 타입 (0-매수,1-매도,2-입금,3-출금)"
    Order_Quant.verbose_name = "주문수량"
    Order_Price.verbose_name = "주문가격"

    Trans_Quant.verbose_name = "체결 수량"
    Trans_Price.verbose_name = "체결 가격"
    Fee_In_Trans.verbose_name = "수수료"
    Selling_Profit.verbose_name = "매도 수익"
    Realized_Profit.verbose_name = "수수료 + 매도수익"

    Deposit_Money.verbose_name = "입/출금액"

    #Ref - Actual_money_by_now in 'Asset'
    Actual_money.verbose_name = "실잔금"
    OtherMsg.verbose_name = "비고"

    class Meta:
        verbose_name = '총 거래 내역: 입/출금, 매수/매도 주문 요청과 처리 내역'

    def save(self, *args, **kwargs):
        self.Share_Name = self.Share_idx.Share_Name
        self.user_id = self.user_idx.user_id
        super(Transaction, self).save(*args, **kwargs)

#미체결 목록이다. 최초 종목의 매수, 매도 주문이 들어오면, 이 테이블로 저장 되게 된다.
#매수를 예시로 설명하면 해당 절차는 다음과 같다.
"""
뷰 함수에서 OrderBuy 함수 호출 -> Transaction에 주문 내역 작성, 미체결 목록 작성 -> 실시간으로 돌아가는 Celery Task인 
Order_Treatment_Alg이 해당 미체결 목록을 '처리'하고 제거한다. 해당 과정에서 주문 처리 행이 Transaction에 추가된다.
또한 고객의 주식 잔고, 자산등을 변화시킨다. 
"""
#즉, 아래의 미체결 테이블은 주문 처리 과정 중간에서 중요한 역할을 수행한다.
@python_2_unicode_compatible
class List_Not_Done(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    Share_idx = models.ForeignKey(
        'Entire_Shares',
        on_delete=models.CASCADE,
    )
    Transaction_idx = models.ForeignKey(
        'Transaction',
        on_delete=models.CASCADE,
    )
    Order_Type = models.IntegerField(default=0)
    Order_Price = models.FloatField(default=0)
    Order_Quant = models.FloatField(default=0)
    Share_Name = models.CharField(max_length=100, null=True, default='a')
    Is_Cancelled = models.BooleanField(default=False) #?


    user_idx.verbose_name = "회원색인"
    Share_idx.verbose_name = "종목색인"
    Transaction_idx.verbose_name = "거래색인"
    Order_Type.verbose_name = "주문타입(0-매수/1-매도)"
    Order_Price.verbose_name = "주문가격"
    Order_Quant.verbose_name = "주문수량"
    Share_Name.verbose_name = "종목이름"
    Is_Cancelled.verbose_name = "취소여부"

    def save(self, *args, **kwargs):
        self.Share_Name = self.Share_idx.Share_Name
        super(List_Not_Done, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '미체결 매수/매도 주문 내역'


#거래 내역의 서브 테이블로서, 입출금에 관한 기록만 따로 저장한다. 입출금 계산과 조회의 편의를 위함이다.
@python_2_unicode_compatible
class Deposit_Withdraw_Order_Done_List(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    user_id = models.CharField(max_length=50, default="-")
    Transaction_idx = models.ForeignKey(
        'Transaction',
        on_delete=models.CASCADE,
    )
    Order_Money_Plus_Minus = models.IntegerField(default=2)

    Order = models.IntegerField(default=2) #2: Deposit Order, 3:Withdraw Order
    TransDateTime = models.DateTimeField(auto_now_add=True)

    #The 'Order Type' left this fields blanks
    MoneyBefore = models.FloatField(default=0) #Ref from Asset
    PlusMinus = models.FloatField(default=0)
    MoneyNow = models.FloatField(default=0)

    TransactionDependency = models.CharField(max_length=100, default='')

    user_idx.verbose_name = "회원색인"
    Transaction_idx.verbose_name = "거래색인"
    Order_Money_Plus_Minus.verbose_name = "주문액수(+/-로 입/출금 액수 표시)"
    Order.verbose_name = "주문타입(2-입금, 3-출금)"
    TransDateTime.verbose_name = "요청/체결 일시"

    #The 'Order Type' left this fields blanks
    MoneyBefore.verbose_name = "체결 전 실잔액"
    PlusMinus.verbose_name = "체결 액수(+/-로 입/출금 액수 표시)"
    MoneyNow.verbose_name = "체결 후 실잔액"

    TransactionDependency.verbose_name = "거래쌍"

    #당일 모든 고객의 총 입금을 반환하는 함수이다.
    @classmethod
    def day_m_i(cls):
        timestamp = time.time()
        dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
        # 한국 시간으로 조정
        kmt = dt_utc + timedelta(hours=9)
        kmt = str(kmt)
        kmt = kmt.split(' ')
        today_dates = kmt[0]

        m_i = Deposit_Withdraw_Order_Done_List.objects.filter(Order=2).exclude(PlusMinus=0)
        summation_of_moneyin_today = 0
        if m_i:
            for x in m_i:
                this_dates = x.TransDateTime + timedelta(hours=9)
                this_dates = str(this_dates)
                this_dates = this_dates.split(' ')
                this_dates = this_dates[0]
                if this_dates == today_dates:
                    summation_of_moneyin_today += x.PlusMinus
            return summation_of_moneyin_today
        else:
            return 0

    #당일 모든 고객의 총 출금을 반환하는 함수이다.
    @classmethod
    def day_m_o(cls):
        timestamp = time.time()
        dt_utc = datetime.fromtimestamp(timestamp, timezone.utc)
        #한국 시간으로 조정
        kmt = dt_utc + timedelta(hours=9)
        kmt = str(kmt)
        kmt = kmt.split(' ')
        today_dates = kmt[0]

        m_o = Deposit_Withdraw_Order_Done_List.objects.filter(Order=3).exclude(PlusMinus=0)
        if m_o:
            summation_of_moneyout_today = 0
            for x in m_o:
                this_dates = x.TransDateTime + timedelta(hours=9)
                this_dates = str(this_dates)
                this_dates = this_dates.split(' ')
                this_dates = this_dates[0]
                if this_dates == today_dates:
                    summation_of_moneyout_today += x.PlusMinus
            return -summation_of_moneyout_today
        else:
            return 0

    def save(self, *args, **kwargs):
        #입출금량을 기준으로 현재 자산을 업데이트 한다. (저장시마다 자동으로 수행)
        x = Asset.objects.get(user_idx=self.user_idx)
        self.user_id = self.user_idx.user_id
        self.MoneyBefore = x.Actual_money_by_now
        self.MoneyNow = self.MoneyBefore + self.PlusMinus
        x.poured_money = x.poured_money + self.PlusMinus
        x.Actual_money_by_now = self.MoneyNow
        x.save()
        # Run default save() method
        super(Deposit_Withdraw_Order_Done_List, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '총 입/출금 요청과 처리 내역'


#대출 내역을 남기는 테이블이다.
@python_2_unicode_compatible
class Loan_Order_Done(models.Model):
    #Loan Trans Idx - It would use auto pk
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    user_id = models.CharField(max_length=50, default="-")
    Stock_Loan_Rate = models.IntegerField(default=0) #Loan Rate
    Dam_bo_geum = models.IntegerField(default=0)
    #50, 100, 200, 300, 500, 1000, 2000, 3000 : 15%
    #Actual Money by now - 15% of Dam_bo_geum = losscut margin - if the user loose all those margin,
    # the system will sell out all the stocks the user has
    Is_Done = models.BooleanField(default=False) #if it is true, that means the order was treated properly
    Order_Date = models.DateTimeField(auto_created=True, auto_now_add=True)
    Done_Date = models.CharField(default="-", max_length=50)


    user_idx.verbose_name = "회원색인"
    Stock_Loan_Rate.verbose_name = "대출금비율"
    Dam_bo_geum.verbose_name = "담보금"
    # 50, 100, 200, 300, 500, 1000, 2000, 3000 : 15%
    # Actual Money by now - 15% of Dam_bo_geum = losscut margin - if the user loose all those margin,
    # the system will sell out all the stocks the user has
    Is_Done.verbose_name = "처리여부"
    Order_Date.verbose_name = "주문 일시"
    Done_Date.verbose_name = "처리 일시" #Should be Specified by Program
    #Actual Money by now -  Ref from 'Asset'
    #Total Available money - Ref from 'Asset'

    def save(self, *args, **kwargs):
        self.user_id = self.user_idx.user_id
        super(Loan_Order_Done, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '대출 요청과 처리 내역'


#매일 매일 고객의 수익을 정산하여 고객별로 행을 생성하는 테이블이다. (고객 수익 정산 테이블) 매일 정해진 시간에 Celery
#가 자동으로 정산하기 때문에, 해당 테이블을 이용하여 기간별 수익등을 회원별로 알아 낼 수 있다.
#해당 정산 후 해당 고객의 실현손익은 다음날 0으로 초기화 된다.
@python_2_unicode_compatible
class Profit(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    Date_jeong_san = models.DateField(auto_created=True, auto_now=True)
    #Needs Jeong-San_Process on total Market
    Total_Estimated_Profit_From_Stocks = models.FloatField(default=0)
    #Total_Fees_In_Transaction = models.BigIntegerField(default=0)
    Total_Realized_Profit = models.FloatField(default=0) #show total_realized on users screen
    TOTAL_PROFIT_BY_NOW = models.FloatField(default=0)
    Real_Profit_Today = models.FloatField(default=0)

    user_idx.verbose_name = "회원색인"
    Date_jeong_san.verbose_name = "정산일시"
    Total_Estimated_Profit_From_Stocks.verbose_name = "금일 평가손익"
    #Total_Fees_In_Transaction.verbose_name = "금일 수수료합"
    Total_Realized_Profit.verbose_name = "금일 실현손익합"

    Real_Profit_Today.verbose_name = "금일 총 손익"
    TOTAL_PROFIT_BY_NOW.verbose_name = "총손익"


    #고객의 현재까지의 총 손익을 저장시에 계산한다.
    def save(self,*args, **kwargs):
        self.Real_Profit_Today = self.Total_Estimated_Profit_From_Stocks + self.Total_Realized_Profit
        # Run default save() method
        objs = Profit.objects.filter(user_idx=self.user_idx) #.latest('Date_jeong_san')

        if objs:
            obj = Profit.objects.filter(user_idx=self.user_idx).latest('Date_jeong_san')
            self.TOTAL_PROFIT_BY_NOW = obj.TOTAL_PROFIT_BY_NOW + self.Real_Profit_Today

            kmt = obj.Date_jeong_san
            kmtstr = str(kmt)
            kmtstr = kmtstr.split(' ')
            # print(kmtstr)
            dates1 = kmtstr[0]

            timestamp = time.time()
            #dt
            dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
            kmt = dt_utc + timedelta(hours=9)
            kmtstr = str(kmt)
            kmtstr = kmtstr.split(' ')
            dates2 = kmtstr[0]
            if dates1 == dates2:
                obj.delete()
            super(Profit, self).save(*args, **kwargs)
        else:
            self.TOTAL_PROFIT_BY_NOW = self.Real_Profit_Today
            super(Profit, self).save(*args, **kwargs)


    class Meta:
        verbose_name = '회원별 일별 수익'

##################################################################################################################

#API receiving Databases

##################################################################################################################

#이 테이블은 주식의 모든 정보를 장외에는 정적, 장중에는 실시간으로 받아 저장하는 중요한 테이블이다. 해당 테이블은 주로
#consumders.py의 RealTime_basic_info_list_holdings클래스와 Kiwoom 클래스, tasks.py의 RD_Modifying에서 다루어 진다
@python_2_unicode_compatible
class RD_Related_To_Shares(models.Model):
    #종목 색인
    Share_idx = models.ForeignKey(
        'Entire_Shares',
        on_delete=models.CASCADE,
    )
    #종목 코드
    Share_Code = models.CharField(max_length=50, default='a')

    #해당 종목의 모든 정보를 딕셔너리 형태의 스트링으로 RDictString에 저장 한다.
    RDDictString = models.TextField(default="")
    Supplied_by = models.IntegerField(default=-1)
    #고객이 해당 종목을 조회 중일 때, 정기적으로 신호를 보낸다. 해당 신호가 오면 아래 값을 참으로 바꾸고,
    # 해당 값이 참일 경우 RDDictString을 업데이트 한다. (요청 수를 최소화하고 리소스 할당을 효율적으로 하기 위함)
    Should_be_updated_now = models.BooleanField(default=True)

    #멀티프로세스용 로드벨런서
    RD_load_balance_num = models.IntegerField(default=0)


    class Meta:
        verbose_name = '조회중인 종목 정보 큐'

    def save(self,*args, **kwargs):
        self.Share_Code = self.Share_idx.Share_Code
        super(RD_Related_To_Shares, self).save(*args, **kwargs)


############################################## ADMIN WEB PAGE #####################################################


#모든 관리자(파트너)의 명단을 담고있다. 해당 양식은 회원 양식과 매우 흡사하다.
@python_2_unicode_compatible
class admins(models.Model):
    admin_id = models.CharField(max_length=50, unique=True)
    admin_pw = models.CharField(max_length=500)
    bank_id = models.CharField(max_length=100)
    admin_pn = models.CharField(max_length=100, null=True)
    admin_bank_name = models.CharField(max_length=50)
    admin_name = models.CharField(max_length=50)
    profit_ratio = models.FloatField(default=0.3)
    grant = models.IntegerField(default=0) #0 : super admin, 1:admin, 2 . . etc

    admin_id.verbose_name = "파트너 ID"
    admin_pn.verbose_name = "파트너 연락처"
    admin_bank_name.verbose_name = "계좌번호"
    admin_name.verbose_name = "파트너 이름"
    profit_ratio.verbose_name = "수익률"

    def verify_password(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.admin_pw)

    def save(self, *args, **kwargs):
        self.admin_pw = pbkdf2_sha256.encrypt(self.admin_pw, rounds=12000, salt_size=32)
        super(admins, self).save(*args, **kwargs)


    class Meta:
        verbose_name = '파트너, 관리자 목록'


#GrantTreeStructure에 소속되지 않으면 관리자를 열람 할 수 없다.
#  '어떤 관리자가' '어떤 관리자'에 대한 정보를 열람 할 수 있는지 관리자 객체-관리자 객체의 쌍으로 저장한 테이블이다.
class GrantTreeStructure(models.Model):
    admin_idx = models.ForeignKey(
        'admins',
        models.SET_NULL,
        blank=True,
        null=True,
    )
    admin_id1 = models.CharField(max_length=50, default='')
    admin_refer_idx = models.ForeignKey(
        'admins',
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='admin_refer_idx'
    )
    admin_id2 = models.CharField(max_length=50, default='')

    admin_id1.verbose_name = "파트너 아이디 (열람자)"
    admin_id2.verbose_name = "파트너 아이디 (피열람자"

    def save(self, *args, **kwargs):
        self.admin_idx = admins.objects.get(admin_id=self.admin_id1)
        self.admin_refer_idx = admins.objects.get(admin_id=self.admin_id2)
        super(GrantTreeStructure, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '파트너 열람 권한 표'

#도메인을 저장한다. 도메인은 어떤 관리자(파트너)에 소속되어 있다.
@python_2_unicode_compatible
class DomainQ(models.Model):
    Domain = models.CharField(max_length=200, default="a")
    is_used = models.BooleanField(default=False)
    admin_idx = models.ForeignKey(
        'admins',
        on_delete=models.CASCADE,
    )

#파트너 출금 기록을 저장한다.
@python_2_unicode_compatible
class M_Out_Q(models.Model):
    admin_idx = models.ForeignKey(
        'admins',
        on_delete=models.CASCADE,
    )
    reqMoment = models.DateTimeField(auto_now_add=True)
    moneyQuant = models.FloatField(default=0)


#회사의 모든 자산 통계를 저장하는 테이블이다.
@python_2_unicode_compatible #main target to be shown on stat screen view
class Profit_Stat(models.Model):

    day = models.DateTimeField(auto_now_add=True) #금일 날짜
    day_In = models.FloatField(default=0) #금일 입금
    day_Out = models.FloatField(default=0) #금일 출금
    day_Profit = models.FloatField(default=0) #금일 수익
    sonic_d = models.FloatField(default=0) #금일 손익
    admin_in_d = models.FloatField(default=0) #금일 관리자 입금 (에러 발생 시 관리자가 직접 특정 회원에게 입,출금처리)
    admin_out_d = models.FloatField(default=0) #금일 관리자 출금
    partner_jeongsan_d = models.FloatField(default=0) #금일 파트너 정산금
    new_user_d = models.IntegerField(default=0) #금일 신규 가입자 수

    #전날 통계 (특성의 양식은 금일의 것과 동일)
    yesterday = models.DateTimeField(default=django.utils.timezone.now)
    yesterday_In = models.FloatField(default=0)
    yesterday_Out = models.FloatField(default=0)
    yesterday_Profit = models.FloatField(default=0)
    sonic_y = models.FloatField(default=0)
    admin_in_y = models.FloatField(default=0)
    admin_out_y = models.FloatField(default=0)
    partner_jeongsan_y = models.FloatField(default=0)
    new_user_y = models.IntegerField(default=0)

    #그저께 통계
    daybefore = models.DateTimeField(default=django.utils.timezone.now)
    daybefore_In = models.FloatField(default=0)
    daybefore_Out = models.FloatField(default=0)
    daybefore_Profit = models.FloatField(default=0)
    sonic_db = models.FloatField(default=0)
    admin_in_db = models.FloatField(default=0)
    admin_out_db = models.FloatField(default=0)
    partner_jeongsan_db = models.FloatField(default=0)
    new_user_db = models.IntegerField(default=0)

    #이번달 통계 (달이 변경되면 집계 시작, 달이 또 변경되면 집계를 종료하고 아래의'이전 달'로 이전)
    monthNow = models.CharField(default="None", max_length=10)
    monthNow_In = models.FloatField(default=0)
    monthNow_Out = models.FloatField(default=0)
    monthNow_Profit = models.FloatField(default=0)
    sonic_m = models.FloatField(default=0)
    admin_in_m = models.FloatField(default=0)
    admin_out_m = models.FloatField(default=0)
    partner_jeongsan_m = models.FloatField(default=0)
    new_user_m = models.IntegerField(default=0)

    #이전 달 통계
    monthLate = models.CharField(default="None", max_length=10)
    monthLate_In = models.FloatField(default=0)
    monthLate_Out = models.FloatField(default=0)
    monthLate_Profit = models.FloatField(default=0)
    sonic_ml = models.FloatField(default=0)
    admin_in_ml = models.FloatField(default=0)
    admin_out_ml = models.FloatField(default=0)
    partner_jeongsan_ml = models.FloatField(default=0)
    new_user_ml = models.IntegerField(default=0)

    #총 입금과 총 출금
    TOTAL_IN_BY_NOW = models.FloatField(default=0)
    TOTAL_OUT_BY_NOW = models.FloatField(default=0)


    #아직 구현되지 않는 가상의 함수. 위 테이블의 무결성을 시험하는 함수이다.
    def analizeIntegrity(self, *args, **kwargs):
        return

    #날짜를 기준으로 집계하고 값을 전날, 혹은 전달로 넘기는 코드이다 (행을 저장 할 때마다 자동으로 시행)
    #이러한 값을 얻어오는 것은 consumers.py의 admin_socket 클래스에서 담당한다 (관리자 소캣에서 주기적으로 업데이트)
    def save(self, *args, **kwargs):
        if Profit_Stat.objects.all():
            # 초기에는 설정 자체를 별도로
            obj = Profit_Stat.objects.all().latest('day')
            objDate = obj.day
            objDate += timedelta(hours=9)

            timestamp = time.time()
            #dt
            dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
            kmt = dt_utc + timedelta(hours=9)
            kmtstr = str(kmt)
            kmtstr = kmtstr.split(' ')
            dates1 = kmtstr[0]
            dates1 = dates1.split('-')

            self.day = kmt - timedelta(hours=9)

            kmtYest = kmt - timedelta(days=1)
            kmtstr = str(kmtYest)
            kmtstr = kmtstr.split(' ')
            dates0 = kmtstr[0]
            dates0 = dates0.split('-')
            self.monthNow = dates1[1]
            if dates1[1] != dates0[1]:
                # string typed month
                self.monthLate = dates0[1]
                self.monthLate_Profit = obj.monthNow_Profit
                self.monthLate_In = obj.monthNow_In
                self.monthLate_Out = obj.monthNow_Out
                self.sonic_ml = obj.sonic_m
                self.admin_in_ml = obj.admin_in_m
                self.admin_out_ml = obj.admin_out_m
                self.partner_jeongsan_ml = obj.partner_jeongsan_m
                self.new_user_ml = obj.new_user_m

                self.monthNow_In = self.day_In
                self.monthNow_Out = self.day_Out

                self.day_Profit = self.day_In - self.day_Out

                self.monthNow_Profit = self.day_Profit
                self.admin_in_m = self.admin_in_d
                self.admin_out_m = self.admin_out_d
                self.partner_jeongsan_m = self.partner_jeongsan_d

                self.sonic_d = self.day_Profit - self.partner_jeongsan_d
                self.sonic_m = self.sonic_d
                self.new_user_m = self.new_user_d

                self.yesterday = obj.day
                self.yesterday_In = obj.day_In
                self.yesterday_Out = obj.day_Out
                self.yesterday_Profit = obj.day_Profit
                self.sonic_y = obj.sonic_d
                self.admin_in_y = obj.admin_in_d
                self.admin_out_y = obj.admin_out_d
                self.partner_jeongsan_y = obj.partner_jeongsan_d
                self.new_user_y = obj.new_user_d

                self.daybefore = obj.yesterday
                self.daybefore_In = obj.yesterday_In
                self.daybefore_Out = obj.yesterday_Out
                self.daybefore_Profit = obj.yesterday_Profit
                self.sonic_db = obj.sonic_y
                self.admin_in_db = obj.admin_in_y
                self.admin_out_db = obj.admin_out_y
                self.partner_jeongsan_db = obj.partner_jeongsan_y
                self.new_user_db = obj.new_user_y

            else:
                self.monthLate = obj.monthLate
                self.monthLate_Profit = obj.monthLate_Profit
                self.monthLate_In = obj.monthLate_In
                self.monthLate_Out = obj.monthLate_Out
                self.sonic_ml = obj.sonic_ml
                self.admin_in_ml = obj.admin_in_ml
                self.admin_out_ml = obj.admin_out_ml
                self.partner_jeongsan_ml = obj.partner_jeongsan_ml
                self.new_user_ml = obj.new_user_ml

                kmtstr = str(self.day)
                kmtstr = kmtstr.split(' ')
                dates1 = kmtstr[0]

                kmtstr = str(obj.day)
                kmtstr = kmtstr.split(' ')
                dates2 = kmtstr[0]

                if dates2 != dates1:
                    self.monthNow_In = obj.monthNow_In + self.day_In
                    self.monthNow_Out = obj.monthNow_Out + self.day_Out

                    self.day_Profit = self.day_In - self.day_Out

                    self.monthNow_Profit = obj.monthNow_Profit + self.day_Profit
                    self.admin_in_m = obj.admin_in_m + self.admin_in_d
                    self.admin_out_m = obj.admin_out_m + self.admin_out_d
                    self.partner_jeongsan_m = obj.partner_jeongsan_m + self.partner_jeongsan_d

                    self.sonic_d = self.day_Profit - self.partner_jeongsan_d
                    self.sonic_m = obj.sonic_m + self.sonic_d
                    self.new_user_m = obj.new_user_m + self.new_user_d

                    self.yesterday = obj.day
                    self.yesterday_In = obj.day_In
                    self.yesterday_Out = obj.day_Out
                    self.yesterday_Profit = obj.day_Profit
                    self.sonic_y = obj.sonic_d
                    self.admin_in_y = obj.admin_in_d
                    self.admin_out_y = obj.admin_out_d
                    self.partner_jeongsan_y = obj.partner_jeongsan_d
                    self.new_user_y = obj.new_user_d

                    self.daybefore = obj.yesterday
                    self.daybefore_In = obj.yesterday_In
                    self.daybefore_Out = obj.yesterday_Out
                    self.daybefore_Profit = obj.yesterday_Profit
                    self.sonic_db = obj.sonic_y
                    self.admin_in_db = obj.admin_in_y
                    self.admin_out_db = obj.admin_out_y
                    self.partner_jeongsan_db = obj.partner_jeongsan_y
                    self.new_user_db = obj.new_user_y

                elif dates1 == dates2:
                    if Profit_Stat.objects.all().exclude(day=obj.day):
                        obj = Profit_Stat.objects.all().exclude(day=obj.day).latest('day')
                    self.TOTAL_OUT_BY_NOW = obj.TOTAL_OUT_BY_NOW
                    self.TOTAL_IN_BY_NOW = obj.TOTAL_IN_BY_NOW
                    self.monthNow_In = obj.monthNow_In + self.day_In
                    self.monthNow_Out = obj.monthNow_Out + self.day_Out

                    self.day_Profit = self.day_In - self.day_Out

                    self.monthNow_Profit = obj.monthNow_Profit + self.day_Profit
                    self.admin_in_m = obj.admin_in_m + self.admin_in_d
                    self.admin_out_m = obj.admin_out_m + self.admin_out_d
                    self.partner_jeongsan_m = obj.partner_jeongsan_m + self.partner_jeongsan_d

                    self.sonic_d = self.day_Profit - self.partner_jeongsan_d
                    self.sonic_m = obj.sonic_m + self.sonic_d
                    self.new_user_m = obj.new_user_m + self.new_user_d

            self.TOTAL_OUT_BY_NOW = obj.TOTAL_OUT_BY_NOW + self.day_Out
            self.TOTAL_IN_BY_NOW = obj.TOTAL_IN_BY_NOW + self.day_In
            super(Profit_Stat, self).save(*args, **kwargs)
        else:
            timestamp = time.time()
            dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
            kmt = dt_utc + timedelta(hours=9)
            kmtstr = str(kmt)
            kmtstr = kmtstr.split(' ')
            dates1 = kmtstr[0]
            dates1 = dates1.split('-')

            kmtYest = kmt - timedelta(days=1)
            kmtstr = str(kmtYest)
            kmtstr = kmtstr.split(' ')
            dates0 = kmtstr[0]
            dates0 = dates0.split('-')
            self.monthNow = dates1[1]

            self.yesterday = kmtYest #- timedelta(hours=9)
            self.monthNow_In += self.day_In
            self.monthNow_Out += self.day_Out

            self.day_Profit = self.day_In - self.day_Out

            self.monthNow_Profit += self.day_Profit
            self.admin_in_m += self.admin_in_d
            self.admin_out_m += self.admin_out_d
            self.partner_jeongsan_m += self.partner_jeongsan_d

            self.sonic_d = self.day_Profit - self.partner_jeongsan_d
            self.sonic_m += self.sonic_d
            self.new_user_m += self.new_user_d

            self.TOTAL_OUT_BY_NOW = self.day_Out
            self.TOTAL_IN_BY_NOW = self.day_In
            super(Profit_Stat, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '수익 통계'


#파트너 통계이다. 회원의 금일 입출금, 전날과 금일의 총 보유 자산등을 통해서 회사와, 회사로부터 분배되는 파트너 전산금을
#계산한다.
@python_2_unicode_compatible  # main target to be shown on stat screen view
class Profit_Stat_Partner(models.Model):
    admin_idx = models.ForeignKey(
        'admins',
        on_delete=models.CASCADE,
    ) #어떤 파트너인지를 명시하는 색인
    admin_id = models.CharField(max_length=50, default="a")

    day = models.DateTimeField(auto_now_add=True)  # standard setting

    day_In = models.FloatField(default=0) #이것은 외부의 입력을 따른다
    day_Out = models.FloatField(default=0)

    users_total_yest = models.FloatField(default=0) #전날 회원 총 금액
    users_total_today = models.FloatField(default=0)

    profit_ratio = models.FloatField(default=0) #파트너별 수익률

    sonic = models.FloatField(default=0)
    commission = models.FloatField(default=0)
    partner_out = models.FloatField(default=0)

    #수익률을 기반으로 한 금일 정산금
    jeongsan_today = models.FloatField(default=0)
    # 정기적으로 일별 정산 합을 regular_total_jeongsan에 담고,
    # 정산이 끝나면 0짜리 새 행을 만든다. 기존의 regular_total_jeongsan은 건드리지 않는다.
    regular_total_jeongsan = models.FloatField(default=0)

    # max 30

    def save(self, *args, **kwargs):
        self.admin_id = self.admin_idx.admin_id
        if Profit_Stat_Partner.objects.filter(admin_idx=self.admin_idx):
            # 초기에는 설정 자체를 별도로
            targetAdmin = self.admin_idx
            self.profit_ratio = targetAdmin.profit_ratio

            obj = Profit_Stat_Partner.objects.filter(admin_idx=targetAdmin).latest('day')
            timestamp = time.time()
            dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
            kmt = dt_utc + timedelta(hours=9)
            kmtstr = str(kmt)
            kmtstr = kmtstr.split(' ')
            # print(kmtstr)
            dates1 = kmtstr[0]
            dates1 = dates1.split('-')

            self.day = kmt - timedelta(hours=9)

            kmtYest = kmt - timedelta(days=1)
            kmtstr = str(kmtYest)
            kmtstr = kmtstr.split(' ')
            dates0 = kmtstr[0]
            dates0 = dates0.split('-')

            assets = Asset.objects.all()
            todayUserTotal_temp = 0
            for i in assets:
                todayUserTotal_temp += i.Actual_money_by_now
            self.users_total_today = todayUserTotal_temp

            kmtstr1 = str(self.day)
            kmtstr1 = kmtstr1.split(' ')
            dates1 = kmtstr1[0]

            kmtstr2 = str(obj.day)
            kmtstr2 = kmtstr2.split(' ')
            dates2 = kmtstr2[0]

            #전 날의 이미 존재하는 다른 날짜의 행이 있는 경우
            if dates1 != dates2:
                self.users_total_yest = obj.users_total_today
                #정산 공식 적용
                p = self.users_total_yest + self.day_In - self.day_Out - self.users_total_today
                self.jeongsan_today = (p * (self.profit_ratio)) - self.partner_out
                self.regular_total_jeongsan = obj.regular_total_jeongsan + self.jeongsan_today
                super(Profit_Stat_Partner, self).save(*args, **kwargs)
            #업데이트의 경우
            else:
                #obj = Profit_Stat_Partner.objects.all().exclude(day=obj.day).latest('day')
                #self.regular_total_jeongsan = obj.regular_total_jeongsan
                temp = self.jeongsan_today
                self.regular_total_jeongsan -= temp
                p = self.users_total_yest + self.day_In - self.day_Out - self.users_total_today
                self.jeongsan_today = (p * (self.profit_ratio)) - self.partner_out
                self.regular_total_jeongsan += self.jeongsan_today
                #정산 공식 적용
                #다만 총 정산을 업데이트 하는 과정은 수동으로 이루어 져야 한다. (정산 시점 기능과 충돌하기 때문에)
                super(Profit_Stat_Partner, self).save(*args, **kwargs)
            return
        #첫 생성인 경우
        else:
            timestamp = time.time()
            dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
            kmt = dt_utc + timedelta(hours=9)
            kmtstr = str(kmt)
            kmtstr = kmtstr.split(' ')
            dates1 = kmtstr[0]
            dates1 = dates1.split('-')

            kmtYest = kmt - timedelta(days=1)
            kmtstr = str(kmtYest)
            kmtstr = kmtstr.split(' ')
            dates0 = kmtstr[0]
            dates0 = dates0.split('-')

            # 첫 생성인 경우, 현재 회원 실잔액 합을 전날 총 금액으로 삼는다
            assets = Asset.objects.all()
            targetAdmin = self.admin_idx
            self.profit_ratio = targetAdmin.profit_ratio

            for i in assets:
                self.users_total_yest += i.Actual_money_by_now
            self.users_total_today = self.users_total_yest

            p = self.users_total_yest + self.day_In - self.day_Out - self.users_total_today
            self.jeongsan_today = (p*(self.profit_ratio))-self.partner_out
            #정산 공식 적용
            #self.jeongsan_today = ...
            # 정산이 끝나면 0짜리 새 행을 만든다. 기존의 regular_total_jeongsan은 건드리지 않는다.
            self.regular_total_jeongsan = self.jeongsan_today

            super(Profit_Stat_Partner, self).save(*args, **kwargs)
            return

    class Meta:
        verbose_name = '파트너 수익 통계'


#도메인 리스트 테이블
@python_2_unicode_compatible
class DomainList(models.Model):
    domain = models.CharField(max_length=200, default="내용을 입력 하세요")
    status = models.BooleanField(default=True) #사용, 미사용
    dtime = models.DateTimeField(auto_now_add=True, auto_created=True)
    admin_id = models.CharField(max_length=50, default="아이디를 입력 하세요")
    p_name = models.CharField(max_length=100, default="파트너 이름을 입력 하세요")

    domain.verbose_name = "도메인"
    status.verbose_name = "도메인 상태(사용:True/미사용:False)"
    dtime.verbose_name = "도메인 신청일시"
    admin_id.verbose_name = "도메인 할당 파트너 아이디"


    def save(self, *args, **kwargs):
        admin = admins.objects.get(admin_id=self.admin_id)
        self.p_name = self.admin.admin_name
        super(DomainList, self).save(*args, **kwargs)
    class Meta:
        verbose_name = '도메인 리스트'


#관리자 입출금 테이블이다. (에러 발생 시 관리자가 직접 특정 회원에게 입,출금처리)
@python_2_unicode_compatible
class Admin_M_IO(models.Model):
    user_idx = models.ForeignKey(
        'User_In',
        on_delete=models.CASCADE,
    )
    dtime_jeongsan = models.DateTimeField(auto_now_add=True)
    Order = models.IntegerField(default=0) # 0 = Admin_in, 1= Admin_out
    Quantity = models.FloatField(default=0)
    #어떤 유저에게 얼마만큼 입출금을 관리자가 임의로 해 주었는가 (오류 수정 차원. 통상적인 입출금과 별도)

    #금일 관리자 입금을 반환한다.
    @classmethod
    def day_m_i_admin(cls):
        timestamp = time.time()
        dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
        kmt = dt_utc + timedelta(hours=9)
        kmt = str(kmt)
        kmt = kmt.split(' ')
        today_dates = kmt[0]

        m_i = Admin_M_IO.objects.filter(Order=0)
        summation_of_moneyin_today = 0
        if m_i:
            for x in m_i:
                this_dates = x.dtime_jeongsan
                this_dates = this_dates + timedelta(hours=9)
                this_dates = str(this_dates)
                this_dates = this_dates.split(' ')
                this_dates = this_dates[0]
                if this_dates == today_dates:
                    summation_of_moneyin_today += x.Quantity
            return summation_of_moneyin_today
        else:
            return 0

    #입출금을 제외한 경우, 출금의 숫자는 무조건 양수이다
    #금일 관리자 출금을 반환한다.
    @classmethod
    def day_m_o_admin(cls):
        timestamp = time.time()
        dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
        kmt = dt_utc + timedelta(hours=9)
        # 여기서부터 day를 추출해서 하면 오류의 여지가 줄어든다
        kmt = str(kmt)
        kmt = kmt.split(' ')
        # print(kmtstr)
        today_dates = kmt[0]

        m_o = Admin_M_IO.objects.filter(Order=1)
        summation_of_moneyout_today = 0
        if m_o:
            for x in m_o:
                this_dates = x.dtime_jeongsan
                this_dates = this_dates + timedelta(hours=9)
                this_dates = str(this_dates)
                this_dates = this_dates.split(' ')
                this_dates = this_dates[0]
                if this_dates == today_dates:
                    summation_of_moneyout_today += x.Quantity
            return summation_of_moneyout_today
        else:
            return 0

    class Meta:
        verbose_name = '관리자 입출금 테이블'

#파트너의 정산 기록을 저장한다. (매일 매일 작성되는 파트너 수익 정산이 아닌, 주기적으로 시행되는 정산)
@python_2_unicode_compatible
class M_P_managementList(models.Model):
    admin_idx = models.ForeignKey(
        'admins',
        on_delete=models.CASCADE,
    )
    admin_id = models.CharField(max_length=50, default="a")
    dtime_jeongsan = models.DateTimeField(auto_now_add=True)
    #sonic = models.IntegerField(default=0)
    #choolgeum = models.IntegerField(default=0)

    #정산은 손익에서 출금액을 뺀 것이다.
    jeongsan = models.FloatField(default=0) #sonic - choolgeum
    profit_ratio = models.FloatField(default=0)


    admin_idx.verbose_name = "파트너색인"
    admin_id.verbose_name = "파트너 아이디"
    dtime_jeongsan.verbose_name = "정산일시"
    profit_ratio.verbose_name = "수익률"

    jeongsan.verbose_name = "정산"

    #금일까지의 총 정산액을 반환하는 클래스 함수
    @classmethod
    def day_m_o_partner(cls):
        timestamp = time.time()
        dt_utc = dt.fromtimestamp(timestamp, timezone.utc)
        kmt = dt_utc + timedelta(hours=9)
        kmt = str(kmt)
        kmt = kmt.split(' ')
        today_dates = kmt[0]

        m_o = M_P_managementList.objects.all()
        summation_of_moneyout_today = 0
        if m_o:
            for x in m_o:
                this_dates = x.dtime_jeongsan + timedelta(hours=9)
                this_dates = str(this_dates)
                this_dates = this_dates.split(' ')
                this_dates = this_dates[0]
                if this_dates == today_dates:
                    summation_of_moneyout_today += x.jeongsan
            return summation_of_moneyout_today
        else:
            return 0

    def save(self, *args, **kwargs):
        self.profit_ratio = self.admin_idx.profit_ratio
        self.admin_id = self.admin_idx.admin_id
        super(M_P_managementList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = '파트너 정산'






