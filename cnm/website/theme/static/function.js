(function() {
     BM = window.BM || {};
     var _write = document.write;
     var _writeln = document.writeln;
     document.writeln = document.write = function(s) {
         var id='';
         if (s.match(/\bflickr_badge_image\b/)) {
             id='flickr_badge_wrapper';
         }
         BM.onavailable(id, function(el) { el.innerHTML = s; });
         return true;
     };
     BM.onavailable = function(id, fn) {
        var el = document.getElementById(id);
        if(!el) {
            window.setTimeout(function() { BM.onavailable(id, fn); id=fn=null; }, 100);
            return;
        }
        fn(el);
     };
     BM.load = function(s, code) {
        var e = document.createElement('script');
        e.type = 'text/javascript';
        e.src=s;
        if(code) {
            e.onreadystatechange = function() { if(e.readyState == 'complete') code(); };
            e.onload = code;
        }
        document.getElementsByTagName('head')[0].appendChild(e);
     };
     BM.slideshow = function() {
         jq("ul.tabs").tabs("div.flickr_badge_wrapper > a", {rotate: true}).slideshow();
         jq("ul.tabs").data("slideshow").play();
     };
     BM.emergency = function() { jq.ajax({
        type: "GET",
        contentType: 'application/json',
        url: "/emergency_message.json",
        dataType: "json",
        success: function(data) {
            if( jq.isEmptyObject(data) == false &&
                jq.isEmptyObject(jQuery(data['html'])) == false ){
                    jq(data['html']).appendTo('#emergency-container');
                    jq("#emergency-container").show(300);
                 }
            }
        });
     };
    BM.columnglue = function() {
        var c1 = $("#portal-column-one");
        var c2 = $("#portal-column-two");
        var cc = $("#portal-column-content").height();
        var ccc = cc + 50
        if (c1.height() < cc ) {c1.css("height",ccc);}
        if (c2.height() < cc ) {c2.css("height",ccc);}
    };

})();

function event_feed(type, number, category, numdays, adpid, nem, sortorder, ver, target) {
    if (typeof jQuery != 'undefined') {
        $(document).ready(function () {
            var adx = "Events are temporarily unavailable. Please check back later.";
            var url = 'http://calendar.activedatax.com/cnm/EventListSyndicator.aspx?type=' + type + '&number=' + number + '&category=' + category + '&numdays=' + numdays + '&adpid=' + adpid + '&nem=' + nem + '&sortorder=' + sortorder + '&ver=' + ver + '&target=' + target;
            jQuery.ajax({   dataType: 'script', 
                            url: url
                        });
            setTimeout(function() {
                if(typeof response=='undefined'){
                    jQuery('#adx101897').html(adx);
                    }}, 5000);
        });
    }
    else { 
        document.getElementById('adx101897').innerHTML = 'Events are temporarily unavailable because the jQuery library cannot be located.'; 
    }
}