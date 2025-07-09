# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
import requests
import pandas
import datetime  # For timestamp

# App title and instructions
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw: {st.__version__}")
st.write("""Choose the fruits you want in your custom smoothie""")

# Input: Name on the smoothie
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

# Fruit options for multiselect
fruit_options = pd_df['FRUIT_NAME'].tolist()

# Input: fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

# Input: checkbox (outside the if block to avoid widget duplication error)
order_filled = st.checkbox("Mark order as filled?")

# If ingredients are selected, show nutrition and submit
if ingredients_list:
    # ✅ Join selected fruits with single space
    ingredients_string = ' '.join(ingredients_list).strip()

    # Show nutrition info for each selected fruit
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on)
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + str(search_on))
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Get current timestamp
    current_ts = datetime.datetime.now().isoformat()

    # ✅ Insert SQL statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled, order_ts)
    VALUES ('{ingredients_string}', '{name_on_order}', {str(order_filled).upper()}, '{current_ts}')
    """

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")

# Show sample fruit info always
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
