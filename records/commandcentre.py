""" This is the command centre for all the commands created in the YA developer console
    This file contains the logic to understand a user message request from YA
    and return a response in the format of a YA message object accordingly

"""

#from django.http import HttpResponse
#from yellowant import YellowAnt
import xmltodict
import json

from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass

from quickauth import getDiscoveryDocument
from quickauth.models import Bearer
from quickauth.services import getBearerTokenFromRefreshToken, stringToBase64
from .models import YellowUserToken,QuickbookUserToken,QuickUserDetails
#import traceback
import requests
#import datetime
#import pytz
from django.conf import settings

class CommandCentre(object):

    """ Handles user commands

        Args:
            yellowant_integration_id (int): The integration id of a YA user
            function_name (str): Invoke name of the command the user is calling
            args (dict): Any arguments required for the command to run
    """
    def __init__(self, yellowant_user_id, yellowant_integration_id, function_name, args):
        self.yellowant_user_id = yellowant_user_id
        self.yellowant_integration_id = yellowant_integration_id
        self.function_name = function_name
        self.args = args

    def parse(self):
        """
        Matching which function to call
        """

        self.commands = {
            'get_company_info' : self.get_company_info,
            'create_invoice' : self.create_invoice,
            'read_invoice': self.read_invoice,
            'list_all_invoice_ids': self.list_all_invoice_ids,
            'update_invoice' : self.update_invoice,
            'get_all_customers':    self.get_all_customers,
            'get_customer_details' : self.get_customer_details,
            'create_customer' : self.create_customer
        }

        self.user_integration = YellowUserToken.objects.get\
            (yellowant_integration_id=self.yellowant_integration_id)

        self.quickbook_access_token_object = QuickbookUserToken.objects.\
            get(user_integration=self.user_integration)

        self.quickbook_user_detail_object = QuickUserDetails.objects.\
            get(user_integration=self.quickbook_access_token_object)

        self.realmID = self.quickbook_user_detail_object.realmId

        self.quickbook_access_token = self.quickbook_access_token_object.\
            accessToken


        return self.commands[self.function_name](self.args)



    def get_company_info(self,args):
        #### Add yellowant message formatting
        print("In get_company_info")
        route = '/v3/company/{0}/companyinfo/{0}'.format(self.realmID)

        # Refresh access token
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        # bearer = Bearer.accessToken
        auth_header = 'Bearer ' + bearer.accessToken

        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        status_code = r.status_code
        print(status_code)
        if status_code != 200:
            response = ''
            return response, status_code

        response = json.loads(r.text)
        print(response['CompanyInfo']['SyncToken'])
        print(response)
        print(status_code)
        return response, status_code

    def create_invoice(self,args):

        #### Add yellowant message formatting
        print("In create invoice")
        route = "/v3/company/" +  self.realmID + "/invoice"

        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        print(args)
        amount = args['amount']
        description = args['description']
        sales_item_value = args['sales_item_value']
        quantity =  args["quantity"]
        unit_price = args['unit_price']
        ## Amount = UnitPrice X Quantity

        payload ={
	    "Line": [{
		    "Id": "1",
		    "LineNum": 1,
		    "Description": "Holiday party - gold level",
		    "Amount": float(amount),
		    "DetailType": "SalesItemLineDetail",
		    "SalesItemLineDetail": {
			"ItemRef": {
				"value": str(sales_item_value),
				"name": description
			},
			"UnitPrice": float(unit_price),
			"Qty": quantity,
			"TaxCodeRef": {
				"value": "2"
			        }
		           }
	         }],
	         "CustomerRef": {
		    "value": str(sales_item_value)
	        }
        }

        r = requests.post(settings.PRODUCTION_BASE_URL + route,headers=headers,json=payload)
        response = json.loads(r.text)
        print(response)
        return r.status_code

    def read_invoice(self,args):

        ### Add YA message format
        print("In read invoice")
        invoiceId = args['invoice_id']
        route = "/v3/company/" + self.realmID + "/invoice/" + invoiceId
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        response = json.loads(r.text)
        print(response)
        return r.status_code

    def list_all_invoice_ids(self,args):
        ### Add YA message format

        print("In list_all_invoice_ids")
        route = "/v3/company/" + self.realmID + "/query?query=select * from Invoice"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        response = json.loads(json.dumps(xmltodict.parse(r.text)))
        print(response)
        return r.status_code

    def update_invoice(self,args):

        ## Bug fixed
        ### Add YA message format
        print("In update_invoice")

        id = args['invoice_id']
        due_date = args['due_date']
        syn_token = args['syn_token']
        #Fetching the invoice
        route = "/v3/company/" + self.realmID + "/invoice/" + id
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        data = {}
        response = json.loads(r.text)
        #print(response)
        data = response['Invoice']
        print("Invoice part")
        print(data)

        #Updating the invoice
        payload = data
        payload["DueDate"] = due_date
        payload["SyncToken"] = syn_token
        route = "/v3/company/" + self.realmID + "/invoice"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}
        r = requests.post(settings.PRODUCTION_BASE_URL + route, headers=headers,json=payload)
        response = json.loads(r.text)
        print(response,r.status_code)
        return r.status_code

    def get_all_customers(self,args):
        ### Add YA message format
        print("In get_all_customers")
        route = "/v3/company/" + self.realmID + "/query?query=select * from Customer"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        response = json.loads(json.dumps(xmltodict.parse(r.text)))
        print(response)
        return r.status_code

    def get_customer_details(self,args):
        ### Add YA message format
        print("In get_customer_details")
        customerId = args['customer_id']
        route = "/v3/company/" + self.realmID + "/customer/" + customerId
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        response = json.loads(json.dumps(xmltodict.parse(r.text)))
        print(response)
        return r.status_code

    def create_customer(self,args):
        ### Add YA message format
        print("In create_customer")
        route = "/v3/company/" + self.realmID + "/customer"

        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        notes = args['notes']
        display_name = args['display_name']
        email = args['e-mail']

        payload = {
            "BillAddr": {
                "Line1": "",
                "City": "",
                "Country": "",
                "CountrySubDivisionCode": "",
                "PostalCode": ""
            },
            "Notes": notes,
            "Title": "",
            "GivenName": "",
            "MiddleName": "",
            "FamilyName": "",
            "Suffix": "",
            "FullyQualifiedName": "",
            "CompanyName": "",
            "DisplayName": display_name,
            "PrimaryPhone": {
                "FreeFormNumber": ""
            },
            "PrimaryEmailAddr": {
                "Address": email
            }
        }

        r = requests.post(settings.PRODUCTION_BASE_URL + route, headers=headers, json=payload)
        response = json.loads(r.text)
        print(response)
        return r.status_code

