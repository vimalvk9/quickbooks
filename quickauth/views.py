import urllib
import uuid

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from yellowant import YellowAnt
from records.models import YellowUserToken,YellowAntRedirectState, AppRedirectState
from quickauth import getDiscoveryDocument
from quickauth.services import (
    getCompanyInfo,
    getBearerTokenFromRefreshToken,
    getUserProfile,
    getBearerToken,
    getSecretKey,
    validateJWTToken,
    revokeToken,
)

'''
def index(request):
    print("In index")

    context = {
        "user_integrations": []
    }
    # Check if user is authenticated otherwise redirect user to login page

    if request.user.is_authenticated:
        user_integrations = YellowUserToken.objects.filter(user=request.user)
        print(user_integrations)
        for user_integration in user_integrations:
            context["user_integrations"].append(user_integration)

        return render(request, "home.html", context)
    else:
        return HttpResponse("Please login !")

    #print("1")
    #return render(request, 'home.html')'''



def connectToQuickbooks(request):
    print("2")
    url = getDiscoveryDocument.auth_endpoint
    params = {'scope': settings.ACCOUNTING_SCOPE, 'redirect_uri': settings.QUICKBOOKS_REDIRECT_URL,
              'response_type': 'code', 'state': get_CSRF_token(request), 'client_id': settings.QUICKBOOKS_CLIENT_ID}
    url += '?' + urllib.urlencode(params)
    return redirect(url)


def signInWithIntuit(request):
    print("3")
    url = getDiscoveryDocument.auth_endpoint
    scope = ' '.join(settings.OPENID_SCOPES)  # Scopes are required to be sent delimited by a space
    params = {'scope': scope, 'redirect_uri': settings.QUICKBOOKS_REDIRECT_URL,
              'response_type': 'code', 'state': get_CSRF_token(request), 'client_id': settings.QUICKBOOKS_CLIENT_ID}
    url += '?' + urllib.urlencode(params)
    return redirect(url)


def getAppNow(request):
    print("4")
    url = getDiscoveryDocument.auth_endpoint
    scope = ' '.join(settings.GET_APP_SCOPES)  # Scopes are required to be sent delimited by a space
    params = {'scope': scope, 'redirect_uri': settings.QUICKBOOKS_REDIRECT_URL,
              'response_type': 'code', 'state': get_CSRF_token(request), 'client_id': settings.QUICKBOOKS_CLIENT_ID}
    url += '?' + urllib.urlencode(params)
    return redirect(url)


def authCodeHandler(request):
    print("5")
    state = request.GET.get('state', None)
    error = request.GET.get('error', None)
    if error == 'access_denied':
        return redirect('sampleAppOAuth2:index')
    if state is None:
        return HttpResponseBadRequest()
    elif state != get_CSRF_token(request):  # validate against CSRF attacks
        return HttpResponse('unauthorized', status=401)

    auth_code = request.GET.get('code', None)
    if auth_code is None:
        return HttpResponseBadRequest()

    bearer = getBearerToken(auth_code)
    realmId = request.GET.get('realmId', None)
    updateSession(request, bearer.accessToken, bearer.refreshToken, realmId)

    # Validate JWT tokens only for OpenID scope
    if bearer.idToken is not None:
        if not validateJWTToken(bearer.idToken):
            return HttpResponse('JWT Validation failed. Please try signing in again.')
        else:
            return redirect('sampleAppOAuth2:connected')
    else:
        return redirect('sampleAppOAuth2:connected')


def connected(request):
    print("6")
    access_token = request.session.get('accessToken', None)
    if access_token is None:
        return HttpResponse('Your Bearer token has expired, please initiate Sign In With Intuit flow again')

    refresh_token = request.session.get('refreshToken', None)
    realmId = request.session['realmId']
    if realmId is None:
        user_profile_response, status_code = getUserProfile(access_token)

        if status_code >= 400:
            # if call to User Profile Service doesn't succeed then get a new bearer token from refresh token
            # and try again
            bearer = getBearerTokenFromRefreshToken(refresh_token)
            user_profile_response, status_code = getUserProfile(bearer.accessToken)
            updateSession(request, bearer.accessToken, bearer.refreshToken, request.session.get('realmId', None),
                          name=user_profile_response.get('givenName', None))

            if status_code >= 400:
                return HttpResponseServerError()
        c = {
            'first_name': user_profile_response.get('givenName', ' '),
        }
    else:
        if request.session.get('name') is None:
            name = ''
        else:
            name = request.session.get('name')
        c = {
            'first_name': name,
        }

    return render(request, 'connected.html', context=c)


def disconnect(request):
    print("7")
    access_token = request.session.get('accessToken', None)
    refresh_token = request.session.get('refreshToken', None)

    revoke_response = ''
    if access_token is not None:
        revoke_response = revokeToken(access_token)
    elif refresh_token is not None:
        revoke_response = revokeToken(refresh_token)
    else:
        return HttpResponse('No accessToken or refreshToken found, Please connect again')

    request.session.flush()
    return HttpResponse(revoke_response)


def refreshTokenCall(request):
    print("8")
    refresh_token = request.session.get('refreshToken', None)
    if refresh_token is None:
        return HttpResponse('Not authorized')
    bearer = getBearerTokenFromRefreshToken(refresh_token)

    if isinstance(bearer, str):
        return HttpResponse(bearer)
    else:
        return HttpResponse('Access Token: ' + bearer.accessToken + ', Refresh Token: ' + bearer.refreshToken)


def apiCall(request):
    print("9")
    access_token = request.session.get('accessToken', None)
    if access_token is None:
        return HttpResponse('Your Bearer token has expired, please initiate C2QB flow again')

    realmId = request.session['realmId']
    if realmId is None:
        return HttpResponse('No realm ID. QBO calls only work if the accounting scope was passed!')

    refresh_token = request.session['refreshToken']
    company_info_response, status_code = getCompanyInfo(access_token, realmId)

    if status_code >= 400:
        # if call to QBO doesn't succeed then get a new bearer token from refresh token and try again
        bearer = getBearerTokenFromRefreshToken(refresh_token)
        updateSession(request, bearer.accessToken, bearer.refreshToken, realmId)
        company_info_response, status_code = getCompanyInfo(bearer.accessToken, realmId)
        if status_code >= 400:
            return HttpResponseServerError()
    company_name = company_info_response['CompanyInfo']['CompanyName']
    address = company_info_response['CompanyInfo']['CompanyAddr']
    return HttpResponse('Company Name: ' + company_name + ', Company Address: ' + address['Line1'] + ', ' + address[
        'City'] + ', ' + ' ' + address['PostalCode'])


def get_CSRF_token(request):
    print("10")
    token = request.session.get('csrfToken', None)
    if token is None:
        token = getSecretKey()
        request.session['csrfToken'] = token
    return token


def updateSession(request, access_token, refresh_token, realmId, name=None):
    print("11")
    request.session['accessToken'] = access_token
    request.session['refreshToken'] = refresh_token
    request.session['realmId'] = realmId
    request.session['name'] = name
