<%inherit file="local:templates.master"/>

<%def name="header()">
<h1>RG&E - Current Outages</h1>
</%def>

<%def name="title()">
  RG&E Current Outages - Map
</%def>

<div id="main" class="stats grid_10 prefix_1 suffix_1" role="main">
	${outage_map.display() | n}
</div>
<div class="grid_6 prefix_1">
	<div class="container_12">
		<div id="outage_stats_head" class="stats grid_6" role="stats">
			<h2>Current Outages</h2>
		</div>
		<div id="affected_stats_head" class="stats grid_6" role="stats">
			<h2>Affected Customers</h2>
		</div>

		<div id="outage_stats" class="stats grid_6" role="stats">
			<h3>21</h3>
		</div>
		<div id="affected_stats" class="stats grid_6" role="stats">
			<h3>200</h3>
		</div>
	</div>
</div>

<div class="grid_4 suffix_1">
<h1>Herp, sparkline</h1>
</div>
