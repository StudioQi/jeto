function ProjectsListController($scope, $routeParams, Projects, $http, $location, createDialog) {
    $scope.update = function() {
        Projects.get({}, function(infos) {
            $scope.projects = infos.projects;
            $scope.projects.sort(function(a, b){ return a.name > b.name; });
            $scope.resource = infos;
            $('.loading').hide();
        });
    };

    $scope.update();
    $scope.resetInfos = function(){
       setTimeout($scope.update, 100);
       $scope.projectInfo = {
           'name': '',
           'base_path': '',
           'git_address': '',
       };
    };

    $scope.resetInfos();
    $scope.resetTabInfos = function() {
        $scope.projectInfo.base_path = '';
        $scope.projectInfo.git_address = '';
    };

    $scope.create = function() {
        createDialog('/partials/admin/projects/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new project',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   $('.loading').show();
                   var project = new Projects();
                   project.name = $scope.projectInfo.name;
                   project.base_path = $scope.projectInfo.base_path;
                   project.git_address = $scope.projectInfo.git_address;
                   project.state = 'create';
                   project.$save();
                   setTimeout($scope.resetInfos, 100);
               }
           },
           cancel: {
               label: 'Cancel',
           },
        });
    };

    $scope.delete = function(project) {
        $scope.deleteProjectId = project.id;
        createDialog({
            id : 'deleteDialog', 
            title: 'Delete project',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + project.name +'</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    $('.loading').show();
                    id = $scope.deleteProjectId;
                    $http.delete('/api/projects/' + id)
                    .success(function() {
                        setTimeout($scope.update, 100);
                    });
                }
            },
            cancel: {
                label: 'Cancel',
            },
        });
    };
}

function ProjectController($scope, $routeParams, Projects, $http, $location, $log) {
    watchFunction = function(newValue, oldValue) {
        if(newValue !== undefined && newValue !== oldValue){
            $scope.project.$save();
        }
    };
    $scope.update = function() {
        Projects.get({id: $routeParams.id}, function(infos) {
            $scope.project = infos;
            $scope.$watch('project', watchFunction, true);
            $scope.resource = infos;
        });
    };

    $scope.update();
    $scope.resetInfos = function(){
       setTimeout($scope.update, 100);
    };
}
