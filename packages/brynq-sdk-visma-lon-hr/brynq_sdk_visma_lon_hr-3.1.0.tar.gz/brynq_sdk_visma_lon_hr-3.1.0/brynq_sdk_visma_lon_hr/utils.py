import pandas as pd
from typing import List

def clean_column_names(columns: List[str]) -> List[str]:
    """
    Clean column names by removing unnecessary characters and standardizing format.
    
    Args:
        columns: List of column names to clean
        
    Returns:
        List of cleaned column names
    """
    return [col.replace('@', '').replace('#', '') for col in columns]

def handle_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle duplicate columns in DataFrame by appending a number to duplicates.
    
    Args:
        df: DataFrame with potential duplicate columns
        
    Returns:
        DataFrame with unique column names
    """
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols == dup] = [f"{dup}_{i}" if i != 0 else dup 
                            for i in range(sum(cols == dup))]
    df.columns = cols
    return df

def parse_xml_to_df(entries: dict) -> list:
    """
    Parse XML entries to a list of dictionaries suitable for DataFrame creation.
    
    Args:
        entries (dict): XML entries from xmltodict.parse
        
    Returns:
        list: List of dictionaries with cleaned data
    """
    # Ensure entries is a list
    if not isinstance(entries, list):
        entries = [entries]

    # Process each entry
    df_data = []
    for entry in entries:
        if 'content' in entry and 'm:properties' in entry['content']:
            properties = entry['content']['m:properties']
            row_data = {}
            
            for key, value in properties.items():
                # Remove 'd:' prefix
                clean_key = key.replace('d:', '')
                
                # Extract the actual value
                if isinstance(value, dict):
                    if '#text' in value:
                        row_data[clean_key] = value['#text']
                    elif '@m:null' in value and value['@m:null'] == 'true':
                        row_data[clean_key] = None
                    else:
                        row_data[clean_key] = None
                else:
                    row_data[clean_key] = value
            
            df_data.append(row_data)

            
    return df_data
