#!/usr/bin/env python3
"""
Database Viewer for Rhizome CBC Analysis
View users, questionnaires, and CBC results in the SQLite database
"""

import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st

def get_database_path():
    """Get the path to the SQLite database"""
    return Path(__file__).parent / "data" / "users.db"

def view_all_tables():
    """Display all tables and their contents"""
    db_path = get_database_path()
    
    if not db_path.exists():
        st.error("Database not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    
    st.title("🗄️ Rhizome Database Viewer")
    
    # Get all table names
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(tables_query, conn)
    
    st.subheader("📋 Available Tables")
    st.write(tables)
    
    # Display each table
    for table_name in tables['name']:
        st.subheader(f"📊 {table_name.upper()} Table")
        
        try:
            # Get table schema
            schema_query = f"PRAGMA table_info({table_name});"
            schema = pd.read_sql_query(schema_query, conn)
            
            with st.expander(f"Schema for {table_name}"):
                st.dataframe(schema)
            
            # Get table data
            data_query = f"SELECT * FROM {table_name};"
            data = pd.read_sql_query(data_query, conn)
            
            st.write(f"**Records: {len(data)}**")
            
            if len(data) > 0:
                # Show first few records
                st.dataframe(data.head(10))
                
                if len(data) > 10:
                    st.info(f"Showing first 10 of {len(data)} records")
                
                # Download option
                csv = data.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {table_name}.csv",
                    data=csv,
                    file_name=f"{table_name}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No records found")
                
        except Exception as e:
            st.error(f"Error reading {table_name}: {e}")
    
    conn.close()

def view_cbc_results_detailed():
    """Show detailed view of CBC results with extracted data"""
    db_path = get_database_path()
    
    if not db_path.exists():
        st.error("Database not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    
    st.subheader("🧬 CBC Results Detailed View")
    
    try:
        # Get CBC results with user info
        query = """
        SELECT 
            u.username,
            u.email,
            cr.filename,
            cr.file_format,
            cr.extraction_success,
            cr.wbc, cr.rbc, cr.hgb, cr.hct, cr.mcv, cr.plt, cr.rdw, cr.nlr,
            cr.risk_score,
            cr.processed_at,
            cr.raw_extraction_data,
            cr.patient_info
        FROM cbc_results cr
        JOIN users u ON cr.user_id = u.id
        ORDER BY cr.processed_at DESC
        """
        
        results = pd.read_sql_query(query, conn)
        
        if len(results) > 0:
            st.dataframe(results)
            
            # Show extraction details for each result
            for idx, row in results.iterrows():
                with st.expander(f"Extraction Details - {row['username']} - {row['filename']}"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Basic Info:**")
                        st.write(f"- Format: {row['file_format']}")
                        st.write(f"- Success: {row['extraction_success']}")
                        st.write(f"- Risk Score: {row['risk_score']}%")
                        st.write(f"- Processed: {row['processed_at']}")
                    
                    with col2:
                        st.write("**CBC Values:**")
                        cbc_values = {
                            'WBC': row['wbc'],
                            'RBC': row['rbc'],
                            'HGB': row['hgb'],
                            'HCT': row['hct'],
                            'MCV': row['mcv'],
                            'PLT': row['plt'],
                            'RDW': row['rdw'],
                            'NLR': row['nlr']
                        }
                        for name, value in cbc_values.items():
                            if value is not None:
                                st.write(f"- {name}: {value}")
                    
                    # Show raw extraction data if available
                    if row['raw_extraction_data']:
                        st.write("**Raw Extraction Data:**")
                        st.json(row['raw_extraction_data'])
                    
                    if row['patient_info']:
                        st.write("**Patient Info from PDF:**")
                        st.json(row['patient_info'])
        else:
            st.info("No CBC results found")
            
    except Exception as e:
        st.error(f"Error: {e}")
    
    conn.close()

def main():
    """Main function for the database viewer"""
    st.set_page_config(
        page_title="Rhizome Database Viewer",
        page_icon="🗄️",
        layout="wide"
    )
    
    tabs = st.tabs(["📊 All Tables", "🧬 CBC Results Detail"])
    
    with tabs[0]:
        view_all_tables()
    
    with tabs[1]:
        view_cbc_results_detailed()

if __name__ == "__main__":
    main()