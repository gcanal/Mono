
var monoApp = angular.module("monoApp");

monoApp.controller("PacketsMITMTabController",['$rootScope', '$scope', '$http',
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
      var columns = [
        //data is the current box of the row
        //type \in { "string", "numeric", "data", "html"}
        //row is a reference to the entire row
        {"data": "selected", "name": "Sel.", "searchable":false,
        "orderable":false, "width":"1%",
        "render": function(data, type, row){
          return '<input type= "checkbox" '+ (data? "checked": "") + '>';
        },
        "table_name":"coucou",
      },
      {"data": "id_packet", "name": "ID packet"},
      {"data": "ip_src", "name": "IP src"},
      {"data": "ip_dst", "name": "IP dst"},
      {"data": "port_src", "name": "Port Src"},
      {"data": "port_dst", "name": "Port Dst"},
      {"data": "l4_proto", "name": "L4 proto"},
      {"data": "packet_length", "name": "Packet length"},
      {"data": "l5_proto", "name": "L5 proto"},
      //constructor : hidden column
      {"data": "domain", "name":"Domain"},
      {"data": "constructor", "name":"Constructor", "visible": false, "orderable": false},
    ];
    return columns;
  };
  //when a the checkbox of a line is selected
  this.addSelectCallback(self.getSelectCallbackPackets());
  //when a row is double clicked
  this.addDoubleClickCallback(self.getDoubleClickCallbackPackets());

  this.init("MITM_PACKETS");

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
