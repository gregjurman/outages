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
<div class="grid_5 prefix_1">
	<div id="outage_stat" class="stats lfloat">
		<span class="num">23</span>
	</div>
	<div id="outage_head_spark" class="lfloat head_spark stats">
		<div id="outage_stats_head">
			<div>
				<span class="head">Current Outages</span>
			</div>
				${outage_chart.display() | n}
		</div>
	</div>
</div>

<div class="grid_5 suffix_1">
	<div id="outage_head_spark" class="head_spark stats ifloat">
		<div id="outage_stats_head">
			<div>
				<span class="head">Affected Customers</span>
			</div>
				${outage_chart.display() | n}
		</div>
	</div>
	<div id="outage_stat" class="stats ifloat">
		<span class="num">2300</span>
	</div>
</div>

<div class="grid_12">&nbsp;</div>
