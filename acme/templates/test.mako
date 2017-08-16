## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .ui.feed>.event>.content .date,
  .ui.feed>.event>.content .summary,
  .ui.feed>.event>.content .extra.text {color: #ccc;}
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Test Area</div>
      <div class="ui inverted segment">

        <div class="ui feed">
          <div class="event">
            <div class="label">
              <img src="/img/logo.png">
            </div>
            <div class="content">
              <div class="date">
                when
              </div>
              <div class="summary">
                 <a>actor</a> action 
              </div>
              <div class="extra text">
                extra text
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
      <div class="content">
        ${dump|n}
      </div>
    </div>
  </div>
</%def>
