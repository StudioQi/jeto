/* Directives */

angular.module('angularFlaskDirectives', [])
.directive('appversion', ['version', function(version) {
  return function(scope, elm, attrs) {
    elm.text('Version : ' + version);
  };
}])
.directive("contenteditable", function() {
  return {
    restrict: "A",
    require: "ngModel",
    link: function(scope, element, attrs, ngModel) {

      function read() {
        ngModel.$setViewValue(element.html());
      }

      ngModel.$render = function() {
        element.html(ngModel.$viewValue || "");
      };

      element.bind("blur", function() {
        scope.$apply(read);
      });
    }
  };
});
