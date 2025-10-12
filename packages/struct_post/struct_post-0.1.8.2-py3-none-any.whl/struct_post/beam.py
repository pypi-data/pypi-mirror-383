from pandas import DataFrame
import pandas as pd

def beam_lvmdata_file(file_name, force_index=2, displ_index=3,
             mid_lvdt_ind=None, left_lvdt_ind=None, right_lvdt_ind=None):
    """
    Read a .lvm file and extract force, displacement, and LVDT data in groups.

    Parameters
    ----------
    file_name : str
        Path to the .lvm file to read.
    force_index : int, default=2
        1-based column index for the force data.
    displ_index : int, default=3
        1-based column index for the displacement (stroke) data.
    mid_lvdt_ind : int or list of int, optional
        Column index/indices for the middle LVDTs.
    left_lvdt_ind : int or list of int, optional
        Column index/indices for the left LVDTs.
    right_lvdt_ind : int or list of int, optional
        Column index/indices for the right LVDTs.

    Returns
    -------
    df_new : pandas.DataFrame
        Extracted data as a DataFrame with columns renamed:
        ['Force (kN)', 'Stroke (mm)', 'Mid_1 (mm)', 'Mid_2 (mm)',
         'Left_1 (mm)', 'Left_2 (mm)', 'Right_1 (mm)', 'Right_2 (mm)'].
        Only existing columns are included; missing columns are ignored.
    file_base_name : str
        Base name of the file without the '.lvm' extension.

    Notes
    -----
    - Automatically detects the start of the data by locating the last
      occurrence of '***End_of_Header***' in the file.
    - Converts all columns to numeric values; non-numeric entries
      are coerced to NaN.
    - The last column is dropped assuming it is empty.
    - Single integer indices are automatically converted to lists.
    - LVDT columns are combined in the order: mid -> left -> right.
    """
    
    mid_lvdt_ind = mid_lvdt_ind or []
    left_lvdt_ind = left_lvdt_ind or []
    right_lvdt_ind = right_lvdt_ind or []
    
    if isinstance(mid_lvdt_ind, int):
        mid_lvdt_ind = [mid_lvdt_ind]
    if isinstance(left_lvdt_ind, int):
        left_lvdt_ind = [left_lvdt_ind]
    if isinstance(right_lvdt_ind, int):
        right_lvdt_ind = [right_lvdt_ind]
    
    lvdt_indices = mid_lvdt_ind + left_lvdt_ind + right_lvdt_ind
    
    with open(file_name, 'r') as f:
        lines = f.readlines()
    start_idx = max(i for i, line in enumerate(lines) if "***End_of_Header***" in line) + 1
    df = pd.read_csv(file_name, sep="\t", skiprows=start_idx)
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.drop(df.columns[-1], axis=1)
    
    user_indices = [force_index, displ_index] + lvdt_indices
    existing_cols = [df.columns[i-1] for i in user_indices if i-1 < len(df.columns)]
    
    df_new = df[existing_cols].copy()
    
    col_names = ['Force (kN)','Stroke (mm)','Mid_1 (mm)','Mid_2 (mm)','Left_1 (mm)','Left_2 (mm)','Right_1 (mm)','Right_2 (mm)']
    df_new.columns = col_names[:len(existing_cols)]
    
    return df_new, file_name[:-4]

def beam_four_point_bending (data: DataFrame, 
                        width: float, 
                        depth: float, 
                        beam_span: float):
    """
    Perform four-point bending analysis to calculate apparent and true modulus of elasticity.

    Parameters
    ----------
    data : tuple
        A tuple containing:
        - data[0] : pandas.DataFrame
            Experimental dataset with columns:
            - 'Moog Force_kN' : Applied load (kN).
            - 'LVDT 1_mm' ... 'LVDT 6_mm' : Deflections from six LVDTs (mm).
        - data[1] : str
            Sample name identifier.
    width : float
        Beam specimen width (mm).
    depth : float
        Beam specimen depth (mm).
    beam_span : float
        Beam span length (mm).

    Returns
    -------
    tuple
        (sample_name, results) where:
        - sample_name : str
            Name of the processed sample.
        - results : dict
            Dictionary containing:
            - "E_app" : float
                Apparent modulus of elasticity (MPa).
            - "E_true" : float
                True modulus of elasticity (MPa).

    Notes
    -----
    - Apparent modulus (E_app) is calculated from mid-span deflection (LVDT 3 & 4).
    - True modulus (E_true) is calculated from relative deflection (mid-span vs. supports).
    - Load range for regression is limited to 10–40% of ultimate load.
    """
    
    import pandas as pd
    import numpy as np

    #Experimental test data post-process
    sample_name = data[1]
    force = data[0]['Force (kN)'] * 1000
    delta_1 = abs(data[0]['Left_1 (mm)'])
    delta_2 = abs(data[0]['Left_2 (mm)'])
    delta_3 = abs(data[0]['Mid_1 (mm)'])
    delta_4 = abs(data[0]['Mid_2 (mm)'])
    delta_5 = abs(data[0]['Right_1 (mm)'])
    delta_6 = abs(data[0]['Right_2 (mm)'])

    F_ult = force.max()
    f_b = (F_ult * beam_span) / (width * depth **2) #MPa

    
    delta_ms = (delta_3 + delta_4)/2
    delta_rel = delta_ms - (delta_1 + delta_2 + delta_5 + delta_6) / 4
    
    
    lower_bound = 0.1 * F_ult
    upper_bound = 0.4 * F_ult

    calcs_reg = (lower_bound <= force) & (force <= upper_bound)
    
    F_ms = force[calcs_reg]
    delta_ms_calcs = delta_ms[calcs_reg]
    delta_rel_calcs = delta_rel[calcs_reg]
    
    Delta_ms, intercept_ms = np.polyfit(delta_ms_calcs,F_ms,1)
    Delta_rel, intercept_rel = np.polyfit(delta_rel_calcs,F_ms,1)
    
    E_app = (23/108) * (beam_span/depth)**3 * Delta_ms * (1/width)
    E_true = (1/36) *  (beam_span/depth)**3 * Delta_rel * (1/width)
    
    results = {
        "E_app": E_app,
        "E_true": E_true,
    }

    print(f"Sample Name: {sample_name}")
    print('-' * 40)
    return sample_name, results

