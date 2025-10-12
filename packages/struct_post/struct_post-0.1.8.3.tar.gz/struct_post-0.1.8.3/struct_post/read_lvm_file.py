def read_lvm_file(file_name: str):
    '''
    Reads a LabVIEW .lvm file and returns a pandas DataFrame.

    Processing steps:
    - Reads the raw .lvm file as CSV text.
    - Finds the last "***End_of_Header***" marker to skip metadata.
    - Uses the first row after the header as column names.
    - Ensures each row has the same number of entries as the header.
    - Converts numeric values where possible.
    - Sets the "X_Value" column as the index.

    Returns:
        pd.DataFrame:
            DataFrame with:
              - Index: "X_Value" (numeric, usually time or sample number).
              - Columns: measurement channels from the .lvm file.
              - Values: floats (where conversion is possible), otherwise strings.
    '''
    import csv
    import pandas as pd
    #Read the lvm file
    with open(file_name, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        raw_data = list(csv_reader)
    # -------------------------------
    # Step 1: Flatten into a list of strings
    # -------------------------------
    lines = []
    for item in raw_data:
        if item:  # make sure it's not empty
            lines.append(item[0])  # take the string inside
    # -------------------------------
    # Step 2: Find the line with the last End_of_Header
    # -------------------------------
    end_header_indices = []
    for i, line in enumerate(lines):
        if "***End_of_Header***" in line:
            end_header_indices.append(i)
    start_idx = end_header_indices[-1] + 1  # the line after header

    # -------------------------------
    # Step 3: Extract header and data
    # -------------------------------
    header_line = lines[start_idx]
    header = header_line.split("\t")
    
    data_lines = []
    for line in lines[start_idx + 1:]:
        if line.strip():  # skip empty lines
            values = line.split("\t")
            # Pad with empty values if too short
            while len(values) < len(header):
                values.append("")
            data_lines.append(values)
    
    # -------------------------------
    # Step 4: Build DataFrame
    # -------------------------------
    df = pd.DataFrame(data_lines, columns=header)
    
    # Convert to numeric where possible
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            pass
            
    df = df.set_index("X_Value").iloc[:, :-1]      
    return df, file_name[:-4]