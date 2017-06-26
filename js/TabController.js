(function(){
  //Warning TabController is not a Controller
  //It is a generic structure  for all controller that manage a datatable tab.
var app = angular.module('monoApp');
  //Abstract Tab Controller as Service
  app.service("TabController", [ '$timeout',  'Model', 'Constants', 'Session',
   'Packet', 'Conversation',
  function( $timeout, Model, Constants, Session, Packet, Conversation) {

    var AbstractTabController =  {
      tab: Constants.CONV_TYPE.PACKETS, //current tab select (might be different from the controller type)
      myConvType:  Constants.CONV_TYPE.PACKETS, // the controller type (constant)
      packet_search_payload: false, // specific to tabs of type 'packet'
      dataTable: {}, //jquery object create by the datatable constructor
      dataTableId: Constants.TABLE_ID.PACKETS,
      select_all: false,
      conv_type: Constants.CONV_TYPE.CONV_IPV4, //used for sublist and sublist_mitm tabs
      id_conv: -1, //used for sublist and sublist_mitm tabs
      constants:{},
      init: function(cst_key){
        this.constants = Constants.getConstants(cst_key);
        this.myConvType = this.constants.convType;
        this.dataTableId = this.constants.tableId;
      },
      setTabType: function(newType){
        this.tabType = newType;
      },
      getSearchString: function(){
        //TODO make it small
        if (this.tab == Constants.CONV_TYPE.PACKETS){
          return $(Constants.FILTER_ID.PACKETS +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.CONV_IPV4){ // #conversations_ipv4_table_filter
          return $(Constants.FILTER_ID.CONV_IPV4 +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.CONV_UDP){
          return $(Constants.FILTER_ID.CONV_UDP +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.CONV_TCP){
          return $(Constants.FILTER_ID.CONV_TCP +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.APPLIS){
          return $(Constants.FILTER_ID.APPLIS +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.SUBLIST){
          return $(Constants.FILTER_ID.SUBLIST +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.SUBLIST_MITM){
          return $(Constants.FILTER_ID.SUBLIST_MITM +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.MITM_PACKETS){
          return $(Constants.FILTER_ID.MITM_PACKETS +' input').val(); //.dataTables_filter input'
        }
        else if (this.tab == Constants.CONV_TYPE.CONV_MITM){
          return $(Constants.FILTER_ID.CONV_MITM +' input').val(); //.dataTables_filter input'
        }
      },
      setTab: function(newTab){
        this.tab = newTab.tab;
        //console.log(this.myConvType);
        if (this.tab ==  this.myConvType) {
          console.log("*********** TabController launching tab " + Constants.CONV_TYPE.toString(this.myConvType))
          if ((this.tab == Constants.CONV_TYPE.SUBLIST) || (this.tab == Constants.CONV_TYPE.SUBLIST_MITM)){
            if ((typeof newTab.conv_type !== 'undefined') && (typeof newTab.id_conv !== 'undefined') ){
              this.conv_type = newTab.conv_type; this.id_conv = newTab.id_conv;
              this.sublistName = "Conversation " + Constants.CONV_TYPE.toString(this.conv_type) + " " + this.id_conv;
              console.log("launching conversation " + Constants.CONV_TYPE.toString(this.conv_type) + " " + this.id_conv);
            }
          }
          this.updateDatatable();
        }
        else{/* Chill out */}
      },
      createDatatatable: function(){
        var current_session = Model.getCurrentSession();
        var self = this;
        if ( $.fn.DataTable.isDataTable(this.dataTableId)) {
          console.log("*********** Destroy")
          this.dataTable.destroy();
        }
        if (current_session.id_session == 0 ){
          return;
        }
        this.dataTable = $(self.dataTableId).DataTable({
          "processing": true,
          "serverSide": true,
          "scrollX": false,
          //"scrollY": "400px",
          "ajax": {
            "url": 'awebservice',
            "type": 'POST',
            "contentType":"application/json",
            "data": function(d){return self.dataCallback(d); },
          },
          "columns": self.getColumns(),
        });
      },
      /* Formatting function for packet details */
      formatPacketDetails: function(d){
        var s = this.getSearchString();
        var s2 = s.replace(/\s+/g,'');
        if (this.packet_search_payload && s && s2){
          //highlight search terms
          //d = d.replace(new RegExp(s, 'g'), "<span style='background:yellow' >" + s + "</span>");
          d = d.split(s).join(" <b>" + s + "</b> ");
        }
        d = d.split("\\r\\n").join("<br/>");
        //console.log(d);
        var ret = "";
        for (var c = 0 ; c < d.length ; c++){
          if ( c%160 == 0) {ret += "<br/>";}
          ret += d[c];
        }
        return ret;
      },
      dataCallback: function(d){
        //Override this
        return JSON.stringify( d ); //submit data as json
      },
      getColumns: function(){
        //Override this
        return [{"data": "id_packet", "name": "ID packet"},];
      },

      close_tr: function(tr){ //close table row
        var row = this.dataTable.row( tr );
        console.log("hide row")
        console.log(row);
        var data = row.data();
        console.log(data);
        row.child.hide();
        $(tr).removeClass('shown');
      },
      open_tr: function(tr){ //open table row
        var row = this.dataTable.row( tr );
        console.log("show row");
        console.log(row);
        var data = row.data();
        console.log(data);
        row.child(this.formatPacketDetails(data.constructor)).show();
        $(tr).addClass('shown');
      },
      hideDetails: function(){
        console.log("hide details");
        //find table rows with role 'row'
        var trs = $(this.constants.tableId + " tbody").find("tr[role='row']");
        var self = this;
        trs.each(function(index){self.close_tr(this);});
      },
      showDetails: function(){
        console.log("show details");
        var trs = $(this.constants.tableId + " tbody").find("tr[role='row']");
        var self = this;
        trs.each(function(index){ self.open_tr(this);});
      },
      //add a function to call when we click on the checkbox of a line
      addSelectCallback: function(cb){
        var self = this;
        $timeout(function(){
          $(self.dataTableId + " tbody").on("click", "tr input", function(event){
            cb(this);
            event.stopPropagation();
          });
        }, 200);
      },
      addDoubleClickCallback: function(cb){
        var self = this;
        $timeout(function(){
          $(self.dataTableId + " tbody").on("dblclick", "tr[role='row']", function(event){
            cb(this);
            event.stopPropagation();
          });
        }, 200);
      },
      selectAll: function(){
        this.select_all = true;
        var self = this;
        self.updateDatatable();
        $timeout(function(){self.select_all = false}, 100);
      },
      unselectAll: function(){
        var current_session = Model.getCurrentSession();
        var self = this;
        Session.unselectAll(current_session.id_session, function(){
          self.updateDatatable();
        })
      },
      updateDatatable: function(){
        console.log("updateDatatable (active=" + Model.getActive()
        + " myConvType=" + Constants.CONV_TYPE.toString(this.myConvType)
        + " myConvType_constant=" + this.constants.string
        + " select_all=" + this.select_all
        + " conv_type=" + this.conv_type
        + " conv_type_str=" + Constants.CONV_TYPE.toString(this.conv_type)
        + " id_conv=" + this.id_conv
        + " dataTableId=" + this.dataTableId
        + " this.tab=" + this.tab
        + " this.tab_str=" + Constants.CONV_TYPE.toString(this.tab)
        + ") ");

        //console.log("current tab is " + this.tab);
        var self = this;

        //recursive auxiliary function
        // We create an auxiliary function in order to keep "self" in the closure.
        // because when calling $timeout(aux, 1000) the reference to "this" changes
        var aux = function(){
          //create datatable if not exist
          if ( ! $.fn.DataTable.isDataTable(self.dataTableId)) {
            if (self.tab == self.myConvType){
              console.log("string" + self.constants.string)
              self.createDatatatable();
            }
          }
          //reload datatable
          if (self.tab == self.myConvType)
          {self.dataTable.ajax.reload( reload_callback, false );}

        };
        //reload callback is recursive while the session is active
        var reload_callback = function(json){
          console.log("Refreshing " + JSON.stringify(json).substring(0, 100));
          if (Model.getActive() || Model.getMitmActive()){
            $timeout(aux, 1000);
          }
        };

        aux();
      },

      /////////////////// Helper functions for specific tabs ///////////////////
      ////////////////////////////////////////////////////////////////////////
      getColumnsPackets: function(){
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
        {"data": "constructor", "name":"Constructor", "visible": false, "orderable": false},
      ];
      return columns;
    },
    dataCallbackPackets: function(d){
      var self = this;
      var current_session = Model.getCurrentSession();
      d["method"] = this.constants.method;
      d["id_session"] = current_session.id_session;
      d["params"] = {"id_session": current_session.id_session,
      "select_all": self.select_all };
      angular.forEach(d["columns"], function(value, key){
        if (value.data == "constructor"){
          value.searchable = self.packet_search_payload;
        }
      });
      return JSON.stringify( d ); //submit data as json
    },
    getSelectCallbackPackets: function(){
      var self = this;
      var cb = function (elem){
        var jq = $(elem);
        var check = jq.is(":checked");
        var data = self.dataTable.row(jq.parent()).data();
        //when a response from the server is received (checked) after we sent
        //a select_packet command
        Packet.SelectPacket(data.id_packet, check, function(checked){
          jq.prop('checked', checked);
          data.selected = checked;
          // console.log("received from server checked " + checked);
          // console.log(self.dataTable.row(jq.parent()).data());
        });
      };
      return cb
    },
    getDoubleClickCallbackPackets: function(){
      var self = this;
      var cb = function (elem){
        var jq = $(elem); //jquery element
        var tr = jq.closest('tr');
        var row = self.dataTable.row(tr);
        var data = self.dataTable.row(elem).data();
        if ( row.child.isShown() ) {
          self.close_tr(tr);
        }
        else {
          self.open_tr(tr)
        }
      };
      return cb
    },
  //For IPV4
  getColumnsIPV4: function(){
    var columns = [
    {"data": "selected", "name": "Sel.", "searchable":false,
    "orderable":false, "width":"1%",
    "render": function(data, type, row){
      return '<input type= "checkbox" '+ (data? "checked": "") + '>';
    }
  },
  {"data": "id_conversation_ipv4", "name": "ID conv", "width":"3%",},
  {"data": "ip_a", "name": "IP A"},
  {"data": "ip_b", "name": "IP B"},
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
},

  dataCallbackConv: function(d){
    var current_session = Model.getCurrentSession();
    d["method"] = this.constants.method;
    d["id_session"] = current_session.id_session;
    d["params"] = {"id_session": current_session.id_session,
     "select_all": this.select_all };
    return JSON.stringify( d ); //submit data as json
  },
  // Select a conversation works for
  //conv_type = IPV4, UDP, TCP, MITM, Packets (Future)
  //id_name = "id_conversation_ipv4", "id_conversation_tcp", ...
  getSelectCallbackConversation: function(id_name){
    var self = this;
    var cb = function (elem){
      var jq = $(elem);
      var data = self.dataTable.row(jq.parent()).data();
      var check = jq.is(":checked");
      var conv_type = self.myConvType; // 0 for IPV4 1 for UDP 2 for TCP
      //CAREFUL data.id_conversation does not work (it must match an exact column name)
      Conversation.SelectConversation(data[id_name], conv_type, check, function(checked){
        jq.prop('checked', checked);
        data.selected = checked;
        //console.log($scope.packets_datatable.row(jq.parent()).data());
      });
      event.stopPropagation();
    };
    return cb
  },
  getDoubleClickCallbackConv: function(id_name){
    var self = this;
    var cb = function (elem){
      console.log("clicked on row");
      var conv_type = self.myConvType; //conversation_type
      var data = self.dataTable.row(elem).data();
      var id_conv = data[id_name]; //id_conversation
      console.error("conversations ipv4 : id_conversation="+id_conv+" conv_type="+conv_type);
     //Launch Sublist tab (with id_conversation and conversation_type)
     if (conv_type == Constants.CONV_TYPE.CONV_MITM){
       console.log("Double ClickCallbackConv -----> going to Sublist MITM");
       Model.forceTab(Constants.CONV_TYPE.SUBLIST_MITM, conv_type, id_conv);
     }
     else{
       Model.forceTab(Constants.CONV_TYPE.SUBLIST, conv_type, id_conv);
     }
    };
    return cb
  },
  //usefull for SUBLIST and SUBLIST_MITM
  dataCallbackSublist: function(d){
    console.log("calling dataCallbackSublist with id_conv " + this.id_conv + "and conv_type " + this.conv_type);
    current_session = Model.getCurrentSession();
    d["method"] = this.constants.method;
    d["id_session"] = current_session.id_session;
    d["params"] = {"conversation_type":this.conv_type,
    "id_session": current_session.id_session,
    "select_all": this.select_all,
    "id_conversation": this.id_conv,};
    //columns are received unprefixed but sent prefixed
    var cols = d["columns"];
    for (var i = 0 ; i < cols.length ; i++){
        if (cols[i].data == "id_conversation") cols[i].data = "pc.id_conversation";
        else{
            cols[i].data = "p." + cols[i].data;
        }
    }
    var self = this;
    angular.forEach(d["columns"], function(value, key){
      if (value.data == "constructor"){
        value.searchable = self.packet_search_payload;
      }
    });
    return JSON.stringify( d ); //submit data as json
  },

  };

  return AbstractTabController;

}]);
})();
