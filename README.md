# Input for IV profile processing.py
1. The script is written based on data from Molecular Devices' sweep, for custom usage, please adjust the input code.
2. The script is meant to take only a window of data, please adjust the window of data so that the voltage starts from -500 mV to +500 mV.
3. The script is meant for you to load a folder of repeated IV measurements and process everything for you. Thus if the folder contains IV from different pore dimension, it will not work.

# Output for IV profile processing.py
1. individual IV curve
2. Plot of IV curve with Standard deviation
3. The Ion current rectification ratio
4. The resistance in MOhm

# Input for Nanopore Diameter Calculation.py
1. The calculation of pore diameter is based on Perry et al. (https://pubs.acs.org/doi/10.1021/acs.analchem.6b01095), with assumptions on cone (theta) angle, 
2. Depending on the electrolyte used to fill the nanopore, the estimation will be different, here are some usful value:
     PBS conductivity: 1.4 S/m
     0.1M KCl conductivity : 1.2 S/m
     3M KCl conductivity : 39 S/cm
3. You must input the resistance calculated from the IV profile processing.py and the solution conductivity.

# Output for Nanopore Diameter Calculation.py
Below is a typical output from the script, it will first indicate the cone angle, followed by the estimation using partial equation (omit the cone angle) or complete equation.
theta =  0.0872665
Measured Resistance =  64.9 MOhm  Pore radius =  65.39 nm
Measured Resistance (complete equation) =  64.9 MOhm  Pore radius =  49.93 nm
Measured Resistance (complete equation) =  64.9 MOhm  Pore diameter =  99.86 nm
