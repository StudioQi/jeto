function InstanceController($scope, $routeParams, Instances, JobDetails, MachineIP, $http, createDialog, $location) {
    $('.loading').show();
    $scope.job = {};
    $scope.runScripts = [];
    $scope.updateInfos = function() {
        Instances.get({id: $routeParams.id},
            function(instance) {
                $scope.instance = instance;
                console.log(instance);

                // Let's say it's disabled by default
                $scope.canSync = false;
                if(instance.git_reference != ''){
                    // It should be of no use to update tag, only branches
                    if(instance.git_reference.indexOf('tags/') !== 0){
                        $scope.canSync = true;
                    }
                }

                angular.forEach($scope.instance.status, function(value, key) {
                    $scope.instance.status[key].stopDisabled = false;
                    if(value.status.indexOf('running') === -1){
                        $scope.instance.status[key].stopDisabled = true;
                    }
                    if($scope.instance.status[key].stopDisabled != false){
                        $scope.instance.stopDisabled = true;
                    }
                });

                if($scope.source === undefined){
                    $scope.source = new EventSource('/pubsub/' + $scope.instance.id);
                    $scope.source.addEventListener('message', pubsubCallback, false);
                }

                $('.loading').hide();
            },
            function(error) {
                alert("Something failed ... try to refresh.\n"
                    +"if you think it's a bug please report it on github\n"
                    +"https://github.com/StudioQi/jeto/issues\n"
                    +"Error message :\n" + error.message);
            }
        );
    };
    $scope.updateInfos();

    $scope.refreshIP = function(event, machineName) {
        clickedElement = angular.element(event.currentTarget);
        refreshIcon = angular.element(clickedElement.find('span')[0]);
        refreshIcon.addClass('icon-refresh-animate');
        MachineIP.get(
            {id: $routeParams.id, machineName: machineName},
            function(info){
                refreshIcon.removeClass('icon-refresh-animate');
                angular.forEach($scope.instance.status, function(value, key){
                    if(value.name == machineName){
                        $scope.instance.status[key].ip = info.ip;
                    }
                });
            }
        );
    };

    $scope.control = function(state, machineName) {
        if(machineName === undefined){
            machineName = '';
        }
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

    $scope.unsetActive = function(elementId) {
        $('#' + elementId).removeClass('active');
    }

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

    $scope.scriptMachineSelected = function(key) {
        $('#btnRunScript_' + key).addClass('btn-warning');
    }

    $scope.runScript = function(machineName, script) {
        $http.post('/api/instances/' + $scope.instance.id, {
            state : 'runScript',
            machine: machineName,
            script: script,
            async: true
        });
    }

    $scope.console = {};
    pubsubCallback = function(consoleData) {
        $scope.$apply(function () {
            if(consoleData.data !== ''){
                $scope.console = consoleData.data;
                $('#console').html($scope.console);
                JobDetails.get({instanceId: $scope.instance.id}, function(details){
                    $scope.job.author = details.user;
                    $scope.job.time_started = details.time_started;
                });

                autoScroll = $('[name="auto-scroll"].active').val();
                if(autoScroll === '1'){
                    autoScrollSep = $('#auto-scroll-separator').get(0);
                    if(autoScrollSep !== undefined){
                        autoScrollSep.scrollIntoView();
                    }
                }
            }
        });
    };
}
