function UsersListController($scope, $routeParams, createDialog, Users) {
    $scope.update = function() {
        Users.get({}, function(infos) {
            $scope.users = infos.users;
            $scope.users.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        })
    };
    $scope.update();
    $scope.delete = function(user) {
        $scope.deleteId = user.id;
        createDialog({
            id : 'createDialog', 
            title: 'Delete user',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + user.name +'</b> ?',
            success: {
                label: 'Yes, delete it',
                fn: function(){
                    $('.loading').show();
                    Users.delete({id: $scope.deleteId});
                    setTimeout($scope.update, 100);
                    $scope.deleteId = undefined;
                }
            },
            cancel: {
                label: 'Cancel',
            },
        });
    }
}

function UserController($scope, $routeParams, Users) {
    $scope.update = function() {
        Users.get({id: $routeParams.id}, function(infos) {
            $scope.user = infos.user;
            console.log($scope.user);
            $scope.resource = infos;
        })
    };
    $scope.update();
}
