angular.module('AngularFlask', ['angularFlaskServices', 'angularFlaskFilters', 'fundoo.services'])
    .config(['$routeProvider', '$locationProvider',
        function($routeProvider, $locationProvider) {
            $routeProvider
                .when('/', {
                    templateUrl: 'static/partials/landing.html',
                    controller: IndexController
                })
                .when('/instances', {
                    templateUrl: 'static/partials/instances.html',
                    controller: InstancesController
                })
                .when('/instances/:id', {
                    templateUrl: '/static/partials/instance.html',
                    controller: InstanceController
                })
                .otherwise({
                    redirectTo: '/'
                })
            ;
            $locationProvider.html5Mode(true);
        }
    ])
;
