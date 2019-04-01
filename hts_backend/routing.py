from __future__ import absolute_import
from django.conf.urls import url
from . import consumers

# url(r'^ws/hts_backend/(?P<_>[^/]+)/$', consumers.RealTime_basic_info0),
# url(r'^ws/hts_backend/(?P<_>[^/]+)/$', consumers.RealTime_basic_info_list_holdings),
websocket_urlpatterns = [
    url(r'^ws/sockettest', consumers.RealTime_basic_info_list_holdings),
    url(r'^ws/admin_socket', consumers.admin_socket),
]
#url(r'^ws/sockettest_basic', consumers.RealTime_basic_info0)

#application = protoco