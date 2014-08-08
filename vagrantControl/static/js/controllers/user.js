function UsersListController($scope, $routeParams, Users) {
    $scope.update = function() {
        Users.get({}, function(infos) {
            $scope.users = infos.users;
            $scope.users.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        })
    };
    $scope.update();
}

function UserController($scope, $routeParams, Users) {
    $scope.update = function() {
        Users.get({id: $routeParams.id}, function(infos) {
            $scope.user = infos.user;
            $scope.resource = infos;
        })
    };
    $scope.update();
}
