from datetime import date, timedelta
import numpy as np

# shared variables for program
INPUT_CSV_DATAFRAME = None
SPRINT_CSV_FILE_NAME = 'SprintData.csv'
SPRINT_INFO_DATAFRAME = None

HIST_TIMEFRAME = {'All': '9999', 'Last Month': '30',
				  'Last 10 Weeks': '70', 'Last 20 Weeks': '140',
				  'Last 30 Weeks': '210', 'Last 6 Months': '182',
				  'Last Year': 'LY', 'YTD': 'YTD'}
HIST_DURATIONS = ['9999', '30',
				  '70', '140',
				  '210', '182',
				  'LY', 'YTD']

FLOW_METRIC_STATS = None
FLOW_METRIC_START_DATE_KEY = 'Start Date'
FLOW_METRIC_END_DATE_KEY = 'End Date'
FLOW_METRIC_DAYS_KEY = 'Days'
FLOW_METRIC_COMPLETED_ITEMS_KEY = 'Completed Items'
FLOW_METRIC_IP_ITEMS_KEY = 'Still In Progress'
FLOW_METRIC_RESULTS = None
FLOW_METRIC_LEAD_TIME_KEY = 'Avg Lead Time'
FLOW_METRIC_WEEKLY_THROUGHPUT_KEY = 'Weekly Throughput'
FLOW_METRIC_AVG_WIP_KEY = 'Average Daily WIP'
FLOW_METRIC_WIP_VIOLATIONS_KEY = 'Days of WIP Violations'
FLOW_METRIC_WIP_VIOLATIONS_PCT_KEY = '% of Days Violating WIP Limit'
FLOW_METRIC_CATEGORY_COUNT_KEY = 'Count'
FLOW_METRIC_CATEGORY_KEY = 'Category'
FLOW_METRIC_CATEGORIES = np.empty(0)
FLOW_METRIC_CATEGORY_RESULTS = None

DEFAULT_DUR = 70
SIM_START_DATE = date.today()
SIM_END_DATE = date.today() + timedelta(days=DEFAULT_DUR)
NUM_ITEMS_TO_SIMULATE = 0
NUM_SIMULATION_ITERATIONS = 0
FILE_READER = None

GOOD_FOR_GO = False
SIMULATIONS_SUCCESSFUL = False
GLOBAL_ERROR_MSG = ''

HOW_MANY_SIM_OUTPUT = None
HOW_MANY_PERCENTILES = None
WHEN_SIM_OUTPUT = None
WHEN_PERCENTILES = None

PERCENTILES_LIST = np.array([0.95,
							 0.85,
							 0.70,
							 0.50])
