# -*- coding: utf-8 -*-
"""Healthcare_Insights_Final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MSiny1wuWHe2tks69K9GYmOe_Ia_Fcaf
"""

# !pip3 install streamlit
# !pip3 install pandas
# !pip3 install numpy
uv install matplotlib
uv install seaborn
uv install sqlite3

# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import streamlit as st

# Import data from GitHub
try:
    url = "https://raw.githubusercontent.com/Althedatascientist1994/Healthcare_Insights/main/Healtcare-Dataset.xlsx"

    df = pd.read_excel(url, engine='openpyxl')
except Exception as e:
    st.error(f"Error importing data: {e}")
    st.stop()


# Split data into different DataFrames based on FollowupDate being NaN
df_fu_eq_na = df[df.isna()['Followup Date']==True]
df_fu_ne_na = df[df.isna()['Followup Date']==False]

df_fu_eq_na['Followup Date']="No followup date available"

#To ensure the datetimes will insert into sqllite, we need to convert to string

df['Admit_Date'] = df['Admit_Date'].astype(str)
df['Discharge_Date'] = df['Discharge_Date'].astype(str)
df['Followup Date'] = df['Followup Date'].astype(str)

df_fu_eq_na['Admit_Date'] = df_fu_eq_na['Admit_Date'].astype(str)
df_fu_eq_na['Discharge_Date'] = df_fu_eq_na['Discharge_Date'].astype(str)

df_fu_ne_na['Admit_Date'] = df_fu_ne_na['Admit_Date'].astype(str)
df_fu_ne_na['Discharge_Date'] = df_fu_ne_na['Discharge_Date'].astype(str)
df_fu_ne_na['Followup Date'] = df_fu_ne_na['Followup Date'].astype(str)

# Create database
conn = sqlite3.connect('Healthcare_data.db')
cursor = conn.cursor()

#Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS all_data (
                  PatientID INTEGER PRIMARY KEY,
                  AdmitDate DATETIME,
                  DischargeDate	DATETIME,
                  Diagnosis	TEXT,
                  Bed_Occupancy	INTEGER,
                  Test TEXT,
                  Doctor TEXT,
                  FollowupDate DATETIME,
                  Feedback DOUBLE,
                  Billing_Amount DOUBLE,
                  Health_Insurance_Amount DOUBLE)'''
)

conn.commit()

##Followup equals na

cursor.execute('''CREATE TABLE IF NOT EXISTS followup_na_data (
                  PatientID INTEGER PRIMARY KEY,
                  AdmitDate DATETIME,
                  DischargeDate	DATETIME,
                  Diagnosis	TEXT,
                  Bed_Occupancy	INTEGER,
                  Test TEXT,
                  Doctor TEXT,
                  FollowupDate DATETIME,
                  Feedback DOUBLE,
                  Billing_Amount DOUBLE,
                  Health_Insurance_Amount DOUBLE)'''
)

conn.commit()

##Non-na data

cursor.execute('''CREATE TABLE IF NOT EXISTS non_na_data (
                  PatientID INTEGER PRIMARY KEY,
                  AdmitDate DATETIME,
                  DischargeDate	DATETIME,
                  Diagnosis	TEXT,
                  Bed_Occupancy	INTEGER,
                  Test TEXT,
                  Doctor TEXT,
                  FollowupDate DATETIME,
                  Feedback DOUBLE,
                  Billing_Amount DOUBLE,
                  Health_Insurance_Amount DOUBLE)'''
)

conn.commit()

#Creating queries for data
query_all_data = '''INSERT INTO all_data (PatientID, AdmitDate, DischargeDate, Diagnosis, Bed_Occupancy, Test, Doctor, FollowupDate, Feedback, Billing_Amount, Health_Insurance_Amount)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

query_followup_na = '''INSERT INTO followup_na_data (PatientID, AdmitDate, DischargeDate, Diagnosis, Bed_Occupancy, Test, Doctor, FollowupDate, Feedback, Billing_Amount, Health_Insurance_Amount)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

query_non_na = '''INSERT INTO non_na_data (PatientID, AdmitDate, DischargeDate, Diagnosis, Bed_Occupancy, Test, Doctor, FollowupDate, Feedback, Billing_Amount, Health_Insurance_Amount)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

query_list = [query_all_data, query_followup_na, query_non_na]
db_list = [df, df_fu_eq_na, df_fu_ne_na]

#importing data with a try-except to account for errors

for i, query in enumerate(query_list):
    try:
        cursor.executemany(query, db_list[i].values.tolist()) # Convert DataFrame to list of lists
        conn.commit()
    except sqlite3.ProgrammingError as e:
        print(f"Error inserting data into table {i}: {e}")
        # If the error is due to incorrect number of bindings, print the problematic row
        if "Incorrect number of bindings supplied" in str(e):
            print(f"Problematic row: {db_list[i].iloc[0].values.tolist()}")
        continue
    except Exception as e:
        print(f"Error inserting data into table {i}: {e}")
        continue

st.title("Healthcare Data Analysis App")

# Sidebar with query options
selected_query = st.sidebar.selectbox(
    "Select a query to display:",
    [
        "Number of Patient Admissions Over Time",
        "Top 5 Diagnoses",
        "Bed Occupancy Distribution",
        "Patient Admissions per Month",
        "Length of Stay Statistics",
        "Top 10 Doctors",
        "Top 10 Tests",
        "Feedback Distribution",
        "Billing Amount Statistics",
        "Health Insurance Amount Statistics",
        "Patients with Followup",
        "Patients without Followup",
        "Time until Followup",
        "Bed Occupancy and Diagnosis",
        "Doctor and Diagnosis",
    ],
)

# Display data based on selected query
if selected_query == "Number of Patient Admissions Over Time":
  query = '''SELECT strftime('%Y-%m',AdmitDate) as Admit_MY, COUNT(*) as total_patients
            FROM all_data
            GROUP BY strftime('%Y-%m',AdmitDate)'''
  df_patient_admit = pd.read_sql_query(query, conn)
  df_patient_admit['Admit_MY'] = pd.to_datetime(df_patient_admit['Admit_MY'], format='%Y-%m')
  st.subheader("Patient Admissions Over Time")
  fig, ax = plt.subplots(figsize=(12, 6))
  sns.lineplot(x='Admit_MY', y='total_patients', data=df_patient_admit, ax=ax)
  st.pyplot(fig)


elif selected_query == "Top 5 Diagnoses":
  query = '''SELECT Diagnosis, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Diagnosis
            ORDER BY total_patients DESC
            LIMIT 5'''
  df_diagnosis = pd.read_sql_query(query, conn)
  st.subheader("Top 5 Diagnoses")
  fig, ax = plt.subplots(figsize=(8, 6))
  sns.barplot(x='Diagnosis', y='total_patients', data=df_diagnosis, ax=ax)
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

elif selected_query == "Bed Occupancy Distribution":
  query = '''SELECT Bed_Occupancy, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Bed_Occupancy
            ORDER BY total_patients DESC'''
  df_bed_occ = pd.read_sql_query(query, conn)
  st.subheader("Bed Occupancy Distribution")
  fig, ax = plt.subplots(figsize=(8, 6))
  sns.barplot(x='Bed_Occupancy', y='total_patients', data=df_bed_occ, ax=ax)
  st.pyplot(fig)

elif selected_query == "Patient Admissions per Month":
  query = '''SELECT strftime('%m',AdmitDate) as Admit_month, COUNT(*) as total_patients
            FROM all_data
            GROUP BY strftime('%m',AdmitDate)'''
  df_patient_admit_month = pd.read_sql_query(query, conn)
  st.subheader("Patient Admissions per Month")
  fig, ax = plt.subplots(figsize=(10, 6))
  sns.barplot(x='Admit_month', y='total_patients', data=df_patient_admit_month, ax=ax)
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

elif selected_query == "Length of Stay Statistics":
  query = '''SELECT AVG(JULIANDAY(DischargeDate)-JULIANDAY(AdmitDate)) as avg_length_of_stay,
                    MAX(JULIANDAY(DischargeDate)-JULIANDAY(AdmitDate)) as max_length_of_stay
            FROM all_data'''
  df_length_of_stay = pd.read_sql_query(query, conn)
  st.subheader("Length of Stay Statistics")
  st.write(df_length_of_stay)

elif selected_query == "Top 10 Doctors":
  query = '''SELECT Doctor, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Doctor
            ORDER BY total_patients DESC
            LIMIT 10'''
  df_doctor = pd.read_sql_query(query, conn)
  st.subheader("Top 10 Doctors")
  fig, ax = plt.subplots(figsize=(10, 6))
  sns.barplot(x='Doctor', y='total_patients', data=df_doctor, ax=ax)
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

elif selected_query == "Top 10 Tests":
  query = '''SELECT Test, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Test
            ORDER BY total_patients DESC
            LIMIT 10'''
  df_test = pd.read_sql_query(query, conn)
  st.subheader("Top 10 Tests")
  fig, ax = plt.subplots(figsize=(10, 6))
  sns.barplot(x='Test', y='total_patients', data=df_test, ax=ax)
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

elif selected_query == "Feedback Distribution":
  query = '''SELECT Feedback, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Feedback
            ORDER BY total_patients DESC'''
  df_feedback = pd.read_sql_query(query, conn)
  st.subheader("Feedback Distribution")
  fig, ax = plt.subplots(figsize=(8, 6))
  sns.barplot(x='Feedback', y='total_patients', data=df_feedback, ax=ax)
  st.pyplot(fig)

elif selected_query == "Billing Amount Statistics":
  query = '''SELECT AVG(Billing_Amount) as avg_billing_amount,
                    MAX(Billing_Amount) as max_billing_amount,
                    MIN(Billing_Amount) as min_billing_amount
            FROM all_data'''
  df_billing_amount = pd.read_sql_query(query, conn)
  st.subheader("Billing Amount Statistics")
  st.write(df_billing_amount)

elif selected_query == "Health Insurance Amount Statistics":
  query = '''SELECT AVG(Health_Insurance_Amount) as avg_health_insurance_amount,
                    MAX(Health_Insurance_Amount) as max_health_insurance_amount,
                    MIN(Health_Insurance_Amount) as min_health_insurance_amount
            FROM all_data'''
  df_health_insurance_amount = pd.read_sql_query(query, conn)
  st.subheader("Health Insurance Amount Statistics")
  st.write(df_health_insurance_amount)

elif selected_query == "Patients with Followup":
  query = '''SELECT COUNT(*) as total_patients_followup
            FROM non_na_data'''
  df_followup = pd.read_sql_query(query, conn)
  st.subheader("Patients with Followup")
  st.write(df_followup)

elif selected_query == "Patients without Followup":
  query = '''SELECT COUNT(*) as total_patients_no_followup
            FROM followup_na_data'''
  df_no_followup = pd.read_sql_query(query, conn)
  st.subheader("Patients without Followup")
  st.write(df_no_followup)

elif selected_query == "Time until Followup":
  query = '''SELECT AVG(JULIANDAY(FollowupDate)-JULIANDAY(DischargeDate)) as avg_length_discharge_until_followup,
                    MAX(JULIANDAY(FollowupDate)-JULIANDAY(DischargeDate)) as max_length
                    AVG(JULIANDAY(FollowupDate)-JULIANDAY(AdmitDate)) as avg_length_admit_until_followup,
                    MAX(JULIANDAY(FollowupDate)-JULIANDAY(AdmitDate)) as max_length
            FROM non_na_data'''
  df_length_until_followup = pd.read_sql_query(query, conn)
  st.subheader("Time until Followup")
  st.write(df_length_until_followup)

elif selected_query == "Bed Occupancy and Diagnosis":
  query = '''SELECT Bed_Occupancy, Diagnosis, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Bed_Occupancy, Diagnosis
            ORDER BY total_patients DESC'''
  df_bed_diagnosis = pd.read_sql_query(query, conn)
  st.subheader("Bed Occupancy and Diagnosis")
  fig, ax = plt.subplots(figsize=(16, 8))
  sns.barplot(x='Bed_Occupancy', y='total_patients', hue='Diagnosis', data=df_bed_diagnosis, ax=ax)
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

elif selected_query == "Doctor and Diagnosis":
  query = '''SELECT Doctor, Diagnosis, COUNT(*) as total_patients
            FROM all_data
            GROUP BY Doctor, Diagnosis
            ORDER BY total_patients DESC'''
  df_doctor_diagnosis = pd.read_sql_query(query, conn)
  st.subheader("Patient Distribution per Doctor and Diagnosis")
  fig, ax = plt.subplots(figsize=(16,8))
  sns.barplot(x='Doctor', y='total_patients', hue='Diagnosis', data=df_doctor_diagnosis, ax=ax)
  plt.xticks(rotation=45, ha='right')
  st.pyplot(fig)

conn.close()
