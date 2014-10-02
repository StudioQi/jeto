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

function TeamController($scope, $routeParams, Teams, Users, Hosts, Projects, $http, $location) {
    watchFunction = function(newValue, oldValue) {
        if(newValue !== undefined && newValue !== oldValue){
            $scope.team.$save();
        }
    };
    // Will fetch the team and all the infos with it
    $scope.init = function() {
        Teams.get({id: $routeParams.id}, function(infos) {
            $scope.team = infos;
            $scope.$watch('team', watchFunction, true);
            $scope.resource = infos;
            $scope.update();
        });

        Hosts.get({}, function(infos) {
            $scope.hosts = infos.hosts;
        });

        Projects.get({}, function(infos) {
            $scope.projects = infos.projects;
        });

        $scope.clearInfos();
        $scope.$watch('newPermission.objectType', function(newType, oldType) {
            if(newType != oldType){
                if(newType == 'host'){
                    Hosts.get({}, function(infos) {
                        $scope.newPermission.objects = infos.hosts;
                    });
                } else if(newType == 'project'){
                    Projects.get({}, function(infos) {
                        $scope.newPermission.objects = infos.projects;
                    });
                }
            }
        });
    };
    $scope.clearInfos = function() {
        $scope.newPermission = { 
            'objectType' : '',
            'objectId': '',
            'objects': Array(),
            'ViewHost': true,
            'ViewInstances': true,
            'ProvisionInstances': false,
            'StartInstances': false,
            'StopInstances': false,
            'DestroyInstances': false,
        };

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
    };


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
        lstPermissions = Array();
        angular.forEach($scope.team.permissions_grids, function(value) {
            lstPermissions.push(value);
        });

        $http.put('/api/teams/' + $scope.team.id, {
            users: lstUsers,
            permissionsGrid: lstPermissions
        })
        .success(function(){
            $location.path('/admin/teams');
        });
    };
    $scope.addPermission = function() {
        if($scope.newPermission.objectType == 'project'){
            $scope.newPermission.ViewHost = false;
        }
        if($scope.newPermission.objectType == 'host'){
            $scope.newPermission.ViewInstances = false;
        }

        newPermission = {
            'objectId': $scope.newPermission.objectId,
            'objectType': $scope.newPermission.objectType,
        }

        if($scope.newPermission.ViewHost || $scope.newPermission.ViewInstances){
            permission = angular.copy(newPermission);
            permission['action'] = 'view';
            $scope.team.permissions_grids.push(permission);
        }
        if($scope.newPermission.StartInstances){
            permission = angular.copy(newPermission);
            permission['action'] = 'start';
            $scope.team.permissions_grids.push(permission);
        }
        if($scope.newPermission.StopInstances){
            permission = angular.copy(newPermission);
            permission['action'] = 'stop';
            $scope.team.permissions_grids.push(permission);
        }
        if($scope.newPermission.DestroyInstances){
            permission = angular.copy(newPermission);
            permission['action'] = 'destroy';
            $scope.team.permissions_grids.push(permission);
        }
        if($scope.newPermission.ProvisionInstances){
            permission = angular.copy(newPermission);
            permission['action'] = 'provision';
            $scope.team.permissions_grids.push(permission);
        }

        $scope.clearInfos();
    }

    $scope.getObjectName = function(objectId, objectType) {
        var found;
        if(objectType == 'host') {
            angular.forEach($scope.hosts, function(host) { 
                if(host.id == objectId) {
                    found = host;
                }
            }, found);
        } else if (objectType == 'project') {
            angular.forEach($scope.projects, function(project) { 
                if(project.id == objectId) {
                    found = project;
                }
            }, found);
        }

        if(found !== undefined){
            return found.name;
        }
        return undefined;
    };

    $scope.removePermission = function(permission) {
        angular.forEach($scope.team.permissions_grids, function(value, key){
            if(value.objectType == permission.objectType && value.objectId == permission.objectId && value.action == permission.action){
                $scope.team.permissions_grids.splice(key, 1);
            }
        });
    };
}
