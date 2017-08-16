## <%! from babel.dates import format_date, format_datetime, format_time %>
<%inherit file="acme:templates/base.mako"/>
<%page cached="True"/>
<%def name="header()">
  <title>ACME - A Cryptocurrency Metadata Explorer</title>
  <style type="text/css">
  .attr {color: rgb(200, 200, 200);}
  .val {color: rgb(255, 230, 30);}
  .date, .time {color: rgba(96, 234, 96, 0.8);}
  .icon {display: inline !important;}
  </style>
  ## <script type="text/javascript" src="/js/springy.js"></script>
  ## <script type="text/javascript" src="/js/springyui.js"></script>
  ## <script type="text/javascript">
  ##   var ngraph = new Springy.Graph();
  ##   // make some nodes
  ##   var node1 = ngraph.newNode({label: '${oitems.get("hash")}', data: {type: 'hash', userid: 123, displayname: 'https://purl.org/net/bel-epa/ccy#C${oitems.get("hash")}'}});
  ##   var node2 = ngraph.newNode({label: '${oitems.get("nextblockhash")}'});
  ##   var node3 = ngraph.newNode({label: '${oitems.get("previousblockhash")}'});
  ##   // connect them with an edge
  ##   ngraph.newEdge(node3, node1);
  ##   ngraph.newEdge(node1, node2);
  ##   // Add txids as links off've node1
  ##   % for cnt, txid in enumerate(oitems.get('txids')):
  ##     var ${'node{}'.format(4 + cnt)|n} = ngraph.newNode({label: '${txid|n}'});
  ##     ngraph.newEdge(node1, ${'node{}'.format(4 + cnt)|n});
  ##   % endfor
  ## </script>

  ## <link href='/css/visualrdf/bootstrap-responsive.min.css' rel='stylesheet' type='text/css' />
  ## <link href='/css/visualrdf/bootstrap.min.css' rel='stylesheet' type='text/css' />
  ## <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js" type="text/javascript"></script>
  ## <script type="text/javascript" src="/js/visualrdf/bootstrap.min.js"></script>
  ## <script type="text/javascript" src="/js/visualrdf/bootstrap-modal.js"></script>
  ## <script type="text/javascript" src="/js/visualrdf/d3/d3.js"></script>
  ## <script type="text/javascript" src="/js/visualrdf/d3/d3.layout.js"></script>
  ## <script type="text/javascript" src="/js/visualrdf/d3/d3.geom.js"></script>
</%def>

<%def name="body()">
  <div class="ui container" style="margin-top:4.6em;">
    <div class="ui inverted segment dark">
      <div class="ui small header">
        <i class="yellow cube icon"></i> Block ${oitems.get('height')}
      </div>
      <div class="ui divided list">
        <div class="item">primechain: <span class="date">${oitems.get('primechain')}</span></div>
        <div class="item">difficulty: <span class="val">${oitems.get('difficulty')}</span></div>
        <div class="item">time: <span class="time" title="${oitems.get('time')+'.000Z'}">${oitems.get('time')}</span>&nbsp;&nbsp;<span class="attr">(${oitems.get('time').replace('T', ' ')})</span></div>
        <div class="item"><i class="yellow cube icon"></i> hash: <span class="val">${oitems.get('hash')}</span></div>
        %if oitems.get('previousblockhash', False):
          <div class="item"><i class="yellow cube icon"></i> previousblockhash: <span class="val">${oitems.get('previousblockhash')}</span></div>
        %endif
        %if oitems.get('nextblockhash', False):
          <div class="item"><i class="yellow cube icon"></i> nextblockhash: <span class="val">${oitems.get('nextblockhash')}</span></div>
        %endif
        <div class="item">headerhash: <span class="val">${oitems.get('headerhash')}</span></div>
        <div class="item">merkleroot: <span class="val">${oitems.get('merkleroot')}</span></div>
        %for txid in oitems.get('txids'):
         <div class="item"><i class="yellow money icon"></i> transaction: <a href="${request.route_url('transaction', net=net, arg=txid)}">${txid}</a></div>
        %endfor
        ## <div class="item"><div class="ui divider"></div></div>
        ## <div style="float: left;border-width: 1px; border-style: solid;width:100%;min-height:500px;height:100%" id='chart'></div>
        <div class="item"><div class="ui divider"></div></div>
        <div class="item">
          <a class="item" href="${request.route_url('block', net=net, arg=oitems.get('nextblockhash'))|n}"><button class="ui right floated ${'disabled' if oitems['height'] >= coin['binfo']['blocks'] else ''} mini primary button" style="margin-right:12em">Next block</button></a>
          <a class="item" href="${request.route_url('block', net=net, arg=oitems.get('previousblockhash'))}"><button class="ui left floated ${'disabled' if oitems['height'] == 0 else ''} mini primary button" style="margin-left:12em">Previous block</button></a>
          </div>
      </div>
      ## <div class="ui inverted segment dark">
      ##   <canvas id="adg" width="900" height="600" />
      ## </div>
    </div>
    <div class="ui inverted accordion">
      <div class="title"><i class="dropdown icon"></i>Unprocessed JSON API response</div>
      <div class="content">
        ${dump|n}
      </div>
    </div>
  </div>
## <script type="text/javascript">
##   $('#adg').springy({ graph: ngraph });
## </script>
  ## <script type="text/javascript">
  ##   var w = document.getElementById("chart").offsetWidth-2,
  ##   h = document.getElementById("chart").offsetHeight;

  ##   var svg = d3.select("#chart").append("svg:svg")
  ##   .attr("width", w)
  ##   .attr("height", h)
  ##   .attr("pointer-events", "all");
  ##   vis = svg
  ##   .append('svg:g')
  ##   .call(d3.behavior.zoom().on("zoom", redraw))
  ##   .append('svg:g');

  ##   vis.append('svg:rect')
  ##   .attr('width', w)
  ##   .attr('height', h)
  ##   .attr('fill', 'black');

  ##   var json = ${rdfasjson|n}
  ##   var preds=false;
  ##   var types=true;
  ##   var nodes = [];
  ##   var links = [];
  ##   var literals = [];
  ##   var linkedArrowhead = [];
  ##   var force;
  ##   var uniquePredicates = {};
  ##   function redraw() {
  ##     vis.attr("transform",
  ##       "translate(" + d3.event.translate + ")"
  ##       + " scale(" + d3.event.scale + ")");
  ##   }


  ##   function mergeGraphs(newNodes, newLinks){
  ##     for(i in newLinks){
  ##       sIdx = newLinks[i].source;
  ##       tIdx = newLinks[i].target;

  ##       if(nodes.indexOf(newNodes[sIdx]) == -1){
  ##         nodes.push(newNodes[sIdx]);
  ##       }
  ##       newLinks[i].source = nodes.indexOf(newNodes[sIdx]);

  ##       if(nodes.indexOf(newNodes[tIdx]) == -1){
  ##         nodes.push(newNodes[tIdx]);
  ##       }
  ##       newLinks[i].target = nodes.indexOf(newNodes[tIdx]);
  ##       links.push(newLinks[i]);
  ##     }

  ##   }

  ##   function init(json){
  ##     literals = json.literals;
  ##     for(i in json.links){
  ##       uniquePredicates[json.links[i].name] = 1;
  ##     }
  ##     createPredicateFilters(uniquePredicates);
  ##     force = self.force = d3.layout.force();
  ##     mergeGraphs(json.nodes, json.links);
  ##     force.nodes(nodes)
  ##     .links(links)
  ##     .gravity(0.2)
  ##     .distance(2000)
  ##     .charge(-2000)
  ##     .linkDistance(100)
  ##     .size([w, h])
  ##     .start();

  ##     var link = vis.selectAll("g.link")
  ##     .data(links)
  ##     .enter()
  ##     .append("svg:g").attr("class", "link").attr("class", function(d){return d.name})
  ##     .call(force.drag);
  ##     link.append("svg:line")
  ##     .attr("class", "link")
  ##     .attr("stroke", "gray")
  ##     .attr("x1", function(d){return d.x1})
  ##     .attr("y1", function(d){return d.y1})
  ##     .attr("x2", function(d){return d.x1})
  ##     .attr("y2", function(d){return d.y2});

  ##     link.append("svg:text")
  ##     .attr("class", "link")
  ##     .attr("x", function(d) { return d.source.x; })
  ##     .attr("y", function(d) { return d.source.y; })
  ##     .text(function(d){return d.name;}).style("display", "none");


  ##     linkArrowhead = link.append("svg:polygon")
  ##     .attr("class", "arrowhead")
  ##     .attr("transform",function(d) {
  ##       angle = Math.atan2(d.target.y-d.source.y, d.target.x-d.source.x);
  ##       return "rotate("+angle+", "+d.target.x+", "+d.target.y+")";
  ##     })
  ##     .attr("points", function(d) {
  ##         //angle = (d.y2-d.y1)/(d.x2-d.x1);
  ##         return [[d.target.x,d.target.y].join(","),
  ##         [d.target.x-3,d.target.y+26].join(","),
  ##         [d.target.x+3,d.target.y+26].join(",")].join(" ");
  ##       });

  ##     var node = vis.selectAll("g.node")
  ##     .data(nodes)
  ##     .enter().append("svg:g")
  ##     .attr("class", "node")
  ##     .attr("dx", "80px")
  ##     .attr("dy", "80px")
  ##     .call(force.drag);

  ##     node.filter(function(d){return d.type == "uri"})/*.append("svg:a")
  ##     .attr("xlink:href", function(d){return "./?url="+d.uri} ).attr("target", "_new")*/
  ##     .append("svg:circle")
  ##     .attr("class", "node")
  ##     .attr("r", 10)
  ##     .attr("x", "-8px")
  ##     .attr("y", "-8px")
  ##     .attr("width", "16px")
  ##     .attr("height", "16px")
  ##     .style("fill", "#CFEFCF")
  ##     .style("stroke", "#000");



  ##     node.filter(function(d){return d.type == "literal"}).append("svg:rect")
  ##     .attr("class", "node")
  ##     .attr("x", "-4px")
  ##     .attr("y", "-8px")
  ##     .attr("width", "60px")
  ##     .attr("height", "16px")
  ##     .style("fill", "#CFEFCF")
  ##     .style("stroke", "#000");

  ##     node.filter(function(d){return d.type == "bnode" || d.type == "uri"}).append("svg:text")
  ##     .attr("class", "nodetext")
  ##     .attr("dx", 12)
  ##     .attr("dy", ".35em").attr("xlink:href", "http://graves.cl").attr("target", "_new")
  ##     .text(function(d) { return d.name });



  ##     node.filter(function(d){return d.type == "literal"}).append("svg:text")
  ##     .attr("class", "literal")
  ##     .attr("dx", 0)
  ##     .attr("dy", ".35em")
  ##     .text(function(d) { return d.name });

  ##     arr1 = d3.selectAll("text.literal");
  ##     arr = arr1[0];
  ##     for(var i=0; i<arr.length; i++){
  ##       x = arr[i].previousSibling;
  ##       d3.select(x).attr("width", arr[i].getBBox().width+8);
  ##     }


  ##     var ticks = 0;
  ##     force.on("tick", function() {
  ##       ticks++;
  ##       if (ticks > 300) {
  ##         force.stop();
  ##         force.charge(0)
  ##         .linkStrength(0)
  ##         .linkDistance(0)
  ##         .gravity(0);
  ##         force.start();
  ##       }
  ##       link.selectAll("line.link").attr("x1", function(d) { return d.source.x; })
  ##       .attr("y1", function(d) { return d.source.y; })
  ##       .attr("x2", function(d) { return d.target.x; })
  ##       .attr("y2", function(d) { return d.target.y; });
  ##       link.selectAll("text.link").attr("x", function(d) { return (d.source.x+d.target.x)/2; })
  ##       .attr("y", function(d) { return (d.source.y+d.target.y)/2; });

  ##       node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")";


  ##     });

  ##       linkArrowhead.attr("points", function(d) {
  ##         return [[d.target.x,d.target.y+10].join(","),
  ##         [d.target.x-3,d.target.y+16].join(","),
  ##         [d.target.x+3,d.target.y+16].join(",")].join(" ");
  ##       })
  ##       .attr("transform",function(d) {
  ##         angle = Math.atan2(d.target.y-d.source.y, d.target.x-d.source.x)*180/Math.PI + 90;
  ##         return "rotate("+angle+", "+d.target.x+", "+d.target.y+")";
  ##       });
  ##       d3.selectAll('circle').on('mouseenter', function(d){
  ##         var currentLiterals = literals[d.name];
  ##         var tablebody = $("#literalbody");
  ##         tablebody.empty();
  ##         $("#literalsubject").html(d.name);
  ##         if (currentLiterals != undefined){
  ##           d3.select("#literaltable").style("display", "block");
  ##           d3.select("#literalmsg").html("")
  ##           $.each(currentLiterals, function(i, item){
  ##             language = (item['l'] == "")?"":" <strong>("+item['l']+")</strong>";
  ##             datatype = (item['d'] == "")?"":"^^<strong>"+item['d']+"</strong>";
  ##             td = "<tr><td>"+item['p']+"</td><td>"+item['o']+datatype+language+"</td></tr>"
  ##             tablebody.append($(td))
  ##           })
  ##         }else{
  ##           d3.select("#literaltable").style("display", "none");
  ##           d3.select("#literalmsg").html("No literals related to this URI")
  ##         }
  ##         var x = d3.event.pageX+"px",
  ##         y = d3.event.pageY+"px";
  ##         var l = d3.select("#literals");
  ##         l.style("top", y).style("left", x).style("display", "block");
  ##       }).on('mouseout', function(d){
  ##         var l = d3.select("#literals");
  ##         l.style("display", "none");

  ##       });

  ##     });

  ##         /*node.filter(function(d){return d.type == "uri"}).on('click', function(d){
  ##             restart(d.uri);
  ##           });*/
  ##   }

  ## </script>
</%def>
