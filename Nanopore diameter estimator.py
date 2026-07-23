# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 14:52:19 2023

Run this code to process the IV from abf file in batch from a single folder.
Output all necessary files, plots and information.
The assumption is that in the same folder, you will have IV curve from the same programme in the same condition.

@author: chalmers
"""

#%%`
import tkinter as tk
from tkinter import filedialog
import pyabf
import numpy as np
import pandas as pd
import math
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from palettable.cartocolors.qualitative import Vivid_10
from palettable.cartocolors.qualitative import Bold_10
import matplotlib as mpl
import matplotlib.ticker as ticker
import cowsay
import pathlib
from pathlib import Path
from matplotlib.ticker import FormatStrFormatter
#%%
plt.close()
#%% colour
Palette = ["#b4396f", "#379cd2", "#aba747", "#bc8fda", "#009374", "#efbd36", "#02531d", "#8adc30", "#26496d", "#bfd6fa"]
#%% essential import, export and file opener
# Get the name of the dataframe
def get_df_name(dataframe): # get the name of the dataframe
    name =[x for x in globals() if globals()[x] is dataframe][0]
    return name
# Only load folder path
def folder_path(): 
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    return filedialog.askdirectory()
folder_path = folder_path()
folder_name = Path(folder_path).stem
abf_files = sorted(glob.glob(os.path.join(folder_path, "*.abf")))
# Export dataframe to csv
def csv_export_dataframe(data, File_name="data", Path=folder_path):
    csv = os.path.join(Path, File_name + '.csv')
    data.to_csv(csv, index=False)
    return csv
def figure_export(Path, Name):
    return plt.savefig(os.path.join(Path, Name)+'.png', format = 'png', dpi = 300)
def figure_export_png(Path = folder_path, Name = 'Combined data for plot' + '_figure' + '_png'):
    return plt.savefig(os.path.join(Path, Name)+'.png', format = 'png', dpi = 300)
def figure_export_svg(Path = folder_path, Name = 'Combined data for plot' + '_figure' + '_svg'):
    return plt.savefig(os.path.join(Path, Name)+'.svg', format = 'svg')
# Export dictionary to Excel
def excel_export(data_dict, Name, Path = folder_path):
    excel_path = os.path.join(Path, Name) + '.xlsx'
    with pd.ExcelWriter(excel_path) as excel_writer:
        for key, df in data_dict.items():
            df.to_excel(excel_writer, index=False, sheet_name=key)
    return
#%% Function to read into abf
def Channel_0_Current_channel(file_path):
    trace_abf = pyabf.ABF(file_path)
    trace_abf.setSweep(sweepNumber=0, channel=0)

    raw_unit = trace_abf.adcUnits[0]  # e.g., 'A', 'mA', 'µA', 'nA', etc.
    Time_axis = trace_abf.sweepX
    Current_axis = trace_abf.sweepY

    # Standardise unit symbols
    if raw_unit == 'uA':  # pyABF sometimes uses 'uA' instead of 'µA'
        raw_unit = 'µA'

    unit_factors = {'A': 1,'mA': 1e-3,'µA': 1e-6,'nA': 1e-9,'pA': 1e-12,'fA': 1e-15}
    export_amp_unit = 'nA'
    if raw_unit not in unit_factors:
        raise ValueError(f"Unknown current unit: {raw_unit}")
    # Convert current to nA
    factor_amp = unit_factors[raw_unit] / unit_factors[export_amp_unit]
    Current_axis = Current_axis * factor_amp

    df_channel0 = pd.DataFrame({'Time (s)': Time_axis,'Current (nA)': Current_axis})
    return df_channel0
def Channel_1_Voltage_channel(file_path):
    trace_abf = pyabf.ABF(file_path)
    trace_current = trace_abf.setSweep(sweepNumber = 0, channel = 1)
    Time_axis = trace_abf.sweepX
    Voltage_axis = trace_abf.sweepY
    df_channel1 = pd.DataFrame({'Voltage (mV)': Voltage_axis})
    return df_channel1
def Merge_CV(file_path):
    df_Current = Channel_0_Current_channel(file_path)
    df_Voltage = Channel_1_Voltage_channel(file_path)
    df_CV = pd.concat([df_Current, df_Voltage], axis = 1)
    return df_CV
def df_CV_Cleaned(dataframe, TimeFrom = 5.3, TimeTo = 15.3):
    df_time_window = dataframe[(dataframe['Time (s)'] >= TimeFrom) & (dataframe['Time (s)'] <= TimeTo)]
    df_time_window_trimmed = df_time_window.iloc[::10, :]
    return df_time_window, df_time_window_trimmed
#%% Function to plot IV of each file
def Plot_IV(
        dataframe,
        #LineColour = Vivid_10.hex_colors[0], 
        LineColour = Palette[0],
            ylimitbottom = -1.0,
            ylimittop = 6.0
            ):
    sns.set_theme(style = 'ticks')
    mpl.rcParams['axes.spines.left'] = True
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = True

    fig, ax = plt.subplots(figsize = (7, 7))
    ax.plot(dataframe['Voltage (mV)'], 
            dataframe['Current (nA)'], 
            color = LineColour,
            #label = 'PBS'
            linewidth = 5,
            zorder = 10)

    ax.axvline(x = 0,
               alpha = 0.2,
               linestyle = '--',
               color = '#666666',
               linewidth = 2)

    ax.axhline(y = 0,
               alpha = 0.2,
               linestyle = '--',
               color = '#666666',
               linewidth = 2)
    
    # force to have 1 decimal place
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    
    # Dynamic Y-axis limits if not provided
    y_min = dataframe['Current (nA)'].min()
    y_max = dataframe['Current (nA)'].max()
    ylimitbottom = y_min - 1.0 if ylimitbottom is None else ylimitbottom
    ylimittop = y_max + 1.0 if ylimittop is None else ylimittop
    # Round down to nearest multiple of 2 for bottom, up for top

    ax.set_xlim([-510, 510])
    ax.set_ylim([ylimitbottom, ylimittop])

    #ax.spines['left'].set_position('center')
    #ax.spines['bottom'].set_position('center')
    #ax.errorbar(df_reduced['Voltage (mV)'], df_reduced['Current (nA)'], yerr = df_reduced['Upper Error'], capsize=5, markersize=4, fmt='x', color='#666666')

    ax.tick_params(axis='x', labelsize=16)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.set_xlabel('Voltage (mV)', fontsize = 18)
    ax.spines['bottom'].set_position(('outward', 5)) 

    ax.tick_params(axis='y', labelsize=16)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.set_ylabel('Current (nA)', fontsize = 18)
    ax.spines['left'].set_position(('outward', 5)) 

    plt.tight_layout()
    return plt.show()
#%% Loop through all ABF files
def batch_process():
    for abf_file in abf_files:
        File_name = pathlib.Path(abf_file).stem

        # Process ABF
        df_CV = Merge_CV(file_path=abf_file)
        df_time_window, df_time_window_trimmed = df_CV_Cleaned(dataframe=df_CV, TimeFrom=5.35, TimeTo=15.35) # My settings
        #df_time_window, df_time_window_trimmed = df_CV_Cleaned(dataframe=df_CV, TimeFrom=3.19, TimeTo=9.2)

        # Export CSVs
        csv_export_dataframe(df_CV, File_name=File_name + '_all data', Path=folder_path)
        csv_export_dataframe(df_time_window, Path=folder_path, File_name=File_name + '_time window')
        csv_export_dataframe(df_time_window_trimmed, Path=folder_path, File_name=File_name + '_time window_trim')
        
        # Plot & Save
        Plot_IV(
            dataframe=df_time_window_trimmed,
            #LineColour=Vivid_10.hex_colors[0],
            LineColour = Palette[0],
            ylimitbottom=None,
            ylimittop=None
        )
        figure_export(Path=folder_path, Name=File_name + '_figure')
    return
batch_process()
#%% Combine csv into a single excel file
# Get all files ending in "_trim.csv"
trimmed_csv_files = sorted(glob.glob(os.path.join(folder_path, '*_trim.csv')))
# Read and store as Record_01, Record_02, ... in a dictionary
Combined_recording = {}
for i, file in enumerate(trimmed_csv_files, start=1):
    df = pd.read_csv(file)
    key = f"Record_{i:02d}"
    Combined_recording[key] = df
excel_export(data_dict=Combined_recording, Name="Combined recording", Path=folder_path)
#%% Export an excel with sheets ready for IV plotting
# Create a new dictionary with empty dataframes
dfs_combine_types = {
                    "df_Current(nA)": pd.DataFrame(),
                    "df_Voltage(mV)": pd.DataFrame()
                    }
# Populate them from Combined_recording
for i, (key, df) in enumerate(Combined_recording.items()):
    dfs_combine_types["df_Current(nA)"][f"Record_{i+1:02d}"] = df.iloc[:, 1]  # 2nd column
    dfs_combine_types["df_Voltage(mV)"][f"Record_{i+1:02d}"] = df.iloc[:, 2]  # 3rd column

# Calculate averages, std, sem
df_voltage = dfs_combine_types["df_Voltage(mV)"]
df_current = dfs_combine_types["df_Current(nA)"]

df_calculated_data_for_plot = pd.DataFrame({
                                            "Voltage (mV)": df_voltage.mean(axis=1),
                                            "Current (nA)": df_current.mean(axis=1),
                                            "Current S.D.": df_current.std(axis=1),
                                            "Current S.E.M.": df_current.sem(axis=1)
                                            })
# Add to dfs_combine_types as the first sheet
dfs_combine_types = {"df_calculated_data_for_plot": df_calculated_data_for_plot, **dfs_combine_types}
# Export final structure to Excel
excel_export(data_dict=dfs_combine_types, Name="! Combined data for plot", Path=folder_path)
#%% resistance and ICR calculation
def df_window(dataframe, VoltageLow=-100, VoltageHigh=100, ExcludeRange=(-49, 49)):
    df_voltage_window = dataframe[
        ((dataframe['Voltage (mV)'] >= VoltageLow) & (dataframe['Voltage (mV)'] <= ExcludeRange[0])) |
        ((dataframe['Voltage (mV)'] >= ExcludeRange[1]) & (dataframe['Voltage (mV)'] <= VoltageHigh))
    ]
    return df_voltage_window
"""ExcludRange = (-49, 49) means to exclude anything between -49 to 49."""
#df_voltage_window = df_window(dataframe=df, VoltageLow=-100, VoltageHigh=100, ExcludeRange=(-49, 49))
def calculate_resistance(dataframe):
    dataframe = dataframe.copy()  # Avoids SettingWithCopyWarning
    dataframe.loc[:, 'Resistance (MOhm)'] = (dataframe['Voltage (mV)'] / dataframe['Current (nA)']) * 1
    return dataframe
df_voltage_window_resistance = calculate_resistance(df_window(dataframe=dfs_combine_types['df_calculated_data_for_plot'], VoltageLow=-100, VoltageHigh=100, ExcludeRange=(-49, 49)))
average_resistance = df_voltage_window_resistance['Resistance (MOhm)'].mean()
average_resistance_SD = df_voltage_window_resistance['Resistance (MOhm)'].std()
df_resistance_value = pd.DataFrame({'Average resistance (MOhm)': [average_resistance], 'average_resistance_SD (MOhm)': [average_resistance_SD]})
print(f'Average Resistance: {average_resistance:.2f} +/-{average_resistance_SD:.2f} MOhm')

#%% Calculate Current Rectification Ratio (ICR)
def calculate_icr(dataframe, positive_range=(450, 500), negative_range=(-500, -450)):
    """
    Calculate the Current Rectification Ratio (ICR).
    ICR = |(mean current at +Vrange) / (mean current at -Vrange)|
    """
    df_positive = dataframe[(dataframe['Voltage (mV)'] >= positive_range[0]) & 
                            (dataframe['Voltage (mV)'] <= positive_range[1])]
    df_negative = dataframe[(dataframe['Voltage (mV)'] >= negative_range[0]) & 
                            (dataframe['Voltage (mV)'] <= negative_range[1])]

    if df_positive.empty or df_negative.empty:
        print("Warning: Data does not contain points in the ±500 mV regions.")
        return np.nan

    mean_pos = df_positive['Current (nA)'].mean()
    mean_neg = df_negative['Current (nA)'].mean()
    std_pos = df_positive['Current (nA)'].std()
    std_neg = df_negative['Current (nA)'].std()
    std_sum = std_pos + std_neg
    global std_mean
    std_mean = std_sum/2
    
    icr = abs(mean_pos / mean_neg) if mean_neg != 0 else np.nan
    return icr

def export_icr(dataframe, file_name_prefix="ICR", path=folder_path):
    icr_value = calculate_icr(dataframe)
    if np.isnan(icr_value):
        print("ICR could not be calculated (missing ±500 mV data).")
        return None
    # Create a small dataframe for CSV export
    df_icr = pd.DataFrame({'Average ICR': [icr_value], 'ICR SD': [std_mean]})
    icr_file_name = f"ICR_{round(icr_value, 4)}"
    csv_file_path = csv_export_dataframe(df_icr, File_name=icr_file_name, Path=path)
    #print(f"ICR exported as CSV to: {csv_file_path}")
    return icr_value, csv_file_path

icr_value, icr_csv_path = export_icr(dataframe = dfs_combine_types['df_calculated_data_for_plot'], file_name_prefix="_")
print(f'Average Ion Current recification: {icr_value:.2f} +/-{std_mean:.2f}')
csv_file_path = csv_export_dataframe(df_resistance_value, File_name = str(round(average_resistance)) + '_' + str(round(average_resistance_SD)) + ' MOhm', Path = folder_path)
#print(f'Resistance exported as CSV to: {csv_file_path}')

#%% Trim a single dataframe to reduce row numbers
def trim_dataframe(dataframe, step=100):
    max_length = len(dataframe)
    indices_to_retain = range(0, max_length, step)
    trimmed_dataframe = dataframe.iloc[indices_to_retain]
    return trimmed_dataframe
IV_summary_trim = trim_dataframe(dataframe=dfs_combine_types['df_calculated_data_for_plot'], step=5)
#%% Plot IV with error bars
def Plot_IV_error_bars(
                           dataframe, 
                           error_type, #SD or SEM
                           ylimitbottom = None,
                           ylimittop = None
                           ):
    #colour = Vivid_10.hex_colors
    colour = Palette
    #colour = ['#5D69B1','#52BCA3','#99C945','#CC61B0','#24796C','#DAA51B','#2F8AC4','#764E9F','#ED645A','#E58606']
    sns.set(style='ticks', #with ticks
            palette=colour,
            )
    mpl.rcParams['axes.spines.left'] = True
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = True
    
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(dataframe['Voltage (mV)'],
            dataframe['Current (nA)'],
            linewidth = 2,
            alpha = 1.0,
            zorder=10)
    if error_type == "S.D.":
        ax.errorbar(dataframe['Voltage (mV)'],
                    dataframe['Current (nA)'],
                    yerr=dataframe['Current S.D.'],
                    linewidth=1,
                    markersize=0,
                    fmt='x',
                    color= '#808080',
                    capsize = 2,
                    alpha = 0.8,
                    )
    elif error_type == "S.E.M.":
        ax.errorbar(dataframe['Voltage (mV)'],
                    dataframe['Current (nA)'],
                    yerr=dataframe['Current S.E.M.'],
                    linewidth=1,
                    markersize=0,
                    fmt='x',
                    color= '#808080',
                    capsize = 2,
                    alpha = 0.8,
                    )
    else:
        print("error_type must be either Standard deviation (S.D.) or Standard Error of the Means (S.E.M.)")
    
    ax.axvline(x = 0,alpha = 0.2,linestyle = '--',color = '#666666',linewidth = 2)
    ax.axhline(y = 0,alpha = 0.2,linestyle = '--',color = '#666666',linewidth = 2)
    
    # force to have 1 decimal place
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    
    # Dynamic Y-axis limits if not provided
    y_min = dataframe['Current (nA)'].min()
    y_max = dataframe['Current (nA)'].max()
    ylimitbottom = y_min - 1.0 if ylimitbottom is None else ylimitbottom
    ylimittop = y_max + 1.0 if ylimittop is None else ylimittop
    
    ax.set_xlim([-510, 510])
    ax.set_ylim([ylimitbottom, ylimittop])
    
    #ax.legend()
    #ax.legend().remove()

    #ax.spines['left'].set_position('center')
    #ax.spines['bottom'].set_position('center')
    #ax.errorbar(df_reduced['Voltage (mV)'], df_reduced['Current (nA)'], yerr = df_reduced['Upper Error'], capsize=5, markersize=4, fmt='x', color='#666666')

    ax.tick_params(axis='x', labelsize=16)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.set_xlabel('Voltage (mV)', fontsize = 18)
    ax.spines['bottom'].set_position(('outward', 5)) 

    ax.tick_params(axis='y', labelsize=16)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.set_ylabel('Current (nA)', fontsize = 18)
    ax.spines['left'].set_position(('outward', 5)) 
    
    #legend_elements = [Line2D([0], [0], linestyle = '-', color=Vivid_10.hex_colors[0], lw=2, label='N = 8 nanopores')]
    #ax.legend(handles=legend_elements, loc='lower right', fontsize = 14)
    
    plt.tight_layout()
    return plt.show()

Plot_IV_error_bars(dataframe = IV_summary_trim, error_type = "S.E.M.", ylimitbottom = None, ylimittop = None)
figure_export_png(Path = folder_path, Name = 'Combined data for plot' + '_IV_SEM_error_png')
figure_export_svg(Path = folder_path, Name = 'Combined data for plot' + '_IV_SEM_error_svg')

Plot_IV_error_bars(dataframe = IV_summary_trim, error_type = "S.D.", ylimitbottom = None, ylimittop = None)
figure_export_png(Path = folder_path, Name = 'Combined data for plot' + '_IV_SD_error_png')
figure_export_svg(Path = folder_path, Name = 'Combined data for plot' + '_IV_SD_error_svg')
#%% Plot IV with shade as error
def Plot_IV_shade_error(dataframe, 
                        error_type, #SD or SEM
                        ylimitbottom=None, 
                        ylimittop=None):
    #colour = Vivid_10.hex_colors
    colour = Palette
    sns.set(style='ticks', palette=colour)
    
    mpl.rcParams['axes.spines.left'] = True
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.bottom'] = True
    
    fig, ax = plt.subplots(figsize=(7, 7))
    voltage = dataframe['Voltage (mV)']
    current = dataframe['Current (nA)']
    if error_type == "S.E.M.":
        error_shade = dataframe['Current S.E.M.']
    elif error_type == "S.D.":
        error_shade = dataframe['Current S.D.']
    else:
        print("error_type must be either Standard deviation (S.D.) or Standard Error of the Means (S.E.M.)")
        
    # Plot the main line
    ax.plot(voltage, 
            current, 
            linewidth = 2, 
            alpha = 1.0, 
            zorder = 10)
    # Fill the area between (current + sem) and (current - sem)
    ax.fill_between(voltage, 
                    current - error_shade, 
                    current + error_shade,
                    alpha = 0.2)

    
    # Add vertical and horizontal lines
    ax.axvline(x=0, alpha=0.2, linestyle='--', color='#666666', linewidth=2)
    ax.axhline(y=0, alpha=0.2, linestyle='--', color='#666666', linewidth=2)
    
    # force to have 1 decimal place
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    
    # Dynamic Y-axis limits if not provided
    y_min = dataframe['Current (nA)'].min()
    y_max = dataframe['Current (nA)'].max()
    ylimitbottom = y_min - 1.0 if ylimitbottom is None else ylimitbottom
    ylimittop = y_max + 1.0 if ylimittop is None else ylimittop
    
    ax.set_xlim([-510, 510])
    ax.set_ylim([ylimitbottom, ylimittop])
    
    # Set labels and ticks
    ax.tick_params(axis='x', labelsize=16)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.set_xlabel('Voltage (mV)', fontsize=18)
    ax.spines['bottom'].set_position(('outward', 5))
    
    ax.tick_params(axis='y', labelsize=16)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.set_ylabel('Current (nA)', fontsize=18)
    ax.spines['left'].set_position(('outward', 5))
    
    # Create custom legend
    #legend_elements = [Line2D([0], [0], linestyle='-', color=colour[0], lw=2, label='N = 8 nanopores')]
    #ax.legend(handles=legend_elements, loc='lower right', fontsize=14)
    
    plt.tight_layout()
    return plt.show()

Plot_IV_shade_error(dataframe = IV_summary_trim, error_type = "S.E.M.", ylimitbottom = None, ylimittop = None)
figure_export_png(Path = folder_path, Name = 'Combined data for plot' + '_IV_SEM_Shade_error_png')
figure_export_svg(Path = folder_path, Name = 'Combined data for plot' + '_IV_SEM_Shade_error_svg')


Plot_IV_shade_error(dataframe = IV_summary_trim, error_type = "S.D.", ylimitbottom = None, ylimittop = None)
figure_export_png(Path = folder_path, Name = 'Combined data for plot' + '_IV_SD_Shade_error_png')
figure_export_svg(Path = folder_path, Name = 'Combined data for plot' + '_IV_SD_Shade_error_svg')

