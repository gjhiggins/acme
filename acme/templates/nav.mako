# -*- coding: utf-8 -*-
<%def name="body()">
<div class="ui container" style="margin-top:3.6em;">
  <div class="ui fixed inverted menu">
    <a href="${request.route_url('home')|n}" title="ACME, A Cryptocurrency Metadata Explorer" class="item"><img style="float: left;vertical-align:top;margin-right:0.6em;height:32px;width:56px;" src="/img/logo.png" />
    </a>
    %if pp == 'front':
    <div class="item"><img style="float: left;vertical-align:top;margin-right:0.1em;height:1.2em;width:1.3em" src="/img/coin.png" />&nbsp;<span style="font-style: italic"><span style="color: green;font-size:140%">${coin.get('name')|n}</span></div>
    %else:
    <div class="item"><a href="${'/test/' if net =='main' else '/main/'}" title=""><img style="float: left;vertical-align:middle;margin-right:0.1em;height:1.3em;width:1.3em" src="/img/coin${'_testnet' if coin['binfo']['testnet'] else ''}.png" />&nbsp;<span style="font-style: italic"><span style="color: green;font-size:140%">${coin.get('name')|n}</span></span></a></div>
    <div class="ui simple dropdown item">
      <i class="yellow cubes icon"></i> Blocks <i class="dropdown icon"></i>
      <div class="menu">
        <a class="item" href="${request.route_url('blocklist', net=net, arg=coin['binfo']['blocks'])|n}">Browse the recent blockchain</a>
        <a class="item" href="${request.route_url('blockbrowser', net=net)|n}">Browse the blockgraph</a>
        <div class="divider"></div>
        <div class="header">History</div>
        %for [k, v] in histoire[:1 if net == 'test' else len(histoire)]:
          <div class="item">
            <i class="dropdown icon"></i>
            ${k|n}
            <div class="menu transition hidden" tabindex="-1">
            %for bheight, datestamp, month in v:
              <a class="item" href="${request.route_url('blocklist', net=net, arg=bheight)|n}">${month}</a>
            %endfor
            </div>
          </div>
        %endfor
      </div>
    </div>

    <div class="ui simple dropdown item">
      <i class="yellow signal icon"></i>Network <i class="dropdown icon"></i>
      <div class="menu">
        <a class="item" href="${request.route_url('nodes', net=net)|n}">Node geoip map</a>
        <a class="item" href="${request.route_url('network', net=net)|n}">Network statistics</a>
      </div>
    </div>

    <div class="ui simple inverted dropdown item">
      <i class="yellow money icon"></i>Transactions <i class="dropdown icon"></i>
      <div class="menu">
        <a class="item" href="${request.route_url('transactions', net=net)|n}">Browse recent transactions</a>
        ## <a class="item" href="${request.route_url('exchange', net=net)|n}">Exchange rate data</a>
        %if net == 'main':
        %for i, addr in enumerate(list(filter(lambda x: x > '', coin['donationaddresses'].split('\n')))):
          <a class="item" href="${request.route_url('address', net=net, arg=addr)|n}">${coin['name']} Donation Address ${i+1}</a>
        %endfor
        %for i, addr in enumerate(list(filter(lambda x: x > '', coin['bountyaddresses'].split('\n')))):
        <a class="item" href="${request.route_url('address', net=net, arg=addr)|n}">${coin['name']} Bounty Address ${i+1}</a>
        %endfor
        %endif
      </div>
    </div>

    <div class="ui simple dropdown item">
      <i class="yellow ticket icon"></i>Publications <i class="dropdown icon"></i>
      <div class="menu">
        <a class="item" href="${request.route_url('publications', net=net)|n}">Recently-published items</a>
      </div>
    </div>

    <div class="ui simple dropdown item">
      <i class="yellow cubes icon"></i> Connections <i class="dropdown icon"></i>
      <div class="menu">
        <a class="item" href="https://bitcointalk.org/index.php?topic=0.0">Discussion Thread</a>
        <a class="item" href="https://github.com/${coin['name'].lower()}-project/${coin['name'].lower()}">Github</a>
        <a class="item" href="https://twitter.com/${coin['name'].lower()}">#${coin['name'].lower()}coin @ Twitter</a>
        <div class="item">
          <i class="dropdown icon"></i>
          Block Explorers
          <div class="menu transition hidden" tabindex="-1">
            <a class="item" href="#">Placeholder</a>
          </div>
        </div>
      </div>
    </div>

    %endif
    <div class="right menu">
      <div class="item">
        <div class="ui search">
          <div class="ui transparent inverted icon input">
            <i class="search icon"></i>
            <input type="text" autocomplete="off" class="prompt" name="query" placeholder="Search">
          </div>
          <div class="results"></div>
        </div>
      </div>
      <a class="item" href="https://github.com/gjhiggins/acme/tree/slimcoin" title="Github repository"><i class="yellow github icon"></i> Github</a>
    </div>
  </div>
</div>
</%def>
