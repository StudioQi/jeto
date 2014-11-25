function DomainsController($scope, $routeParams, Domains, $http, createDialog, Htpassword) {
    $scope.update = function() {
        Domains.query({}, function(infos) {
            $scope.domains = infos;
            $scope.domains.sort(function(a, b){ return a.domain > b.domain; });
            $scope.resource = infos;
            $scope.resetInfosUpstream();
        });

        Htpassword.get({}, function(infos){
            $scope.htpasswdLst = infos.lists.map(function(current){ return current.slug; });
        });
    };
    $scope.upstream_states = [
        'up', 'down', 'backup'
    ];
    $scope.update();
    $scope.ssl_keys = [
        { name:'Development', value:'dev'},
        { name:'QA', value:'qa'},
        { name:'Validation', value:'val'},
    ];

    $scope.resetInfosUpstream = function(){
        $scope.upstreamInfo = {
            'ip': '',
            'port': '',
            'port_ssl': '',
            'state': 'up',
        };
    }
    $scope.resetInfos = function(){
        $scope.domainInfo = {
            'id': '',
            'uri': '',
            'htpasswd': '',
            'ssl_key': '',
            'upstreams': [],
        };
        $scope.resetInfosUpstream();
        setTimeout($scope.update, 200);
    };

    $scope.addUpstream = function() {
        upstream = angular.copy($scope.upstreamInfo)
        if(upstream.port == ''){
            upstream.port = 80;
        }

        $scope.domainInfo.upstreams.push(upstream);
        $scope.resetInfosUpstream();
    }
    $scope.deleteUpstream = function(upstream) {
        $scope.domainInfo.upstreams = $scope.domainInfo.upstreams.filter(function(value){
            if(value.ip == upstream.ip && value.port == upstream.port && value.port_ssl == upstream.port_ssl){
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
                   domain.ssl_key = $scope.domainInfo.ssl_key;

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
                   domain.ssl_key = $scope.domainInfo.ssl_key;

                   domain.$save();

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
