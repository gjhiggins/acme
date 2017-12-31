## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  </style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Admin Dashboard</div>
      <div class="ui inverted segment">
        <div class="ui header small">Blockchain and RDF Graph status</div>
        <a class="ui green label">Blockchain height: ${coin['binfo']['blocks']}</a>
        <a class="ui ${'green' if str(gblocks) == str(coin['binfo']['blocks']) else 'red'} label">RDF Graph height: ${gblocks}</a>
        %if str(gblocks) != str(coin['binfo']['blocks']):
          <div class="ui mini primary button" id="catchup" data-action="catchup" data-id="${gblocks}">Catch up</div>
        %endif
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
