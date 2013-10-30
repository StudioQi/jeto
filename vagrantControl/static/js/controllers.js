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
        createDialog('/static/partials/create.html',{ 
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

    $scope.stopInstance = function(instanceId) {
        $http.post('/api/instances/', {
            state : 'stop',
            id : instanceId,
        })
        .success(function(result) {
        });
    };

    $scope.startInstance = function(instanceId) {
        angular.forEach($scope.instances, function(instance, idx){
            if(instance.id == instanceId){
                $scope.instances[idx].state = 'start';
            }
        });
        $scope.resource.$save();
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
            $scope.instances = infos.instances;
            $scope.resource = infos;
        });
    };

}

function InstanceController($scope, $routeParams, Instances) {
    var instancesQuery = Instances.get({id: $routeParams.id}, function(instance) {
        $scope.instance = instance;
    });
    $scope.setName = function(newName) {
        $scope.instance.$save();
    };
    $scope.stop = function() {
        $scope.instance.state = 'stop';
        $scope.instance.$save();
    };
    $scope.start = function() {
        $scope.instance.state = 'start';
        $scope.instance.$save();
    };
}
