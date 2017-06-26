(function(){

  angular.module("monoApp").service('Toast', ['$http', '$timeout', 'Model',
  function($http, $timeout, Model) {

    this.toast = function(message){
      $('#toast').text(message).fadeIn(400).delay(3000).fadeOut(400);
    };

  }]);
})();
