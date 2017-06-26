(function(){
  var app = angular.module("monoApp");

  // Iface API
  app.service("Iface", ['$http', 'Model', function($http, Model) {
    //retrieve ifaces
    this.getIfaces = function(cb){
      $http.post('/awebservice', {method:"get_ifaces", params:{},}
    ).then(function(response) {
      var ifaces = response.data.ifaces || [];
      for ( i =0 ; i < ifaces.length ; i++){
        ifaces[i] = {"index": i, "name":ifaces[i]};
      }
      //update model
      Model.setIfaces(ifaces);
      console.log("initializing ifaces=" + JSON.stringify(Model.ifaces));
      //call callback
      if (cb instanceof Function) cb.call(ifaces);
    }, function(error) {console.log(error);});
  };

}]);

})();
