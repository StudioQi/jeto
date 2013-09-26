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
        $scope.resource = infos;
    })

    $scope.stopInstance = function(instanceId) {
        angular.forEach($scope.instances, function(instance, idx){
            if(instance.id == instanceId){
                $scope.instances[idx].state = 'stop';
            }
        })
        $scope.resource.$save();
    }

    $scope.startInstance = function(instanceId) {
        angular.forEach($scope.instances, function(instance, idx){
            if(instance.id == instanceId){
                $scope.instances[idx].state = 'start';
            }
        })
        $scope.resource.$save();
    }

}

function InstanceController($scope, $routeParams, Instances) {
    var instancesQuery = Instances.get({instanceId: $routeParams.instanceId}, function(instance) {
        $scope.instance = instance;
    });
    $scope.setName = function(newName) {
        $scope.instance.test = 'stopped';
        $scope.instance.$save();
    }
    $scope.stop = function() {
        $scope.instance.state = 'stop';
        $scope.instance.$save();
    };
    $scope.start = function() {
        $scope.instance.state = 'start';
        $scope.instance.$save();
    }
}
