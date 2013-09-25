'use strict';

/* Controllers */

function IndexController($scope) {
}

function InstancesController($scope, Instances, $http) {
    var instancesQuery = Instances.get({}, function(infos) {
        $scope.instances = infos.instances;
        $scope.regions = infos.regions;
        $scope.stopped = infos.stopped;
        $scope.running = infos.running;
        //console.log(infos);
    })

    $scope.stopInstance = function(instanceId) {
        $http.post('/api/instances/' + instanceId + '/status', {
            status : 'stopped',
        })
        .success(function(test) {
            //console.log(test);
        })
    }

    $scope.startInstance = function(instanceId) {
        $http.post('/api/instances/' + instanceId + '/status', {
            status : 'start',
        })
        .success(function(test) {
            //console.log(test);
        })
    }

}

function InstanceController($scope, $routeParams, Instances) {
    var instancesQuery = Instances.get({instanceId: $routeParams.instanceId}, function(instance) {
        $scope.instance = instance;
        //console.log(instance);
    })
}
