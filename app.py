import streamlit as st 
import plotly.express as px 
import plotly.graph_objects as go 
import pandas as pd 
import os

df=pd.read_excel('District Malaria data for GIS_2020-2022.xls')
def formatIndex(df1):
    df1['S/No.'] = range(1, len(df1) + 1)
    df1 = df1.set_index('S/No.')
    return df1
def case_fatality_uder_five_graph(merged_u5_df,pivot_df):
    Region=[['Ahafo','Ashanti','Bono','Bono East','Central','Eastern',
'Greater Accra','North East','Northern','Oti','Savannah','Upper East','Upper West',
'Volta','Western','Western North']]
# 'Year','Ahafo','Ashanti','Bono','Bono East','Central','Eastern',
# 'Greater Accra','North East','Northern','Oti','Savannah','Upper East','Upper West',
# 'Volta','Western','Western North','CFR National'
    fig=px.bar(merged_u5_df,x='Region',y='CFR',
          color='Year',
          barmode='group',
          title='Malaria Case Fatality Rate(Children under 5),Regions, Half Year 2020 - 2022',
#           text_auto='0.3f'
          )

    fig.update_yaxes(title_text='Case Fatality Rate Per 1000')
    st.plotly_chart(fig,use_container_width=True)
    pivot_df['Year'] = pivot_df['Year'].astype(str)
    pivot_df=formatIndex(pivot_df)
    st.write('Case Fatality Rate Per 1000')
    st.dataframe(pivot_df,use_container_width=True)

def case_fatality_under_five():
    patient_u5_died_region=df.groupby(['Year','Region']).agg({'Patients dying of Malaria,  < 5 years':'sum'}).reset_index()
    patient_u5_admitted_region=df.groupby(['Year','Region']).agg({'Patients admitted with Malaria,  < 5 years':'sum'}).reset_index()
    merged_u5_df = patient_u5_admitted_region.merge(patient_u5_died_region, on=['Year','Region'])
    
    merged_u5_df['CFR']=1000*merged_u5_df['Patients dying of Malaria,  < 5 years']/merged_u5_df['Patients admitted with Malaria,  < 5 years']
    merged_u5_df['CFR']=round(merged_u5_df['CFR'],3).fillna(0.00)
    merged_u5_df['Year']=merged_u5_df['Year'].astype(str)
    
    pivot_df = merged_u5_df.pivot(index='Year', columns='Region', values='CFR')
    pivot_df = pivot_df.reset_index()
    merged_u5_died_national=df.groupby('Year').agg({
    'Patients dying of Malaria,  < 5 years':'sum'}).reset_index()#merged_u5_df['Patients admitted with Malaria,  < 5 years']
    merged_u5_admitted_national=df.groupby('Year').agg({
    'Patients admitted with Malaria,  < 5 years':'sum'}).reset_index()#merged_u5_df['Patients admitted with Malaria,  < 5 years']
    merged_national=merged_u5_admitted_national.merge(merged_u5_died_national,on='Year')
    
    merged_national['CFR National']=100*round(merged_national['Patients dying of Malaria,  < 5 years']/merged_national['Patients admitted with Malaria,  < 5 years'],3)
    # Convert 'Year' column in pivot_df to int64
    pivot_df['Year'] = pivot_df['Year'].astype(int)
    pivot_df=pivot_df.merge(merged_national[['CFR National','Year']],on='Year')
    # st.write(pivot_df.columns)
    return merged_u5_df,pivot_df
    
def case_fatality_all():
    patient_u5_died_region=df.groupby(['Year']).agg({'Patients dying of Malaria,  < 5 years':'sum'}).reset_index()
    patient_u5_admitted_region=df.groupby(['Year']).agg({'Patients admitted with Malaria,  < 5 years':'sum'}).reset_index()
    merged_u5_df = patient_u5_admitted_region.merge(patient_u5_died_region, on=['Year'])
    
    merged_u5_df['CFRU5']=1000*merged_u5_df['Patients dying of Malaria,  < 5 years']/merged_u5_df['Patients admitted with Malaria,  < 5 years']
    merged_u5_df['CFRU5']=round(merged_u5_df['CFRU5'],3).fillna(0.00)
    merged_u5_df['Year']=merged_u5_df['Year'].astype(str)
    cfr_u5=merged_u5_df[['Year','CFRU5']]

    patient_a5_died_region=df.groupby(['Year']).agg({'Patients dying of Malaria,  ≥ 5 years':'sum'}).reset_index()
    patient_a5_admitted_region=df.groupby(['Year']).agg({'Patients admitted with Malaria,  ≥ 5 years':'sum'}).reset_index()
    merged_a5_df = patient_a5_admitted_region.merge(patient_a5_died_region, on=['Year'])
    
    merged_a5_df['CFR']=1000*merged_a5_df['Patients dying of Malaria,  ≥ 5 years']/merged_a5_df['Patients admitted with Malaria,  ≥ 5 years']
    merged_a5_df['CFR']=round(merged_a5_df['CFR'],3).fillna(0.00)
    merged_a5_df['Year']=merged_a5_df['Year'].astype(str)
    cfr_a5=merged_a5_df[['Year','CFR']]

    cfr_u5_a5=cfr_u5.merge(cfr_a5,on='Year')
    df['admitted']=df['Patients admitted with Malaria,  < 5 years']+df['Patients admitted with Malaria,  ≥ 5 years']
    df['died']=df['Patients dying of Malaria,  < 5 years']+df['Patients dying of Malaria,  ≥ 5 years']
    group_admitted=df.groupby(['Year']).agg({'admitted':'sum'}).reset_index()
    group_died=df.groupby(['Year']).agg({'died':'sum'}).reset_index()

    merged_all_df=group_admitted.merge(group_died,on='Year')

    merged_all_df['CFRall']=1000*merged_all_df['died']/merged_all_df['admitted']
    merged_all_df['CFRall']=round(merged_all_df['CFRall'],3).fillna(0.00)
    merged_all_df['Year']=merged_all_df['Year'].astype(str)
    cfr_all=merged_all_df[['Year','CFRall']]

    cfr_all=cfr_u5_a5.merge(cfr_all,on='Year')

    cfr_all=cfr_all.rename(columns={'CFRU5':'< 5 Malaria CFR','CFR':'> 5 Malaria CFR','CFRall':'Malaria CFR'})

    # Reshape the data into a long format
    cfr_all_long = pd.melt(cfr_all, id_vars='Year', var_name='Type', value_name='Value')
    my_title='Malaria Case Fatality Rate for children under 5 years and persons above 5 years per 1000, Half Year 2020 - 2022'
    # Create the line plot
    fig = px.line(cfr_all_long, x='Year', y='Value', color='Type',
                  title=my_title,
                  )
    # set xaxes values to string
    fig.update_xaxes(type='category')
    fig.update_yaxes(title_text='Case Fatality Rate')

    st.plotly_chart(fig,use_container_width=True)
    st.write(my_title)
    cfr_all=formatIndex(cfr_all)
    st.dataframe(cfr_all,use_container_width=True)

def get_admitted_cases():
    df['admitted']=df['Patients admitted with Malaria,  < 5 years']+df['Patients admitted with Malaria,  ≥ 5 years']
    # df['died']=df['Patients dying of Malaria,  < 5 years']+df['Patients dying of Malaria,  ≥ 5 years']
    admitted_df=df.groupby('Year').agg({'admitted':'sum'}).reset_index()
    admitted_df['Year']=admitted_df['Year'].astype(str)
    fig=px.bar(admitted_df,x='Year',y='admitted',
               title='Number of admitted cases attributable to malaria , Ghana, Half Year 2020 - 2022',
               text_auto='0.0f',
               text='admitted'
               )
    # set xaxes values to string
    fig.update_xaxes(type='category')
    # set yaxes title
    fig.update_yaxes(title_text='Number of malaria admissions')
    # set font size
    fig.update_traces(texttemplate='%{text:.0f}', insidetextfont_size=20)  # Format and adjust the font size as needed


    fig.update_xaxes(title_text='Year (Jan - Jun)')
    st.plotly_chart(fig,use_container_width=True)

def get_suspected_cases():
    suspected_df=df.groupby(['Year','Region']).agg({'Uncomplicated Malaria Suspected Tested':'sum'}).reset_index()
    suspected_national_df=suspected_df.groupby(['Year']).agg({'Uncomplicated Malaria Suspected Tested':'sum'}).reset_index()
    pivot_df = suspected_df.pivot(index='Year', columns='Region', values='Uncomplicated Malaria Suspected Tested')
    suspected=pivot_df.merge(suspected_national_df,on='Year')
    suspected=suspected.rename(columns={'Uncomplicated Malaria Suspected Tested':'National'})

    
    fig=px.bar(suspected,x='Year',y=['Ahafo', 'Ashanti', 'Bono', 'Bono East', 'Central', 'Eastern',
       'Greater Accra', 'North East', 'Northern', 'Oti', 'Savannah',
       'Upper East', 'Upper West', 'Volta', 'Western', 'Western North',
       'National'],
           barmode='group',
           title='Proportion of suspected malaria cases tested by Regions, Half Year 2020 - 2022',
           height=600,
          )
    fig.update_xaxes(type='category')
    # set yaxes title
    fig.update_yaxes(title_text='Proportions')
    # set font size
    # fig.update_traces(texttemplate='%{text:.0f}', insidetextfont_size=20)  # Format and adjust the font size as needed

    st.plotly_chart(fig,use_container_width=True)
    suspected['Year']=suspected['Year'].astype(str)
    suspected=formatIndex(suspected)
    st.dataframe(suspected,use_container_width=True)

def get_deaths():
    df['Deaths']=df['Patients dying of Malaria,  < 5 years']+df['Patients dying of Malaria,  ≥ 5 years']
    year_death_df=df.groupby(['Year']).agg({'Deaths':'sum'}).reset_index()
    year_death_df['Year']=year_death_df['Year'].astype(str)
    fig=px.bar(year_death_df,x='Year',y='Deaths',
           barmode='group',
           title='In-patient malaria Death, Ghana, Half Year 2020 - 2022',
        #    height=600,
        text='Deaths',
        # color='Year',

          )
    
    fig.update_xaxes(type='category')
    # set yaxes title
    fig.update_yaxes(title_text='Number of Malaria Deaths')
    # set font size
    fig.update_traces(texttemplate='%{text:.0f}', insidetextfont_size=20)  # Format and adjust the font size as needed
    fig.update_layout(showlegend=False)
    
    st.plotly_chart(fig,use_container_width=True)
   
    year_death_df=formatIndex(year_death_df)
    st.dataframe(year_death_df,use_container_width=True)


cfr, admitted_cases, suspected_cases,death,all_cases = st.tabs(["Casse Fatality Rate", "Admitted Cases", "Suspected Cases",'Deaths','All Cases'])

with cfr:
    merged_u5_df,pivot_df=case_fatality_under_five()
    case_fatality_uder_five_graph(merged_u5_df,pivot_df)
with admitted_cases:
    st.write('Admitted Cases')
    get_admitted_cases()

with suspected_cases:
    st.write('Suspected Cases')
    get_suspected_cases()

with death:
    st.write('Malaria Deaths')
    get_deaths()

with all_cases:
    case_fatality_all()

    

