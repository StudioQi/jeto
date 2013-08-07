'use strict';

/* Controllers */

function IndexController($scope) {
}

function InstancesController($scope, Instances) {
    var instancesQuery = Instances.get({}, function(instances) {
        $scope.instances = instances.instances;
    })
}

function InstanceController($scope, $routeParams, Instances) {
    var instancesQuery = Instances.get({instanceId: $routeParams.instanceId}, function(instance) {
        console.log(instance)
        $scope.instance = instance;
    })
}
