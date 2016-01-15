var app = angular.module('jeto');

app.controller('GenericController', ['$scope', 'CurrentUser', function($scope, CurrentUser){
    $scope.current_user = CurrentUser.get();
    window.test = $scope.current_user;

}]);
