"""
Functions corresponding to URL patterns of web app

"""


import json
import urllib

import requests
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from yellowant import YellowAnt

from quickauth import getDiscoveryDocument
from quickauth.views import get_CSRF_token
from quickbooks import settings
from records.models import YellowUserToken, QuickbookUserToken, AppRedirectState

'''
def UserLogin(request):
    """Sample login page"""
    return render(request, "login.html")
'''

def index(request,path):
    """ Loads the homepage of the app.
        index function loads the home.html page
    """
    #print('test')

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

def user_list_view(request):
    """
    userdetails function shows the vital integration details of the user

    """
    print("in userdetails")
    user_integrations_list = []

    # Check if user is authenticated otherwise redirect user to login page
    if request.user.is_authenticated:
        user_integrations = YellowUserToken.objects.filter(user=request.user)
        print(user_integrations)
        for user_integration in user_integrations:
            try:
                qut = QuickbookUserToken.objects.get(user_integration=user_integration)
                print(qut)
                user_integrations_list.append({"user_invoke_name":user_integration.\
                                              yellowant_integration_invoke_name,
                                               "id":user_integration.id, "app_authenticated":True,
                                               "is_valid":qut.login_update_flag,"redirect_url":settings.QUICKBOOKS_REDIRECT_URL})
            except QuickbookUserToken.DoesNotExist:
                user_integrations_list.append({"user_invoke_name":user_integration.\
                                              yellowant_integration_invoke_name,
                                               "id":user_integration.id, "app_authenticated":False})
    return HttpResponse(json.dumps(user_integrations_list), content_type="application/json")




def user_detail_update_delete_view(request, id=None):
    print("In user_detail_update_delete_view")
    """
    delete_integration function deletes the particular integration
    """

    print("In user_detail_update_delete_view")
    print(id)
    user_integration_id = id
    #
    # if request.method == "GET":
    #     pass
    #     return HttpResponse(json.dumps({"ok" : True,"is_valid" : False}))

    if request.method == "DELETE":
        print("Deleting integration")
        access_token_dict = YellowUserToken.objects.get(id=id)
        access_token = access_token_dict.yellowant_token
        print(access_token)
        user_integration_id = access_token_dict.yellowant_integration_id
        print(user_integration_id)
        url = "https://api.yellowant.com/api/user/integration/%s"%(user_integration_id)
        yellowant_user = YellowAnt(access_token=access_token)
        print(yellowant_user)
        yellowant_user.delete_user_integration(id=user_integration_id)
        response = YellowUserToken.objects.get(yellowant_token=access_token).delete()
        print(response)
        return HttpResponse("successResponse", status=200)

    elif request.method == "POST":
        print("In submitting data")
        data = json.loads(request.body.decode("utf-8"))
        print(data)

        user_integration = data['user_integration']
        qut_object = QuickbookUserToken.objects.get(user_integration_id=user_integration)
        qut_object.login_update_flag = True
        qut_object.save()

        return HttpResponse(json.dumps({
            "ok": True,
            "is_valid": True
        }))

        # url = getDiscoveryDocument.auth_endpoint
        # params = {'scope': settings.ACCOUNTING_SCOPE, 'redirect_uri': settings.QUICKBOOKS_REDIRECT_URL,
        #           'response_type': 'code', 'state': get_CSRF_token(request), 'client_id': settings.QUICKBOOKS_CLIENT_ID}
        # url += '?' + urllib.parse.urlencode(params)
        # print(url)
        # return HttpResponseRedirect(url)
    #
    # return HttpResponse("Success",status=200)




