function UsersListController($scope, $routeParams, Teams, $http, $location, createDialog) {
    $scope.update = function() {
        Teams.get({}, function(infos) {
            $scope.teams = infos.teams;
            $scope.teams.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        })
    };
    $scope.update();
    $scope.resetInfos = function(){
       setTimeout($scope.update, 100);
       $scope.teamInfo = {
           'name': '',
       };
    };
    $scope.resetInfos();


    $scope.create = function() {
        createDialog('/partials/admin/teams/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new team',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   $('.loading').show();
                   var host = new Teams();
                   host.name = $scope.teamInfo.name;
                   host.params = $scope.teamInfo.params;
                   host.provider = $scope.teamInfo.provider;
                   host.state = 'create';
                   host.$save();
                   setTimeout($scope.resetInfos, 100);
               }
           },
           cancel: {
               label: 'Cancel',
           },
        });
    };

    $scope.delete = function(item) {
        $scope.deleteItemId = item.id;
        createDialog({
            id : 'deleteDialog', 
            title: 'Delete team',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + item.name +'</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    $('.loading').show();
                    id = $scope.deleteItemId;
                    $http.delete('/api/teams/' + id)
                    .success(function() {
                        setTimeout($scope.update, 100);
                    });
                }
            },
            cancel: {
                label: 'Cancel',
            },
        });
    };
}

function UserController($scope, $routeParams, Teams, $http, $location) {
    $scope.update = function() {
        Teams.get({id: $routeParams.id}, function(infos) {
            $scope.team = infos.team;
            $scope.resource = infos;
        })
    };
    $scope.update();
    $scope.resetInfos = function(){
       setTimeout($scope.update, 100);
    };
}
