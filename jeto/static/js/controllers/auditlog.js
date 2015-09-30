function AuditlogListController($scope, AuditLog) {
    $scope.currentPage = 1;
    $scope.getResults = function() {
        AuditLog.query({page: $scope.currentPage}, function (data, headers) {
            $scope.auditlogs = data;
            console.log($scope.auditlogs);

            headers_data = headers();
            $scope.currentPage = headers_data.page;
            $scope.itemsCount = headers_data.count;
            $scope.itemsPerPage = headers_data.per_page;
        });
    }
    $scope.pageChanged = function(newPage){
        $scope.currentPage = newPage;
        $scope.getResults();
    }

    // init
    $scope.getResults();
}
