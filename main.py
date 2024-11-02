import streamlit as st
import pandas as pd
from modal import Function
import os

def main():
    st.title("Financial Statement Analyzer")
    
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        for file in uploaded_files:
            st.write(f"Processing {file.name}...")
            
            # Process PDF through Modal backend
            try:
                pdf_processor = Function.lookup("stem", "process_pdf")
                financial_data = pdf_processor.remote(file)
                
                if financial_data:
                    # Display results
                    st.success(f"Successfully processed {file.name}")
                    st.dataframe(pd.DataFrame(financial_data))
                else:
                    st.error(f"Failed to process {file.name}")
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")

if __name__ == "__main__":
    main()