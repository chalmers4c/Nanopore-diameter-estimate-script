# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 13:08:01 2021

Pore Radius Estimation

useful value:
    PBS conductivity: 1.4 S/m
    0.1M KCl conductivity : 1.2 S/m
    3M KCl conductivity : 39 S/cm
@author: eenfma
"""
import numpy
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import io
import sys
#%%
# Select folder
def folder_path():
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    return filedialog.askdirectory()

folder_path = folder_path()
folder_name = Path(folder_path).stem
#%%
def Nanopore_radius_estimation(Resistance_MOhm, Solution_conductivity= 1.2):
    R_measured = Resistance_MOhm * 1e+6 # Ohm (measured resistance via potentiometry)
    d_taper = 4/1000 # m  (taper length)
    #d_taper = 50/1000 # for ms tip
    C_solution = Solution_conductivity # S/m (solution conductivity)
    rho = 1/C_solution # (PBS resistivity)
    r_shank = 0.25/1000 # m (radius of shank = ID/2 capillary)
    #theta = numpy.arctan(r_shank/d_taper) # in radians
    #theta = 0.004363323 # 0.25 degree in radian
    #theta = 0.0174533 # 1 degree in radian
    #theta = 0.0349066 # 2 degree in radian
    #theta = 0.0523599 # 3 degree in radian
    #theta = 0.0698132 # 4 degree in radian
    theta = 0.0872665 # 5 degree in radian
    #theta = 0.10472 #6 degree in radian
    #theta = 0.122173 # 7 degree in radian

    r_tip = (rho*d_taper)/(numpy.pi*r_shank*R_measured)

    r_tip_compl= (1/(C_solution*numpy.pi*R_measured*numpy.tan(theta))) + (1/(4*C_solution*R_measured))
    
    print('theta = ', theta)
    print('Measured Resistance = ', R_measured*1e-6, 'MOhm', ' Pore radius = ', numpy.round(r_tip*1e+9, decimals =2), 'nm')
    print('Measured Resistance (complete equation) = ', R_measured*1e-6, 'MOhm', ' Pore radius = ', numpy.round(r_tip_compl*1e+9, decimals =2), 'nm')
    print('Measured Resistance (complete equation) = ', R_measured*1e-6, 'MOhm', ' Pore diameter = ', numpy.round(r_tip_compl*1e+9, decimals =2)*2, 'nm')
    
    radius = []
    return
#%% Simple run
Nanopore_radius_estimation(Resistance_MOhm = 64.9, #as measured in MegaOhm
                           Solution_conductivity= 1.2 #conductivity of the solution, m/S, 1.45 for 1XPBS
                           )
#%%  3M KCl
Nanopore_radius_estimation(#Resistance_MOhm = 24.11, #as measured in MegaOhm
                           Resistance_MOhm = 40.3,
                           Solution_conductivity= 39 #conductivity of the solution, m/S, 1.45 for 1XPBS
                           )
#%%
#%% function calculation
#resistance_values = [124.1184, 158.1375, 192.1274, 215.7369]
resistance_values = [40.3]
# Redirect print output to a string buffer
buffer = io.StringIO()
sys_stdout = sys.stdout  # Backup original stdout
sys.stdout = buffer



for R in resistance_values:
    print(f"\n--- Calculating for Resistance = {R} MOhm ---")
    #Nanopore_radius_estimation(Resistance_MOhm=R, Solution_conductivity=1.2)
    Nanopore_radius_estimation(Resistance_MOhm=R, Solution_conductivity=39)



#Nanopore_radius_estimation(Resistance_MOhm = 309, #as measured in MegaOhm
#                           Solution_conductivity= 1.2 #conductivity of the solution, m/S, 1.45 for 1XPBS
#                           )

#%% Export print file to a folder:
sys.stdout = sys_stdout
output_text = buffer.getvalue()
buffer.close()

print(output_text)

output_file_path = Path(folder_path) / "nanopore_radius_results.txt"
with open(output_file_path, "w") as f:
    f.write(output_text)

print(f"Results saved to: {output_file_path}")

