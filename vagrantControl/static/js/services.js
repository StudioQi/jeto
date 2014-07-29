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
    .factory('Domains', function($resource) {
        return $resource('/api/domains/:slug', {slug:'@slug'}, {
            query: {
                method: 'GET',
                params: { slug: '' },
                isArray: true
            }
        });
    })
    .factory('Htpassword', function($resource) {
        return $resource('/api/htpassword/:slug', {slug:'@slug'}, {
            query: {
                method: 'GET',
                params: { slug: '' },
                isArray: true
            }
        });
    })
    .factory('Projects', function($resource) {
        return $resource('/api/projects/:id', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '' },
                isArray: true
            }
        });
    })
    .factory('Hosts', function($resource) {
        return $resource('/api/hosts/:id', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '' },
                isArray: true
            }
        });
    })
    .factory('Teams', function($resource) {
        return $resource('/api/teams/:id', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '' },
                isArray: true
            }
        });
    })
;
