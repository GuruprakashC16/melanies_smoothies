# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Pandas
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)

fruit_options = pd_df['FRUIT_NAME'].tolist()

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:',
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        if not search_on_row.empty and search_on_row.iloc[0]:
            search_on = search_on_row.iloc[0]
            st.subheader(fruit_chosen + ' Nutrition Information')
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning(f"No SEARCH_ON value found for {fruit_chosen}")

    # ✅ New checkbox to mark order as filled
    order_filled = st.checkbox("Mark order as filled?")

    # ✅ Updated insert with order_filled
    name_on_order = name_on_order or "Guest"
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order, order_filled)
            values ('""" + ingredients_string + """', '""" + name_on_order + """', """ + str(order_filled).upper() + """)"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        st.code(my_insert_stmt)
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
