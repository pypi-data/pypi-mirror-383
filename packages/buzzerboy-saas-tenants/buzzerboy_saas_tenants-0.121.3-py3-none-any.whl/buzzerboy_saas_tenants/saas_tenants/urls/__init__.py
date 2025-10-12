

from .account_settings import urlpatterns as account_settings_urls
from .accounts import urlpatterns as accounts_urls
from .authentication import urlpatterns as authentication_urls
from .home import urlpatterns as home_urls
from .invites import urlpatterns as invites_urls
from .tenant_setting import urlpatterns as tenant_setting_urls
from .tenant import urlpatterns as tenant_urls
from .ai_chat import urlpatterns as ai_chat_urls

urlpatterns = [
    
]

urlpatterns += account_settings_urls
urlpatterns += accounts_urls
urlpatterns += authentication_urls
urlpatterns += home_urls
urlpatterns += invites_urls
urlpatterns += tenant_setting_urls
urlpatterns += tenant_urls
urlpatterns += ai_chat_urls
