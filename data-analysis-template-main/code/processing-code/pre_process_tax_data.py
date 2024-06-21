from pandas import read_csv, set_option, merge
from tqdm import tqdm # unnecessary dependency, adding as a meme 
from numpy import mean
from pyspark.sql import SparkSession
set_option('display.max_columns', None)

def data_dict_pre_process(filename: str):
    strip_variable_whitespace_list = []
    data_dict_df = read_csv(f'data/raw-data/{filename}.csv')
    for idx, row in data_dict_df.iterrows():
        variable = row['VARIABLE NAME'].strip()
        strip_variable_whitespace_list.append(variable)
    data_dict_df['VARIABLE NAME'] = strip_variable_whitespace_list

    data_dict_df_variable_names = data_dict_df['VARIABLE NAME'].tolist()
    
    tax_qualitative_variables = data_dict_df_variable_names[:19]
    format_tax_qualitative_variables = []
    for code in tqdm(tax_qualitative_variables):
        format_tax_qualitative_variables.append(code)
    
    tax_numerical_variables = data_dict_df_variable_names[19:]
    total_count_return_variables = []
    total_amount_return_variables = []
    for code in tqdm(tax_numerical_variables):
        if code.startswith('N'):
            total_count_return_variables.append(code)
        else:
            total_amount_return_variables.append(code)

    amount_return_variables_new = format_tax_qualitative_variables + total_amount_return_variables
    count_return_variables_new = tax_qualitative_variables + total_count_return_variables
    description_amount_data_dict_list = data_dict_df['DESCRIPTION'].loc[data_dict_df['VARIABLE NAME'].isin(amount_return_variables_new)].tolist()
    description_count_data_dict_list = data_dict_df['DESCRIPTION'].loc[data_dict_df['VARIABLE NAME'].isin(count_return_variables_new)].tolist()

    amount_data_dict_df = data_dict_df.loc[data_dict_df['VARIABLE NAME'].isin(amount_return_variables_new)]
    count_data_dict_df = data_dict_df.loc[data_dict_df['VARIABLE NAME'].isin(count_return_variables_new)]
    amount_data_dict_df.to_csv('data/intermediate-data/data_dict_variable_total_amount.csv', index=False)
    count_data_dict_df.to_csv('data/intermediate-data/data_dict_variable_total_number_returns.csv', index=False)

def tax_data_pre_process(filename: str, state: str):
    tax_data_df = read_csv(f'data/raw-data/{filename}.csv').drop('agi_stub', axis=1)
    tax_data_df = tax_data_df.loc[tax_data_df['STATE'] == f'{state}']

    amount_data_dict_df = read_csv(f'data/intermediate-data/data_dict_variable_total_amount.csv')
    amount_data_dict_df_variables_list = amount_data_dict_df['VARIABLE NAME'].tolist()
    description_amount_list = amount_data_dict_df['DESCRIPTION'].tolist()
    total_amount_tax_data_df = tax_data_df.loc[:, tax_data_df.columns.isin(amount_data_dict_df_variables_list)]
    total_amount_tax_data_df.columns = description_amount_list
    total_amount_tax_data_df = total_amount_tax_data_df.rename(
        columns={
            '5-digit Zip code': 'ZIPCODE'
        }
    )
    total_amount_tax_data_df.to_csv(f'data/intermediate-data/{state}_total_amount_tax_data.csv', index=False)
    
    number_data_dict_df = read_csv(f'data/intermediate-data/data_dict_variable_total_number_returns.csv')
    number_data_dict_df_variables_list = number_data_dict_df['VARIABLE NAME'].tolist()
    description_number_list = number_data_dict_df['DESCRIPTION'].tolist()
    total_number_tax_data_df = tax_data_df.loc[:, tax_data_df.columns.isin(number_data_dict_df_variables_list)]
    total_number_tax_data_df.columns = description_number_list
    total_number_tax_data_df = total_number_tax_data_df.rename(
        columns={
            '5-digit Zip code': 'ZIPCODE'
        }
    )
    total_number_tax_data_df.to_csv(f'data/intermediate-data/{state}_total_number_returns_tax_data.csv', index=False)

def ev_data_pre_process(state: str):
    ev_data_df = read_csv('data/raw-data/Electric_Vehicle_Population_Data.csv').rename(columns={
        'Postal Code': 'ZIPCODE'
    })
    ev_data_df['ZIPCODE'] = ev_data_df['ZIPCODE'].fillna(0).astype(int)
    null_values = ev_data_df.isnull().sum()
    ev_data_df.dropna(inplace=True)
    ev_data_df_2020 = ev_data_df.loc[(ev_data_df['Model Year'] <= 2020) & (ev_data_df['Electric Range'] > 0) & (ev_data_df['Model Year'] > 2010) & (ev_data_df['State'] == f'{state}')]
    ev_duplicated_df = ev_data_df[ev_data_df.duplicated()]

    zip_code_count_brand_model_year = ev_data_df_2020.groupby(['City', 'State', 'ZIPCODE', 'Model Year', 'Make', 'Model', 'Electric Vehicle Type', 'Clean Alternative Fuel Vehicle (CAFV) Eligibility']).agg({
        'Electric Range': mean,
        'County': 'count',
    }).reset_index()
    zip_code_count_brand_model = ev_data_df_2020.groupby(['City', 'State', 'ZIPCODE', 'Make', 'Model', 'Electric Vehicle Type', 'Clean Alternative Fuel Vehicle (CAFV) Eligibility']).agg({
        'Electric Range': mean,
        'County': 'count',
    }).reset_index()
    zip_code_count_brand = ev_data_df_2020.groupby(['City', 'State', 'ZIPCODE', 'Make', 'Electric Vehicle Type', 'Clean Alternative Fuel Vehicle (CAFV) Eligibility']).agg({
        'Electric Range': mean,
        'County': 'count',
    }).reset_index()
    zip_code_count_brand_model_year.to_csv(f'data/intermediate-data/{state}_zip_code_brand_model_year.csv', index=False)
    zip_code_count_brand_model.to_csv(f'data/intermediate-data/{state}_zip_code_brand_model.csv', index=False)
    zip_code_count_brand.to_csv(f'data/intermediate-data/{state}_zip_code_brand.csv', index=False)

def join_tax_ev_data(state: str):
    zip_code_count_brand_model_year = read_csv(f'data/intermediate-data/{state}_zip_code_brand_model_year.csv')
    zip_code_count_brand_model= read_csv(f'data/intermediate-data/{state}_zip_code_brand_model.csv')
    zip_code_count_brand = read_csv(f'data/intermediate-data/{state}_zip_code_brand.csv')
    amount_tax_data = read_csv(f'data/intermediate-data/{state}_total_amount_tax_data.csv')
    # print(amount_tax_data)

    final_zip_code_count_brand_model_year = merge(zip_code_count_brand_model_year, amount_tax_data, on='ZIPCODE').rename(
        columns={
            'County': 'Vehicle Count'
        }
    )
    final_zip_code_count_brand_model = merge(zip_code_count_brand_model, amount_tax_data, on='ZIPCODE').rename(
        columns={
            'County': 'Vehicle Count'
        }
    )
    final_zip_code_count_brand = merge(zip_code_count_brand, amount_tax_data, on='ZIPCODE').rename(
        columns={
            'County': 'Vehicle Count'
        }
    )
    final_zip_code_count_brand_model_year.to_csv('data/processed-data/brand_model_year_tax_data.csv', index=False)
    final_zip_code_count_brand_model.to_csv('data/processed-data/brand_model_tax_data.csv', index=False)
    final_zip_code_count_brand.to_csv('data/processed-data/brand_tax_data.csv', index=False)

data_dict_pre_process(filename='data_dict2021')
tax_data_pre_process(filename='tax_data_2021', state='WA')
ev_data_pre_process(state='WA')
join_tax_ev_data(state='WA')