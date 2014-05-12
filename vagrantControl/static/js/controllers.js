/* Controllers */

function IndexController($scope) {
}

function InstancesController($scope, Instances, $http, createDialog, $log) {
    var instancesQuery = Instances.get({}, function(infos) {
        $scope.instances = infos.instances;
        $scope.stopped = infos.stopped;
        $scope.running = infos.running;
        $scope.resource = infos;
    });

    $scope.states = [
        {label: 'Development', type:'dev'},
        {label: 'Sandbox', type:'sandbox'},
        {label: 'QA', type:'qa'},
        {label: 'Validation', type:'validation'}
    ];

    $scope.updateInfos = function() {
        var instancesQuery = Instances.get({}, function(infos) {
            $scope.instances = infos.instances;
            $scope.stopped = infos.stopped;
            $scope.running = infos.running;
            $scope.resource = infos;
            $('.loading').hide();
        });
    };

    $scope.instanceInfo = {
        'name': '',
        'path': '',
    };

    $scope.create = function() {
        createDialog('/partials/instances/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new machine',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   $('.loading').show();
                   var instance = new Instances();
                   instance.name = $scope.instanceInfo.name;
                   instance.path = $scope.instanceInfo.path;
                   instance.environment = $scope.instanceInfo.environment;
                   instance.state = 'create';
                   instance.$save();
                   setTimeout($scope.updateInfos, 100);
               }
           },
           cancel: {
               label: 'Cancel',
           },
        });
    };


    $scope.control = function(instanceId, state) {
        $http.post('/api/instances/', {
            state : state,
            id : instanceId,
        })
        .success(function(result) {
            instanceInfos = result.instance;
            angular.forEach($scope.instances, function(instance, idx){
                if(instance.id == instanceInfos.id){
                    $scope.instances[idx] = instanceInfos;
                }
            });
        });
    };

    $scope.delete = function(instanceId) {
        $http.delete('/api/instances/' + instanceId)
        .success(function(infos) {
            setTimeout($scope.updateInfos, 100);
        });
    };

}

function InstanceController($scope, $routeParams, Instances, $http, $location) {
    $('.loading').show();
    var instancesQuery = Instances.get({id: $routeParams.id}, function(instance) {
        $scope.instance = instance;
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
        $('.loading').show();
        $http.post('/api/instances/' + $scope.instance.id, {
            state : state,
        })
        .success(function(result) {
           setTimeout($scope.updateInfos, 100);
        });
    };

    $scope.delete = function() {
        $http.delete('/api/instances/' + $scope.instance.id)
        .success(function(infos) {
            $location.path('/instances');
        });
    };

    $scope.console = {};
    pubsubCallback = function(line) {
        $scope.$apply(function () {
            if(line.data !== ''){
                $scope.console += line.data + '<br />';
                $('#console').html($scope.console);
            }
        });
    };
    var source = new EventSource('/pubsub')
    // source.addEventListener('message', pubsubCallback, false);
}

function DomainsController($scope, $routeParams, Domains, $http, $location, createDialog, Htpassword) {
    $scope.update = function() {
        Domains.get({}, function(infos) {
            $scope.domains = infos.domains;
            $scope.resource = infos;
        });

        Htpassword.get({}, function(infos){
            $scope.htpasswdLst = infos.lists.map(function(current){ return current.slug });
        });
    };
    $scope.update();
    $scope.sslkeys = [
        { name:'Development', value:'dev'},
        { name:'QA', value:'qa'},
        { name:'Validation', value:'val'},
    ];

    $scope.resetInfos = function(){
        $scope.domainInfo = {
            'domain': '',
            'ip': '',
            'htpasswd': '',
            'slug': '',
            'sslkey': '',
        };
       setTimeout($scope.update, 100);
    };

    $scope.create = function() {
        createDialog('/partials/domains/form.html',{ 
           id : 'createDialog', 
           title: 'Create a new domain',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Create',
               fn: function(){
                   var domain = new Domains();
                   domain.domain = $scope.domainInfo.domain;
                   domain.ip = $scope.domainInfo.ip;
                   domain.htpasswd = $scope.domainInfo.htpasswd;
                   if($scope.domainInfo.sslkey != undefined){
                        domain.sslkey = $scope.domainInfo.sslkey.value;
                   }
                   domain.$save();

                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
               fn: $scope.resetInfos(),
           },
           controller: 'DomainsController',
        });
    };

    $scope.edit = function(domainInfo) {
        $scope.domainInfo = {
            'domain': domainInfo.domain,
            'ip': domainInfo.ip,
            'slug': domainInfo.slug,
            'htpasswd': domainInfo.htpasswd,
        };
        angular.forEach($scope.sslkeys, function(sslkey) {
            if(sslkey != undefined && sslkey.value == domainInfo.sslkey){
                $scope.domainInfo.sslkey = sslkey;
            }
        });
        createDialog('/partials/domains/form.html',{ 
           id : 'editDialog', 
           title: 'Edit a domain',
           backdrop: true, 
           scope: $scope,
           success: {
               label: 'Edit',
               fn: function(){
                   var domain = new Domains();
                   domain.domain = $scope.domainInfo.domain;
                   domain.ip = $scope.domainInfo.ip;
                   domain.slug = $scope.domainInfo.slug;
                   domain.htpasswd = $scope.domainInfo.htpasswd;
                   if($scope.domainInfo.sslkey != undefined){
                     domain.sslkey = $scope.domainInfo.sslkey.value;
                   }
                   domain.$save();

                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    };

    $scope.delete = function(slug) {
        $http.delete('/api/domains/' + slug)
        .success(function() {
            $scope.update();
        });
    };
}

function HtpasswordController($scope, $routeParams, Htpassword, $http, $location, createDialog) {
    $scope.update = function() {
        Htpassword.get({}, function(infos) {
            $scope.lists = infos.lists;
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
       var list = new Htpassword();
       list.name = slug;
       list.slug = slug;
       list.$delete();
       $scope.update();
    };
}

function HtpasswordListController($scope, $routeParams, Htpassword, $http, $location, createDialog) {
    $scope.update = function() {
        Htpassword.get({slug: $routeParams.slug}, function(infos) {
            $scope.item = infos.item;
            $scope.changed = false;
            $scope.resource = infos;
        });
    };
    $scope.update();

    $scope.resetInfos = function(){
        $scope.newItem = {
            'username': '',
            'password': '',
            'state': 'CREATE',
        };
       setTimeout($scope.update, 100);
    };

    $scope.add = function(){
        $scope.item.users.push({'username':$scope.newItem.username, 'password': $scope.newItem.password, 'state': 'CREATE'});
        $scope.changed = true;
    };

    $scope.deleteUser = function(username){
        angular.forEach($scope.item.users, function(value, key){
            if(value.username == username){
                if(value.state == 'CREATE'){
                    $scope.item.users.splice(key, 1);
                } else {
                    $scope.item.users[key].state = 'DELETE';
                    $scope.changed = true; }
            }
        });
    };

    $scope.cancelDeleteUser = function(username){
        angular.forEach($scope.item.users, function(value, key){
            if(value.username == username){
                $scope.item.users[key].state = 'DEFAULT';
            }
        });
    };

    $scope.save = function(){
        $http.put('/api/htpassword/' + $scope.item.slug, {
            users: $scope.item.users,
        })
        .success(function(infos){
            $scope.resetInfos();
            $location.path('/htpassword');
        });
    };

    $scope.cancel = function(){
        $scope.resetInfos()
        $location.path('/htpassword');
    };

    $scope.delete = function(){
        var list = new Htpassword();
        list.name = $scope.item.slug;
        list.slug = $scope.item.slug;
        list.$delete();
        $location.path('/htpassword');
    };
}
