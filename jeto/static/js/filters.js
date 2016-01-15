'use strict';

/* Filters */

angular.module('jetoFilters', [])
	.filter('uppercase', function() {
		return function(input) {
			if(input){
				return input.toUpperCase();
			}
			return null;
		}
	})
	.filter('console', function() {
		return function(test) {
			console.log(test);
		}
	})
;
