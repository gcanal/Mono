
var monoApp = angular.module("monoApp");

monoApp.controller("SublistTabController",['$rootScope', '$scope', '$http',
'$timeout',  'Iface', 'Session', 'Model', 'Packet', 'Conversation', 'Constants', 'TabController',
function($rootScope, $scope, $http, $timeout, Iface, Session, Model,
           Packet, Conversation, Constants, TabController) {

angular.extend(this, TabController);
var self = this;
//d : data sent to the server by the datatable
this.dataCallback = function(d){
  return self.dataCallbackSublist(d);
};
this.getColumns = function(){
  return self.getColumnsPackets();
};
//when a the checkbox of a line is selected
this.addSelectCallback(self.getSelectCallbackPackets());
//when a row is double clicked
this.addDoubleClickCallback(self.getDoubleClickCallbackPackets());

this.init("SUBLIST");

//Listen to the global model
$scope.$on('Model::tabUpdate', function(event, newTab) {
  //console.log("PacketTabController received tabUpdate : " + newTab);
  self.setTab(newTab);
});
$scope.$on('Model::activeUpdate', function(event, active) {
  if (active){
    self.updateDatatable();
  }
});

$scope.$on('Model::currentSessionUpdate', function(event, curr) {
  //reset tab names
  // self.conv_type = -1;
  // self.id_conv   = -1;
  // self.sublistName = Constants.STRING.SUBLIST_MITM;
});


}]);
