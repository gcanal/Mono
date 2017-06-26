
var monoApp = angular.module("monoApp");

monoApp.controller("PacketsTabController",['$rootScope', '$scope', '$http',
'$timeout',  'Iface', 'Session', 'Model', 'Packet', 'Conversation', 'Constants', 'TabController',
function($rootScope, $scope, $http, $timeout, Iface, Session, Model,
  Packet, Conversation, Constants, TabController) {

    angular.extend(this, TabController);
    var self = this;
    //d : data sent to the server by the datatable
    this.dataCallback = function(d){
      return self.dataCallbackPackets(d);
    };
    this.getColumns = function(){
      return self.getColumnsPackets();
    };
    //when a the checkbox of a line is selected
    this.addSelectCallback(self.getSelectCallbackPackets());
    //when a row is double clicked
    this.addDoubleClickCallback(self.getDoubleClickCallbackPackets());

    this.init("PACKETS");

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
