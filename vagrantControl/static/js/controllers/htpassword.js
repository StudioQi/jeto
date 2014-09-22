function HtpasswordController($scope, $routeParams, Htpassword, $http, $location, createDialog) {
    $scope.update = function() {
        Htpassword.get({}, function(infos) {
            $scope.lists = infos.lists;
            $scope.lists.sort(function(a, b){ return a.slug > b.slug; });
            $scope.resource = infos;
        });
    };
    $scope.update();


    $scope.resetInfos = function(){
        $scope.list = {
            'slug': '',
            'name': '',
        };
       setTimeout($scope.update, 100);
    };

    $scope.create = function() {
        createDialog('/partials/htpassword/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new list',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   var list = new Htpassword();
                   list.name = $scope.list.name;
                   list.$save();
                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
               fn: $scope.resetInfos(),
           }
        });
    };

    $scope.edit = function(list) {
        $scope.list = {
            'name': list.slug,
        };
        createDialog('/partials/htpassword/form.html',{ 
           id : 'editDialog', 
           title: 'Edit a list',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Edit',
               fn: function(){
                   var list = new Htpassword();
                   list.name = $scope.list.name;
                   list.$save();
                   $scope.update();
                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    };

    $scope.delete = function(slug) {
        $scope.deleteSlug = slug;
        createDialog('', {
            id : 'deleteDialog', 
            title: 'Delete user list',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + slug + '</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    var list = new Htpassword();
                    slug = $scope.deleteSlug;
                    list.name = slug;
                    list.slug = slug;
                    list.$delete();
                    setTimeout($scope.update, 100);
                    $scope.deleteSlug = undefined;
                }
            },
            cancel: {
                label: 'Cancel',
            },
        });
    };
}
