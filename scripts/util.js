// Utilities
var mth = [ "xxx", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec" ];
function utilPrettyDate(theDate)
{
    if ( theDate.length < 10 )
        return ("unknown");
    return theDate.substr(8,2) + "-" + mth[Number(theDate.substr(5,2))] +
           "-" + theDate.substr(0,4);
}
function utilPrettyDateObj(theDate)
{
  return theDate.getDate() + "-" + mth[theDate.getMonth()+1] + "-" + theDate.getFullYear();
}
// This will produce a date string suitable to set as the default date value in
// the html <input type='date'> field
function utilDateForInput(daysBack)
{
  var dt = new Date();
  dt.setDate(dt.getDate() - daysBack);
  m = '0' + (dt.getMonth()+1).toString();
  d = '0' + dt.getDate().toString();
  return dt.getFullYear() + '-' + m.substr(m.length-2) + '-' + d.substr(d.length-2);
}
function dateFromIntegerDate(iDate)
{
  if (iDate < 20160101)
    return new Date(2016,1,1);
  var sDate = iDate.toString();
  var y = sDate.substr(0,4);
  var m = sDate.substr(4,2);
  var d = sDate.substr(6,2);
  return new Date(y,m,d);
}
// Sort an object array
var utilSort_by = function(field, reverse, primer){
   var key = function (x) {return primer ? primer(x[field]) : x[field]};

   return function (a,b) {
	  var A = key(a), B = key(b);
	  return ( (A < B) ? -1 : ((A > B) ? 1 : 0) ) * [-1,1][+!!reverse];
   }
}

function utilReplaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function utilPrettyNbr(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function utilFixDecimal(x, n) {
  return parseFloat(Math.round(x * 100) / 100).toFixed(n);
}

function utilPrettyFixDecimal(x,n) {
  return utilPrettyNbr(Number(utilFixDecimal(x,n)));
}

function utilBaseUrl() {
  var pathParts = window.location.pathname.split('/');      // Like /ncc2018-test/registration.html
  var pathName = "/";
  for (var i=0; i<pathParts.length; i++) {
    if (pathParts[i].toLowerCase().indexOf("info") == 0) {
      pathName += pathParts[i];
      break;
    }
  }
  var homeUrl = window.location.origin + pathName;          // Like https://connect2nature.ca
  return homeUrl;
}

// Color stuff
function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}
function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}
function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

// Create cookie
function setCookie(cname, cvalue, hours) {
    var d = new Date();
    d.setTime(d.getTime() + (hours*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}

// Read cookie
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// Erase cookie
function eraseCookie(name) {
    setCookie(name.trim(),"",-1);
}

// Get query string parameters
var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

// Popup message - requires a <div id='msg'><div id='msgContent'>
// which is properly styled
var msgCloseWindow = false; // Close current tab when closing message
function message(msg, secondsOpen, closeWindow)
{
  switch(arguments.length) {
    case 3:
      break;
    case 2:
      closeWindow = false;
      break;
    case 1:
      secondsOpen = 5;
      closeWindow = false;
      break;
    default:
      msg = 'No message available';
      stayOpen = false;
      closeWindow = false;
  }
  $("#msgContent").html(msg);
  $("#msg").fadeIn(500);
  setTimeout(msgClose, secondsOpen*1000);
  msgCloseWindow = closeWindow;
}
function msgClose()
{
  $("#msgContent").html("");
  $("#msg").fadeOut(500);
  if (msgCloseWindow)
    window.close();
}

function loginMessage(msg, secondsOpen)
{
  if (arguments.length == 1)
    secondsOpen = 0;
  $('#loginMsg').html(msg);
  $('#loginMsg').fadeIn(1000);
  if (secondsOpen > 0)
    setTimeout(loginMsgClose, secondsOpen*1000);
}
function loginMsgClose()
{
  $("#loginMsg").fadeOut(1000);
}
