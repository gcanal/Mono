
(function(){

  angular.module("monoApp").service('Conversation', ['$http', '$timeout', 'Model',
  function($http, $timeout, Model) {



    //test if the session is active at server side and update local $scope.active var
    //Call when you want to select a single packet
    this.SelectConversation = function (id_conversation, conversation_type, check,  cb){
      $http.post('/awebservice', {method:"select_conversation",params:{
        "id_conversation": id_conversation,
        "conversation_type": conversation_type,
        "check": check,
      },})
      .then(function(response) {
        console.log("received response " + JSON.stringify(response));
        var checked = response.data.checked;
        if (cb instanceof Function) cb.call(response, checked);

      }, function(error) {console.log(error);});
    };

  }]);
})();
