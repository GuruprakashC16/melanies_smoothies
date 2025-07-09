# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col,when_matched
import requests
import pandas

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruits you want in your custom smoothie
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on thesmoothie will be:", name_on_order)
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Pandas
pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:'
    , my_dataframe
    ,max_selections=5
)
if ingredients_list:
    
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + str(search_on))
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

     #order filled checkbox
     order_filled = st.checkbox("Mark order as filled?")


    #st.write(ingredients_string)

    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order, order_filled, order_ts)
        values ('""" + ingredients_string.strip() + """', '""" + name_on_order + """', """ + str(order_filled).upper() + """, '""" + current_ts + """')"""


    #st.write(my_insert_stmt)
    time_to_insert = st.button('Sumbit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_order+' !', icon="✅")



smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

       

        
    
   
