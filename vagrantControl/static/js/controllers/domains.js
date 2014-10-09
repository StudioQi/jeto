function DomainsController($scope, $routeParams, Domains, $http, createDialog, Htpassword) {
    $scope.update = function() {
        Domains.get({}, function(infos) {
            $scope.domains = infos.domains;
            $scope.domains.sort(function(a, b){ return a.domain > b.domain; });
            $scope.resource = infos;
        });

        Htpassword.get({}, function(infos){
            $scope.htpasswdLst = infos.lists.map(function(current){ return current.slug; });
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
       setTimeout($scope.update, 200);
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
                   if($scope.domainInfo.sslkey !== undefined){
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
            if(sslkey !== undefined && sslkey.value == domainInfo.sslkey){
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
                   if($scope.domainInfo.sslkey !== undefined){
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

    $scope.delete = function(domain) {
        $scope.deleteDomain = domain.slug;
        createDialog({
            id : 'deleteDialog', 
            title: 'Delete domain',
            backdrop: true, 
            scope: $scope,
            btntype: 'danger',
            template: 'Are you sure you want to delete <b>' + domain.slug +'</b> ?',
            success: {
                label: 'Delete',
                fn: function(){
                    slug = $scope.deleteDomain;
                    $http.delete('/api/domains/' + slug)
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
