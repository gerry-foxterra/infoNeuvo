var target = "#theForm";

var prefix = "<tr id='tr_x-x-x'><td valign='top' class='";
var suffix = "</td></tr>\n";
function buildForm(attributes, editOrder, layerMetadataOrder, metadataAttributes)
{
  var bfr = "";
  for (var i=0; i<editOrder.length; i++)
  {
    if (editOrder[i] != "_defaults")
      if (editOrder[i] == "metadata") {
        bfr += oneEntry(attributes[editOrder[i]], attributes["_defaults"], editOrder[i], "");
        j = 0;
        for (j=0; j<layerMetadataOrder.length; j++) {
          if (layerMetadataOrder[j][1] > 0) {
            metaKey = layerMetadataOrder[j][0];
            bfr += oneEntry(metadataAttributes[metaKey], attributes["_defaults"], metaKey, " metadata");
          }
        }
      }
      else
        bfr += oneEntry(attributes[editOrder[i]], attributes["_defaults"], editOrder[i], "");
  }
  $(target).html(bfr);
  $(".chosen_multi").chosen({
    placeholder_text_multiple: "Select one or more",
    width: "50%"
  });
  $(".chosen_single").chosen({
    width: "50%"
  });

  setTimeout(function() {         // Give the form time to build
    $(".metadata").change(function() {
      metadata[this.id] = this.value;
    });
  }, 400);
}

function oneEntry(attributes, defaults, key, extraClass)
{
  var bfr = "";
  var entry = setDefaults(attributes, defaults);
  if (entry.active) {
    var inputClass = " class='" + entry.inputClass + extraClass + "'";
    var prefixID = prefix.replace("x-x-x", key);
    if (entry.tagType == "table") {
      bfr += prefixID + entry.labelClass + "'>" + entry.label + "</td>";
      var t_label= [];
      for (var j=0; j<entry.columns.length; j++) {
        t_label.push(entry.columns[j].label);
        var oneColumn = entry.columns[j];
        oneColumn.active = false;
        entry.push(oneColumn);  // We need this as an entry in the table so we can access its attributes when populating the form.
      }
      bfr += "<td valign='top'>" + "<table id='" + entry.id + "' style=\"display:block\"'><thead><tr>";
      for (var j=0; j<t_label.length; j++)
        bfr += "<th align='center'>" + t_label[j] + "</th>";
      bfr += "</tr></thead><tbody id='tbody_" + key + "'>";
      var vals = ['','','',''];
      bfr += oneTableRow(key, 0, entry.columns, vals);
      bfr += "</tbody></table>" + suffix;
    }
    if (entry.tagType == "button")
      bfr += prefixID + entry.labelClass + "'>" + entry.label + "</td><td><" + buildOneEntry(entry, entry.id, extraClass, entry.label) + suffix;
    else if (entry.tagType.indexOf("select") >= 0) {
      var multi = (entry.tagType.indexOf("multi") < 0) ? "" : " multiple='multiple'";
      var theName = (entry.tagType.indexOf("multi") < 0) ? key : key + "[]";
      bfr += prefixID + entry.labelClass + "'>" + entry.label + "</td><td><select id='" + key +
             "' name='" + theName + "'" + multi + inputClass + ">";
      for (var j=0; j<entry.options.length; j++) {
        var val = entry.options[j].value;
        if (typeof(val) == "string" )
          val = "'" + val + "'";
        bfr += "<option value=" + val + ">" + entry.options[j].text + "</option>";
      }
      bfr += "</select>";
    }
    else
      bfr += prefixID + entry.labelClass + "'>" + entry.label + "</td><td><" + buildOneEntry(entry, key, extraClass) + suffix;
  }
  return bfr;
}

function oneTableRow(parentID, rowNbr, theColumns, theValues)
{
  var oneTr = "<tr id='tr_" + parentID + '_' + rowNbr + "'>";
  for (var j=0; j<theColumns.length; j++)
    oneTr += "<td><" + buildOneEntry(theColumns[j], theColumns[j].id+"["+rowNbr.toString()+"]", "", theValues[j]) + "</td>";
  return oneTr + "</tr>";
}

function buildOneEntry(oneEntry, theID, extraClass, theValue)
{
    var inputVal = oneEntry.hasOwnProperty("value") ? " value='" + oneEntry.value + "'": "";
    if (inputVal == "")
      inputVal = theValue ===  undefined ? "" : " value='" + theValue + "'";
    var onclick = oneEntry.hasOwnProperty("onclick") ? " onclick='" + oneEntry.onclick + "'" : "";
    var extra = "";
    if (oneEntry.tagType == "number" && oneEntry.min != oneEntry.max)
      extra = "' min='" + oneEntry.min + "' max='" + oneEntry.max;
    else if (oneEntry.tagType == "text" )
      extra = "' maxlength='" + oneEntry.maxLength;
    var endTag = oneEntry.tagType.indexOf("textarea") >=0 ? "</textarea>" : "";
    var disabled = oneEntry.disabled ? " disabled " : "";   // Disable any visible input field that is labelled with 'ID'
    var inputClass = oneEntry.inputClass + extraClass;
    var oneRow = oneEntry.tagType + " id='" + theID + "' name='" + theID +
           "' type='" + oneEntry.tagType + extra + "' class='" + inputClass + "'" + onclick + disabled + inputVal + ">" + endTag
    return oneRow;
}

function encodeFormData()
{
  $("#uniqueID").prop('disabled', false);
  $(".metadata").prop('disabled', true);  // All fields which are metadata elements shouldn't be encoded and sent to the server
  $("#metadata").prop('disabled', false); // The metadata field itself should be encoded
  var jsonMetadata = JSON.stringify(metadata);
  $("#metadata").val(jsonMetadata);
  var f = $('form#form_meta').serializeObject();
  var json = JSON.stringify(f);
  $("#uniqueID").prop('disabled', true);
  $(".metadata").prop('disabled', false);
  $("#metadata").prop('disabled', true);
  // If there have been array elements deleted, they will still
  // exist as an array element in the original list.  Get rid of their null entries.
  json = json.replace(",null,", ",");
  json = json.replace(",null", "");
  json = json.replace("null,", "");
  console.log("encodeFormData:\n" + json);
  return json;
}
