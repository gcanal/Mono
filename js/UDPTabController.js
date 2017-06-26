var monoApp = angular.module("monoApp");

monoApp.controller("UDPTabController",['$rootScope', '$scope', '$http',
'$timeout',  'Iface', 'Session', 'Model', 'Packet', 'Conversation', 'Constants', 'TabController',
function($rootScope, $scope, $http, $timeout, Iface, Session, Model,
  Packet, Conversation, Constants, TabController) {

    angular.extend(this, TabController);
    var self = this;
    this.dataCallback = function(d){
      return self.dataCallbackConv(d);
    };

    this.getColumns = function(){
      var columns = [
        {"data": "selected", "name": "Sel.", "searchable":false,
        "orderable":false, "width":"1%",
        "render": function(data, type, row){
          return '<input type= "checkbox" '+ (data? "checked": "") + '>';
        }
      },
      {"data": "id_conversation_udp", "name": "ID conv", "width":"3%"},
      {"data": "ip_a", "name": "IP A"},
      {"data": "port_a", "name": "Port A"},
      {"data": "ip_b", "name": "IP B"},
      {"data": "port_b", "name": "Port B"},
      {"data": "bytes", "name": "Bytes"},
      {"data": "packets", "name": "Packets"},
      {"data": "rel_start", "name": "Rel Start", "width":"7%"},
      {"data": "duration", "name": "Duration", "width":"7%"},
      {"data": "packets_a_b", "name": "Packets A-B"},
      {"data": "packets_b_a", "name": "Packets B-A"},
      {"data": "bytes_a_b", "name": "Bytes A-B"},
      {"data": "bytes_b_a", "name": "Bytes B-A"},
    ];
    return columns;
  };
  //when a the checkbox of a line is selected
  this.addSelectCallback(self.getSelectCallbackConversation("id_conversation_udp"));
  this.addDoubleClickCallback(self.getDoubleClickCallbackConv("id_conversation_udp"));
  this.init("CONV_UDP");

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
