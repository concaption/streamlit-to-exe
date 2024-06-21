# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:21:58 2024
@author: dduha
"""

import streamlit as st
import pandas as pd
import numpy as np
import base64
import os
from io import BytesIO
import xlsxwriter

# configure screen width
st.set_page_config(layout="wide")

# function to create a border
def add_border_image(border_image_path):
    resolved_path = os.path.join(os.path.dirname(__file__), border_image_path)
    with open(resolved_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    .border-container {{
        position: relative;
        width: 100%;
        height: 50px; 
        overflow: hidden;
    }}
    .border-container:before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('data:image/png;base64,{encoded_image}');
        background-size: cover;
        pointer-events: none;
    }}
    </style>
    <div class="border-container"></div>
    """
    st.markdown(css, unsafe_allow_html=True)

# call add_border_image function
add_border_image("s_background.png")

# Function to calculate total sales by school size
def calculate_revenue_per_sale(num_students, students_per_tutor, base_cost, tutor_cost_per_year, training_cost_per_year, customize_platform_cost, branded_platform_cost, ai_cost, training_multiplier, customize_multiplier, branded_multiplier, ai_multiplier):
    training_multiplier = min(training_multiplier, 1.0)
    customize_multiplier = min(customize_multiplier, 1.0)
    branded_multiplier = min(branded_multiplier, 1.0)
    ai_multiplier = min(ai_multiplier, 1.0)
    
    num_tutors = num_students / students_per_tutor
    revenue_base = base_cost
    revenue_tutor = num_tutors * tutor_cost_per_year
    revenue_training = num_tutors * training_cost_per_year * training_multiplier
    revenue_customize = customize_platform_cost * customize_multiplier
    revenue_branded = branded_platform_cost * branded_multiplier
    revenue_ai = ai_cost * ai_multiplier
    
    revenue_per_sale = revenue_base + revenue_tutor + revenue_training + revenue_customize + revenue_branded + revenue_ai
    return revenue_per_sale, revenue_base, revenue_tutor, revenue_training, revenue_customize, revenue_branded, revenue_ai

def calculate_sales(sales_fraction_small, sales_fraction_medium, sales_fraction_large, revenue_per_sale_small, revenue_per_sale_medium, revenue_per_sale_large, expenses, profit):
    num_sales = (expenses + profit) / (sales_fraction_small * revenue_per_sale_small + sales_fraction_medium * revenue_per_sale_medium + sales_fraction_large * revenue_per_sale_large)
    return num_sales

# Function to convert DataFrame to Excel
def to_excel(df, selected_option, user_inputs):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1})

    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    worksheet.write(len(df) + 2, 0, f"Selected Option: {selected_option}")

    row = len(df) + 4
    worksheet.write(row, 0, "User Inputs:")
    for key, value in user_inputs.items():
        worksheet.write(row, 1, key)
        worksheet.write(row, 2, str(value))
        row += 1

    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Streamlit app
st.title("Break-even Sales by District Size")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Target Sales Calculation", "Key Assumptions", "Formulas & Calculation Steps"])

with tab1:
    st.sidebar.title("Expense & Profit Controls")
    expenses = st.sidebar.number_input("Enter the amount of expenses to cover (Total costs less expected philanthropy)", min_value=0, value=5000000, step=50000)
    profit = st.sidebar.number_input("Enter desired profit", min_value=0, value=0, step=50000)

    st.sidebar.title("Expected Case Probability Controls")
    df0 = pd.DataFrame([["Base", 0.6], ["Best", 0.2], ["Worst", 0.2]], columns=["Scenario", "Probability"])
    df0 = df0.set_index("Scenario")
    edf0 = st.sidebar.data_editor(df0, disabled=["_index"])

    st.sidebar.title("Scenario Controls: Base Case")
    training_multiplier = st.sidebar.number_input("Enter tutor training multiplier (% of customers who purchase)", min_value=0.0, max_value=1.0, value=0.5, step=0.05)
    customize_multiplier = st.sidebar.number_input("Enter customized platform multiplier (% of customers who purchase)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    branded_multiplier = st.sidebar.number_input("Enter branded platform multiplier (% of customers who purchase)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    ai_multiplier = st.sidebar.number_input("Enter AI multiplier (% of customers who purchase)", min_value=0.0, max_value=1.0, value=0.01, step=0.01)

    st.sidebar.title("Scenario Controls: Best & Worst Cases")
    best_multiplier = st.sidebar.number_input("Enter best case scenario multiplier (increase over base)", min_value=0.99, value=1.5, step=0.1)
    worst_multiplier = st.sidebar.number_input("Enter worst case scenario multiplier (decrease from base)", min_value=0.0, max_value=1.0, value=0.5, step=0.1)

    st.sidebar.title("School Size & Sales Mix Controls")
    df1 = pd.DataFrame([[2500, 0.33], [3750, 0.34], [5000, 0.33]], index=["Small", "Medium", "Large"], columns=["Number of students", "Sales mix"])
    df1.index.name = "School size"
    edf1 = st.sidebar.data_editor(df1, disabled=["_index"])

    students_per_tutor = st.sidebar.slider("Select tutor-student ratio", min_value=1, max_value=50, value=36, step=1)

    st.sidebar.title("Pricing Controls")
    df2 = pd.DataFrame([["Connect", 3500], ["Live online platform /tutor", 50], ["Coach-tutor training /tutor", 40], ["Customized platform", 1000], ["Branded platform", 6000], ["AI Insights", 7500]], columns=["Product", "Price($)"])
    df2 = df2.set_index("Product")
    edf2 = st.sidebar.data_editor(df2, disabled=["Product"])

    Scenarios = ["Base Case", "Best Case", "Worst Case"]
    Scenario_multiplier = [1.0, best_multiplier, worst_multiplier]
    product_multiplier = np.array([training_multiplier, customize_multiplier, branded_multiplier, ai_multiplier])
    num_students = edf1["Number of students"]
    sales_fraction = edf1["Sales mix"]
    cost = edf2["Price($)"]
    probability = edf0["Probability"]

    if sales_fraction.sum() != 1.0:
        st.error("The percentages must sum to 1.0")
    elif probability.sum() != 1.0:
        st.error("The probabilities must sum to 1.0")
    else:
        df_l = {}
        for scenario, multiplier in zip(Scenarios, Scenario_multiplier):
            eff_multiplier = multiplier * product_multiplier
            v_small = calculate_revenue_per_sale(num_students["Small"], students_per_tutor, *cost, *eff_multiplier)
            v_medium = calculate_revenue_per_sale(num_students["Medium"], students_per_tutor, *cost, *eff_multiplier)
            v_large = calculate_revenue_per_sale(num_students["Large"], students_per_tutor, *cost, *eff_multiplier)
            total_sales = calculate_sales(*sales_fraction, v_small[0], v_medium[0], v_large[0], expenses, profit)
            df = pd.DataFrame([total_sales * sales_fraction["Small"] * np.array(v_small), total_sales * sales_fraction["Medium"] * np.array(v_medium), total_sales * sales_fraction["Large"] * np.array(v_large)], columns=["Total Revenue", "Connect", "Live online platform", "Tutor training", "Custom platform", "Branded platform", "AI Insights"], index=["Small", "Medium", "Large"])
            df["Sales"] = total_sales * sales_fraction
            cols = df.columns.values
            df = df[[cols[-1], *cols[0:7]]]
            df.loc['Total'] = df.sum()
            df_l[scenario] = df

        df_l["Expected Case"] = probability["Base"] * df_l["Base Case"] + probability["Best"] * df_l["Best Case"] + probability["Worst"] * df_l["Worst Case"]

        summary_df = pd.DataFrame({
            "Scenario": ["Expected Case", "Base Case", "Best Case", "Worst Case"],
            "Total Sales": [df_l["Expected Case"].loc["Total", "Sales"], df_l["Base Case"].loc["Total", "Sales"], df_l["Best Case"].loc["Total", "Sales"], df_l["Worst Case"].loc["Total", "Sales"]],
            "Total Revenue": [df_l["Expected Case"].loc["Total", "Total Revenue"], df_l["Base Case"].loc["Total", "Total Revenue"], df_l["Best Case"].loc["Total", "Total Revenue"], df_l["Worst Case"].loc["Total", "Total Revenue"]]
        })

        summary_df["Total Sales"] = summary_df["Total Sales"].round(1)

        view_option = st.radio("Select View", ["Summary Table", "Detail Table"], key="view_option")
        if view_option == "Summary Table":
            st.write("### Summary Tables")
            st.dataframe(summary_df)
        else:
            selected_scenario = st.radio("Select Scenario to Display", options=["Expected Case"] + Scenarios, key="selected_scenario")
            st.write(f"{selected_scenario}")
            st.table(df_l[selected_scenario].style.format(precision=0, thousands=","))

        user_inputs = {
            "Expenses": expenses,
            "Profit": profit,
            "Scenario Probabilities": dict(edf0["Probability"]),
            "Training Multiplier": training_multiplier,
            "Customize Multiplier": customize_multiplier,
            "Branded Multiplier": branded_multiplier,
            "AI Multiplier": ai_multiplier,
            "Best Scenario Multiplier": best_multiplier,
            "Worst Scenario Multiplier": worst_multiplier,
            "District Sizes and Sales Mix": edf1.to_dict("records"),
            "Tutor-Student Ratio": students_per_tutor,
            "Product Pricing": dict(edf2["Price($)"])
        }

        st.sidebar.title("Download Options")
        download_option = st.sidebar.radio("Select Download Option", ["Summary Table", "Detail Table"], key="download_option")
        if download_option == "Summary Table":
            excel_data = to_excel(summary_df, "Summary Table", user_inputs)
        else:
            if "selected_scenario" not in st.session_state:
                st.session_state.selected_scenario = "Expected Case"
            excel_data = to_excel(df_l[st.session_state.selected_scenario], st.session_state.selected_scenario, user_inputs)

        st.sidebar.download_button(
            label="Download Excel",
            data=excel_data,
            file_name='sales_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

with tab2:
    st.write("### Key Assumptions")
    st.markdown("""
    #### 1. Tutor-Student Ratio
    - 1 tutor per 36 students
    - Connect & live-online platform are sold together
    #### 2. Number of Students by School Size
    - Small: 2,500 students
    - Medium: 3,750 students
    - Large: 5,000 students
    #### 3. Product Pricing
    - Connect: $3,500
    - Live-online platform: $50 per tutor
    - Coach tutor training: $40 per tutor
    - Customized platform: $1,000
    - Branded platform: $6,000
    - AI Insights: $7,500
    #### 4. Scenario Assumptions (Adoption rates)
    The base case, worst case, and best case scenarios are based on the following assumptions for product adoption rates, where the worst case is 50% of the base case, and best case multipliers relative to the base case are listed in the table:
    | Product | Base Case | Worst Case | Best Case |
    |-|-|-|-|
    | Coach-tutor training | 50% | 25% | 75% |
    | Customized platform | 5% | 2.5% | 7.5% |
    | Fully branded platform | 5% | 2.5% | 7.5% |
    | AI Insights | 1% | 0% | 3% |
    #### 5. Expected Case
    The expected case uses the concept of expected value to arrive at the most plausible outcome. It is calculated by taking the weighted average of all possible outcomes, where the weights are the probabilities of each scenario. This approach provides a balanced view that considers both the likelihood and impact of different scenarios.
    """)

with tab3:
    st.write("### Formulas and Calculation Steps")
    st.write("##### Based on User Inputs for Base Case, Assuming 100% sales to small schools")
    
    st.markdown(f"""
    #### 1. Calculate the Number of Tutors
    - **Formula**: 
      Number of Tutors = Number of Students / Students per Tutor
    - **Calculation** (Base Case, Small School):
      Number of Tutors = {num_students["Small"]} / {students_per_tutor} ≈ {num_students["Small"] / students_per_tutor:.2f}
    """)
    
    # Create tables for revenue components and adoption rates
    st.write("#### 2. Pricing Inputs")
    
    st.table(pd.DataFrame({
        "Product": ["Connect", "Live on-line platform", "Coach tutor training", "Customized platform", "Branded platform", "AI Insights"],
        "Cost": [cost["Connect"], cost["Live online platform /tutor"], cost["Coach-tutor training /tutor"], cost["Customized platform"], cost["Branded platform"], cost["AI Insights"]]
    }))
    
    st.write("#### 3. Adoption Rates (Base Case)")
    
    st.table(pd.DataFrame({
        "Product": ["Coach tutor training", "Customized platform", "Branded platform", "AI Insights"],
        "Multiplier": [f"{training_multiplier:.2f}", f"{customize_multiplier:.2f}", f"{branded_multiplier:.2f}", f"{ai_multiplier:.2f}"]
    }))
    
    st.markdown(f"""
    - **Revenue Calculations** (Base Case, Small School):
      - Connect = {cost["Connect"]}
      - Live on-line platform = {num_students["Small"] / students_per_tutor:.2f} × {cost["Live online platform /tutor"]} = {num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"]:.2f}
      - Coach tutor training = {num_students["Small"] / students_per_tutor:.2f} × {cost["Coach-tutor training /tutor"]} × {training_multiplier:.2f} = {num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier:.2f}
      - Customized platform = {cost["Customized platform"]} × {customize_multiplier:.2f} = {cost["Customized platform"] * customize_multiplier:.2f}
      - Branded platform = {cost["Branded platform"]} × {branded_multiplier:.2f} = {cost["Branded platform"] * branded_multiplier:.2f}
      - AI Insights = {cost["AI Insights"]} × {ai_multiplier:.2f} = {cost["AI Insights"] * ai_multiplier:.2f}

    #### 4. Calculate Average Revenue per Sale
    - **Formula**:
      Total Revenue per Sale = Connect + Live on-line platform + Coach tutor training + Customized platform + Branded platform +  AI Insights
    - **Calculation** (Base Case, Small School):
      Average Revenue per Sale = {cost["Connect"]} + {num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"]:.2f} + {num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier:.2f} + {cost["Customized platform"] * customize_multiplier:.2f} + {cost["Branded platform"] * branded_multiplier:.2f} + {cost["AI Insights"] * ai_multiplier:.2f} = {cost["Connect"] + num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"] + num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier + cost["Customized platform"] * customize_multiplier + cost["Branded platform"] * branded_multiplier + cost["AI Insights"] * ai_multiplier:.2f}

    #### 5. Calculate Break-even Sales
    - **Formula**:
      Break-even Sales = (Expenses + Profit) / Average revenue per sale
    - **Calculation** (Base Case, Small School):
      Break-even Sales = ({expenses} + {profit}) / {cost["Connect"] + num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"] + num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier + cost["Customized platform"] * customize_multiplier + cost["Branded platform"] * branded_multiplier + cost["AI Insights"] * ai_multiplier:.2f} ≈ {(expenses + profit) / (cost["Connect"] + num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"] + num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier + cost["Customized platform"] * customize_multiplier + cost["Branded platform"] * branded_multiplier + cost["AI Insights"] * ai_multiplier):.2f}

    #### 6. Break-even Sales Check
    - **Formula**:
      Total Revenue by Product = Break-even sales × Average revenue per sale
    - **Calculation** (Base Case, Small School):
      Total Revenue by Product = {(expenses + profit) / (cost["Connect"] + num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"] + num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier + cost["Customized platform"] * customize_multiplier + cost["Branded platform"] * branded_multiplier + cost["AI Insights"] * ai_multiplier):.2f} × {cost["Connect"] + num_students["Small"] / students_per_tutor * cost["Live online platform /tutor"] + num_students["Small"] / students_per_tutor * cost["Coach-tutor training /tutor"] * training_multiplier + cost["Customized platform"] * customize_multiplier + cost["Branded platform"] * branded_multiplier + cost["AI Insights"] * ai_multiplier:.2f} ≈ {(expenses + profit)}
    """)
