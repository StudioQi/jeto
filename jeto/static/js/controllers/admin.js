/* Controllers */

function AdminController($scope, SSLKeys, Users, Teams, Projects, Hosts, DomainControllers) {
    $scope.update = function() {
        SSLKeys.get({}, function(infos) {
            $scope.ssl_keys = infos.ssl_keys;
        });
        Users.get({}, function(infos) {
            $scope.users = infos.users;
        });
        Teams.get({}, function(infos) {
            $scope.teams = infos.teams;
        });
        Projects.get({}, function(infos) {
            $scope.projects = infos.projects;
        });
        Hosts.get({}, function(infos) {
            $scope.hosts = infos.hosts;
        });
        DomainControllers.get({}, function(infos) {
            $scope.domain_controllers = infos.domain_controllers;
        });
    };
    $scope.update();
}
