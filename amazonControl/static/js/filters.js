'use strict';

/* Filters */

angular.module('angularFlaskFilters', [])
	.filter('uppercase', function() {
		return function(input) {
			return input.toUpperCase();
		}
	})
	.filter('console', function() {
		return function(test) {
			console.log(test);
			return test;
		}
	})
	.filter('stateClass', function() {
		return function(state) {
			if(state == 'running') {
				return 'success';
			}
			return 'warning';
		}
	})
;
