import streamlit as st
import pandas as pd
import requests
import inflection

# won't use sidebar in this app
st.set_page_config(layout = 'wide')

df = pd.read_csv('./X_test.csv')

@st.cache(allow_output_mutation=True)
def call_api( df ):

    url = 'https://stormy-falls-09064.herokuapp.com/churn/predict'
    data = df.to_json(orient = 'records')
    header = {'Content-Type' : 'application/json'}

    res = requests.post( url = url, data = data, headers = header)

    res = pd.DataFrame.from_dict(res.json())
    return res
    

# makes a slider between min and max values of a given dataframe column
def make_slider( label, column ):
    min = int(df[column].min())
    max = int(df[column].max())
    return st.slider( label, min, max, (min,max) )

def format_result(result):
    result = result.iloc[:, 1:]
    result = result[['customer_id', 'surname', 'geography', 'gender', 'has_cr_card', 'active_member', 'age', 'credit_score', 'tenure', 'num_of_products', 'balance', 'salary', 'churn_proba', 'ltv']].copy()

    result['has_cr_card'] = result['has_cr_card'].apply(yes_no)
    result['active_member'] = result['active_member'].apply(yes_no)
    result['churn_proba'] = result['churn_proba'].apply(lambda x: x*100)

    result.rename( columns = {'balance' : 'balance $', 'salary' : 'salary $', 'num_of_products' : 'nº_of_products', 'churn_proba' : 'churn_probability %'}, inplace = True )
    cols = result.columns.tolist()
    result.columns = map(lambda x: inflection.humanize(x), cols)
    result.rename( columns = {'Ltv' : 'LTV $' }, inplace = True )
    st.dataframe( result.style.format({"Salary $" : "{:,.2f}", "Balance $" : "{:,.2f}", "LTV $" : "{:,.2f}", 'Churn probability %': "{:,.2f}"}) )
    return None

#st.write('#### Select Operation Mode')
operation_mode = st.selectbox('Select Operation Mode', ['Find Customer by ID', 'Filter Customers by Attributes', 'Show All Customers', 'Simulate Customer'] )

# formated values yes/no for 1 and 0
yes_no = lambda x: 'Yes' if x == 1 else 'No'


if operation_mode == 'Find Customer by ID':
    customer_id =st.multiselect( 'Customer ID', df['customer_id'].unique().tolist(), df['customer_id'].unique()[0] )
    selection = df.loc[ (  df['customer_id'].isin(customer_id) )]

elif operation_mode == 'Filter Customers by Attributes':
    col1, col2 = st.columns(2)
    with col1:
        geography = st.multiselect( 'Geography', df['geography'].unique().tolist(), df['geography'].unique().tolist() )

        gender = st.multiselect( 'Gender' , df['gender'].unique().tolist(), df['gender'].unique().tolist() )

        # has_cr_card
        has_cr_card = st.multiselect( 'Credit Card' , df['has_cr_card'].unique().tolist(), df['has_cr_card'].unique().tolist(),  format_func = yes_no )

        # active_member
        active_member = st.multiselect( 'Active Member' , df['active_member'].unique().tolist(), df['active_member'].unique().tolist(),  format_func = yes_no )

        # leaving this in last position
        surname = st.multiselect( 'Surname' , df['surname'].unique().tolist() )
        
        # NUMERICAL FILTERS
        # age
        age = make_slider('Age (years)', 'age')
        

    with col2:
        # credit_score
        credit = make_slider( 'Credit Score', 'credit_score' )

        # tenure
        tenure = make_slider( 'Tenure (years)', 'tenure' )

        # balance
        balance = make_slider( 'balance', 'balance' )

        # salary
        salary = make_slider( 'salary', 'salary' )

        # num_of_products
        num_of_products = make_slider( 'num_of_products', 'num_of_products' )
    
    
    selection = df.loc[ (df['age'] >= age[0]) & (df['age'] <= age[1]) &                    
                        ( df['credit_score'] >= credit[0] ) & ( df['credit_score'] <= credit[1] ) & 
                        ( df['balance'] >= balance[0] ) & ( df['balance'] <= balance[1] ) & 
                        ( df['num_of_products'] >= num_of_products[0] ) & ( df['num_of_products'] <= num_of_products[1] ) & 
                        ( df['salary'] >= salary[0] ) & ( df['salary'] <= salary[1] ) &
                        ( df['has_cr_card'].isin(has_cr_card) )]
    if surname:
        selection = selection.loc[( df['surname'].isin(surname) )]

    if geography:
        selection = selection.loc[(  df['geography'].isin(geography) )]

    if gender:
        selection = selection.loc[df['gender'].isin(gender)]

    if  active_member:
        selection = selection.loc[df['active_member'].isin(active_member)]

elif operation_mode == 'Show All Customers':
    selection = df.copy()

else:
    col1, col2, col3 = st.columns(3)
    with col1:
    # categorical / state variables
        geography = st.selectbox( 'Geography', df['geography'].unique().tolist(), 0 )
        gender = st.selectbox( 'Gender' , df['gender'].unique().tolist(), 0 )
        active_member = st.selectbox( 'Active Member' , df['active_member'].unique().tolist(), 0,  format_func = yes_no )
        num_of_products = int( st.text_input( 'num_of_products ({} ~ {})'.format( df['num_of_products'].min(), df['num_of_products'].max() ), df['num_of_products'].min()) )
    
    with col2:
        has_cr_card = st.selectbox( 'Credit Card' , df['has_cr_card'].unique().tolist(), 0,  format_func = yes_no )
        credit_score = int( st.text_input( 'Credit Score ({} ~ {})'.format( df['credit_score'].min(), df['credit_score'].max() ) , df['credit_score'].min() ) )
        age = int( st.text_input( 'age ({} ~ {})'.format( df['age'].min(), df['age'].max() ), df['age'].min()) )
    
    with col3:
        tenure = int( st.text_input( 'tenure ({} ~ {})'.format( df['tenure'].min(), df['tenure'].max() ), df['tenure'].min()) )
        salary = float( st.text_input( 'salary ({} ~ {})'.format( df['salary'].min(), df['salary'].max() ), df['salary'].min()) )
        balance = float( st.text_input( 'balance ({} ~ {})'.format( df['balance'].min(), df['balance'].max() ), df['balance'].min()) )

    # numerical variables

    # creating dataframe to make request on API
    selection = pd.DataFrame({'row_number' : 1,  'customer_id' : 1,  'surname' : 'Fictional Customer',  'credit_score' : credit_score,
      'geography' : geography,  'gender' : gender,  'age' : age,  'tenure' : tenure,  'balance' : balance,
      'num_of_products' : num_of_products,  'has_cr_card' : has_cr_card,  'active_member' : active_member,  'salary' : salary}, index = [0])


# Calling API 
result = call_api(selection)

st.write( "Interact with the results bellow by clicking on the headers of the table")
# Formatting output

format_result( result )

footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
right: 0;
bottom: 0;
width: 10%;
background-color: white;
color: black;
text-align: center;
font-size: 14px;
}
</style>
<div class="footer">
App designed by:<a style='display: block; text-align: center;' href="https://www.linkedin.com/in/humberto-aguiar-840108179" target="_blank">Humberto Aguiar</a>
</div>
"""
# Find me through [LinkedIn](https://www.linkedin.com/in/humberto-aguiar-840108179)
st.markdown(footer,unsafe_allow_html=True)