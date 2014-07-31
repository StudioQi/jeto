function TeamsListController($scope, $routeParams, Teams, $http, $location, createDialog) {
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

function TeamController($scope, $routeParams, Teams, Users, $http, $location) {
    // Will fetch the team and all the infos with it
    $scope.init = function() {
        Teams.get({id: $routeParams.id}, function(infos) {
            $scope.team = infos.team;
            $scope.resource = infos;
            $scope.update();
        });
    };
    // Will fetch all users and remove those already in team.users
    // Used in the "Add user" box, also called to filter out values
    // when a new user is added into the team
    $scope.update = function() {
        Users.get({}, function(infos) {
            $scope.users = infos.users.filter(function(value) {
                keepItem = true;
                angular.forEach($scope.team.users, function(teamUser){
                    if(keepItem == true && value.id == teamUser.id){
                        keepItem = false;
                    }
                });
                return keepItem;
            });
        });
    }

    $scope.init();
    $scope.add = function() {
        if($scope.newUser !== ''){
            Users.get({id: $scope.newUser}, function(infos) {
                user = infos.user;
                found = false;
                angular.forEach($scope.team.users, function(value) {
                    if(found == false && value.id == user.id){
                        found = true;
                    }
                }, this);
                if(found == false){
                    $scope.team.users.push(infos.user);
                }
                $scope.update();
            });
        }
    }
    $scope.removeUser = function(user) {
        $scope.team.users = $scope.team.users.filter(function(value) {
            return user.id != value.id;
        });
        $scope.update();
    }
    $scope.save = function() {
        lstUsers = Array();
        angular.forEach($scope.team.users, function(value) {
            lstUsers.push(value.id);
        }, lstUsers);
        $http.put('/api/teams/' + $scope.team.id, {
            users: lstUsers
        })
        .success(function(){
            $location.path('/admin/teams');
        });
    };
}
