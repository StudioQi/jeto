function UsersListController($scope, $routeParams, createDialog, Users) {
    $scope.update = function() {
        Users.get({}, function(infos) {
            $scope.users = infos.users;
            $scope.users.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        });
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

function AdminUserController($scope, $routeParams, Users) {
    $scope.update = function() {
        Users.get({id: $routeParams.id}, function(infos) {
            $scope.user = infos.user;
            $scope.resource = infos;
        });
    };
    $scope.giveAdminRights = function() {
        $scope.user.role = 'admin';
        $scope.resource.$save({id: $scope.user.id});
    };
    $scope.removeAdminRights = function() {
        $scope.user.role = 'dev';
        $scope.resource.$save({id: $scope.user.id});
    };
    $scope.update();
}

function UserController($scope, $routeParams, Users) {
    Users.get({'id': $routeParams.id},
        function(infos){
            $scope.user = infos.user;
            $scope.resource = infos;
        }
    );
    $scope.delete = function(api_key){
        angular.forEach($scope.user.api_keys, function(api_key, index){
            console.log(api_key.value);
            console.log(this.value);
            if(api_key.value == this.value){
               $scope.user.api_keys.splice(index, 1);
            }
        }, api_key);
        $scope.resource.$save({'id': $scope.resource.user.id});
    }
}
