import streamlit as st
import pandas as pd
import numpy as np
from SimulationCalcClass import SimulationCalcClass

import Globals


def app():

    if Globals.INPUT_CSV_DATAFRAME is not None:
        mc_form = st.sidebar.form('Monte Carlo Submit')
        start_col = mc_form.selectbox('Choose Start Status', Globals.INPUT_CSV_DATAFRAME.columns)
        end_col = mc_form.selectbox('Choose End Status', Globals.INPUT_CSV_DATAFRAME.columns)
        hist_duration = mc_form.selectbox('Choose Historical Duration for Monte Carlo', list(Globals.HIST_TIMEFRAME.keys()))
        sim_start_date = mc_form.date_input('Simulation Start Date', value=Globals.SIM_START_DATE)
        sim_end_date = mc_form.date_input('Simulation End Date', value=Globals.SIM_END_DATE)
        items_to_complete = mc_form.number_input('How Many items to complete?', min_value=0, max_value=50, value=20,
                                                    step=1)
        Globals.NUM_SIMULATION_ITERATIONS = mc_form.number_input('How Many iterations to run?', min_value=1000, max_value=50000,
                                                    value=10000,
                                                    step=1000)
        submit_button = mc_form.form_submit_button(label='Run Simulation')

    st.title('Monte Carlo Simulations')
    st.write('Complete the information on the sidebar to see results of a Monte Carlo simulation')

    if Globals.INPUT_CSV_DATAFRAME is not None:
        if submit_button:
            simulator = SimulationCalcClass(hist_duration, start_col, end_col, str(sim_start_date), str(sim_end_date), items_to_complete)
            simulator.prep_for_simulation()
            if not Globals.GOOD_FOR_GO:
                return
            simulator.run_mc_simulations(Globals.NUM_SIMULATION_ITERATIONS)

            st.header('Assumptions made during simulation')
            st.write(simulator.get_monte_carlo_assumptions())

            st.header(f'How Many items will we complete by {sim_end_date}?')
            how_many_results = Globals.HOW_MANY_SIM_OUTPUT.value_counts().to_frame().reset_index()
            how_many_results.columns = ['Count', 'Output']
            how_many_disp_df = pd.DataFrame(how_many_results['Output'], index=how_many_results['Count'])
            st.bar_chart(how_many_disp_df)
            st.bar_chart(Globals.HOW_MANY_PERCENTILES)

            st.header(f'When will we finish {items_to_complete} items?')
            display_df = pd.DataFrame(Globals.WHEN_PERCENTILES['end_date'], index=Globals.WHEN_PERCENTILES.index)
            st.bar_chart(display_df)
