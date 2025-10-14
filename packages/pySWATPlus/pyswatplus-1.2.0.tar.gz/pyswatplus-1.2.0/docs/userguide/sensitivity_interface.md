# Sensitivity Interface

Sensitivity interface helps quantify how variation in input parameters affects model outputs. This tutorial demonstrates how to perform sensitivity analysis on SWAT+ model parameters.  


## Configuration Settings

Before running a sensitivity simulation, you must define the necessary configuration settings.  
These settings specify key parameters such as the simulation timeline, output print options, and other essential model controls.


```python
import pySWATPlus

# Initialize the project's TxtInOut folder
txtinout_reader = pySWATPlus.TxtinoutReader(
    tio_dir=r"C:\Users\Username\project\Scenarios\Default\TxtInOut"
)

# Copy required files to an empty simulation directory
sim_dir = r"C:\Users\Username\custom_folder" 
sim_dir = txtinout_reader.copy_required_files(
    sim_dir=sim_dir
)

# Initialize TxtinoutReader with the simulation directory
sim_reader = pySWATPlus.TxtinoutReader(
    tio_dir=sim_dir
)

# Disable CSV file generation to save time
sim_reader.disable_csv_print()

# Disable daily time series in print.prt (saves time and space)
sim_reader.enable_object_in_print_prt(
    obj=None,
    daily=False,
    monthly=True,
    yearly=True,
    avann=True
)

# Set simulation period and run a trial simulation to verify expected time series outputs
sim_reader.run_swat(
    begin_date='01-Jan-2010',
    end_date='31-Dec-2012',
    warmup=1,
    print_prt_control={
        'channel_sd': {}
    }  # enable daily time series for 'channel_sd'
```

## Sensitivity Simulation

This high-level interface builds on the above configuration to run sensitivity simulations using sampling, powered by the [SALib](https://github.com/SALib/SALib) Python package.  
Currently, it supports [Sobol](https://doi.org/10.1016/S0378-4754(00)00270-6) sampling from a defined parameter space. The interface provides:

- Automatic generation of samples for the parameter space  
- Parallel computation to accelerate simulations  
- Output extraction with filtering options  
- Structured export of results for downstream analysis


```python
# Sensitivity parameter space
parameters = [
    {
        'name': 'esco',
        'change_type': 'absval',
        'lower_bound': 0,
        'upper_bound': 1
    },
    {
        'name': 'perco',
        'change_type': 'absval',
        'lower_bound': 0,
        'upper_bound': 1
    }
]

# Target data extraction from sensitivity simulation
extract_data = {
    'channel_sdmorph_yr.txt': {
        'has_units': True,
        'ref_day': 15,
        'ref_month': 6,
        'apply_filter': {'gis_id': [561]},
        'usecols': ['gis_id', 'flo_out']
    },
    'channel_sd_mon.txt': {
        'has_units': True,
        'begin_date': '01-Jun-2011',
        'ref_day': 15,
        'apply_filter': {'name': ['cha561'], 'yr': [2012]},
        'usecols': ['gis_id', 'flo_out']
    }
}

# Sensitivity simulation
if __name__ == '__main__':
    output = pySWATPlus.SensitivityAnalyzer().simulation_by_sample_parameters(
        parameters=parameters,
        sample_number=1,
        sensim_dir=r"C:\Users\Username\simulation_folder",
        txtinout_folder=sim_dir,
        extract_data=extract_data
    )
    print(output)
```

## Sensitivity Indices

Sensitivity indices (first, second, and total orders) are computed using the indicators available in the `pySWATPlus.PerformanceMetrics` class, along with their confidence intervals.


```python
output = pySWATPlus.SensitivityAnalyzer().parameter_sensitivity_indices(
    sensim_file=r"C:\Users\Username\simulation_folder\sensitivity_simulation.json",
    df_name='channel_sd_mon_df',
    sim_col='flo_out',
    obs_file=r"C:\Users\Username\observed_folder\discharge_monthly.csv",
    date_format='%Y-%m-%d',
    obs_col='discharge',
    indicators=['KGE', 'RMSE'],
    json_file=r"C:\Users\Username\sensitivity_indices.json"
)
```