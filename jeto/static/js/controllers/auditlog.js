function AuditlogListController($scope, Auditlog) {
    $scope.get_logs = function() {
        Auditlog.query({}, function(datas) {
            console.log(datas);
            $scope.auditlog = datas;
        });
    };
    $scope.get_logs();
}
