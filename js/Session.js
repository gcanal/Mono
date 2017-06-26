
(function(){

  angular.module("monoApp").service('Session', ['$http', '$timeout', 'Model',
  function($http, $timeout, Model) {
    var self_Session = this;
    this.getSessions = function(cb){
      $http.post('/awebservice',{method:"get_sessions",params:{},}
    ).then(function(response) {
      var sessions = response.data.sessions || []
      console.log("init sessions=" + JSON.stringify(sessions));
      Model.setSessions(sessions);
      if (cb instanceof Function) cb.call();
    }, function(error) {console.log(error);});
  };

  this.deleteSession = function(id_sess, cb){
    $http.post('/awebservice',{
      method:"remove_session",
      params:{"id_session":id_sess},
    }).then(function(response){
      console.log("del session -> response received=" + JSON.stringify(response));
      if (cb instanceof Function)
      cb.call();
    }, function(error) {console.log(error);});
  };

  this.setCurrentSession = function(id_sess, cb){
    if (Model.active){
      console.log("cannot switch session while active/retrieving packets");
      return;
    }
    id_sess = id_sess || 0 ;
    if (id_sess > 0){
      console.log("setting current session to id "+ id_sess);
      //setting current version from selected id_session
      var result = Model.getSessions().filter(function(o){
        return o.id_session == id_sess;
      });
      var r = (result.length > 0) ? result[0] : Model.current_session;
      r.packets = r.packets || [];
      Model.setCurrentSession(r);
      //now retrieving packets of selected session
      if (cb instanceof Function) cb.call();
    }
  };

  this.addSession = function(sess, cb){
    $http.post('/awebservice',{method:"add_session",params:
    {session: sess},}
  ).then(function(response) {
    console.log("add session=" + JSON.stringify(response));
    if (cb instanceof Function) cb.call();
  }, function(error) {console.log(error);});
};

//updates any session
this.updateSession = function(sess, cb){
  $http.post('/awebservice',{method:"update_session",params:
  {session: sess},}
).then(function(response) {
  sess = response.data.session;
  if (cb instanceof Function) cb.call(sess, sess);
}, function(error) {console.log(error);});
};

//use this function when you have changed the current_session
this.updateCurrentSession = function(sess, cb){
  this.updateSession(sess, function(rec_sess){
    new_curr_sess = rec_sess || Model.getCurrentSession();
    Model.setCurrentSession(new_curr_sess);
    if (cb instanceof Function) cb.call();
  })
};

//The Scapy and MITM proxy processes at the server side might take some time
//to terminate. That's why we'll check the activity every 500 ms until all
//processes have finished
this.checkActive = function (){
  $http.post('/awebservice',{method:"is_any_session_active",params:{},})
  .then(function(response) {
    var sess_active = response.data.session_active;
    var mitm_active = response.data.mitm_active;
    Model.setActive(sess_active);
    Model.setMitmActive(mitm_active);
    console.log("ACTIVITY CHECK:  session_active" + Model.getActive() + " mitm_active" + Model.getMitmActive());
    if (sess_active || mitm_active){ // keep checking if active
      $timeout(self_Session.checkActive, 500);
    }
    else{
    }
  }, function(error) {console.log(error);});
};

this.stopRecording = function(){
  $http.post('/awebservice',{method:"stop_session",params:{},}
).then(function(response) {
  var s = response.data.success;
  if (s) self_Session.checkActive();
  else console.log("stop_request  unsuccessfull " + JSON.stringify(response));
}, function(error) {console.log(error);});
};

this.startRecording = function(id_sess, cb_success){
  $http.post('/awebservice',{method:"start_session",params:
  {id_session: id_sess},}
).then(function(response) {
  var s = response.data.success;
  Model.setActive(s);
  if (Model.getActive()){
    //TODO add test session_started == current_session
    if (cb_success instanceof Function) cb_success.call();
  }
  else{
    //request stop
    this.stopRequest();
  }
}, function(error) {console.log(error);});
};

//Set current session to empty session
//(Usefull when no sessions exists and None can be selected as default)
this.setToNoSession = function(){
  Model.setCurrentSession({id_session:0, date:"", packets:[], iface:''});
};

this.setDefaultSession = function(){
  var sessions = Model.getSessions();
  if (sessions.length > 0)
    Model.setCurrentSession(sessions[sessions.length - 1]);
  else{
    this.setToNoSession();
  }
};

//Mitm TODO maybe place this in another file
this.stopMitm = function(){
  $http.post('/awebservice',{method:"stop_mitm",params:{},}
).then(function(response) {
  var answer = response.data.mitm_active;
  Model.setMitmActive(answer);
}, function(error) {console.log(error);});
};

this.startMitm = function(id_sess, cb_success){
  $http.post('/awebservice',{method:"start_mitm",params:{},}
).then(function(response) {
  var answer = response.data.mitm_active;
  console.log("starting_mitm received answer="+answer);
  Model.setMitmActive(answer);
  if (cb_success instanceof Function) cb_success.call(answer, answer);
}, function(error) {console.log(error);});
};

this.unselectAll = function(id_sess, cb_success){
  $http.post('/awebservice',{method:"unselect_all",params:{"id_session":id_sess},}
).then(function(response) {
  var data = response.data;
  if (cb_success instanceof Function) cb_success.call(data, data);
}, function(error) {console.log(error);});
};

}]);
})();
