import template from './app.html';
import { AppController as controller } from './app.controller';
import './app.scss';

controller.$inject = ["$state"];

export let AppComponent = {
  template,
  controller
}