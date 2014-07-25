function HtpasswordListController($scope, $routeParams, Htpassword, $http, $location, createDialog) {
    $scope.update = function() {
        Htpassword.get({slug: $routeParams.slug}, function(infos) {
            $scope.item = infos.item;
            $scope.changed = false;
            $scope.resource = infos;
        });
    };
    $scope.update();

    $scope.resetInfos = function(){
        $scope.newItem = {
            'username': '',
            'password': '',
            'state': 'CREATE',
        };
       setTimeout($scope.update, 100);
    };

    $scope.add = function(){
        $scope.item.users.push({'username':$scope.newItem.username, 'password': $scope.newItem.password, 'state': 'CREATE'});
        $scope.changed = true;
        $scope.newItem['username'] = '';
        $scope.newItem['password'] = '';
    };

    $scope.deleteUser = function(username){
        angular.forEach($scope.item.users, function(value, key){
            if(value.username == username){
                if(value.state == 'CREATE'){
                    $scope.item.users.splice(key, 1);
                } else {
                    $scope.item.users[key].state = 'DELETE';
                    $scope.changed = true; }
            }
        });
    };

    $scope.cancelDeleteUser = function(username){
        angular.forEach($scope.item.users, function(value, key){
            if(value.username == username){
                $scope.item.users[key].state = 'DEFAULT';
            }
        });
    };

    $scope.save = function(){
        $http.put('/api/htpassword/' + $scope.item.slug, {
            users: $scope.item.users,
        })
        .success(function(infos){
            $scope.resetInfos();
            $location.path('/htpassword');
        });
    };

    $scope.cancel = function(){
        $scope.resetInfos()
        $location.path('/htpassword');
    };

    $scope.delete = function() {
        createDialog('', {
            id : 'deleteDialog', 
            title: 'Delete user list',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>[[ item.slug ]]</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    var list = new Htpassword();
                    list.name = $scope.item.slug;
                    list.slug = $scope.item.slug;
                    list.$delete();
                    $location.path('/htpassword');
                }
            },
            cancel: {
                label: 'Cancel',
            },
        });
    };
}
