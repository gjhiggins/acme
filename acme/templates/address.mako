## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="False"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .attr {color: rgb(200, 200, 200);}
  .crd {/*color: rgba(30, 112, 191, 0.9);*/color: rgba(96, 234, 96, 0.8); font-weight:bold; font-size:120%;}
  .dbt {color: rgba(234, 96, 96, 0.8); font-weight:bold; font-size:120%;}
  .bal {color: rgba(255, 230, 30, 0.8); font-weight:bold; font-size:120%;}
  .pyqrline, .val {color: rgb(255, 230, 30);}
  .input, .date, .time {color: rgba(96, 234, 96, 0.8);}
  .output {color: #f12500;}
  .tiny {font-size:70%; color: rgb(255, 230, 30);}
  .sotto {font-weight:normal; font-style:italic; font-size:80%;}
  .ui.card .meta>a:not(.ui), .ui.cards>.card .meta>a:not(.ui) {color:#4183c4;}
  .ui.card .meta>a:hover(.ui):hover, .ui.cards>.card .meta>a:not(.ui):hover {color:rgb(200, 200, 200);;}
  .ui.header.small .icon {display:inline!important;}
  .card {background: transparent!important; color:rgb(200, 200, 200);}
  .stet {font-family: monospace;}
  th {color:#aaa!important;}
  </style>
  <script type="text/javascript" src="/js/sgvizler.js"></script>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui small header">Gapcoin Address <span class="val">${adattrs.get('addr')}</span></div>
      <table class="ui inverted striped padded table">
        <tbody>
          <tr>
            <th> Hash </th>
            <td>${adattrs['pubkeyhash']}</td>
          </tr>
          <tr>
            <th> Number of confirmed transactions </th>
            <td id="total_tx">${len(inputs)}</td>
          </tr>
          <tr>
            <th> First transaction </th>
            <td id="time_first_tx" updater="1">
            %if inputs is not UNDEFINED and inputs != []: 
              ${inputs[-1].get('datetime').replace('T', ' ')[:-3]}
              (<span class="time" title="${inputs[-1].get('datetime')}">
                ${inputs[-1].get('datetime').replace('T', ' ')[:-3]}
              </span>) 
            %else:
            </td>
            %endif
            </td>
          </tr>
          <tr>
            <th> Last transaction </th>
            <td id="time_last_tx" updater="2">
            %if inputs is not UNDEFINED and inputs != []: 
              <span class="time" title="${inputs[0].get('datetime')}">
                ${inputs[0].get('datetime').replace('T', ' ')[:-3]}
              </span> 
              (${inputs[0].get('datetime').replace('T', ' ')[:-3]})
            %else:
              ???
            %endif
            </td>
          </tr>
          <tr>
            <th> Total Received </th>
            <td id="sum_in"><span class="crd">
              %if inputs is not UNDEFINED and inputs != []:
                ${sum([i['value'] for i in inputs])}
              %else:
                ???
              %endif
              </span> GAP</td>
          </tr>
          <tr>
            <th> Balance </th>
            <td id="balance"><span class="bal">
            %if inputs is not UNDEFINED and inputs != [] and outputs is not UNDEFINED and outputs != []:
              ${"{0:.2f}".format(sum([i['value'] for i in inputs]) - sum([o['value'] for o in outputs]))}</span>
            %else:
              ???
            %endif
              GAP</td>
          </tr>
        </tbody>
      </table>

      <div class="ui two column grid">
        <div class="row">

          <div class="column">
            <div class="ui small header">Inputs</div>
            % if inputs != []:
              <table class="ui inverted striped padded table">
                <thead>
                  <tr>
                    <th> Date &amp; Transaction / Address</th>
                    <th> Value </th>
                  </tr>
                </thead>
                <tbody>
                </tbody>
              </table>

              <table class="ui inverted striped padded table">
                <tbody>
                % for i in inputs:
                  <tr>
                    <td>
                      <span class="date" title="${i.get('datetime')}.00Z">${i.get('datetime')}</span>
                      <span class="tiny">${i.get('datetime').replace('T', ' ')[:-3]}</span>
                      <a href="${i['transaction']}">${i['transaction'].split('/')[-1][:24]}</a>
                      <br/>
                      <a href="${i['address']}">${i['address'].split('/')[-1]}</a>
                    </td>
                    <td>
                      <span class="crd">${i['value']}</span>
                    </td>
                  </tr>
                %endfor
                </tbody>
              </table>
            %endif
          </div>

          <div class="column">
            <div class="ui small header">Outputs</div>
            % if outputs != []:
              <table class="ui inverted striped padded table">
                <thead>
                  <tr>
                    <th> Date &amp; Transaction / Type</th>
                    <th> Value </th>
                  </tr>
                </thead>
                <tbody>
                </tbody>
              </table>
              <table class="ui inverted striped padded table">
                <tbody>
                  % for o in outputs:
                  <tr>
                    <td>
                      <span class="date" title="${o.get('datetime')}.00Z">${o.get('datetime')}</span>
                      <span class="tiny">${o.get('datetime').replace('T', ' ')[:-3]}</span>
                      <a href="${o['transaction']}">${o['transaction'].split('/')[-1][:24]}</a>
                      <br/>
                      ${o['stype']}
                    </td>
                    <td>
                      <span class="dbt">${o['value']}</span>
                    </td>
                  </tr>
                  %endfor
                </tbody>
              </table>
            %endif
            </div>
            ## <!-- TODO: present a paginated transaction list
            ## <table class="ui inverted striped padded table">
            ##   <tfoot>
            ##     <tr>
            ##       <th colspan="3">
            ##         <div class="ui right floated inverted pagination menu">
            ##           <a class="icon item">
            ##             <i class="left chevron icon"></i>
            ##           </a>
            ##           <a class="item">1</a>
            ##           <a class="item">2</a>
            ##           <a class="item">3</a>
            ##           <a class="item">4</a>
            ##           <a class="icon item">
            ##             <i class="right chevron icon"></i>
            ##           </a>
            ##         </div>
            ##       </th>
            ##     </tr>
            ##   </tfoot>
            ## </table>
          </div>
        </div>
      </div>

      <div class="ui inverted accordion">
        <div class="title"><i class="dropdown icon"></i>Unprocessed SPARQL response</div>
        <div class="content">
          <div class="ui inverted segment dark">inputs <pre>${inputsdump|n}</pre></div>
          <div class="ui inverted segment dark">outputs <pre>${outputsdump|n}</pre></div>
        </div>
      </div>
    </div>
  </div>
<script type="text/javascript">
</script>
</%def>
