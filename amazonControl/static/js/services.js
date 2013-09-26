'use strict';

angular.module('angularFlaskServices', ['ngResource'])
    .factory('Instances', function($resource) {
        return $resource('/api/instances/:instanceId', {instanceId:'@id'}, {
            query: {
                method: 'GET',
                params: { instanceId: '' },
                isArray: true
            }
        });
    })
;
