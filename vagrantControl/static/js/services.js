angular.module('angularFlaskServices', ['ngResource'])
    .factory('Instances', function($resource) {
        return $resource('/api/instances/:id', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '' },
                isArray: true
            }
        });
    })
;
