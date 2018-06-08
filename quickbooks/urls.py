"""quickbooks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.views.generic.base import RedirectView
from quickauth import urls as quickauth_urls
from web import urls as web_urls
from records.views import redirectToYellowAntAuthenticationPage, yellowantRedirecturl, yellowantapi
from records.views import quickbookRedirecturl

urlpatterns = [

    url(r'^admin/', admin.site.urls),


    # For creating new integration
    url(r'^create-new-integration/', redirectToYellowAntAuthenticationPage,
         name="quickbook-ya-auth-redirect"),

    # For redirecting from yellowant
    url(r'^yellowantredirecturl/', yellowantRedirecturl,
         name="yellowant-auth-redirect"),

    # For redirecting to qucikbooks
    url(r'^quickbookauthurl/', quickbookRedirecturl, name="quickbookRedirecturl"),

    # url(r'^quickauth/',quickauth,name="quickauth"),

    # For redirecting to yellowant authentication page
    url("yellowantauthurl/", redirectToYellowAntAuthenticationPage,
         name="yellowant-auth-url"),
    # For getting command specific information from slack on executing a command
    url("yellowant-api/", yellowantapi, name="yellowant-api"),

    url("",include(web_urls)),
    #url("",include(quickauth_urls)),


    #url("integrate_app/",integrate_app_account),
    #url(r'^$', RedirectView.as_view(pattern_name='sampleAppOAuth2:index')),
    #url(r'^(?i)sampleAppOAuth2/', include('quickauth.urls', namespace='sampleAppOAuth2')),

]
