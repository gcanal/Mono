
var monoApp = angular.module("monoApp");

monoApp.controller("SublistMITMTabController",['$rootScope', '$scope', '$http',
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
      var columns = [
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
      {"data": "constructor", "name":"Constructor", "visible": false, "orderable": false},
    ];
    return columns;
  };

  this.addSelectCallback(self.getSelectCallbackPackets());
  this.addDoubleClickCallback(self.getDoubleClickCallbackPackets());

  this.init("SUBLIST_MITM");

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
