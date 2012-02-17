<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
        ${self.meta()}

		<title>${self.title()}</title>

		<script src="//ajax.googleapis.com/ajax/libs/webfont/1/webfont.js"></script>
		<script src="${tg.url('/javascript/pre-load.js')}"></script>

        <meta name="viewport" content="width=device-width,initial-scale=1" />

        <link rel="stylesheet" href="${tg.url('/css/style.css')}" />
		<link rel="stylesheet" href="${tg.url('/css/960_fluid_grid.css')}" />

        <script src="${tg.url('/javascript/libs/modernizr-2.0.6.min.js')}"></script>
    </head>
    <body>

    <div id="container" class="container_12">
        <header id="masterheader" class="grid_10 prefix_1 suffix_1">
            ${self.header()}
        </header>
		<div class="clear"></div>

		${self.body()}
		<div class="clear" /></div>

        <footer class="grid_12">
            ${self.footer()}
        </footer>
    </div> <!--! end of #container -->

    </body>
</html>

<%def name="meta()">
  <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
</%def>

<%def name="title()"></%def>

<%def name="header()">
</%def>

<%def name="footer()">
</%def>

<%def name="content_wrapper()">
	${self.body()}
</%def>

