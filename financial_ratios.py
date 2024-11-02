import pandas as pd

def calculate_ratios(financial_data):
    df = pd.DataFrame()
    
    # Calculate all required ratios
    df['Total_Debt'] = financial_data['total_debt']
    df['Net_Debt'] = financial_data['total_debt'] - financial_data['cash']
    df['EBITDA'] = financial_data['ebitda']
    df['Net_Debt_to_EBITDA'] = df['Net_Debt'] / df['EBITDA']
    df['Interest_to_EBITDA'] = financial_data['interest_expense'] / df['EBITDA']
    df['Capital_to_Assets'] = financial_data['total_capital'] / financial_data['total_assets']
    df['ROE'] = financial_data['net_income'] / financial_data['total_equity']
    df['ROA'] = financial_data['net_income'] / financial_data['total_assets']
    
    return df