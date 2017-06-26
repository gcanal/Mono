(function(){
  //proxy Model
  //Is an event emitter
  angular.module('monoApp').service("Model", ['$rootScope', 'Constants', function($rootScope, Constants) {
    this.ifaces = [];
    this.active = false;
    this.mitm_active = false
    this.sessions = [];
    this.current_session = {};
    this.tab = Constants.CONV_TYPE.UNDEFINED;

    this.setIfaces = function(ifaces){
      this.ifaces = ifaces;
      //transmit to all scopes
      $rootScope.$broadcast('Model::ifacesUpdate', this.ifaces);
    };
    this.setActive = function(newAct){
      this.active = newAct;
      $rootScope.$broadcast('Model::activeUpdate', this.active);
    };
    this.setMitmActive = function(is_mitm_active){
      this.mitm_active = is_mitm_active;
      $rootScope.$broadcast('Model::mitmActiveUpdate', this.mitm_active);
    };
    this.setSessions = function(new_sessions){
      this.sessions = new_sessions;
      $rootScope.$broadcast('Model::sessionsUpdate', this.sessions);
    };
    this.setCurrentSession = function(new_curr_session){
      angular.extend(this.current_session, new_curr_session)
      //this.current_session = new_curr_session;
      $rootScope.$broadcast('Model::currentSessionUpdate', this.current_session);
    };
  // conv_type and id_conv are optional (usefull to go from a conversation list
  // to conversation details)
    this.setTab = function(newTab, conv_type, id_conv){
      this.tab = newTab;
      var tab_object = {"tab":this.tab, "conv_type":conv_type, "id_conv":id_conv};
      $rootScope.$broadcast('Model::tabUpdate', tab_object );
      //console.log("Model set tab " + JSON.stringify(tab_object));
    };
    this.forceTab = function(newTab, conv_type, id_conv){
      this.tab = newTab;
      var tab_object = {"tab":this.tab, "conv_type":conv_type, "id_conv":id_conv};
      $rootScope.$broadcast('Model::forceTab', tab_object );
    }

    this.getIfaces = function(){
      return this.ifaces;
    };
    this.getCurrentSession = function (){
      return this.current_session;
    };
    this.getActive = function(){
      return this.active;
    };
    this.getMitmActive = function(){
      return this.mitm_active;
    };
    this.getSessions = function(){
      return this.sessions;
    };
    this.getTab = function(){
      return this.tab;
    };

  }]);
})();
