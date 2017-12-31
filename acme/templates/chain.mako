## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  annotation {color: rgba(255, 255, 255, 0.6);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  .val {color: rgb(255, 230, 30);}
  .attr {color: rgba(255, 255, 255, 0.8);}
  .muted {color: rgba(255, 255, 255, 0.6);}
</style>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui header">Prime Gaps</div>
      <div class="ui inverted segment">
    % for i in request.tmpl_context.gaps:
      <div class="ui inverted segment dark">
        %for j in i[1:]: 
          <div class="ui header">${j[1][0]['primechain'].split('.')[0].upper()}: ${j[0]}-digit primes</div>
          <table class="ui striped inverted table">
            <thead>
            % for k in flds:
              % if k not in ['ismine', 'primedigit']:
                <td>${k + '{}'.format(' / primedigit' if k == 'primechain' else '')}</td>
              % endif
            % endfor
            </thead>
          %for l in j[1]:
            <tr>
            % for k in flds:
              % if k == 'time':
                <td><span class="time" title="${l[k].replace(' ', 'T')[:-4]+'.000Z'}">${l[k]}</span>&nbsp;&nbsp;<span class="muted">(${l[k][:-4]})</span></td>
              % elif k == 'primechain':
                <td>
                  <span class="date">${l[k].split('.')[0]}</span>.<span class="val">${l[k].split('.')[1]}</span>
                  / <span class="attr">${l['primedigit']}</span>
                  </td>
              % elif k == 'height':
                <td><a href="${request.route_url('blocklist', net=net, arg=l[k])}">${l[k]}</span></td>
              % elif k == 'mineraddress':
                % if l[k] != 'multiple':
                  <td>
                    % if l['ismine'] is True:
                    <i class="green user icon"></i>
                    % endif
                    <a href="${request.route_url('address', net=net, arg=l[k])}">${l[k]}</span>
                  </td>
                %else:
                  <td>${l[k]}</td>
                %endif
              % elif k in ['primeorigin', 'primorialform']:
                <td>
                  <span title="${l[k]}" class="attr">${l[k][:6]} ... ${l[k][-6:]}</span>
                </td>
              % elif k not in ['ismine', 'primedigit']:
                <td>${l[k]}</td>
              % endif
            % endfor
            </tr>
          %endfor
          </table>
        %endfor
      </div>
    %endfor
    </div>


    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
      <div class="content">
        ${dump|n}
      </div>
    </div>
  </div>
</%def>
