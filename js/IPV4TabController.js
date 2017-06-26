
var monoApp = angular.module("monoApp");

monoApp.controller("IPV4TabController",['$rootScope', '$scope', '$http',
'$timeout',  'Iface', 'Session', 'Model', 'Packet', 'Conversation', 'Constants', 'TabController',
function($rootScope, $scope, $http, $timeout, Iface, Session, Model,
           Packet, Conversation, Constants, TabController) {

angular.extend(this, TabController);
var self = this;
//redefine callback functions
//d : data sent to the server by the datatable
this.dataCallback = function(d){
  return self.dataCallbackConv(d);
};
this.getColumns = function(){
  return self.getColumnsIPV4();
};
//when a the checkbox of a line is selected
this.addSelectCallback(self.getSelectCallbackConversation("id_conversation_ipv4"));
this.addDoubleClickCallback(self.getDoubleClickCallbackConv("id_conversation_ipv4"));
this.init("CONV_IPV4");


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

}]);
