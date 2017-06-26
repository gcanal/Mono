
var monoApp = angular.module("monoApp", ["xeditable",]);

monoApp.run(function(editableOptions) {
  editableOptions.theme = 'bs3';
  console.log("app run");
});

// monoApp.config( function() {
//   console.log("app config");
// });
monoApp.config(['$qProvider', function($qProvider) {
     $qProvider.errorOnUnhandledRejections(false);
 }]);

monoApp.controller("monoController", ['$scope', '$http', '$timeout',  'Iface', 'Session', 'Model', 'Toast',
function($scope, $http, $timeout, Iface, Session, Model, Toast) {
  var self = this;

  //-------------------------- Controller Attributes
  this.newSession = "";
  this.newIface = "";
  this.newName = "";

  //-------------------------- Controller Methods

  //tab navigation
  this.isCurrent=function(id){
    return $scope.current_session.id_session == id;
  };
  this.isSelected = function(id){
    return $scope.current_session.id_session === id;
  };
  this.current_session_exist = function(arg){
    //console.log("current session exist" + ($scope.current_session.id_session > 0))
    console.log(arg)
    return $scope.current_session.id_session > 0;
  };
  //EVOL test if session exists server side before switching to it
  this.setCurrent = function (id_sess){
    Session.setCurrentSession(id_sess, function(){
    });
  };
  //should stay here in the controller
  this.deleteSessionAsk = function (){
    if ($scope.active){
      Toast.toast("Cannot delete session while active");
      return;
    }
    var curr = $scope.current_session;
    if (confirm('Are you sure you want to delete current session '
    + curr.name +' (id:' + curr.id_session +')'))
    {
      //call deleteSession then getSessions then setDefaultSession
      Session.deleteSession(curr.id_session, function(){
        Session.getSessions( function(){
          Session.setDefaultSession();
          self.setCurrent($scope.current_session.id_session);
        });
      });
    }
  };
  //stays here in the controller
  this.addSession = function(){
    if (this.newSession){
      Session.addSession({"name":self.newSession,"iface":"eth0"}, function(){
        Session.getSessions();
        self.newSession = "";
      });
    }
    else console.log("Refuse to create session with empty name");
  };
  //should stay in the controller
  this.updateIface = function(){
    //toast
    if ($scope.active) {
      Toast.toast("Cannot update iface while session is active");
      self.newIface = $scope.current_session.iface;
      return;
    }
    var session_clone = angular.extend({}, $scope.current_session);
    session_clone.iface = $scope.ifaces[self.newIface].name;
    self.newIface = session_clone.iface;
    console.log("updating iface to " + session_clone.iface);
    Session.updateCurrentSession(session_clone);
  };
  // start stop functions
  //TODO write $scope.startRequest -> only update datatables
  this.startStopRequest = function(){
    if ($scope.active) Session.stopRecording();
    else Session.startRecording($scope.current_session.id_session, function(){});
  };
  this.startStopMitm = function(){
    if ($scope.mitm_active) Session.stopMitm();
    else Session.startMitm($scope.current_session.id_session, function(answer){});
  };
  this.updateName =  function(){
    var session_clone = angular.extend({}, $scope.current_session);
    session_clone.name = self.newName;
    Session.updateCurrentSession(session_clone);
  };

//At the beginning, event are not properly propagated because
//controllers are not properly setup
//So we wait a few milliseconds before initializing
$timeout(function(){

  //-------------------------- Initialize Model
  Iface.getIfaces();
  Model.setActive(false);
  Model.setMitmActive(false);

  //-------------------------- Initialize View
  //get all sessions and set current session
  Session.getSessions(function(){
    Session.setDefaultSession();
    self.setCurrent($scope.current_session.id_session);
  });
}, 200);

  //Listen to the global model
  $scope.$on('Model::ifacesUpdate', function(event, data) {
    $scope.ifaces = data;
  });
  $scope.$on('Model::activeUpdate', function(event, is_active) {
    $scope.active = is_active;
  });
  $scope.$on('Model::mitmActiveUpdate', function(event, is_active) {
    $scope.mitm_active = is_active;
  });
  $scope.$on('Model::sessionsUpdate', function(event, sesss) {
    $scope.sessions = sesss;
  });
  $scope.$on('Model::currentSessionUpdate', function(event, curr) {
    $scope.current_session = curr;
    self.newIface = $scope.current_session.iface;
    self.newName = $scope.current_session.name;
    var res = $scope.sessions.find(function(element){
        return element.id_session == curr.id_session;
    });
    angular.extend(res, curr);
  });
}]);
