function HostsListController($scope, $routeParams, Hosts, $http, createDialog) {
    $scope.update = function() {
        Hosts.get({}, function(infos) {
            $scope.hosts = infos.hosts;
            $scope.hosts.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        })
    };
    $scope.update();
    $scope.resetInfos = function(){
       setTimeout($scope.update, 100);
       $scope.hostInfo = {
           'name': '',
           'provider': '',
           'params': '',
       };
    };
    $scope.resetInfos();

    $scope.create = function() {
        createDialog('/partials/admin/hosts/form.html',{
           id : 'createDialog',
           title: 'Create a new host',
           backdrop: true,
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   $('.loading').show();
                   var host = new Hosts();
                   host.name = $scope.hostInfo.name;
                   host.params = $scope.hostInfo.params;
                   host.provider = $scope.hostInfo.provider;
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

    $scope.delete = function(host) {
        $scope.deleteHostId = host.id;
        createDialog({
            id : 'deleteDialog',
            title: 'Delete host',
            backdrop: true,
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + host.name +'</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    $('.loading').show();
                    id = $scope.deleteHostId;
                    $http.delete('/api/hosts/' + id)
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

function HostController($scope, $routeParams, $log, Hosts) {
    watchFunction = function(newValue, oldValue) {
        if(newValue !== undefined && newValue !== oldValue){
            $scope.host.$save();
        }
    };
    $scope.update = function() {
        Hosts.get({id: $routeParams.id}, function(infos) {
            $scope.host = infos;
            $scope.$watch('host', watchFunction, true);
            $scope.resource = infos;
        });
    };
    $scope.update();
}
