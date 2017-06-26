
var monoApp = angular.module("monoApp");

monoApp.controller("ConvsController",['$rootScope', '$scope', '$http',
'$timeout',  'Iface', 'Session', 'Model', 'Packet', 'Conversation', 'Constants',
function($rootScope, $scope, $http, $timeout, Iface, Session, Model, Packet, Conversation, Constants) {
  var self = this;
  this.tab = Constants.CONV_TYPE.PACKETS;
  console.log("presetting tab to " + this.tab)
  this.all_packets_checked = false; // DEPRECATED  We don't need this now
  this.sublist_name = "Sublist";
  this.sublist_mitm_name = "Sublist MITM";
  this.select_all = 0;
  this.packet_search_payload = 0;

  //csts
  this.packets_tab = Constants.CONV_TYPE.PACKETS
  this.ip_tab = Constants.CONV_TYPE.CONV_IPV4
  this.udp_tab = Constants.CONV_TYPE.CONV_UDP
  this.tcp_tab = Constants.CONV_TYPE.CONV_TCP
  this.applis_tab = Constants.CONV_TYPE.APPLIS
  this.sublist_tab = Constants.CONV_TYPE.SUBLIST
  //mitm csts
  this.sublist_mitm_tab = Constants.CONV_TYPE.SUBLIST_MITM
  this.mitm_packets_tab = Constants.CONV_TYPE.MITM_PACKETS
  this.mitm_conv_tab = Constants.CONV_TYPE.CONV_MITM

  this.isSelected = function(i){
    //console.log("call to is Selected");
    return this.tab === i;
  };
  this.setTab = function(i, conv_type, id_conv){
    //before switching tab, unselect all packets
    //if (i != this.tab) Packet.selectAllPacketsInSession($scope.current_session.id_session, false, function(){});
    this.tab = i;
    console.log("ConvsController setting tab to " + Constants.CONV_TYPE.toString(this.tab)+ " (" + this.tab +")");


     if (this.tab == Constants.CONV_TYPE.SUBLIST){
      //console.error("Setting the sublist tab with conv_type="+conv_type+" and id_conv="+id_conv)
      if ((typeof conv_type !== 'undefined') && (typeof id_conv !== 'undefined') ){
        self.sublist_name = "Conversation " + Constants.CONV_TYPE.toString(conv_type) + " " + id_conv;
        console.log(" going to " + self.sublist_name);
      }
    }
    else if (this.tab == Constants.CONV_TYPE.SUBLIST_MITM){
      //console.error("Setting the sublist tab with conv_type="+conv_type+" and id_conv="+id_conv)
      if ((typeof conv_type !== 'undefined') && (typeof id_conv !== 'undefined') ){
        self.sublist_mitm_name = "Decrypt " + Constants.CONV_TYPE.toString(conv_type) + " " + id_conv;
        console.log(" Convs Set Tab ----> going to " + self.sublist_mitm_name);
      }
    }
    Model.setTab(this.tab, conv_type, id_conv);
    //$scope.$apply();
    return;
  };

//Listen to the global model
$scope.$on('Model::currentSessionUpdate', function(event, curr) {
  //reset tab names
  // self.sublist_tab = Constants.STRING.SUBLIST;
  // self.sublist_mitm_tab = Constants.STRING.SUBLIST_MITM;

  self.setTab(Constants.CONV_TYPE.PACKETS);
});

$scope.$on('Model::forceTab', function(event, newTab) {
  // $scope.$eval(function(){
  //   self.setTab(newTab.tab, newTab.conv_type, newTab.id_conv);
  // });
  self.setTab(newTab.tab, newTab.conv_type, newTab.id_conv);
  $scope.$apply();
  console.log("scope apply");
});

$scope.$on('Model::activeUpdate', function(event, active) {
  if (active){
    //self.updateDatatable();
  }
});



}]);
