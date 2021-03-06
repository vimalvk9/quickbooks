""" This is the command centre for all the commands created in the YA developer console
    This file contains the logic to understand a user message request from YA
    and return a response in the format of a YA message object accordingly

"""

#from django.http import HttpResponse
#from yellowant import YellowAnt
import xmltodict
import json

from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass

from ..quickauth import getDiscoveryDocument
from ..quickauth.models import Bearer
from ..quickauth.services import getBearerTokenFromRefreshToken, stringToBase64
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
            'list_all_invoices' : self.list_all_invoices,
            'list_all_invoice_ids': self.list_all_invoice_ids,
            'update_invoice' : self.update_invoice,
            'get_all_customers':    self.get_all_customers,
            'get_customer_details' : self.get_customer_details,
            'create_customer' : self.create_customer,
            'list_all_customer_ids' : self.list_all_customer_ids
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

        print("In get_company_info")

        # API parameteres for getting company information
        route = '/v3/company/{0}/companyinfo/{0}'.format(self.realmID)
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            response = json.loads(r.text)

            print(response)
            print(type(response))

            # Creating message objects to structure the message to be shown
            message = MessageClass()
            message.message_text = "Company Details:"

            attachment = MessageAttachmentsClass()
            try:
                field1 = AttachmentFieldsClass()
                field1.title = "Name :"
                field1.value = response["CompanyInfo"]['LegalName']
                attachment.attach_field(field1)
            except:
                pass

            try:
                field2 = AttachmentFieldsClass()
                field2.title = "Compnay start date :"
                field2.value = response["CompanyInfo"]['CompanyStartDate']
                attachment.attach_field(field2)
            except:
                pass

            try:
                field3 = AttachmentFieldsClass()
                field3.title = "Email Id :"
                field3.value = response["CompanyInfo"]['Email']['Address']
                attachment.attach_field(field3)
            except:
                pass

            try:
                field4 = AttachmentFieldsClass()
                field4.title = "Contact Number :"
                field4.value = response["CompanyInfo"]['PrimaryPhone']['FreeFormNumber']
                attachment.attach_field(field4)
            except:
                pass

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)


    def create_invoice(self,args):

        print("In create invoice")

        # API call parameters for creating an invoice
        route = "/v3/company/" +  self.realmID + "/invoice"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        print(args)

        # Fetching arguments from slack
        amount = args['amount']
        description = args['description']
        sales_item_value = args['sales_item_value']
        quantity =  args["quantity"]
        unit_price = args['unit_price']

        ###  Amount = UnitPrice X Quantity must satisfy  ###

        # payload for API call
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

        # Consuming the API
        r = requests.post(settings.PRODUCTION_BASE_URL + route,headers=headers,json=payload)

        # Response check
        if (r.status_code == requests.codes.ok):
            response = json.loads(r.text)

            print(response)

            # Creating message from YA SDK
            message = MessageClass()
            message.message_text = "New Invoice Created :"

            attachment = MessageAttachmentsClass()
            try:
                field1 = AttachmentFieldsClass()
                field1.title = "Id :"
                field1.value = description
                attachment.attach_field(field1)
            except:
                pass

            try:
                field2 = AttachmentFieldsClass()
                field2.title = "Amount"
                field2.value = amount
                attachment.attach_field(field2)
            except:
                pass

            try:
                field3 = AttachmentFieldsClass()
                field3.title = "Description :"
                field3.value = description
                attachment.attach_field(field3)
            except:
                pass

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)


    def read_invoice(self,args):

        print("In read invoice")

        # Arguments passed from slack
        invoiceId = args['invoice_id']

        # API call parameters for reading an invoice
        route = "/v3/company/" + self.realmID + "/invoice/" + invoiceId
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Fetching response in JSON
            response = json.loads(r.text)
            print(response)

            # Creating a message object from YA SDK
            message = MessageClass()
            message.message_text = "Invoice details :"

            attachment = MessageAttachmentsClass()
            try:
                field1 = AttachmentFieldsClass()
                field1.title = "Description :"
                field1.value = response['Invoice']['Line'][0]['Description']
                attachment.attach_field(field1)
            except:
                pass
            try:
                field2 = AttachmentFieldsClass()
                field2.title = "Amount :"
                field2.value = response['Invoice']['TotalAmt']
                attachment.attach_field(field2)
            except:
                pass

            try:
                field3 = AttachmentFieldsClass()
                field3.title = "DueDate :"
                field3.value = response['Invoice']['DueDate']
                attachment.attach_field(field3)
            except:
                pass

            try:
                field4 = AttachmentFieldsClass()
                field4.title = "Customer:"
                field4.value = response['Invoice']['CustomerRef']['name']
                attachment.attach_field(field4)
            except:
                pass

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)


    def update_invoice(self,args):

        print("In update_invoice")

        # Arguments passed from slack
        id = args['invoice_id']
        due_date = args['due_date']
        syn_token = args['syn_token']

        ## First we make an API call to fetch the particular invoice

        # API call parameters to fetch the invoice
        route = "/v3/company/" + self.realmID + "/invoice/" + id
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            response = json.loads(r.text)
            #print(response)
            data = response['Invoice']
            print("Invoice part")
            print(data)

            # Updating the invoice
            payload = data
            payload["DueDate"] = due_date
            payload["SyncToken"] = syn_token

            ## Once invoice is successfully fetched, we update it

            # API call parameters to update the invoice
            route = "/v3/company/" + self.realmID + "/invoice"
            bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
            auth_header = 'Bearer ' + bearer.accessToken
            headers = {'Authorization': auth_header, 'accept': 'application/json'}

            # Consuming the API
            r = requests.post(settings.PRODUCTION_BASE_URL + route, headers=headers,json=payload)

            # Response check
            if r.status_code == requests.codes.ok:

                # Getting response in JSON
                response = json.loads(r.text)
                print(response,r.status_code)

                message = MessageClass()
                message.message_text = "Invoice updated"
                return message.to_json()
            else:
                return "{0}: {1}".format(r.status_code, r.text)
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)

    def get_all_customers(self,args):

        print("In get_all_customers")

        # API call parameters for getting all customers
        route = "/v3/company/" + self.realmID + "/query?query=select * from Customer"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Error check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON format
            response = json.loads(json.dumps(xmltodict.parse(r.text)))

            #print(response)

            # Making message from YA SDK
            message = MessageClass()
            message.message_text = " All Customer details :"

            customer_data = response['IntuitResponse']['QueryResponse']['Customer']
            print("-------------------")
            print(customer_data)
            print(len(customer_data))
            print(customer_data[0]['DisplayName'])
            print(customer_data[0]['PrimaryEmailAddr']['Address'])
            print(customer_data[0]['Balance'])

            for i in range(0,len(customer_data)):

                attachment = MessageAttachmentsClass()
                try:
                    field1 = AttachmentFieldsClass()
                    field1.title = "Customer ID :"
                    field1.value = customer_data[i]['Id']
                    attachment.attach_field(field1)
                except:
                    pass

                try:
                    field2 = AttachmentFieldsClass()
                    field2.title = "Name :"
                    field2.value = customer_data[i]['DisplayName']
                    attachment.attach_field(field2)
                except:
                    pass

                try :
                    field3 = AttachmentFieldsClass()
                    field3.title = "Email Id :"
                    field3.value = customer_data[i]['PrimaryEmailAddr']['Address']
                    attachment.attach_field(field3)
                except:
                    pass

                try:
                    field4 = AttachmentFieldsClass()
                    field4.title = "Balance:"
                    field4.value = customer_data[i]['Balance']
                    attachment.attach_field(field4)
                except:
                    pass
                message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)

    def get_customer_details(self,args):

        print("In get_customer_details")

        # Fetching arguments passed from Slack
        customerId = args['customer_id']

        # API call parameters for getting customer details
        route = "/v3/company/" + self.realmID + "/customer/" + customerId
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            response = json.loads(json.dumps(xmltodict.parse(r.text)))
            print(response)

            #'IntuitResponse'
            #'DisplayName'
            #'Balance'
            #'PrimaryEmailAddr' 'Address'

            # Creating message object using YA SDK
            message = MessageClass()
            message.message_text = "Customer details :"

            attachment = MessageAttachmentsClass()
            try:
                field1 = AttachmentFieldsClass()
                field1.title = "Name :"
                field1.value = response['IntuitResponse']['Customer']['DisplayName']
                attachment.attach_field(field1)
            except:
                pass

            try:
                field2 = AttachmentFieldsClass()
                field2.title = "Email Id :"
                field2.value = response['IntuitResponse']['Customer']['PrimaryEmailAddr']['Address']
                attachment.attach_field(field2)
            except:
                pass

            try:
                field3 = AttachmentFieldsClass()
                field3.title = "Balance:"
                field3.value = response['IntuitResponse']['Customer']['Balance']
                attachment.attach_field(field3)
            except:
                pass

            try:
                field4 = AttachmentFieldsClass()
                field4.title = "Customer Id:"
                field4.value = response['IntuitResponse']['Customer']['Id']
                attachment.attach_field(field4)
            except:
                pass

            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            #d = json.loads(r.text)
            m.message_text = "You entered an invalid customer id.\nPlease try again with valid arguments."  #d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)

    def create_customer(self,args):


        print("In create_customer")

        # API call parameters for creating a customer
        route = "/v3/company/" + self.realmID + "/customer"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'accept': 'application/json'}

        # Fetching the arguments passed from slack
        notes = args['notes']
        display_name = args['display_name']
        email = args['e-mail']

        # payload for API call
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

        # Consuming the API
        r = requests.post(settings.PRODUCTION_BASE_URL + route, headers=headers, json=payload)

        # Response check
        if (r.status_code == requests.codes.ok):

            # Getting the response
            response = json.loads(r.text)

            print(response)

            # Creating message using YA SDK
            message = MessageClass()
            message.message_text = "New customer " + display_name +  " created successfully !"
            attachment = MessageAttachmentsClass()
            try:
                field1 = AttachmentFieldsClass()
                field1.title = "Name :"
                field1.value = display_name
                attachment.attach_field(field1)
            except:
                pass

            try:
                field2 = AttachmentFieldsClass()
                field2.title = "ID :"
                field2.value = response["Customer"]["Id"]
                attachment.attach_field(field2)
            except:
                pass
            try:
                field3 = AttachmentFieldsClass()
                field3.title = "Balance :"
                field3.value = response["Customer"]["Balance"]
                attachment.attach_field(field3)
            except:
                pass
            message.attach(attachment)
            return message.to_json()
        else:
            m = MessageClass()
            print(r.text)
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)

    def list_all_invoices(self,args):

        print("In list_all_invoice_ids")

        # API parameters for getting all invoices
        route = "/v3/company/" + self.realmID + "/query?query=select * from Invoice"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Getting response in JSON
            response = json.loads(json.dumps(xmltodict.parse(r.text)))

            # print(response)
            data = response['IntuitResponse']['QueryResponse']['Invoice']

            print(data)

            # Creating message object from YA SDK
            message = MessageClass()
            message.message_text = "All Invoice details :"

            for i in range(0, len(data)):
                attachment = MessageAttachmentsClass()
                try:
                    field1 = AttachmentFieldsClass()
                    field1.title = "Invoice Id :"
                    field1.value = data[i]['Id']
                    attachment.attach_field(field1)
                except:
                    pass

                try:
                    field2 = AttachmentFieldsClass()
                    field2.title = "Total Amount :"
                    field2.value = data[i]['TotalAmt']
                    attachment.attach_field(field2)
                    message.attach(attachment)
                except:
                    pass

                try:
                    field3 = AttachmentFieldsClass()
                    field3.title = "For :"
                    field3.value = data[i]['CustomerRef']['@name']
                    attachment.attach_field(field3)
                    message.attach(attachment)
                except:
                    pass

                try:
                    field4 = AttachmentFieldsClass()
                    field4.title = "Due date :"
                    field4.value = data[i]['DueDate']
                    attachment.attach_field(field4)
                    message.attach(attachment)
                except:
                    pass

            return message.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)

    def list_all_customer_ids(self, args):
        '''
        Picklist function to get list of customer ids
        '''

        print("In list_all_customer_ids")

        # API call parameters for getting all customer ids
        route = "/v3/company/" + self.realmID + "/query?query=select * from Customer"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Fetching response in JSON
            response = json.loads(json.dumps(xmltodict.parse(r.text)))
            # print(response)

            customer_data = response['IntuitResponse']['QueryResponse']['Customer']

            # Creating a message object using YA SDK functions
            m = MessageClass()
            m.message_text = "This is list all customer picklist function"

            ### Hardcoded
            ### Change It !
            data = []
            #customer_data[i]
            for i in range(0,len(customer_data)):
                data.append({"id":"12"})
            m.data = data
            return m.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text)
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)


    def list_all_invoice_ids(self, args):

        print("In list_all_invoice_ids")

        # API call parameters to get all invoice ids
        route = "/v3/company/" + self.realmID + "/query?query=select * from Invoice"
        bearer = getBearerTokenFromRefreshToken(self.quickbook_access_token_object.refreshToken, self.user_integration)
        auth_header = 'Bearer ' + bearer.accessToken
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}

        # Consuming the API
        r = requests.get(settings.PRODUCTION_BASE_URL + route, headers=headers)

        # Response check
        if r.status_code == requests.codes.ok:

            # Fetching response in JSON
            response = json.loads(json.dumps(xmltodict.parse(r.text)))
            # print(response)
            data = response['IntuitResponse']['QueryResponse']['Invoice']
            print(data)
            m = MessageClass()
            m.message_text = "This is list all invoices picklist function"
            #data[i]["Id"]

            ## Hardcoded
            ## Change It

            data = []
            # for i in range(0,len(data)):
            data.append({"id":"12"})
            m.data = data
            return m.to_json()
        else:
            m = MessageClass()
            d = json.loads(r.text.decode("utf-8"))
            m.message_text = d["Fault"]["Error"][0]["Detail"]
            return m.to_json() #"{0}: {1}".format(r.status_code, r.text)
