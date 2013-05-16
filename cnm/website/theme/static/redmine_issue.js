$(document).ready(function(){
  var redmine_api = "/redmine/issues.json";
  var page = window.location.href;
  var agent = navigator.userAgent;
  var issue_form = "<form id='issue' action='/redmine/issues.json' method='post'><p>Problem Description:</p><p><textarea name='description' class='issue_description'></textarea></p><input type='submit' value='Report this Problem' /><input id='cancel_issue' type='button' value='Nevermind' /></form>";
  var success = "<p>Your issue has been submitted.</p>"
  var failure = "<p>There was a problem submitting your issue.</p>"


  $('#personaltools-report_issue a').click(function (event){
    $("#issue_container").html(issue_form);
    $("#issue_container").prependTo("#content");
    $("#issue_container").addClass("visible");
    $("#issue").submit(function (event){
      //alert(JSON.stringify(build_post(redmine_api, process_form($(this)))));
      var issue = build_issue();
      $("#issue_container").html('<img class="sub-status-image" src="/++theme++cnm.website/static/ajax-loader.gif" />');
      $.ajax(build_post(redmine_api, issue));
      return false;
    });
    $("#cancel_issue").click(function (event){
      $("#issue_container").removeClass("visible");
    });
    $("#portal-personaltools").removeClass("activated").addClass("deactivated");
    return false;
  });


  function agent_info () {
    return(agent.match(/(Chrome|Safari|Firefox|msie)(\/|\s)(\w|\.)*/gi)[0]);
  };


  function build_post(uri, issue) {
    return({
      url: uri,
      type: "POST",
      data: JSON.stringify(issue),
      processData: false,
      dataType: "json",
      contentType: "application/json",
      beforeSend: function(xhr, settings) {
        xhr.setRequestHeader('X-Redmine-API-Key', 'e7c3bb002ec9a46cfc1f6f34505ceb076dedd182');
      },
      error: function(xhr, status, error) {
        $("#issue_container").html(failure);
      },
      success: function(data, status, xhr) {
        $("#issue_container").html(success);
      },
      cache: false
    });
  };


  function build_issue() {
    return({
      'issue': {
        'project_id': 'web-issue-tracker',
        'description': $('.issue_description').val(),
        'subject': page + ' - ' + $('#user-name').text(),
        'custom_fields': [ 
                            { 'value': page, 'name': 'URL', 'id': '1' },
                            { 'value': agent_info(), 'name': 'Browser', 'id': '2' },
                            { 'value': navigator.platform, 'name': 'OS', 'id': '4' },
                            { 'value': navigator.userAgent, 'name': 'User Agent', 'id': '5' }
                          ]
      }
    });
  };
});