
(function(){

  angular.module("monoApp").service('Packet', ['$http', '$timeout', 'Model',
  function($http, $timeout, Model) {

    //test if the session is active at server side and update local $scope.active var
    //Call when you want to select a single packet
    this.SelectPacket = function (id_packet, check, cb){
      $http.post('/awebservice', {method:"select_packet",params:{
        "id_packet": id_packet,
        "check": check,
      },})
      .then(function(response) {
        console.log("received response " + JSON.stringify(response));
        var checked = response.data.checked;
        if (cb instanceof Function) cb.call(response, checked);

      }, function(error) {console.log(error);});
    };

    //TODO move to Packet
    //asks the server if all packets of the given session are selected
    this.areAllPacketsCheckedInSession = function(id_session, cb){
      $http.post('/awebservice', {method:"are_all_packets_checked_in_session",params:{
        "id_session": id_session,
      },})
      .then(function(response) {
        console.log("received response " + JSON.stringify(response));
        var checked = response.data.checked;
        if (cb instanceof Function) cb.call(response, checked);

      }, function(error) {console.log(error);});
    }

    //TODO move to Packet
    //Ask the server to the set the "selected" attribute of all packets in the
    //given session to the value of the parameter "check"
    this.selectAllPacketsInSession = function(id_session, check, cb){
      $http.post('/awebservice', {method:"select_all_packets_in_session",params:{
        "id_session": id_session, "check": check,
      },})
      .then(function(response) {
        console.log("received response " + JSON.stringify(response));
        var checked = response.data.checked;
        if (cb instanceof Function) cb.call(response, checked);
      }, function(error) {console.log(error);});
    };

    this.getPacketdetails = function(id_packet,  cb){
      $http.post('/awebservice', {method:"get_packet_details",params:{
        "id_packet": id_packet,
      },})
      .then(function(response) {
        console.log("received response " + JSON.stringify(response));
        var packet_details = response.data.packet_details;
        if (cb instanceof Function) cb.call(response, packet_details);
      }, function(error) {console.log(error);});
    };

  }]);
})();
