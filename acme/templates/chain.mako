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
      <div class="ui header">Primes</div>
      <div class="ui inverted segment">
        <div class="ui header"><span class="date">1CC</span>: Cunningham chain of 1st kind</div>
        <p>A <b>Cunningham chain of the first kind</b> of length <i>n</i> is a sequence of prime numbers (<i>p</i><sub>1</sub>,&nbsp;...,&nbsp;<i>p</i><sub><i>n</i></sub>) such that for all 1&nbsp;≤&nbsp;<i>i</i>&nbsp;&lt;&nbsp;<i>n</i>, <i>p</i><sub><i>i</i>+1</sub>&nbsp;=&nbsp;2<i>p</i><sub><i>i</i></sub>&nbsp;+&nbsp;1. (Hence each term of such a chain except the last one is a <a href="https://en.wikipedia.org/wiki/Sophie_Germain_prime" title="Sophie Germain prime">Sophie Germain prime</a>, and each term except the first is a <a href="https://en.wikipedia.org/wiki/Safe_prime" title="Safe prime">safe prime</a>).</p>
        <div class="ui header"><span class="date">2CC</span>: Cunningham chain of 2nd kind</div>
        <p>A <b>Cunningham chain of the second kind</b> of length <i>n</i> is a sequence of prime numbers (<i>p</i><sub>1</sub>,...,<i>p</i><sub><i>n</i></sub>) such that for all 1&nbsp;≤&nbsp;<i>i</i>&nbsp;&lt;&nbsp;<i>n</i>, <i>p</i><sub><i>i</i>+1</sub>&nbsp;=&nbsp;2<i>p</i><sub><i>i</i></sub>&nbsp;−&nbsp;1.</p>
        <div class="ui header"><span class="date">TWN</span>: bi-twin chain</div>
        <p>In <a href="/wiki/Number_theory" title="Number theory">number theory</a>, a <b>bi-twin chain</b> of length <i>k</i>&nbsp;+&nbsp;1 is a sequence of natural numbers</p>
        <dl>
        <dd><span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
                <mo>,</mo>
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
                <mo>,</mo>
                <mn>2</mn>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
                <mo>,</mo>
                <mn>2</mn>
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
                <mo>,</mo>
                <mo>…<!-- … --></mo>
                <mo>,</mo>
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>k</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
                <mo>,</mo>
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>k</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
                <mspace width="thinmathspace"></mspace>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle n-1,n+1,2n-1,2n+1,\dots ,2^{k}n-1,2^{k}n+1\,}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/233ca65e6ad4c0cffcbe61bf78427724d0017baf" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.671ex; width:49.232ex; height:3.009ex;" alt="n-1,n+1,2n-1,2n+1,\dots ,2^{k}n-1,2^{k}n+1\,"></span></dd>
        </dl>
        <p>in which every number is <a href="/wiki/Prime_number" title="Prime number">prime</a>.<sup id="cite_ref-1" class="reference"><a href="#cite_note-1">[1]</a></sup></p>
        <p>The numbers <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
                <mo>,</mo>
                <mn>2</mn>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
                <mo>,</mo>
                <mo>…<!-- … --></mo>
                <mo>,</mo>
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>k</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle n-1,2n-1,\dots ,2^{k}n-1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/20cf653d0216915bd5788823221cdfd06f752248" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.671ex; width:25.983ex; height:3.009ex;" alt="n-1,2n-1,\dots ,2^{k}n-1"></span> form a <a href="/wiki/Cunningham_chain" title="Cunningham chain">Cunningham chain</a> of the first kind of length <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <mi>k</mi>
                <mo>+</mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle k+1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/552a558062ed4c0486297b5b5531c5ee044dbd9b" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.505ex; width:5.245ex; height:2.343ex;" alt="k+1"></span>, while <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
                <mo>,</mo>
                <mn>2</mn>
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
                <mo>,</mo>
                <mo>…<!-- … --></mo>
                <mo>,</mo>
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>k</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle n+1,2n+1,\dots ,2^{k}n+1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/ce2084bdbf423ae19ad0cd322dd8158ff04e098b" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.671ex; width:25.983ex; height:3.009ex;" alt="n+1,2n+1,\dots ,2^{k}n+1"></span> forms a Cunningham chain of the second kind. Each of the pairs <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>i</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
                <mo>,</mo>
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>i</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>+</mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle 2^{i}n-1,2^{i}n+1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/58eb31efa6cc001efa6264a7c5850d50b96ee6e2" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.671ex; width:15.862ex; height:3.009ex;" alt="2^{i}n-1,2^{i}n+1"></span> is a pair of <a href="/wiki/Twin_primes" class="mw-redirect" title="Twin primes">twin primes</a>. Each of the primes <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>i</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle 2^{i}n-1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/7ad6c75d4bf8c321282c368bad723abe6c3b79ff" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.338ex; width:7.409ex; height:2.676ex;" alt="2^{i}n-1"></span> for <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <mn>0</mn>
                <mo>≤<!-- ≤ --></mo>
                <mi>i</mi>
                <mo>≤<!-- ≤ --></mo>
                <mi>k</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle 0\leq i\leq k-1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/252522375b741fb617dd857c18886a3ac917d3c4" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.671ex; width:13.449ex; height:2.509ex;" alt="0\leq i\leq k-1"></span> is a <a href="/wiki/Sophie_Germain_prime" title="Sophie Germain prime">Sophie Germain prime</a> and each of the primes <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <msup>
                  <mn>2</mn>
                  <mrow class="MJX-TeXAtom-ORD">
                    <mi>i</mi>
                  </mrow>
                </msup>
                <mi>n</mi>
                <mo>−<!-- − --></mo>
                <mn>1</mn>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle 2^{i}n-1}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/7ad6c75d4bf8c321282c368bad723abe6c3b79ff" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.338ex; width:7.409ex; height:2.676ex;" alt="2^{i}n-1"></span> for <span class="mwe-math-element"><span class="mwe-math-mathml-inline mwe-math-mathml-a11y" style="display: none;"><math xmlns="http://www.w3.org/1998/Math/MathML">
          <semantics>
            <mrow class="MJX-TeXAtom-ORD">
              <mstyle displaystyle="true" scriptlevel="0">
                <mn>1</mn>
                <mo>≤<!-- ≤ --></mo>
                <mi>i</mi>
                <mo>≤<!-- ≤ --></mo>
                <mi>k</mi>
              </mstyle>
            </mrow>
            <annotation encoding="application/x-tex">{\displaystyle 1\leq i\leq k}</annotation>
          </semantics>
        </math></span><img src="https://wikimedia.org/api/rest_v1/media/math/render/svg/83de74da899efbafa01ec98ebf478e9ce5679fc6" class="mwe-math-fallback-image-inline" aria-hidden="true" style="vertical-align: -0.671ex; width:9.425ex; height:2.509ex;" alt="1\leq i\leq k"></span> is a <a href="/wiki/Safe_prime" title="Safe prime">safe prime</a>.</p>
      </div>
    % for i in request.tmpl_context.primelists:
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
