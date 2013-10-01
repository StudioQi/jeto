'use strict';

/* Controllers */

function IndexController($scope) {
}

function InstancesController($scope, Instances, $http, createDialog) {
    var instancesQuery = Instances.get({}, function(infos) {
        $scope.instances = infos.instances;
        $scope.stopped = infos.stopped;
        $scope.running = infos.running;
        $scope.resource = infos;
    })

    $scope.create = function() {
        createDialog('/static/partials/create.html',{ 
           id : 'createDialog', 
           title: 'Create a new machine',
           backdrop: true, 
           success: {
               label: 'Create',
               fn: function(){
                   console.log('Successfully closed modal');
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    }

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

    $scope.control = function(instanceId, state) {
        $http.post('/api/instances/', {
            state : state,
            instanceId : instanceId,
        })
        .success(function(infos) {
            $scope.instances = infos.instances;
            $scope.stopped = infos.stopped;
            $scope.running = infos.running;
            $scope.resource = infos;
        })
    }

}

function InstanceController($scope, $routeParams, Instances) {
    var instancesQuery = Instances.get({instanceId: $routeParams.instanceId}, function(instance) {
        $scope.instance = instance;
        console.log(instance);
    });
    $scope.setName = function(newName) {
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
