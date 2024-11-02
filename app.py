import streamlit as st
import pandas as pd
from modal import Function
from app.financial_ratios import calculate_ratios

st.set_page_config(
    page_title="STEM Financial Analyzer",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Financial Statement Analyzer")
    st.markdown("""
    Upload Russian financial statements (PDF) to analyze key financial ratios.
    """)
    
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type="pdf", 
        accept_multiple_files=True,
        help="Upload Consolidated Financial Statements"
    )
    
    if uploaded_files:
        for file in uploaded_files:
            with st.expander(f"Processing {file.name}", expanded=True):
                progress_bar = st.progress(0)
                status = st.empty()
                
                try:
                    status.info("Starting PDF processing...")
                    progress_bar.progress(25)
                    
                    # Process PDF through Modal backend
                    pdf_processor = Function.lookup("stem", "process_pdf")
                    financial_data = pdf_processor.remote(file)
                    progress_bar.progress(75)
                    
                    if financial_data:
                        # Calculate ratios
                        ratios = calculate_ratios(financial_data)
                        progress_bar.progress(100)
                        
                        # Display results in tabs
                        tab1, tab2 = st.tabs(["Financial Ratios", "Raw Data"])
                        
                        with tab1:
                            st.subheader("Key Financial Ratios")
                            st.dataframe(ratios)
                            
                            # Visualization
                            if st.checkbox("Show Ratio Trends", key=f"trend_{file.name}"):
                                st.line_chart(ratios)
                        
                        with tab2:
                            st.subheader("Extracted Financial Data")
                            st.dataframe(pd.DataFrame(financial_data))
                            
                        status.success("Processing complete!")
                    else:
                        status.error("Failed to extract financial data")
                        
                except Exception as e:
                    status.error(f"Error: {str(e)}")
                    progress_bar.empty()

if __name__ == "__main__":
    main()