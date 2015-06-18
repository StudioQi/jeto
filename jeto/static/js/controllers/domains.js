function DomainsController($scope, $routeParams, Domains, $http, createDialog, Htpassword, DomainControllers, SSLKeys) {
    $scope.update = function() {
        Domains.query({}, function(infos) {
            $scope.domains = infos;
            $scope.domains.sort(function(a, b){ return a.domain > b.domain; });
            $scope.resource = infos;
            $scope.resetInfos(false);
        });

        Htpassword.get({}, function(infos){
            $scope.htpasswdLst = infos.lists.map(function(current){ return current.slug; });
        });

        DomainControllers.get({}, function(infos){
            $scope.domain_controllers = infos.domain_controllers;
        });

    };
    $scope.get_keys = function() {
        var dc = $scope.domainInfo.domain_controller;
        dc = dc ? {'domain_controller': $scope.domainInfo.domain_controller} : {};
        SSLKeys.get(
            dc,
            function(infos) {
                $scope.ssl_keys = infos.keys;
                $scope.ssl_keys.sort(function(a, b){ return a.name > b.name; });
                $scope.resource = infos;
                $('.loading').hide();
            });
    };

    $scope.upstream_states = [
        'up', 'down', 'backup'
    ];
    $scope.update();
    
    $scope.$watch('domainInfo.domain_controller', $scope.get_keys, true);

    $scope.resetInfosUpstream = function(){
        $scope.upstreamInfo = {
            'ip': '',
            'port': '',
            'port_ssl': '',
            'state': 'up',
        };
    }
    $scope.resetInfosAlias = function(){
        $scope.aliasInfo = {uri: ''};
    }
    $scope.resetInfos = function(refresh){
        if(refresh == undefined){
            refresh = true;
        }
        $scope.domainInfo = {
            'id': '',
            'uri': '',
            'htpasswd': '',
            'ssl_key': '',
            'upstreams': [],
            'aliases': [],
            'domain_controller': '',
        };
        $scope.resetInfosUpstream();
        $scope.resetInfosAlias();
        if(refresh){
            setTimeout($scope.update, 200);
        }
    };

    $scope.addUpstream = function() {
        upstream = angular.copy($scope.upstreamInfo)
        if(upstream.port == ''){
            upstream.port = 80;
        }

        $scope.domainInfo.upstreams.push(upstream);
        $scope.resetInfosUpstream();
    }

    $scope.addAlias = function() {
        alias = angular.copy($scope.aliasInfo);
        $scope.domainInfo.aliases.push(alias);
        $scope.resetInfosAlias();
    }
    $scope.deleteUpstream = function(upstream) {
        $scope.domainInfo.upstreams = $scope.domainInfo.upstreams.filter(function(value){
            if(value.ip == upstream.ip && value.port == upstream.port && value.port_ssl == upstream.port_ssl){
                return false;
            }
            return true;
        });
    }
    $scope.deleteAlias = function(alias) {
        $scope.domainInfo.aliases = $scope.domainInfo.aliases.filter(function(value){
            if(value.toString() == alias.toString()){
                return false;
            }
            return true;
        });
    }

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
                   domain.uri = $scope.domainInfo.uri;
                   domain.htpasswd = $scope.domainInfo.htpasswd;
                   domain.upstreams = $scope.domainInfo.upstreams;
                   domain.aliases = $scope.domainInfo.aliases;
                   domain.ssl_key = $scope.domainInfo.ssl_key;

                   if($scope.domainInfo.domain_controller !== undefined){
                       angular.forEach($scope.domain_controllers, function(value){
                           if(value.id == $scope.domainInfo.domain_controller){
                               domain.domain_controller = value;
                           }
                       });
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
            'id': domainInfo.id,
            'uri': domainInfo.uri,
            'htpasswd': domainInfo.htpasswd,
            'upstreams': domainInfo.upstreams,
            'aliases': domainInfo.aliases,
            'domain_controller': domainInfo.domain_controller.id,
            'ssl_key': domainInfo.ssl_key,
        };
        createDialog('/partials/domains/form.html',{
           id : 'editDialog',
           title: 'Edit a domain',
           backdrop: true,
           scope: $scope,
           success: {
               label: 'Save',
               fn: function(){
                   var domain = new Domains();
                   domain.id = $scope.domainInfo.id;
                   domain.uri = $scope.domainInfo.uri;
                   domain.htpasswd = $scope.domainInfo.htpasswd;
                   domain.upstreams = $scope.domainInfo.upstreams;
                   domain.aliases = $scope.domainInfo.aliases;
                   domain.ssl_key = $scope.domainInfo.ssl_key;

                   if($scope.domainInfo.domain_controller !== undefined){
                       angular.forEach($scope.domain_controllers, function(value){
                           if(value.id == $scope.domainInfo.domain_controller){
                               domain.domain_controller = value;
                           }
                       });
                   }
                   domain.$update({'id': domain.id});

                   $scope.resetInfos();
               }
           },
           cancel: {
               label: 'Cancel',
           }
        });
    };

    $scope.delete = function(domain) {
        $scope.deleteDomain = domain.slug;
        createDialog({
            id : 'deleteDialog',
            title: 'Delete domain',
            backdrop: true,
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + domain.uri +'</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    $http.delete('/api/domains/' + domain.id)
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
