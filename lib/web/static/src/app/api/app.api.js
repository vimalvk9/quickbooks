import angular from 'angular';

import { djangoConstants } from 'yellowant-common-client/src/angularjs/django-constants';

export let appApi = angular
  .module('appApi', [
    djangoConstants
  ])
  .factory('AppApi', AppApi).name;

AppApi.$inject = ['$http', 'DjangoConstants'];

function AppApi(http, DjangoConstants) {
  var baseEndpoint = DjangoConstants.base_href;

  var endpoint = {
    userAccounts: function () { return baseEndpoint + 'user/' },
    userWebhooks: function (integrationId) { return endpoint.userAccounts() + integrationId + "/webhook/"}
  };

  return {
    getUserAccounts : getUserAccounts,
    getUserAccount: getUserAccount,
    deleteUserAccount: deleteUserAccount,
    deleteUserWebhook: deleteUserWebhook,
    submitForm : submitForm
  }

  function submitForm(data){
    return http.post(baseEndpoint + 'apiKey/', data)
  }

  function getUserAccounts() {
    return http.get(endpoint.userAccounts());
  }

  function getUserAccount(integrationId) {
    return http.get(endpoint.userAccounts() + integrationId + "/");
  }

  function deleteUserAccount(integrationId) {
    return http.delete(endpoint.userAccounts() + integrationId + "/");
  }

  function deleteUserWebhook(integrationId, webhookId) {
    return http.delete(endpoint.userWebhooks(integrationId) + webhookId + "/");
  }
}