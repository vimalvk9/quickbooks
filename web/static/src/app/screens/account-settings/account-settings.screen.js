import template from './account-settings.html';
import { AccountSettingsController as controller } from './account-settings.controller';
import './account-settings.scss';

controller.$inject = ["AppApi", "$stateParams", "$mdDialog", "$mdToast", "$state"];

export let AccountSettingsScreen = {
  template,
  controller
}