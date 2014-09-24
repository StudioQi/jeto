angular.module('angularFlaskServices', ['ngResource'])
    .value('version', '0.1.3')
    .factory('Instances', function($resource) {
        return $resource('/api/instances/:id', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '' },
                isArray: true
            }
        });
    })
    .factory('MachineIP', function($resource) {
        return $resource('/api/instances/:id/:machineName/ip', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '', machineName: '' },
                isArray: false
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
        return $resource('/api/projects/:id', {id:'@id'});
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
    .factory('Users', function($resource) {
        return $resource('/api/users/:id', {id:'@id'}, {
            query: {
                method: 'GET',
                params: { id: '' },
                isArray: true
            }
        });
    })
;
