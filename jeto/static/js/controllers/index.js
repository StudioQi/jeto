/* Controllers */

function IndexController($scope, PrivateSocket) {
  PrivateSocket.emit('test', {'data1': '44444'}, function(data){
      console.log(data);
  });
  PrivateSocket.forward('test', $scope);
  $scope.$on('private:test', function(event, data){
      console.log('Inside private socket forward');
      console.log(data);
  });
}
