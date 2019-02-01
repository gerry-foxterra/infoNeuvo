var baseUrl;
var serviceUrl;

var authCode = "";
var username;

jQuery(document).ready(function(){
  baseUrl = utilBaseUrl()
  serviceUrl = baseUrl + "/services/";
  username = getCookie("meta_username");
  authCode = getCookie("meta_authCode");
  $("#password").keypress(function(e) {
    if(e.which == 13)
      doLogin();
  });
});

// Check the login cookie, don't go to the server
function jsLoggedIn()
{
  authCode = getCookie("meta_authCode");
  if (authCode.length > 1)
    return true;
  userID = 0;
  return false;
}

function doLogin()
{
    var theUrl = serviceUrl + "login.py";
    var jsonData = $("#loginform").serialize();
    $("#loginMsg").val("");
    $("#loginMsg").hide();
    $.ajax(
    {
        url: theUrl,
        data: jsonData,
        dataType: 'json',
        type: 'POST',
        cache: false,
        success: function(rtn) {
          var userObj = eval(rtn);
          if (userObj.hasOwnProperty("error")) {
            if (userObj["error"] == "ERROR")
              loginMessage(userObj["reason"], 0);
          }
          else {
            authCode = userObj["authCode"];
            maxDuration = userObj["maxDuration"];
            setCookie("meta_authCode", authCode, maxDuration);
            userID = userObj["uniqueID"];
            username = userObj["name"];
            setCookie("meta_username", username);
            setCookie("meta_userID", userID);
            var siteLink = "admin.html";
            window.location.replace(siteLink);
          }
        },
        error: function (jqXHR, ajaxOptions, thrownError) {
          console.log(thrownError);
        }
    });
}

function logout()
{
    var theUrl = serviceUrl + "logout.py";
    var data = "meta_authCode=" + authCode;
    eraseCookie("meta_authCode");
    eraseCookie("meta_userID");
    userID = 0;
    $.ajax(
    {
        url: theUrl,
        data: data,
        type: 'POST',
        cache: false,
        success: function(rtn) {
          loginMessage("Successfully logged out", 100);
        },
        error: function (jqXHR, ajaxOptions, thrownError) {
            ; }
    });
    var siteLink = "index.html";
    window.location.replace(siteLink);

}
