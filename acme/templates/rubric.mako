# -*- coding: utf-8 -*-
<%def name="body()">

  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <!-- View -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
  <!-- Standard Meta -->
  <link rel="image_src" type="image/png" href="/img/logo.png" />
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <!-- <script type="text/javascript" src="https://www.google.com/jsapi"></script> -->
  <link rel="dns-prefetch" href="//ajax.googleapis.com" />
  <link rel="dns-prefetch" href="//fonts.googleapis.com" />
  <!-- Site Properities -->
  <title>ACME: A Cryptocurrency Metadata Explorer</title>
  <meta name="description" content="ACME: A Cryptocurrency Metadata Explorer" />
  <meta name="keywords" content="acme, block explorer" />
  <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.10/semantic.min.css" type="text/css" />
  <link rel="stylesheet" href="/css/acme.css" type="text/css" />

  <!-- Site Properities -->
  <meta property='og:locale' content='en_UK'/>
  <meta property="og:title" content="ACME">
  <meta property='og:description' content='A Cryptocurrency Metadata Explorer'/>
  <meta property='og:url' content='https://github.com/gjhiggins/acme'/>
  <meta property="og:type" content="article" />
  <meta property="og:image" content="/img/logo${'_testnet' if net == 'test' else ''}.svg" />
  <meta property="og:site_name" content="ACME" />
  <!-- Dublin Core metadata statements -->

  <link rel="shortcut icon" href="/img/favicon${'_testnet' if net == 'test' else ''}.ico">
  <link rel="icon" href="/img/favicon${'_testnet' if net == 'test' else ''}.ico" type="image/x-icon" />
  <meta name="ICBM" content="51.96659,-2.481413" />
  <meta name="Robots" content="index, follow" />
  <link rel="icon" href="/img/favicon${'_testnet' if net == 'test' else ''}.svg" type="image/svg+xml" />

  <!--[if IE]><script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script><![endif]-->

  <!-- For third-generation iPad with high-resolution Retina display: -->
  <link rel="apple-touch-icon-precomposed" sizes="144x144" href="/img/ico/apple-touch-icon-144x144-precomposed.png" />
  <!-- For iPhone with high-resolution Retina display: -->
  <link rel="apple-touch-icon-precomposed" sizes="114x114" href="/img/ico/apple-touch-icon-114x114-precomposed.png" />
  <!-- For first- and second-generation iPad: -->
  <link rel="apple-touch-icon-precomposed" sizes="72x72" href="/img/ico/apple-touch-icon-72x72-precomposed.png" />
  <!-- For non-Retina iPhone, iPod Touch, and Android 2.1+ devices: -->
  <link rel="apple-touch-icon-precomposed" href="/img/assets/ico/apple-touch-icon-57-precomposed.png" />

  <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js" type="text/javascript" ></script>
  <script src="//cdnjs.cloudflare.com/ajax/libs/jquery-migrate/3.0.0/jquery-migrate.min.js" type="text/javascript" ></script>
  <script src="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.10/semantic.min.js" type="text/javascript" ></script>
  <script src="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.10/components/api.min.js" type="text/javascript" ></script>
  <script type="text/javascript" src="https://www.google.com/jsapi"></script>
  <script type="text/javascript" src="/js/humane_dates.js"></script>
  <script type="text/javascript" src="/js/acme.js"></script>
</%def>
