

(function(){

  angular.module("monoApp").service('Constants', ['$http', '$timeout',
  function($http, $timeout) {
    var self = this;
    this.CONV_TYPE = {}
    this.CONV_TYPE.UNDEFINED         = -2;
    this.CONV_TYPE.PACKETS           = -1;
    this.CONV_TYPE.CONV_IPV4         = 0 ;
    this.CONV_TYPE.CONV_UDP          = 1 ;
    this.CONV_TYPE.CONV_TCP          = 2 ;
    this.CONV_TYPE.APPLIS            = 3 ;
    this.CONV_TYPE.SUBLIST           = 4 ;
    this.CONV_TYPE.SUBLIST_MITM      = 5 ;
    this.CONV_TYPE.MITM_PACKETS      = 6 ;
    this.CONV_TYPE.CONV_MITM         = 7 ;

    this.TABLE_ID = {}
    this.TABLE_ID.UNDEFINED          = "";
    this.TABLE_ID.PACKETS            = "#packets_table";
    this.TABLE_ID.CONV_IPV4          = "#conversations_ipv4_table" ;
    this.TABLE_ID.CONV_UDP           = "#conversations_udp_table" ;
    this.TABLE_ID.CONV_TCP           = "#conversations_tcp_table" ;
    this.TABLE_ID.APPLIS             = "#conversations_applis_table" ;
    this.TABLE_ID.SUBLIST            = "#sublist_table";
    this.TABLE_ID.SUBLIST_MITM       = "#sublist_mitm_table";
    this.TABLE_ID.MITM_PACKETS       = "#packets_mitm_table";
    this.TABLE_ID.CONV_MITM          = "#conversations_mitm_table" ;

    this.FILTER_ID = {}
    this.FILTER_ID.UNDEFINED         = "";
    this.FILTER_ID.PACKETS           = "#packets_table_filter";
    this.FILTER_ID.CONV_IPV4         = "#conversations_ipv4_table_filter" ;
    this.FILTER_ID.CONV_UDP          = "#conversations_udp_table_filter" ;
    this.FILTER_ID.CONV_TCP          = "#conversations_tcp_table_filter" ;
    this.FILTER_ID.APPLIS            = "#conversations_applis_table" ;
    this.FILTER_ID.SUBLIST           = "#sublist_table_filter";
    this.FILTER_ID.SUBLIST_MITM      = "#sublist_mitm_table_filter";
    this.FILTER_ID.MITM_PACKETS      = "#packets_mitm_table_filter";
    this.FILTER_ID.CONV_MITM         = "#conversations_mitm_table_filter" ;

    //METHOD is the string sent to the server to get the content of each datatable
    this.METHOD = {}
    this.METHOD.UNDEFINED            = "";
    this.METHOD.PACKETS              = "datatatables_packets";
    this.METHOD.CONV_IPV4            = "datatatables_ipv4_conversation" ;
    this.METHOD.CONV_UDP             = "datatatables_udp_conversation" ;
    this.METHOD.CONV_TCP             = "datatatables_tcp_conversation" ;
    this.METHOD.APPLIS               = "datatatables_applis_conversation" ;
    this.METHOD.SUBLIST              = "datatatables_sublist";
    this.METHOD.SUBLIST_MITM         = "datatatables_sublist_mitm";
    this.METHOD.MITM_PACKETS         = "datatatables_mitm_packets";
    this.METHOD.CONV_MITM            = "datatatables_mitm_conversation" ;

    this.STRING = {}
    this.STRING.UNDEFINED            = "Undefined";
    this.STRING.PACKETS              = "Packets";
    this.STRING.CONV_IPV4            = "Ipv4" ;
    this.STRING.CONV_UDP             = "UDP" ;
    this.STRING.CONV_TCP             = "TCP" ;
    this.STRING.APPLIS               = "Applis" ;
    this.STRING.SUBLIST              = "Sublist";
    this.STRING.SUBLIST_MITM         = "Sublist MITM";
    this.STRING.MITM_PACKETS         = "MITM Packets";
    this.STRING.CONV_MITM            = "MITM Conversations" ;

    this.getConstants = function(key){
      //if the given parameter is an integer, we convert it to key
      if (key === parseInt(key, 10)){
        key = this.convTypeToKey(key);
      }
      var c = {"convType":this.CONV_TYPE[key], "tableId":this.TABLE_ID[key],
      "filterId":this.FILTER_ID[key], "method":this.METHOD[key], "string":this.STRING[key]};
      return c;
    };

    this.convTypeToKey = function(value){
      for( var prop in this.CONV_TYPE ) {
        if( this.CONV_TYPE.hasOwnProperty( prop ) ) {
          if( this.CONV_TYPE[ prop ] === value )
          return prop;
        }
      }
    };

    this.TAB_TYPE = {};
    this.TAB_TYPE.PACKET             = 1;
    this.TAB_TYPE.CONV               = 2;

    this.CONV_TYPE.toString = function(conv_type){
      var key = self.convTypeToKey(conv_type);
      var conv_string = self.STRING[ key ];
      return conv_string;
    }
  }]);
})();
