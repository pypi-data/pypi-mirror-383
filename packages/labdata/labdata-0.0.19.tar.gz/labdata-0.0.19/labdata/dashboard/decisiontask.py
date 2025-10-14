import pandas as pd
import streamlit as st
import numpy as np
import altair as alt

def black_label_theme():
    return {
        'config': {
            'axis': {
                'labelColor': 'black',
                'titleColor': 'black'
            },
            'header': {
                'labelColor': 'black',
                'titleColor': 'black'
            }
        }
    }
alt.themes.register('black_labels', black_label_theme)
alt.themes.enable('black_labels')

def decisionmaking_tab(schema = None):
    @st.cache_data
    def get_subjects_last_ran():
        subs = schema.Subject & schema.DecisionTask
        max_date = (subs).aggr(schema.Session,ss='max(session_datetime)').fetch('ss').max().strftime('%Y-%m-%d')
        subjects = (schema.Subject() & (schema.DecisionTask()*schema.Session & f'session_datetime > (DATE("{max_date}") - INTERVAL 3 MONTH)')).fetch(format = 'frame').reset_index()
        subjects = np.unique(subjects.subject_name.values)
        keys = [dict(subject_name = s) for s in subjects]
        return subs.fetch('subject_name'), keys

    @st.cache_data
    def get_summary_data(selected_indices):
        keys = [dict(subject_name = i) for i in selected_indices]
        max_date = schema.Subject.aggr(schema.Session & keys,ss='max(session_datetime)').fetch('ss').max().strftime('%Y-%m-%d')
        ses = (schema.Session()*schema.DecisionTask.TrialSet() & keys & f'session_datetime > (DATE("{max_date}") - INTERVAL 3 MONTH)').proj().fetch(as_dict = True)
    
        from datetime import timedelta
        summarysource = pd.DataFrame((schema.Session*schema.DecisionTask.TrialSet() & keys & 'trialset_description NOT LIKE "%opto%"'
                                    & 'session_datetime > (NOW() - INTERVAL 3 MONTH)').fetch())
        days = np.array([(summarysource.session_datetime.max() - timedelta(days=d)).date() for d in range(40,-2,-1)])
        summarysource['date'] = summarysource.session_datetime.map(
                    lambda x: x.strftime("%y-%m-%d"))
        return summarysource


    all_subjects,subjects = get_subjects_last_ran()
    if not len(subjects):
        st.write('There are no sessions.')
        return
    
    selected_indices = st.multiselect('Select subjects:',all_subjects,default = [s['subject_name'] for s in subjects])
    if len(selected_indices):
        # cache data to run faster
        summarysource = get_summary_data(selected_indices)

        point_selector = alt.selection_point(on="click")
        chart = alt.Chart(summarysource).mark_rect().encode(
            x=alt.X('session_datetime:T',timeUnit = 'yearmonthdate',
                    scale=alt.Scale(nice={'interval': 'day', 'step': 1})).axis(labelAngle=45,format='%Y-%m-%d').title('Date'),  
            y=alt.Y('subject_name:O').title('Subject name'),
                    color=alt.Color('performance_easy:Q',
                    scale=alt.Scale(scheme='spectral', reverse=True,domain = [0.5,1])).title('Perf easy'),
                    tooltip = ['subject_name','session_datetime','performance_easy','performance','n_trials']                 

        ).properties(width=1000, title ='Behavioral performance').add_params(point_selector)
        event_data = st.altair_chart(chart,on_select='rerun')
        
        if len(event_data["selection"]["param_1"]):
            subject_name = event_data["selection"]["param_1"][0]["subject_name"]
            st.write(subject_name)
            
            @st.cache_resource
            def get_subject_data(subject_name):
                trial_sets = pd.DataFrame((schema.DecisionTask.TrialSet*schema.Session & dict(subject_name = subject_name)).fetch())
                weights = pd.DataFrame((schema.Weighing & dict(subject_name = subject_name)).fetch())
                watering = pd.DataFrame((schema.Watering & dict(subject_name = subject_name)).fetch())
                return trial_sets, weights,watering

            trialset,weights,watering = get_subject_data(subject_name)

            
            chart = line_point_plot(trialset,
                            x='session_datetime:T',
                            y='performance_easy:Q',
                            tooltip=['session_datetime', 'performance_easy','performance'],
                            color = 'black',
                            subject_name = subject_name)
            chart2 = line_point_plot(trialset,
                            x='session_datetime:T',
                            y='performance:Q',
                            tooltip=['session_datetime', 'performance_easy','performance'],
                            color = 'red',
                            subject_name = subject_name)

            st.altair_chart(chart+chart2)       
            chartw = line_point_plot(weights,
                            x='weighing_datetime:T',
                            y='weight:Q',
                            tooltip=['weighing_datetime', 'weight'],
                            color = 'orange',
                            subject_name = subject_name)
            st.altair_chart(chartw)
            charth2o = line_point_plot(watering,
                            x='watering_datetime:T',
                            y='water_volume:Q',
                            tooltip=['watering_datetime', 'water_volume'],
                            color = 'cyan',
                            subject_name = subject_name)
            st.altair_chart(charth2o)

def line_point_plot(data,x,y,tooltip,color,subject_name):
    scatter = alt.Chart(data).mark_point(color = color).encode(
                x=alt.X(x,axis=alt.Axis(domain=True)),
                y=alt.Y(y,axis=alt.Axis(domain=True)),
                tooltip=tooltip)
    line = alt.Chart(data).mark_line(color=color).encode(
                x=x,
                y=y,).properties(width=1000, title =f'{subject_name} performance')
    return scatter+line