import streamlit as st
import pandas as pd
import altair as alt
from altair import datum
from datetime import date, timedelta
import Globals
from ChartBuilderClass import ChartBuilderClass


def app():
	# TODO: Make the dataframes for each chart downloadable
	st.title('Charts')

	uploaded_file = st.sidebar.file_uploader("Select Date File", type='csv')
	if uploaded_file is not None:
		Globals.INPUT_CSV_DATAFRAME = Globals.build_date_csv_file(uploaded_file)
	else:
		st.write('Please select a UTF-8 CSV file with "Flow" data to continue.')
		st.subheader('Expected format of CSV File:')
		display_example_csv_dataframe()
		return

	chart_form = st.sidebar.form('Charts Form')
	start_col = chart_form.selectbox('Choose Start Status', Globals.INPUT_CSV_DATAFRAME.columns)
	end_col = chart_form.selectbox('Choose End Status', Globals.INPUT_CSV_DATAFRAME.columns)
	name_col = chart_form.selectbox('Choose Column Containing Item Names', Globals.INPUT_CSV_DATAFRAME.columns)
	daily_wip_limit = chart_form.number_input('Daily WIP limit', min_value=1, max_value=100, value=10,
											  step=1)
	use_start_date = chart_form.checkbox('Check to specify a starting date below:')
	chart_start_date = chart_form.date_input('Data Start Date', value=date.today() - timedelta(days=90))
	chart_end_date = chart_form.date_input('Data End Date', value=date.today())

	submit_button = chart_form.form_submit_button(label='Build Charts')

	if not submit_button:
		st.write('Complete the form on the sidebar to view charts.')
		return

	if start_col == end_col:
		st.write('Please make sure the Start and End Status Columns are different')
		return

	if use_start_date:
		if chart_start_date > chart_end_date:
			st.write('Start Date must be less than or equal to End Date')
			return

	# This markdown fixes the tooltip overlay for charts when you go to full screen mode.
	st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',
				unsafe_allow_html=True)

	# =========================================
	# Build Chart Data
	# =========================================
	chart_builder = ChartBuilderClass(start_col, end_col, name_col, use_start_date, str(chart_start_date),
									  str(chart_end_date), daily_wip_limit)
	chart_builder.prep_for_charting()
	if chart_builder.prep_errors_were_found():
		st.subheader('Errors were found when preparing to Chart data:')
		st.write(chart_builder.get_errors())
		return

	chart_builder.build_charts()
	if chart_builder.build_errors_were_found():
		st.subheader('Errors were found while creating Charts:')
		st.write(chart_builder.get_errors())
		return

	st.subheader('Assumptions from building Charts:')
	st.write(chart_builder.get_assumptions())
	st.subheader('Helpful tips for reading Charts:')
	st.write(build_helpful_tips())

	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """,
				unsafe_allow_html=True)

	st.header('Raw reference Data:')
	st.write(chart_builder.get_clean_df())

	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

	# =========================================
	# Flow and In-Progress Charts
	# =========================================
	# ===== CUMULATIVE FLOW DIAGRAM (CFD) =====
	build_cfd_chart(chart_builder)
	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

	# ===== AGING WIP =====
	build_aging_wip(chart_builder)
	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

	# ===== WIP RUN CHART =====
	build_wip_run_chart(chart_builder)
	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

	# =========================================
	# Throughput Charts
	# =========================================
	# ===== THROUGHPUT HISTOGRAM =====
	build_throughput_histogram(chart_builder)
	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

	# ===== THROUGHPUT RUN CHART =====
	build_throughput_run_chart(chart_builder)
	build_monthly_velocity_chart(chart_builder)
	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

	# =========================================
	# Cycle Time Charts
	# =========================================
	# ===== CYCLE TIME HISTOGRAM =====
	build_cycle_time_histogram(chart_builder)

	# Horizontal Separator
	st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """,
				unsafe_allow_html=True)

	# ===== CYCLE TIME SCATTERPLOT =====
	build_cycle_time_scatterplot(chart_builder)


# =========================================
# Internal Functions
# =========================================
def build_helpful_tips():
	tips_list = [['Red dashed lines = 85% confidence level'], ['Green dashed lines = 50% confidence level'],
				 ['Black dashed lines = Average of data'],
				 ['Click the "View Full screen" arrows at the right side of any chart to see it in full-screen'],
				 ['Dataframes have been included below charts to show you the raw data']]
	return pd.DataFrame(tips_list, columns=['Tips'])


def display_example_csv_dataframe():
	st.write('You can as many date columns as your process needs, but they must be sequential and grouped together '
			 '(no other columns between date columns).')
	st.write('You can also add additional columns for grouping or naming')
	st.write('Cancelled items should be denoted with either a "Cancelled" column, or a "Resolution" column (Jira Export) '
			 'which has "Yes" or "Cancelled" for the applicable rows.')
	example_df = pd.DataFrame([['Name of item', 'Ready Date (YYYY-MM-DD)', 'In Progress Date (YYYY-MM-DD)',
								'Done Date (YYYY-MM-DD)', '"Yes" or "Cancelled" to exclude', 'Category Name'],
							   ['Improve Sales','2021-11-15', '2021-12-15', '2022-01-15', '', 'Strategic'],
							   ['Decrease Call Return Time', '2021-05-27', '2021-06-20', '2021-07-15', 'Yes', 'Maintenance']],
							  columns=['Name','Ready', 'In Progress', 'Done', 'Cancelled', 'Grouping'])
	st.write(example_df)


def build_cfd_chart(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			A Cumulative Flow Diagram is a visual representation of the three basic metrics of flow: WIP, Cycle Time, and
			Throughput (through averages or approximate averages). A CFD should adhere to the following six properties \n
			1: The top line always represents the cumulative arrivals to a process. The bottom line always represents 
			cumulative departures from a process \n
			2: Due to the cumulative nature, no line on a CFD can ever decrease (go down). \n
			3: The vertical distance between any two lines is the total amount of work that is in progress between the 
			two workflow steps represented by the two chosen lines. \n
			4: The horizontal distance between any two lines on a CFD represents the Approximate Average Cycle Time 
			for items that finished between the two workflow steps represented by the chosen two lines. \n
			5: The data displayed on a CFD depicts only what has happened for a given process, not a projection of what 
			will happen. \n
			6: The slope of any line between any two reporting intervals on a CFD represents the exact 
			Average Arrival Rate of the process state represented by the succeeding band. \n
			To read more on how Cumulative Flow Diagrams can be utilized, check out
			"Actionable Agile Metrics for Predictability" by Dan Vacanti. A summary of the CFD section can be found here:
			https://tameflow.com/blog/2015-03-12/actionable-agile-metrics-review-part-4/
		""")
	cfd_df = chart_builder.get_cfd_df()
	cfd_columns = cfd_df.columns.tolist()
	cfd_chart = alt.Chart(cfd_df, title='Cumulative Flow Diagram (CFD)').transform_fold(
		chart_builder.get_date_column_list(), as_=['Status', 'Count'])
	cfd_lines = cfd_chart.mark_area(opacity=0.75).encode(
		x=alt.X('Date:T', title='Date'),
		y=alt.Y('Count:Q', stack=None),
		color=alt.Color('Status:N', legend=alt.Legend(title='Categories')),
		tooltip=cfd_columns
	).interactive()
	# The basic line for real-time labels of the different phases
	ref_line = cfd_chart.mark_line(interpolate='basis').encode(
		x='Date:T',
		y='Count:Q'
	)
	# Create a selection that chooses the nearest point & selects based on x-value or y-value
	nearest_x = alt.selection(type='single', nearest=True, on='mouseover',
							fields=['Date'], empty='none')
	nearest_y = alt.selection(type='single', nearest=True, on='mouseover',
							  fields=['Count'], empty='none')
	# Transparent selectors across the chart. This is what tells us the x-value or y-value of the cursor
	selectors_x = cfd_chart.mark_point().encode(
		x='Date:T',
		opacity=alt.value(0),
	).add_selection(
		nearest_x
	)
	selectors_y = cfd_chart.mark_point().encode(
		y='Count:Q',
		opacity=alt.value(0),
	).add_selection(
		nearest_y
	)
	# Draw points on the line, and highlight based on selection
	points_x = ref_line.mark_point().encode(
		opacity=alt.condition(nearest_x, alt.value(10), alt.value(0)),
		color='Status:N'
	)
	points_y = ref_line.mark_point().encode(
		opacity=alt.condition(nearest_y, alt.value(10), alt.value(0)),
		color='Status:N'
	)
	# Draw text labels near the points, and highlight based on selection
	text_x = ref_line.mark_text(align='left', dx=5, dy=-5, color='black').encode(
		text=alt.condition(nearest_x, 'Count:Q', alt.value(' '))
	)
	text_y = ref_line.mark_text(align='left', dx=5, dy=-5, color='black').encode(
		text=alt.condition(nearest_y, 'Date:T', alt.value(' '))
	)

	# Draw a rule at the location of the selection
	rules_x = cfd_chart.mark_rule(color='gray').encode(
		x='Date:T',
	).transform_filter(
		nearest_x
	)
	rules_y = cfd_chart.mark_rule(color='gray').encode(
		y='Count:Q',
	).transform_filter(
		nearest_y
	)
	st.altair_chart(cfd_lines + selectors_x + points_x + text_x + rules_x)

	# Build the vectors chart
	cfd_vectors = alt.Chart(chart_builder.get_cfd_vectors(), title='CFD Status Trajectory').mark_line().encode(
		x=alt.X('Date:T', title='Date'),
		y=alt.Y('Count:Q', title='Trajectory'),
		color=alt.Color('Status:N')
	).interactive()

	st.altair_chart(cfd_vectors)
	# TODO: Enhance CFD Stats
	# show_cfd_stats = st.checkbox('Show CFD Stats')
	st.write(chart_builder.get_cfd_df())


def build_cfd_stats(chart_builder: ChartBuilderClass):
	# TODO: Build actual average throughput for each phase with rise/run calc for each column.
	# TODO: Give a inclination of Flow Debt status.
	# Can we build in something that takes a few samples of approx. avg cycle time? Use that against actual avg.
	# cycle time to see if we are generally incurring, paying back, or not realizing flow debt.
	pass


def build_aging_wip(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			This Aging WIP diagram shows the 85th (red) and 50th (green) percentiles for completed items, 
			as well as the age of all In Progress items. 
			Use this to gauge if the work currently in progress is on track to complete in a timely manner, 
			or if it may be headed towards a long cycle time. 
			The older an item gets, the higher it's probability that it will continue to get older. 
			Hover over any dot on the chart to see more details of where the time has been spent for each item.
			""")
	aging_df = chart_builder.get_aging_wip_df()
	# remove done items
	in_progress_mask = (aging_df['Status'] != chart_builder.get_end_column_name())
	aging_df = aging_df.loc[in_progress_mask]
	aging_df.reset_index(drop=True, inplace=True)
	aging_columns = aging_df.columns.tolist()
	aging_columns.remove('Done_Date')

	cycle_time_85_confidence = int(aging_df.loc[0, 'CycleTime85'])
	cycle_time_50_confidence = int(aging_df.loc[0, 'CycleTime50'])
	st.write(f'Some interesting facts: \n'
			 f'85% of items have finished within {cycle_time_85_confidence} days.\n'
			 f'If an item reaches {cycle_time_50_confidence} days old, it now has a 30% chance of being longer than '
			 f'{cycle_time_85_confidence} total days to delivery. Does that cause any concern?')

	aging_chart = alt.Chart(aging_df, title="Aging WIP")
	aging_wip = aging_chart.mark_circle(size=100).encode(
		x=alt.X('Status', title='Status'),
		y=alt.Y('Age', title='Age'),
		color='Status',
		tooltip=aging_columns
	).interactive()
	cycle_time_85_confidence_y = aging_chart.mark_rule(strokeDash=[12, 6], size=2, color='red').encode(
		y='CycleTime85:Q'
	)
	cycle_time_50_confidence_y = aging_chart.mark_rule(strokeDash=[12, 6], size=2, color='green').encode(
		y='CycleTime50:Q'
	)
	cycle_time_average_y = aging_chart.mark_rule(strokeDash=[12, 6], size=2, color='black').encode(
		y='CycleTimeAvg:Q'
	)
	label_85 = aging_chart.mark_text(align='right', baseline='bottom', dx=40, color='red').encode(
		alt.X('Status', aggregate='max'),
		alt.Y('CycleTime85:Q'),
		alt.Text('CycleTime85:Q')
	)
	label_50 = aging_chart.mark_text(align='right', baseline='bottom', dx=60, color='green').encode(
		alt.X('Status', aggregate='max'),
		alt.Y('CycleTime50:Q'),
		alt.Text('CycleTime50:Q')
	)
	label_avg = aging_chart.mark_text(align='right', baseline='bottom', dx=40, color='black').encode(
		alt.X('Status', aggregate='max'),
		alt.Y('CycleTimeAvg:Q'),
		alt.Text('CycleTimeAvg:Q')
	)
	st.altair_chart(aging_wip + cycle_time_85_confidence_y + cycle_time_50_confidence_y + cycle_time_average_y +
					label_85 + label_50 + label_avg, use_container_width=True)
	# TODO: Enhance Aging WIP Stats
	st.write(chart_builder.get_aging_wip_df())


def build_wip_run_chart(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			The WIP Run Chart shows the number of items in progress each day. \n
			- Is the number of items in progress consistent, or moving up/down?\n
			- How many days are the items above the WIP limit (blue line)?\n
			- The less adherence to a WIP limit, the less predictable delivery can be.
			""")

	wip_run_chart = alt.Chart(chart_builder.get_run_df(), title="WIP Run Chart")
	wip_line = wip_run_chart.mark_line(point=alt.OverlayMarkDef(color="red")).encode(
		x=alt.X('Date:T', title='Date'),
		y=alt.Y('WIP:Q', title='WIP'),
		tooltip=['Date', 'WIP']
	).interactive()
	average_wip = wip_run_chart.mark_line(color='black').transform_window(
		rolling_mean='mean(WIP)',
		frame=[-30, 30],
		groupby=['WIPLimit']
	).encode(
		x='Date:T',
		y='rolling_mean:Q'
	)
	wip_limit = wip_run_chart.mark_rule(strokeDash=[12, 6], size=2, color='blue').encode(
		y='WIPLimit:Q'
	)
	label_wip = wip_run_chart.mark_text(align='right', baseline='bottom', dx=-20, color='black').encode(
		alt.X('Date:T', aggregate='max'),
		alt.Y('WIPLimit:Q'),
		alt.Text('WIPLimit:Q')
	)
	st.altair_chart(wip_line + wip_limit + label_wip + average_wip)
	# TODO: Enhance WIP Run Stats
	st.write(chart_builder.get_run_df())


def build_throughput_histogram(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			The Throughput Histogram is a representation of how many times a particular number of items were completed 
			on a single day. One reason a histogram is helpful is that it shows the distribution of throughput for 
			forecast modeling (use the Monte Carlo option at the top of this page).\n
			- Do you see any trends in the number of items that can be delivered in one day?\n
			- Do you think that should be higher or lower?
			""")
	throughput_hist_graph = alt.Chart(chart_builder.get_throughput_hist_df(), title="Throughput Histogram")
	bar_graph = throughput_hist_graph.mark_bar(size=40).encode(
		x=alt.X('Throughput:Q', title='Throughput'),
		y=alt.Y('Count:Q', title='Count'),
		tooltip=['Throughput', 'Count']
	).interactive()
	throughput_85_confidence = throughput_hist_graph.mark_rule(strokeDash=[12, 6], size=2, color='red').encode(
		x='Throughput85:Q'
	)
	throughput_50_confidence = throughput_hist_graph.mark_rule(strokeDash=[12, 6], size=2, color='green').encode(
		x='Throughput50:Q'
	)
	throughput_avg = throughput_hist_graph.mark_rule(strokeDash=[12, 6], size=2, color='black').encode(
		x='ThroughputAvg:Q'
	)
	throughput_hist_label_85 = throughput_hist_graph.mark_text(align='right', baseline='top', dx=-20,
															   color='red').encode(
		alt.X('Throughput85:Q'),
		alt.Y('Count:Q', aggregate='mean'),
		alt.Text('Throughput85:Q')
	)
	throughput_hist_label_50 = throughput_hist_graph.mark_text(align='right', baseline='top', dx=-20,
															   color='green').encode(
		alt.X('Throughput50:Q'),
		alt.Y('Count:Q', aggregate='mean'),
		alt.Text('Throughput50:Q')
	)
	throughput_hist_label_avg = throughput_hist_graph.mark_text(align='right', baseline='top', dx=-20,
																color='black').encode(
		alt.X('ThroughputAvg:Q'),
		alt.Y('Count:Q', aggregate='mean'),
		alt.Text('ThroughputAvg:Q')
	)
	st.altair_chart(bar_graph + throughput_85_confidence + throughput_50_confidence + throughput_avg +
					throughput_hist_label_85 + throughput_hist_label_50 + throughput_hist_label_avg)
	# TODO: Enhance Throughput Run Stats
	st.write(chart_builder.get_throughput_hist_df())


def build_throughput_run_chart(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			The Throughput Run Chart shows how many items were completed each day within the given date range.
			This is helpful to see possible trends in delivery.\n
			- Do you see any trends for when you are delivering value?\n
			- Are you batching work when it could be delivered more frequently?\n
			- Are there any gaps in delivery that should be discussed?
			""")
	throughput_run_chart = alt.Chart(chart_builder.get_run_df(), title="Throughput Run Chart")
	throughput_line = throughput_run_chart.mark_line(point=alt.OverlayMarkDef(color="red")).encode(
		x='Date:T',
		y='Throughput:Q',
		tooltip=['Date', 'Throughput']
	).interactive()

	rolling_avg = throughput_run_chart.mark_line(color='black').transform_window(
		rolling_mean='mean(Throughput)',
		frame=[-30, 0],
		groupby=['WIPLimit']
	).encode(
		x='Date:T',
		y='rolling_mean:Q'
	)

	st.altair_chart(throughput_line + rolling_avg)


def build_monthly_velocity_chart(chart_builder: ChartBuilderClass):
	base_chart_data = chart_builder.get_run_df()
	# calculate average monthly velocity
	total_completed = sum(base_chart_data['Throughput'])
	max_date = base_chart_data['Date'].max()
	min_date = base_chart_data['Date'].min()
	num_months = ((max_date.year - min_date.year) * 12) + (max_date.month - min_date.month)
	avg_monthly_velocity = round(total_completed / num_months, 2)
	base_chart_data['MonthlyVelocity'] = avg_monthly_velocity

	st.write('The Monthly Velocity Chart can show how the above throughput run chart translates to a monthly pattern. '
			 'Are there any trends which would indicate a need for change of behaviors in delivery?')

	velocity_chart = alt.Chart(base_chart_data, title="Monthly Velocity Chart")
	bar_graph = velocity_chart.mark_bar().encode(
		x=alt.X('yearmonth(Date):T', title='Date'),
		y=alt.Y('sum(Throughput):Q', title='Count'),
		tooltip=['sum(Throughput)', 'yearmonth(Date)']
	).interactive()
	velocity_avg_y = velocity_chart.mark_rule(strokeDash=[12, 6], size=2, color='black').encode(
		y='MonthlyVelocity:Q'
	)
	velocity_avg_label = velocity_chart.mark_text(align='left', baseline='bottom', dx=10, color='black', clip=False).encode(
		alt.X('Date:T', aggregate='max'),
		alt.Y('MonthlyVelocity:Q'),
		alt.Text('MonthlyVelocity:Q')
	)
	st.altair_chart(bar_graph + velocity_avg_y + velocity_avg_label)
	# TODO: Create Enhance Run Stats
	st.write(chart_builder.get_run_df())


def build_cycle_time_histogram(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			The Cycle Time Histogram is a representation of how many times items have had a particular cycle time 
			when completed. One reason a histogram is helpful is that it shows the frequency of different 
			cycle times for forecast modeling (use the Monte Carlo option at the top of this page).\n
			- Do you see any trends in cycle time of items?\n
			- What would it take to make these cycle times lower?
			""")
	cycle_time_hist_graph = alt.Chart(chart_builder.get_cycle_time_hist_df(), title="Cycle Time Histogram")
	bar_graph = cycle_time_hist_graph.mark_bar(size=4).encode(
		x=alt.X('Age:Q', title='Age'),
		y=alt.Y('Count:Q', title='Count'),
		tooltip=['Age', 'Count']
	).interactive()
	cycle_time_85_confidence = cycle_time_hist_graph.mark_rule(strokeDash=[12, 6], size=2, color='red').encode(
		x='CycleTime85:Q'
	)
	cycle_time_50_confidence = cycle_time_hist_graph.mark_rule(strokeDash=[12, 6], size=2, color='green').encode(
		x='CycleTime50:Q'
	)
	cycle_time_avg = cycle_time_hist_graph.mark_rule(strokeDash=[12, 6], size=2, color='black').encode(
		x='CycleTimeAvg:Q'
	)
	cycle_time_hist_label_85 = cycle_time_hist_graph.mark_text(align='right', baseline='top', dx=-20,
															   color='red').encode(
		alt.X('CycleTime85:Q'),
		alt.Y('Count:Q', aggregate='mean'),
		alt.Text('CycleTime85:Q')
	)
	cycle_time_hist_label_50 = cycle_time_hist_graph.mark_text(align='right', baseline='top', dx=-20,
															   color='green').encode(
		alt.X('CycleTime50:Q'),
		alt.Y('Count:Q', aggregate='mean'),
		alt.Text('CycleTime50:Q')
	)
	cycle_time_hist_label_avg = cycle_time_hist_graph.mark_text(align='right', baseline='top', dx=-20,
																color='black').encode(
		alt.X('CycleTimeAvg:Q'),
		alt.Y('Count:Q', aggregate='mean'),
		alt.Text('CycleTimeAvg:Q')
	)
	st.altair_chart(bar_graph + cycle_time_85_confidence + cycle_time_50_confidence + cycle_time_avg +
					cycle_time_hist_label_85 + cycle_time_hist_label_50 + cycle_time_hist_label_avg)
	# TODO: Enhance Cycle Time Histogram Stats
	st.write(chart_builder.get_cycle_time_hist_df())

# WIP
def build_cycle_time_scatterplot(chart_builder: ChartBuilderClass):
	st.header("How do I use this chart?")
	st.write("""
			The Cycle Time Scatterplot is a visual representation of cycle time for items that completed on any given day. \n
			The Orange LINE represents the Cycle Time of 85% of items. 
			The Blue LINE represents the Cycle Time of 50% of items.
			The Red LINE represents the average Cycle Time of all completed items.
			The Black LINE represents a rolling 30 day average cycle time to help see if there are trends over time. \n
			- Do you see any outliers with long Cycle Time which should be discussed?\n
			- Do you see any trends or shapes with the delivery of items (ex. an upwards ramp indicates that the Cycle Time
			is slowly getting longer as you progress through time.)\n
			- Are there any gaps in delivery that should be discussed?
			""")
	scatter_df = chart_builder.get_cycle_time_scatter_df()
	scatter_columns = scatter_df.columns.tolist()
	cycle_scatter_chart = alt.Chart(scatter_df, title="Cycle Time Scatterplot")
	scatter_plot = cycle_scatter_chart.mark_circle(size=100).encode(
		x=alt.X('Done_Date:T', title='Completed Date'),
		y=alt.Y('Age:Q', title='Age'),
		tooltip=scatter_columns
	).interactive()
	cycle_time_percentiles = cycle_scatter_chart.mark_rule(strokeDash=[12, 6], size=2).transform_fold(
		fold=['CycleTime85', 'CycleTime50', 'CycleTimeAvg'],
		as_=['percentile', 'value']
	).encode(
		y='value:Q',
		color='percentile:N'
	)
	label_85 = cycle_scatter_chart.mark_text(align='left', baseline='bottom', dx=10, clip=False, size=15).encode(
		alt.X('Done_Date:T', aggregate='max'),
		alt.Y('CycleTime85:Q'),
		alt.Text('eightFiveLabel:N')
	).transform_calculate(
		eightFiveLabel=alt.datum.CycleTime85 + ' days'
	)
	label_50 = cycle_scatter_chart.mark_text(align='left', baseline='bottom', dx=10, clip=False, size=15).encode(
		alt.X('Done_Date:T', aggregate='max'),
		alt.Y('CycleTime50:Q'),
		alt.Text('fiftyLabel:N')
	).transform_calculate(
		fiftyLabel=alt.datum.CycleTime50 + ' days'
	)
	label_avg = cycle_scatter_chart.mark_text(align='left', baseline='bottom', dx=10, clip=False, size=15).encode(
		alt.X('Done_Date:T', aggregate='max'),
		alt.Y('CycleTimeAvg:Q'),
		alt.Text('avgLabel:N')
	).transform_calculate(
		avgLabel=alt.datum.CycleTimeAvg + ' days'
	)

	rolling_avg = cycle_scatter_chart.mark_line(color='black').transform_window(
		rolling_mean='mean(Age)',
		frame=[-30, 0],
		groupby=['CycleTimeAvg']
	).encode(
		x='Done_Date:T',
		y='rolling_mean:Q'
	)

	st.altair_chart(scatter_plot + cycle_time_percentiles + label_85 + label_50 + label_avg + rolling_avg,
					use_container_width=True)

	st.subheader('Insights')
	cycleTime50 = int(round(scatter_df['CycleTime50'].iloc[0], 0))
	cycleTime85 = int(round(scatter_df['CycleTime85'].iloc[0], 0))
	percentileDiff = cycleTime85 - cycleTime50
	future50Date = date.today() + timedelta(days=cycleTime50)
	future85Date = date.today() + timedelta(days=cycleTime85)
	pastPercentileDate = date.today() - timedelta(days=percentileDiff)
	st.write(f'50% of items were completed in {cycleTime50} days. '
			 f'85%  of items were completed in {cycleTime85} days.')
	st.write(f'This means, if you started an item today ({date.today().strftime("%B %d, %Y")}), '
			 f'you would have a 50/50 chance of getting it done by '
			 f'{future50Date.strftime("%B %d, %Y")} and a high confidence chance (85%) of getting it done by '
			 f'{future85Date.strftime("%B %d, %Y")}.')
	st.write(f'The difference between a flip of a coin chance (50%) and high confidence (85%) is {percentileDiff} days. '
			 f'To put this in perspective, {percentileDiff} days ago was {pastPercentileDate.strftime("%B %d, %Y")}. '
			 f'What were you doing on {pastPercentileDate.strftime("%B %d, %Y")}?')
	st.subheader('Raw Data')
	st.write(scatter_df)
