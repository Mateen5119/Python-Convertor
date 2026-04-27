import os
import pandas as pd

def convert(input_path, target_format, temp_dir):
    filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
    
    if target_format == 'xlsx':
        df = pd.read_csv(input_path)
        output_path = os.path.join(temp_dir, f"{filename_without_ext}.xlsx")
        df.to_excel(output_path, index=False)
        return output_path
        
    elif target_format == 'csv':
        df = pd.read_excel(input_path)
        output_path = os.path.join(temp_dir, f"{filename_without_ext}.csv")
        df.to_csv(output_path, index=False)
        return output_path
        
    else:
        raise NotImplementedError(f"Spreadsheet conversion to {target_format} not supported.")
