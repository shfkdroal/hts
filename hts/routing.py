
from __future__ import absolute_import
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from hts_backend import routing
from hts_backend import consumers
#hts.hts_backend

#KiwoomObj = consumers.KiwoomEventHandler1()
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
    "channel": ChannelNameRouter({
        "ReqToKiwoom": consumers.KiwoomEventHandler1,
        #"thunbnails-delete": consumers.DeleteConsumer,
    }),

})
#ChannelNameRouther was designed for BGProc

"""
#not belong here
"channel": ChannelNameRouter({
    "thumbnails-generate": consumers.GenerateConsumer,
    "thunbnails-delete": consumers.DeleteConsumer,
}),
"""