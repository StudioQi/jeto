angular.module('AngularFlask', ['angularFlaskServices', 'angularFlaskFilters', 'fundoo.services'])
    .config(['$routeProvider', '$locationProvider', '$interpolateProvider',
        function($routeProvider, $locationProvider, $interpolateProvider) {
            $locationProvider.html5Mode(true);
            $routeProvider
                .when('/', {
                    templateUrl: '/partials/landing.html',
                    controller: IndexController
                })
                .when('/instances', {
                    templateUrl: '/partials/instances/list.html',
                    controller: InstancesController
                })
                .when('/instances/:id', {
                    templateUrl: '/partials/instances/instance.html',
                    controller: InstanceController
                })
                .when('/domains', {
                    templateUrl: '/partials/domains/list.html',
                    controller: DomainsController
                })
                .when('/htpassword', {
                    templateUrl: '/partials/htpassword/list.html',
                    controller: HtpasswordController
                })
                .when('/htpassword/:slug', {
                    templateUrl: '/partials/htpassword/view.html',
                    controller: HtpasswordListController
                })
                .when('/admin', {
                    templateUrl: '/partials/admin/index.html',
                    controller: IndexController
                })
                .when('/admin/projects', {
                    templateUrl: '/partials/admin/projects/list.html',
                    controller: ProjectsListController
                })
                .when('/admin/projects/:id', {
                    templateUrl: '/partials/admin/projects/item.html',
                    controller: ProjectController
                })
                .when('/admin/teams', {
                    templateUrl: '/partials/admin/teams/list.html',
                    controller: IndexController
                })
                .when('/admin/hosts', {
                    templateUrl: '/partials/admin/hosts/list.html',
                    controller: HostsListController
                })
                .when('/admin/hosts/:id', {
                    templateUrl: '/partials/admin/hosts/item.html',
                    controller: HostController
                })
                .when('/admin/users', {
                    templateUrl: '/partials/admin/users/list.html',
                    controller: IndexController
                })
                .otherwise({
                    redirectTo: '/'
                });
            $interpolateProvider.startSymbol('[['); 
            $interpolateProvider.endSymbol(']]');
        }
    ])
;
