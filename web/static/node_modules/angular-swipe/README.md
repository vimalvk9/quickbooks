Simple vertical/horizontal swipe gesture directives and a swipe service for AngularJS

#angular-swipe

Should be used as a replacement for ngTouch and its ngSwipeLeft and ngSwipeRight directives. The problem with ngTouch is that it replaces all default ngClick directives and can screw up how focus event works in input fields which are wrapped with ngClick directive. More on the problem with ngTouch here: https://github.com/angular/angular.js/issues/6432#issuecomment-54636616. 

## Install

+ This is intended to be used as npm module only and works really well with browserify.

>
``` 
npm install angular-swipe --save-dev
```

+ Require the angular-swipe module

>
``` javascript
import swipe from 'angular-swipe'
```

+ Add dependency to the angular-swipe ng module

>
``` javascript
angular.module('app', [ swipe.name ]);
```

## Usage

#### Directives

* ng-swipe-up
* ng-swipe-down
* ng-swipe-left
* ng-swipe-right

#### Directive attributes

`ng-swipe-disable-mouse` "This attribute is useful for text that should still be selectable by the mouse and not trigger the swipe action."

#### Service

* swipe

## Example

>
```html
<div class="page" ng-controller="AppController">
    <div class="container" ng-swipe-up="swipe($event)">
      <h1>Swipe me up!</h1>
    </div>
</div>
```

>
```javascript
import { module, bootstrap } from 'angular';
import swipe from 'angular-swipe';
module('app', [ swipe.name ])
    .controller('AppController', $scope => {
      $scope.swipe = $event => console.log($event);
    })
```

## Known issues and workarounds

* ng-swipe-up and ng-swipe-down uses preventDefault when you start swiping. This prevents clicks from giving focus to input fields. Adding a `noPreventDefault` class to these elements will not preventDefault when the swipe start on them and thus allow clicks to work.
