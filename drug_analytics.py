# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

def write_to_csv(input_data_frame, file_name = 'Drug_condition'):
  try:
    input_data_frame.to_csv(file_name + ".csv", index=False)
    print("Written to file!")
  except:
    print("Not written to file")

def read_file_csv(input_file):
  try:
    pd.read_csv(input_file)
    print("File read into Pandas Dataframe....")
  except:
    print("File not found or empty...")

def col_replace(raw_df, col_name, placeholder = 'Unknown', str_to_replace = '\r\r\n'):
  return raw_df[col_name].replace(str_to_replace, placeholder)

def clean_process(raw_df, col1 = 'Condition', col2 = 'Reviews', col3 = 'Type', col4 = 'Indication'):
  raw_df[col1] = raw_df[col1].str.capitalize()
  raw_df[col2] = raw_df[col2].round().astype(int)
  raw_df[col3] = col_replace(raw_df, col3, '\r\r\n', 'Unknown')
  raw_df[col4] = col_replace(raw_df, col4, '\r\r\n', 'Unknown')
  return raw_df.drop_duplicates()

#define a custom rank matrix
def rank_matrix(raw_df):
  unique_conditions = raw_df['Condition'].unique()
  selected_condition = list(unique_conditions)
  output_df = pd.DataFrame()

  # Filter the DataFrame for the selected condition
  for item in selected_condition:
    condition_df = raw_df[raw_df['Condition'] == item].copy()
    condition_df['CombinedRank'] = condition_df['Satisfaction'] + condition_df['Effective'] + condition_df['EaseOfUse']
    condition_df = condition_df.sort_values(by=['CombinedRank', 'Price'], ascending=[False, False])
    top_10_drugs = condition_df.head(10)
    top_10_drugs.sort_values(by= 'Price', ascending = False)
    output_df.append(top_10_drugs)

  return output_df

# Iterate through unique conditions and calculate averages
def custom_cost_condition(raw_df):
  unique_conditions = raw_df['Condition'].unique()
  cost_condition = pd.DataFrame()

  for condition in unique_conditions:
      condition_df = raw_df[raw_df['Condition'] == condition].copy()
      result_condition = condition_df.groupby('Form').agg({'Price': 'mean', 'Satisfaction': 'mean'}).round(2)
      result_condition = result_condition.reset_index()
      result_condition['Condition'] = condition
      cost_condition = cost_condition.append(result_condition)

  cost_condition = cost_condition.reset_index(drop=True)
  cost_condition = cost_condition.rename(columns={'Price': 'Avg Price', 'Satisfaction': 'Avg Satisfaction'})
  return cost_condition

def join_data(drug_df, drug_metrics_df):
  drug_df['Condition'] = drug_df['Condition'].str.lower()
  drug_df['Drug'] = drug_df['Drug'].str.lower()
  drug_metrics_df['Condition'] = drug_metrics_df['Condition'].str.lower()
  drug_metrics_df['Drug'] = drug_metrics_df['Drug'].str.lower()
  return drug_metrics_df.merge(drug_df[['Condition', 'Drug', 'Information']], on=['Condition', 'Drug'], how='left')

def categorize_price(price):
    if price < 20:
        return 1  # Very Low
    elif price < 50:
        return 2  # Low
    elif price < 100:
        return 3  # Moderate
    elif price < 200:
        return 4  # High
    else:
        return 5  # Very High

if __name__ == "__main__":

  #input csv files
  input_file1, input_file2 = "", ""

  drug_df = read_file_csv(input_file1)
  drug_metrics_df = read_file_csv(input_file2)

  #drug_df = drug_df.drop_duplicates(subset=['Condition', 'Drug'])
  merged_df = join_data(drug_df, drug_metrics_df)
  cleaned_df = clean_process(merged_df)
  cleaned_df = rank_matrix(cleaned_df)
  cleaned_df['PriceRating'] = cleaned_df['Price'].apply(categorize_price)
  write_to_csv(cleaned_df)
