import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from plotly.subplots import make_subplots

### Config
st.set_page_config(
    page_title="getaround",
    page_icon="🚗 ",
    layout="wide"
)

DATA_URL = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')

### App
# Create a function to load datas from an URL
def load_data():
    df = pd.read_excel(DATA_URL)
    return df

df=load_data()

## Let's define all the variables and dataframe that we need for our visualization

# proportion of ended / canceled rentals
states= df.state.value_counts()

# How many cars / rentals are concerned
nb_cars=len(df['car_id'].unique())
rentals = len(df['rental_id'].unique())

# Let' calculate the average delay
mean_delay= round(df.delay_at_checkout_in_minutes.mean(),3)
# Average delay by device
mean_delay_mobile=round(df[df["checkin_type"]=='mobile']["delay_at_checkout_in_minutes"].mean(),3)
mean_delay_connect=round(df[df["checkin_type"]=='connect']["delay_at_checkout_in_minutes"].mean(),3)

#Let's create a column that indicated if a rental is late or not
df['delay'] = df['delay_at_checkout_in_minutes'].apply(lambda x: 'late' if x > 0 else 'in time')
df['delta']=  df["time_delta_with_previous_rental_in_minutes"].isna().apply(lambda x: x if x == False else '> 720 minutes')

# Proportion of late vs in time checkouts
checkout_states= df.delay.value_counts()

# Checking type repartition
checkin_types= df.checkin_type.value_counts()

# we focus on time delta with previous rentals
delta=df.delta.value_counts()
mask=df[df['delta']!= '> 720 minutes']
time_delta=mask.time_delta_with_previous_rental_in_minutes.value_counts()

# We create a "cleaned" dataframe delating the null values for dalays at checkout and we count how differents values of this feature we have
df_clean = df[df["delay_at_checkout_in_minutes"].isna() == False]
delays=df_clean.delay.value_counts()

# we keep only rentals with delay at checkout of previous rental between -12h (early checkout) and +12h (late checkout)
# we consider as outlier the checkout delays out of this range
checkout_in_range = df[(df.delay_at_checkout_in_minutes > -720) & (df.delay_at_checkout_in_minutes < 720)]

# we keep only rentals with time delta with previous rental between -12h  and +12h 
# we consider as outlier the time delta out of this range
time_delta_in_range = df[(df.delay_at_checkout_in_minutes > -720) & (df.delay_at_checkout_in_minutes < 720)]

# Create a dataframe with canceled rentals
df_canceled=df[df["state"]=='canceled'].copy()

# we focus on delta with previous rentals for canceled rentals
delta_for_canceled= df_canceled.delta.value_counts()
mask=df_canceled[df_canceled['delta']!= '> 720 minutes'] # we create a dataframe to keep only delta different from the ordinary delta of >720min
time_delta_for_canceled= mask.time_delta_with_previous_rental_in_minutes.value_counts()

#I focus on Canceled Rentals 
#I keep canceled rentals, I create a dataframe with previous rental id as rental id and I merge to have canceled rentals and delay at checkout 
#of previous rental on the same line


# We create a mask to keep only the rows with revious ended rental id not null
clean_df_canceled=df_canceled[df_canceled[['previous_ended_rental_id']].notna().all(axis=1)]

# Create a list of the column time delta
previous_id=clean_df_canceled["previous_ended_rental_id"]

# Create dataframe with previous rentals in this list
df_previous_rentals = df[df["rental_id"].isin(previous_id)]

#we merge our previous rental dataframe with next rental dataframe
df_merged = df_previous_rentals.merge(df, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')
# Drop useless columns
df_merged.drop(['state_x', 'previous_ended_rental_id_x','previous_ended_rental_id_y', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)

# ratio of checkin type for cancelation
cancelations_checkin_device = df_merged['checkin_type_x'].value_counts()

# Proportion of delayed previous rentals
data_canceled_prev_delay = df_merged['delay_x'].value_counts()

# Canceled rentals with previous rental late
df_merged_canceled=df_merged[df_merged['state_y'] == "canceled"].copy().reset_index()

df_canceled_PrevLate=df_merged_canceled[df_merged_canceled["delay_at_checkout_in_minutes_x"]>0].copy().reset_index()

# We need to calculate the sum of the columns time delta and delay at checkout to calculate their ratio
delay_at_checkout_sum=df_canceled_PrevLate['delay_at_checkout_in_minutes_x'].sum()
time_delta_sum= df_canceled_PrevLate['time_delta_with_previous_rental_in_minutes_y'].sum()
ratioDelayDelta= delay_at_checkout_sum/time_delta_sum

# Now let's calculate the Time delta average between twe rentals 
mean_TimeDelta = round(df_canceled_PrevLate['time_delta_with_previous_rental_in_minutes_y'].mean(), 0)
# We can determine the threshold using this ratio * the late delays mean
threshold = round(ratioDelayDelta * mean_TimeDelta, 0)

treshold_delay = df_canceled_PrevLate["delay_at_checkout_in_minutes_x"].mean()

#Let's get back to all datas to see the impact of our threshold

# Create dataframe with all the previous rental id not null  
prev_rentals = df[df[['previous_ended_rental_id']].notna().all(axis=1)]
# Extract all the previous rental ids as a list
prev_rental_id = prev_rentals["previous_ended_rental_id"]
# Create dataframe with these previous rentals id as main "rental_id" 
df_prev_rentals = df[df["rental_id"].isin(prev_rental_id)]

# Merge the main dataframe df with previous rentals dataframe in order to have all the informations about previous rentals on the same row 
all_data = df_prev_rentals.merge(df, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')
#drop useless columns
all_data.drop(['state_x', 'previous_ended_rental_id_x','previous_ended_rental_id_y', 'time_delta_with_previous_rental_in_minutes_x', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)
# Create a mask of the dataframe with only ended rentals
rentals_ended = all_data[all_data["state_y"] == "ended"].copy()

# We add a column to indicate if the ended rental has a time delta with the previous one > or < our threshold
rentals_ended["over or under threshold"]= rentals_ended['time_delta_with_previous_rental_in_minutes_y'].apply(lambda x: 'over' if x > 130 else 'under') 

# Define how many rentals are affected by treshold
rentals_under= rentals_ended[rentals_ended["over or under threshold"]=="under"].reset_index().copy()
affected_rentals=len(rentals_ended) - len(rentals_ended[rentals_ended["over or under threshold"]=="under"])

# Define the loss by owner, regarding the datas we have a car id so we can evaluate a loss by car
rentals_under.car_id_y= rentals_under.car_id_y.apply(lambda x: str(x)) #To display a graph later we need to convert this variable to string rather than continious variable
loss_by_car= rentals_under.groupby(['car_id_y'])["car_id_y"].count().sort_values(ascending=False).rename_axis('Car Id').reset_index(name='Lost rentals')

# Create ratio of lost and sucessful rentals
ratio_status = [(len(rentals_under)*100)/len(rentals_ended), 100-(len(rentals_under)*100)/len(rentals_ended)]
# Define graph objects pie chart lables and values
labels = ['Sucessful rentals', ' Lost rentals']
values = ratio_status

#streamlit vizualisaitons
image = Image.open('logo.jpg')

col1, col2, col3 = st.columns(3)

with col1:
    st.write(" ")

with col2:
    st.image("logo.jpg", width=300 )

with col3:
    st.write(" ")


st.markdown("""<h1 style='text-align: left; color: white;}'>Dashbord </h1>""", unsafe_allow_html=True)


st.subheader("🚗 General information")

st.subheader("How many cars / rentals are concerned?")
st.text(f'There are {nb_cars} vehicles in this dataset')

st.subheader("Proportion of ended / canceled rentals")
st.text(f'There are {rentals} rentals in this dataset')

st.subheader("The average delay at checkout")
st.text(f'The average delay at checkout is {mean_delay} minutes')

st.subheader("The average delay at checkout per device")
st.text(f'For mobile checkings the average delay at checkout is: {mean_delay_mobile} minutes')
st.text(f'For connect checkings the average delay at checkout is: {mean_delay_connect} minutes')

st.markdown("****")

st.subheader("🚗 Vizualisations")

col1, col2=st.columns(2)

with col1:

    fig_1 = go.Figure(data=[go.Pie(labels=states.index,values=states.values, pull=[0.2, 0])])
    fig_1.update_layout(template='plotly_dark',
    title={

            'text': "1 - Rental states repartition ",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            font=dict(
            family="arial",
            size=18,
            color="white"),
            width=600, height=400,)
        
    st.plotly_chart(fig_1)

with col2:
    fig_2 = px.pie(delays,
                values=delays.values,
                names=delays.index, 
                color ='delay',
                color_discrete_map={'late':'lightgreen',
                                    'in time':'lightblue'})

    fig_2.update_layout(template='plotly_dark',
    title={
            'text': "2 - Proportion of late or in time cars for the checkout",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            font=dict(
            family="arial",
            size=18,
            color="white"),
            width=600, height=400)
            
    st.plotly_chart(fig_2)

st.markdown("****")

col1,col2= st.columns(2)

with col1:
    fig_3 = go.Figure(data=[go.Pie(labels=checkin_types.index,values=checkin_types.values, pull=[0.2, 0])])
    fig_3.update_layout(template='plotly_dark',
    title={
            'text': "Checkin' Type repartition ",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            font=dict(
            family="arial",
            size=18,
            color="white"),
            width=400, height=500,)   
    st.plotly_chart(fig_3)
    st.text("we can see that mobile checkin' represents more than 79% of all rentals")

with col2:
    # Rental repartition by checkin' type
    fig_4=px.histogram(df,
             x = 'checkin_type', 
             color = 'state',
             barmode = 'group',
             nbins=10,
             width=500,
             labels=dict(checkin_type="Checkin device", state="Rental status"),
             color_discrete_sequence=["lightgreen","lightblue"])

    fig_4.update_layout(template='plotly_dark',
        title={

        'text': "4 - State per checkin type",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        font=dict(
        family="arial",
        size=18,
        color="white"),
        width=600, height=400)
        
    st.plotly_chart(fig_4)

st.markdown("****")

col1,col2= st.columns(2)

with col1:

    fig_5 = px.pie(time_delta,
                    values=time_delta.values,
                    names=time_delta.index,

                    #color_discrete_map={'late':'lightgreen',
                                    # 'in time':'lightblue'}
                                        )
    fig_5.update_layout(template='plotly_dark',
    title={
            'text': "5 - Time delta with previous rental",
            'y':0.97,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            font=dict(
            family="arial",
            size=18,
            color="white"),
            width=600, height=500)

    st.plotly_chart(fig_5)

with col2:

    # delays repartition by checkin' type
    fig_6=px.histogram(df_clean,
                x = 'delay', 
                color = 'checkin_type',
                barmode = 'group',
                nbins=10,
                width=400,
                labels=dict(checkin_type="Checkin device", state="Checkout of previous rental"),
                color_discrete_sequence=["lightpink","lightblue"])

    fig_6.update_layout(template='plotly_dark',
    title={

            'text': "6 - Checkout status per checkin type",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
            font=dict(
            family="arial",
            size=16,
            color="white"),
            width=600, height=400)
            
    st.plotly_chart(fig_6)

st.markdown("****")  

col1,col2= st.columns(2)

with col1:
    # Display delay at checkout in minutes distribution within 12 hours range
    fig_7 = px.histogram(checkout_in_range, x="delay_at_checkout_in_minutes",
                        title = '7 - Distribution for a delay at checkout in minutes within 12 hours range',
                        width= 500,
                        height = 400,
                        color_discrete_map={'connect':'lightcyan',
                                            'mobile':'royalblue',
                                    })
                        
    fig_7.update_layout(title_x = 0.5, 
                        margin=dict(l=50,r=50,b=50,t=50,pad=4),
                        xaxis_title = '',
                        yaxis_title = '',
                        template = 'plotly_dark'
                        )

    st.plotly_chart(fig_7)
    st.text("we can see the distribution of the delay at checkout which is between -200 and 200 minutes")

with col2:
    # Display time delta with previous rental distribution within 12 hours range
    fig_8 = px.histogram(time_delta_in_range, x="delay_at_checkout_in_minutes",
                        title = '8 - Distribution for a Time delta with previous rental in minutes within 12 hours range',
                        width= 500,
                        height = 400,
                        color_discrete_map={'connect':'lightcyan',
                                            'mobile':'royalblue',
                                    })
                        
    fig_8.update_layout(title_x = 0.5, 
                        margin=dict(l=50,r=50,b=50,t=50,pad=4),
                        xaxis_title = '',
                        yaxis_title = '',
                        template = 'plotly_dark'
                        )
    st.plotly_chart(fig_8)
    st.text("we can see the time delta with previous rentals distribution between -200 and 200 minutes")


st.markdown("****")  
                  
fig_9 = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
fig_9.add_trace(go.Pie(labels=delta_for_canceled.index, values=delta_for_canceled.values, name="Time delta with previous rentals" ),
              1, 1)
fig_9.add_trace(go.Pie(labels=time_delta_for_canceled.index, values=time_delta_for_canceled.values, name="Details of Time delta with previous rentals"),
              1, 2)

# Use `hole` to create a donut-like pie chart
fig_9.update_traces(hole=.4, hoverinfo="label+percent+name")

fig_9.update_layout(
    template='plotly_dark',
    title={
        'text': "9 - Canceled rentals : Time delta with previous rentals repartition",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    # Add annotations in the center of the donut pies.
    annotations=[dict(text='> 720 min or not', x=0.165, y=0.5, font_size=12, showarrow=False),
                 dict(text='In minutes', x=0.82, y=0.5, font_size=15, showarrow=False)],
    width=1200, height=600)

st.plotly_chart(fig_9)

st.markdown("****")  

st.text(" ** FOCUS ON CANCELED RENTALS ** ")

col1, col2= st.columns(2)

with col1:
# Piechart proporion for checkin type influence on cancelation
    fig_10 = px.pie(cancelations_checkin_device,
                    values=cancelations_checkin_device.values,
                    names=cancelations_checkin_device.index, 
                    title='Cancelation per checkin device'
                    )           
    fig_10.update_layout(title_x = 0.5, 
                    template = 'plotly_dark',
                    width=600, height=400
                    )  

    st.plotly_chart(fig_10)

    st.text('The checkin type affects a little the cancelations: 60% connect vs 40% mobile')

with col2:

    # Piechart to see delays influence on cancelation
    fig_10b = px.pie(data_canceled_prev_delay,
                    values=data_canceled_prev_delay.values,
                    names=data_canceled_prev_delay.index, 
                    title='Delays of previous checkout influence on cancelationss'
                    )           
    fig_10b.update_layout(title_x = 0.5, 
                    template = 'plotly_dark',
                    width=600, height=400
                    )  
    st.plotly_chart(fig_10b)
    st.text("The delays of previous checkout doesn't really impact the cancelations")

st.markdown("****")  

st.text(" if we study only canceled rentals and the checkout of their previous rental: ")

fig_11 = px.histogram(df_canceled_PrevLate, x="delay_at_checkout_in_minutes_x",
                      title = '11 - Distribution late previous checkout in minutes for canceled rentals',
                      width= 600,
                      height = 400,
                      color_discrete_map={'connect':'lightcyan',
                                          'mobile':'royalblue',
                                })
                    
fig_11.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = 'delay at checkout of previous rental',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
                      
st.plotly_chart(fig_11)
st.text('The major delay at checkout of previous rental for each canceled rental is between 100 & 200 min')

st.markdown("****")  

st.text("To find the treshold we have calculate the following elements: ")

#Let's calculate the glotal ratio between all the "late" delay at checkout of these canceled rentals and the total of time delta with the previous rental
st.text("1: ratio between delays and deltas = delay at checkout previous rentals of canceled cars / time delta with previous rentals of these canceled cars")

# Now let's calculate the Time delta average between twe rentals 
st.text("2: Time delta average")
st.text(f"3: then we found the threshold multiplying ratio Delay Delta * Time Delta average: {threshold} minutes")

st.markdown("****")  

st.text("WHAT IS THE IMPACT of this threshold if we apply it to all rentals")

fig_12 = px.pie(rentals_ended,
                values=values,
                names=labels,
                color_discrete_map={'sucessful rentals':'lightgreen',
                                    'lost rentals':'red'})

fig_12.update_traces(hole=.4, hoverinfo="label+percent+name")

fig_12.update_layout(
    template='plotly_dark',
    title={
        'text': "Successful vs Lost Rentals",
        'y':0.97,
        'x':0.45,
        'xanchor': 'center',
        'yanchor': 'top'},
    # Add annotations in the center of the donut pies.
    width=600, height=400)
                      
st.plotly_chart(fig_12)

st.text("With the application of this threshold we would have had more than 44% of canceled rentals ")

st.markdown("****")  

st.text("Here are the loss by car if wy have had applied this threshold: ")
st.dataframe(loss_by_car)


