'use strict';

import { module, bootstrap } from 'angular';
import swipe from './../src/angular-swipe';

module('app', [
  swipe.name
])
  .controller('AppController', $scope => {
    $scope.message = 'Hey!';
    $scope.inputtest = '';
    $scope.swipe = $event => console.log($event);
    $scope.$watch('inputtest', newVal => $scope.message = `Hey ${ newVal } !`);
  });

bootstrap(document.body, ['app']);