import angular from 'angular';
import uiRouter from 'angular-ui-router';
import angularMaterial from 'angular-material';

import { appToolbar } from 'yellowant-common-client/src/angularjs/components/app-toolbar/app-toolbar';

import { angularMaterialConfig } from 'yellowant-common-client/src/angularjs/config/angular-material.config';
import { csrfConfig } from 'yellowant-common-client/src/angularjs/config/csrf.config';

import { AppComponent } from './app.component';

import { accountListScreen } from './screens/account-list/account-list';
import { accountSettingsScreen } from './screens/account-settings/account-settings';
import { fourOhFourScreen } from 'yellowant-common-client/src/angularjs/screens/four-oh-four/four-oh-four';

export let statuspageApp = angular
  .module('quickbooks-app', [
    angularMaterial,
    uiRouter,
    appToolbar,
    angularMaterialConfig,
    csrfConfig,
    accountListScreen,
    accountSettingsScreen,
    fourOhFourScreen
  ])
  .config(routeConfig)
  .component('yellowantQuickbooksApp', AppComponent)
  .name;


routeConfig.$inject = ['$locationProvider', '$stateProvider', '$urlRouterProvider', "$urlMatcherFactoryProvider"];
function routeConfig($locationProvider, $stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
  $locationProvider.html5Mode(true);

  $urlRouterProvider.otherwise('/404/');
  $urlMatcherFactoryProvider.strictMode(false);

  var accountListState = {
    name: 'accountList',
    url: '/',
    component: 'accountListScreen'
  };
  var accountSettingsState = {
    name: 'accountSettings',
    url: '/accounts/{accountId}',
    component: 'accountSettingsScreen'
  };

  var fourOhFourState = {
    name: 'fourOhFour',
    url: '/404/',
    component: 'fourOhFourScreen'
  };

  $stateProvider.state(accountListState);
  $stateProvider.state(accountSettingsState);
  $stateProvider.state(fourOhFourState);
}