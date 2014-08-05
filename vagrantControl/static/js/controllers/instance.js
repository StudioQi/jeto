function InstanceController($scope, $routeParams, Instances, MachineIP, $http, createDialog, $location) {
    $('.loading').show();
    Instances.get({id: $routeParams.id}, function(instance) {
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

    $scope.refreshIP = function(event, machineName) {
        clickedElement = angular.element(event.currentTarget); 
        refreshIcon = angular.element(clickedElement.find('span')[0]);
        refreshIcon.addClass('icon-refresh-animate');
        MachineIP.get(
            {id: $routeParams.id, machineName: machineName},
            function(info){
                refreshIcon.removeClass('icon-refresh-animate');
                angular.forEach($scope.instance.status, function(value, key){
                    if(value['name'] == machineName){
                        $scope.instance.status[key]['ip'] = info['ip'];
                    }
                });
            }
        );
    };

    $scope.control = function(state, machineName) {
        // $('.loading').show();
        $http.post('/api/instances/' + $scope.instance.id, {
            state : state,
            machine: machineName,
            async: true
        })
        .success(function(result) {
           setTimeout($scope.updateInfos, 100);
        });
    };

    $scope.setName = function(newName) {
        $scope.instance.$save();
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
