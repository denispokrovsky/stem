import streamlit as st
import pandas as pd
from modal import Function
import os
from financial_ratios import calculate_ratios

def main():
    st.title("Financial Statement Analyzer")
    
    # File upload
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each file
        for idx, file in enumerate(uploaded_files):
            status_text.text(f"Processing {file.name}...")
            
            # Call Modal backend for OCR and extraction
            pdf_processor = Function.lookup("financial-analyzer", "process_pdf")
            financial_data = pdf_processor.remote(file)
            
            # Calculate financial ratios
            if financial_data:
                ratios_df = calculate_ratios(financial_data)
                
                # Display results
                st.subheader(f"Financial Ratios - {file.name}")
                st.dataframe(ratios_df)
            
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("Processing complete!")

if __name__ == "__main__":
    main()