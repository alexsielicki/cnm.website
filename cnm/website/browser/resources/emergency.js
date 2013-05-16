
function displayMessage(data) {
    var isFrontpage;
    var url = location.href;
    isFrontpage = data.portal_url == url || data.alt_portal_url == url;
    if (data.display_emergency && (data.show_on_all_pages || isFrontpage)) {
        jQuery('#emergencyMessage').empty();
        jQuery('#emergencyMessage').append('<div id="emergencyLastUpdatedTime">' + data.last_updated + '</div>');
        jQuery('#emergencyMessage').append(data.message);
        jQuery('#emergencyMessage').show();
    }
}

function getEmergencyMessage() {
    jQuery.getJSON('emergency_message.json', displayMessage);
}

jQuery(getEmergencyMessage);
