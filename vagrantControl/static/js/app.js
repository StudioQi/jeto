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
                .otherwise({
                    redirectTo: '/'
                });
            $interpolateProvider.startSymbol('[['); 
            $interpolateProvider.endSymbol(']]');
        }
    ])
;
