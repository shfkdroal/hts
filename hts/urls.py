"""hts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import absolute_import
from django.contrib import admin
from hts_backend.views import *
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('api/account/signup', create_signin_row, name='0_signup'),
    path('api/set_interest', set_interest, name='1_set_interest'),
    path('api/set_interestgroup', set_interestgroup, name='1_set_interestgroup'),
    path('api/show_interest_all', show_interest, name='1_show_interest'),
    path('api/show_interest_group_all', show_interestgroup, name='1_show_interest'),
    path('api/unset_interest', unset_interest, name='1_unset_interest'),
    path('api/unset_interestgroup', unset_interest_group, name='1_unset_interestgroup'),
    path('api/account/login', check_login, name='2_login'),
    path('api/cgpw', change_pw, name='2_login'),
    #path('api/mainpage', check_login2, name='2_main'),
    path('api/search', searh_among_stocks, name='3_search'),

    path('api/moneyin', moneyin, name='4_moneyin'),
    path('api/moneyout', moneyout, name='4_moneyout'),
    path('api/loan', loan, name='5_loan'),
    path('api/orderBuy', orderBuy, name='6_orderBuy'),
    path('api/orderSell', orderSell, name='7_orderSell'),
    path('api/ovn', ovn, name='8_ovn'),
    path('api/holdings', showHoldings, name='9_show'),
    path('api/asset', showAsset, name='9_show'),
    path('api/transaction', showTrans, name='9_show'),
    path('api/money_io_show', show_M_io, name='9_show'),
    path('api/profit_show', showProfit, name='9_show'),
    path('api/notlist_show', showNot_List, name='9_show'),
    path('api/spk_to_name', spk_to_name, name='9_show'),
    path('api/scd_to_name', scd_to_name, name='9_show'),

    path('api/show_top_kospi', show_top_kospi, name='9_show'),
    path('api/show_top_kosdaq', show_top_kosdq, name='9_show'),
    path('api/show_top_coin', show_top_coin, name='9_show'),
    path('api/show_info', show_info, name='9_show'),
    path('api/show_popup', show_popup, name='9_show'),
    path('api/mypg', mypg, name='9_show'),
    path('api/show_loan', show_loan, name='9_show'),
    path('api/show_loan_Admin', show_loan_Admin, name='9_show'),
    path('api/chart', chart, name='9_show'),
    path('api/cancell_not_done', cancell_not_done, name='9_show'),



    path('api/shutdown', shutdown, name='10_admin'),
    path('api/shutdown2', shutdown2, name='10_admin'),

    path('api/jeongsan', jeongsan, name='10_admin'),
    path('api/JeongSan_Partner', JeongSan_Partner, name='10_admin'),

    path('api/JeongSan_Company', JeongSan_Company, name='10_admin'),
    path('api/users_list', users_list, name='10_admin'),
    path('api/search_user', search_among_users, name='10_admin'),
    path('api/show_domains', show_domains, name='10_admin'),

    path('api/show_partners', show_partners, name='10_admin'),
    path('api/show_Profit_Stat_Partner', show_Profit_Stat_Partner, name='10_admin'),
    path('api/show_M_P_managementList', show_M_P_managementList, name='10_admin'),
    path('api/mypg_admin', mypg_admin, name='10_admin'),
    path('api/show_MarketStatus', show_MarketStatus, name='10_admin'),
    path('api/modify_MarketStatus', modify_MarketStatus, name='10_admin'),
    path('api/admin_in', admin_in, name='10_admin'),
    path('api/admin_out', admin_Out, name='10_admin'),

    path('api/show_signin_req', show_signin_req, name='10_admin'),
    path('api/show_loan_req', show_loan_req, name='10_admin'),
    path('api/show_deposit_req', show_deposit_req, name='10_admin'),
    path('api/show_width_req', show_width_req, name='10_admin'),

    path('api/show_signin_appr', show_signin_appr, name='10_admin'),
    path('api/show_loan_appr', show_loan_appr, name='10_admin'),
    path('api/show_deposit_appr', show_deposit_appr, name='10_admin'),
    path('api/show_width_appr', show_width_appr, name='10_admin'),

    path('api/holdings_Admin', showHoldings_Admin, name='9_show'),
    path('api/asset_Admin', showAsset_Admin, name='9_show'),
    path('api/transaction_Admin', showTrans_Admin, name='9_show'),
    path('api/money_io_show_Admin', show_M_io_Admin, name='9_show'),
    path('api/profit_show_Admin', showProfit_Admin, name='9_show'),
    path('api/notlist_show_Admin', showNot_List_Admin, name='9_show'),

    path('api/admin_out_Partner', admin_out_Partner, name='9_show'),
]

# jeongsan, JeongSan_Partner는 수동 함수 - 운영 탭에 존재
# JeongSan_Company는 자동 시행되나, 필요할 시 수동으로 시행 될 수 있도록 운영 탭에 둔다.


"""
    path('api/shutdown', shutdown, name='10_admin'),
    path('api/jeongsan', jeongsan, name='10_admin'),
    path('api/JeongSan_Partner', JeongSan_Partner, name='10_admin'),

    path('api/JeongSan_Company', JeongSan_Company, name='10_admin'),
    path('api/users_list', users_list, name='10_admin'),                작업중 
    path('api/search_user', search_among_users, name='10_admin'),
    path('api/show_domains', show_domains, name='10_admin'),

    path('api/show_partners', show_partners, name='10_admin'),
    path('api/show_Profit_Stat_Partner', show_Profit_Stat_Partner, name='10_admin'),
    path('api/show_M_P_managementList', show_M_P_managementList, name='10_admin'),
    path('api/mypg_admin', mypg_admin, name='10_admin'),
    path('api/show_MarketStatus', show_MarketStatus, name='10_admin'),
    path('api/modify_MarketStatus', modify_MarketStatus, name='10_admin'),

"""