function InstanceController($scope, $routeParams, Instances, $http, createDialog, $location) {
    $('.loading').show();
    var instancesQuery = Instances.get({id: $routeParams.id}, function(instance) {
        $scope.instance = instance;
        $scope.source = new EventSource('/pubsub/' + $scope.instance.id);
        $scope.source.addEventListener('message', pubsubCallback, false);
        $('.loading').hide();
    });

    $scope.updateInfos = function() {
        var instanceQuery = Instances.get({id: $routeParams.id}, function(instance) {
            $scope.instance = instance;
            $('.loading').hide();
        });
    };

    $scope.setName = function(newName) {
        $scope.instance.$save();
    };

    $scope.control = function(state) {
        // $('.loading').show();
        $http.post('/api/instances/' + $scope.instance.id, {
            state : state,
            async: true
        })
        .success(function(result) {
           setTimeout($scope.updateInfos, 100);
        });
    };

    $scope.delete = function() {
        createDialog('', {
            id : 'deleteDialog', 
            title: 'Delete instance',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete the instance <b>[[instance.name]]</b>?',
            success: {
                label: 'Delete',
                fn: function(){
                    $('.loading').show();
                    $http.delete('/api/instances/' + $scope.instance.id)
                        .success(function(infos) {
                            $('.loading').hide();
                            $location.path('/instances');
                        });
                }
            },
            cancel: {
                label: 'Cancel',
            },
        });
    };

    $scope.console = {};
    pubsubCallback = function(consoleData) {
        $scope.$apply(function () {
            if(consoleData.data !== ''){
                $scope.console = consoleData.data;
                $('#console').html($scope.console);
                consoleDiv = $('#console').get(0);
                if(consoleDiv !== undefined){
                    consoleDiv.scrollTop = consoleDiv.scrollHeight;
                }
            }
        });
    };
}
