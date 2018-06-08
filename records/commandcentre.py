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
        if status_code != 200:
            response = ''
            return response, status_code

        response = json.loads(r.text)
        print(response)
        print(type(response))



        # Creating message objects to structure the message to be shown
        message = MessageClass()
        message.message_text = "Company Details:"

        attachment = MessageAttachmentsClass()
        field1 = AttachmentFieldsClass()
        field1.title = "Name :"
        field1.value = response["CompanyInfo"]['LegalName']
        attachment.attach_field(field1)

        field2 = AttachmentFieldsClass()
        field2.title = "Created at"
        field2.value = response["CompanyInfo"]['CompanyStartDate']
        attachment.attach_field(field2)

        field3 = AttachmentFieldsClass()
        field3.title = "Email Id"
        field3.value = response["CompanyInfo"]['Email']['Address']
        attachment.attach_field(field3)

        message.attach(attachment)
        return message.to_json()


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
        message = MessageClass()
        message.message_text = "New Invoice Created :"

        attachment = MessageAttachmentsClass()
        field1 = AttachmentFieldsClass()
        field1.title = "Description :"
        field1.value = description
        attachment.attach_field(field1)

        field2 = AttachmentFieldsClass()
        field2.title = "Amount"
        field2.value = amount
        attachment.attach_field(field2)

        message.attach(attachment)
        return message.to_json()

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

        message = MessageClass()
        message.message_text = "Invoice details :"

        attachment = MessageAttachmentsClass()
        field1 = AttachmentFieldsClass()
        field1.title = "Description :"
        field1.value = response['Invoice']['Line'][0]['Description']
        attachment.attach_field(field1)

        field2 = AttachmentFieldsClass()
        field2.title = "Amount :"
        field2.value = response['Invoice']['TotalAmt']
        attachment.attach_field(field2)

        field3 = AttachmentFieldsClass()
        field3.title = "DueDate :"
        field3.value = response['Invoice']['DueDate']
        attachment.attach_field(field3)

        field4 = AttachmentFieldsClass()
        field4.title = "Customer:"
        field4.value = response['Invoice']['CustomerRef']['name']
        attachment.attach_field(field4)

        message.attach(attachment)
        return message.to_json()


    def list_all_invoice_ids(self,args):
        ### Add YA message format

        print("In list_all_invoice_ids")
        route = "/v3/company/" + self.realmID + "/query?query=select * from Invoice"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        response = json.loads(json.dumps(xmltodict.parse(r.text)))
        #print(response)
        data = response['IntuitResponse']['QueryResponse']['Invoice']

        print(data)
        message = MessageClass()
        message.message_text = "All Invoice details :"

        for i in range(0,len(data)):

            attachment = MessageAttachmentsClass()
            field1 = AttachmentFieldsClass()
            field1.title = "Id :"
            field1.value = i
            attachment.attach_field(field1)

            field2 = AttachmentFieldsClass()
            field2.title = "Total Amount :"
            field2.value = data[i]['TotalAmt']
            attachment.attach_field(field2)
            message.attach(attachment)

        return message.to_json()


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

        message = MessageClass()
        message.message_text = "Invoice updated"
        return message.to_json()

    def get_all_customers(self,args):
        ### Add YA message format
        print("In get_all_customers")
        route = "/v3/company/" + self.realmID + "/query?query=select * from Customer"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)
        response = json.loads(json.dumps(xmltodict.parse(r.text)))
        #print(response)

        message = MessageClass()
        message.message_text = " All Customer details :"

        customer_data = response['IntuitResponse']['QueryResponse']['Customer']
        print("-------------------")
        print(customer_data)
        print(len(customer_data))
        print(customer_data[0]['DisplayName'].decode("utf-8"))
        print(customer_data[0]['PrimaryEmailAddr']['Address'].decode("utf-8"))
        print(customer_data[0]['Balance'].decode("utf-8"))

        for i in range(0,len(customer_data)):

            attachment = MessageAttachmentsClass()
            field1 = AttachmentFieldsClass()
            field1.title = "Name :"
            field1.value = customer_data[i]['DisplayName'].decode("utf-8")
            attachment.attach_field(field1)
            try :
                field2 = AttachmentFieldsClass()
                field2.title = "Email Id :"
                field2.value = customer_data[i]['PrimaryEmailAddr']['Address'].decode("utf-8")
                attachment.attach_field(field2)
            except:
                pass

            field3 = AttachmentFieldsClass()
            field3.title = "Balance:"
            field3.value = customer_data[i]['Balance'].decode("utf-8")
            attachment.attach_field(field3)
            message.attach(attachment)

        return message.to_json()

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

        #'IntuitResponse'
        #'DisplayName'
        #'Balance'
        #'PrimaryEmailAddr' 'Address'

        message = MessageClass()
        message.message_text = "Customer details :"

        attachment = MessageAttachmentsClass()
        field1 = AttachmentFieldsClass()
        field1.title = "Name :"
        field1.value = response['IntuitResponse']['Customer']['DisplayName']
        attachment.attach_field(field1)

        field2 = AttachmentFieldsClass()
        field2.title = "Email Id :"
        field2.value = response['IntuitResponse']['Customer']['PrimaryEmailAddr']['Address']
        attachment.attach_field(field2)

        field3 = AttachmentFieldsClass()
        field3.title = "Balance:"
        field3.value = response['IntuitResponse']['Customer']['Balance']
        attachment.attach_field(field3)

        message.attach(attachment)
        return message.to_json()

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

        message = MessageClass()
        message.message_text = "New customer " + display_name +  " created successfully !"

        return message.to_json()
