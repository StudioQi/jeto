function AuditlogListController($scope, AuditLog) {
    $scope.currentPage = 1;
    $scope.getResults = function() {
        AuditLog.query({page: $scope.currentPage}, function (data, headers) {
            $scope.auditlogs = data;
            console.log($scope.auditlogs);
            $scope.hasObjectId = false;
            $scope.hasObjectType = false;
            $scope.hasObjectName = false;
            $scope.hasUserName = false;

            angular.forEach($scope.auditlogs, function(value, key){
                if(value.objectId !== undefined)
                    $scope.hasObjectId = true;

                if(value.objectType !== undefined)
                    $scope.hasObjectType = true;

                if(value.objectName !== undefined)
                    $scope.hasObjectName = true;

                if(value.user_name !== undefined)
                    $scope.hasUserName = true;
            });

            console.log($scope.hasObjectType);
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
