function SSLKeysListController($scope, $routeParams, SSLKeys, DomainControllers, $http, $location, createDialog) {
    $scope.update = function() {
        SSLKeys.get({}, function(infos) {
            $scope.ssl_keys = infos.keys;
            $scope.ssl_keys.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        });
        DomainControllers.get({}, function(infos){
            $scope.domain_controllers = infos.domain_controllers;
        });
    };

    $scope.update();
    $scope.resetInfos = function(){
       setTimeout($scope.update, 100);
       $scope.ssl_keyInfo = {
           'name': '',
           'domain_controller': '',
           'cert': '',
           'key': '',
       };
    };

    $scope.resetInfos();

    $scope.create = function() {
        createDialog('/partials/admin/SSLKeys/form.html',{
           id : 'createDialog',
           title: 'Add a new SSL Key',
           backdrop: true,
           scope: $scope,
           success: {
               label: 'Add',
               fn: function(){
                   $('.loading').show();
                   var ssl_keys = new SSLKeys();
                   ssl_keys.name = $scope.ssl_keyInfo.name;
                   ssl_keys.domain_controller = $scope.ssl_keyInfo.domain_controller;
                   ssl_keys.cert = $scope.ssl_keyInfo.cert;
                   ssl_keys.key = $scope.ssl_keyInfo.key;
                   ssl_keys.state = 'create';
                   ssl_keys.$save();
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
            title: 'Delete SSL Key',
            backdrop: true,
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + item.name +'</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    $('.loading').show();
                    id = $scope.deleteItemId;
                    $http.delete('/api/SSLKeys/' + id)
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

function SSLKeyController($scope, $routeParams, SSLKeys, $http, $location, createDialog) {
    watchFunction = function(newValue, oldValue) {
        if(newValue !== undefined && newValue !== oldValue){
            $scope.ssl_key.$save();
        }
    };
    $scope.update = function() {
        SSLKeys.get({id: $routeParams.id}, function(infos) {
            $scope.ssl_key = infos;
            $scope.$watch('ssl_key', watchFunction, true);
            $scope.resource = infos;
        });
    };

    $scope.update();
}
