import pandas as pd

def load_data(uploaded_file):
    """
    Reads an uploaded file (streamlit FileUploader object) and returns a DataFrame.
    """
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(uploaded_file)
        elif file_extension == "json":
            df = pd.read_json(uploaded_file)
        else:
            raise ValueError("Unsupported file format. Please upload CSV, Excel, or JSON.")
            
        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("The uploaded file contains no data.")
            
        # Verify required columns exist
        required_columns = ['price', 'customer_id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Required columns missing: {', '.join(missing_columns)}")
            
        return df
        
    except Exception as e:
        # Log the error but return an empty DataFrame instead of raising an exception
        print(f"Error in load_data: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame instead of raising exception