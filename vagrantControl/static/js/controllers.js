/* Controllers */

function IndexController($scope) {
}

function InstancesController($scope, Instances, $http, createDialog, $log) {
    var instancesQuery = Instances.get({}, function(infos) {
        $scope.instances = infos.instances;
        $scope.stopped = infos.stopped;
        $scope.running = infos.running;
        $scope.resource = infos;
    });

    $scope.updateInfos = function() {
        var instancesQuery = Instances.get({}, function(infos) {
            $scope.instances = infos.instances;
            $scope.stopped = infos.stopped;
            $scope.running = infos.running;
            $scope.resource = infos;
        });
    };

    $scope.instanceInfo = {
        'name': '',
        'path': '',
    };

    $scope.create = function() {
        createDialog('/partials/instances/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new machine',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   var instance = new Instances();
                   instance.name = $scope.instanceInfo.name;
                   instance.path = $scope.instanceInfo.path;
                   instance.environment = $scope.instanceInfo.environment;
                   instance.state = 'create';
                   instance.$save();
                   $scope.updateInfos();
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    };

    $scope.control = function(instanceId, state) {
        $http.post('/api/instances/', {
            state : state,
            id : instanceId,
        })
        .success(function(result) {
            instanceInfos = result.instance;
            angular.forEach($scope.instances, function(instance, idx){
                console.log(instance);
                if(instance.id == instanceInfos.id){
                    $scope.instances[idx] = instanceInfos;
                }
            });
        });
    };

    $scope.delete = function(instanceId) {
        $http.delete('/api/instances/' + instanceId)
        .success(function(infos) {
            $scope.updateInfos();
        });
    };

    $scope.status = {};
    pubsubCallback = function(status) {
        $scope.$apply(function() {
            $scope.status = JSON.parse(infos.data);
        });
    };
    var source = new EventSource('/pubsub', pubsubCallback, false);
}

function InstanceController($scope, $routeParams, Instances, $http, $location) {
    var instancesQuery = Instances.get({id: $routeParams.id}, function(instance) {
        $scope.instance = instance;
    });

    $scope.updateInfos = function() {
        var instanceQuery = Instances.get({id: $routeParams.id}, function(instance) {
            $scope.instance = instance;
        });
    };

    $scope.setName = function(newName) {
        $scope.instance.$save();
    };

    $scope.control = function(state) {
        $http.post('/api/instances/' + $scope.instance.id, {
            state : state,
        })
        .success(function(result) {
            instanceInfos = result.instance;
            angular.forEach($scope.instances, function(instance, idx){
                $scope.instance = instanceInfos;
            });
        });
    };

    $scope.delete = function() {
        $http.delete('/api/instances/' + $scope.instance.id)
        .success(function(infos) {
            $location.path('/instances');
        });
    };
}

function DomainsController($scope, $routeParams, Domains, $http, $location, createDialog) {
    $scope.update = function() {
        Domains.get({}, function(infos) {
            $scope.domains = infos.domains;
            $scope.resource = infos;
        });
    };
    $scope.update();


    $scope.resetInfos = function(){
        $scope.domainInfo = {
            'domain': '',
            'ip': '',
        };
    };

    $scope.create = function() {
        createDialog('/partials/domains/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new domain',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   var domain = new Domains();
                   domain.domain = $scope.domainInfo.domain;
                   domain.ip = $scope.domainInfo.ip;
                   domain.$save();
                   $scope.update();
                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
               fn: $scope.resetInfos(),
           }
        });
    };

    $scope.edit = function(domainInfo) {
        $scope.domainInfo = {
            'domain': domainInfo.domain,
            'ip': domainInfo.ip,
            'slug': domainInfo.slug,
        };
        createDialog('/partials/domains/form.html',{ 
           id : 'editDialog', 
           title: 'Edit a domain',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Edit',
               fn: function(){
                   var domain = new Domains();
                   domain.domain = $scope.domainInfo.domain;
                   domain.ip = $scope.domainInfo.ip;
                   domain.slug = $scope.domainInfo.slug;
                   domain.$save();
                   $scope.update();
                   $scope.domainInfo = {
                       'domain': '',
                       'ip': '',
                   };
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    };

    $scope.delete = function(slug) {
        $http.delete('/api/domains/' + slug)
        .success(function() {
            $scope.update();
        });
    };
}

function HtpasswordController($scope, $routeParams, Htpassword, $http, $location, createDialog) {
    $scope.update = function() {
        Htpassword.get({}, function(infos) {
            $scope.lists = infos.lists;
            $scope.resource = infos;
        });
    };
    $scope.update();


    $scope.resetInfos = function(){
        $scope.list = {
            'slug': '',
            'name': '',
        };
    };

    $scope.create = function() {
        createDialog('/partials/htpassword/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new list',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   var list = new Htpassword();
                   list.name = $scope.list.name;
                   list.$save();
                   $scope.update();
                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
               fn: $scope.resetInfos(),
           }
        });
    };

    $scope.edit = function(list) {
        $scope.list = {
            'name': list.slug,
        };
        createDialog('/partials/domains/form.html',{ 
           id : 'editDialog', 
           title: 'Edit a list',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Edit',
               fn: function(){
                   var list = new Htpassword();
                   list.name = $scope.list.name;
                   list.$save();
                   $scope.update();
                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    };

    $scope.delete = function(slug) {
       var list = new Htpassword();
       list.name = slug;
       list.slug = slug;
       list.$delete();
    };
}
