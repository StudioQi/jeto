'use strict';

/* Controllers */

function IndexController($scope) {
}

function InstancesController($scope, Instances) {
    var instancesQuery = Instances.get({}, function(infos) {
        $scope.instances = infos.instances;
        $scope.regions = infos.regions;
        $scope.stopped = infos.stopped;
        $scope.running = infos.running;
        console.log(infos);
    })
}

function InstanceController($scope, $routeParams, Instances) {
    var instancesQuery = Instances.get({instanceId: $routeParams.instanceId}, function(instance) {
        $scope.instance = instance;
        console.log(instance);
    })
}
