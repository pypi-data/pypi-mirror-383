import pandas
import pathlib
import typing
from . import utils
from . import validators


class PerformanceMetrics:
    '''
    Provide functionality to compute errors between simulated and ovserved values.
    '''

    @property
    def indicator_names(
        self
    ) -> dict[str, str]:
        '''
        Return a dictionary of available indicators. Keys are the commonly used abbreviations,
        and values are the corresponding full indicator names.
        '''

        abbr_name = {
            'NSE': 'Nash-Sutcliffe Efficiency',
            'KGE': 'Kling-Gupta Efficiency',
            'MSE': 'Mean Squared Error',
            'RMSE': 'Root Mean Squared Error',
            'PBIAS': 'Percent Bias',
            'MARE': 'Mean Absolute Relative Error'
        }

        return abbr_name

    def compute_nse(
        self,
        df: pandas.DataFrame,
        sim_col: str,
        obs_col: str
    ) -> float:
        '''
        Calculate the [`Nash-Sutcliffe Efficiency`](https://doi.org/10.1016/0022-1694(70)90255-6)
        metric between simulated and observed values

        Args:
            df (pandas.DataFrame): DataFrame containing at least two columns with simulated and observed values.

            sim_col (str): Name of the column containing simulated values.

            obs_col (str): Name of the column containing observed values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.compute_nse
            ),
            vars_values=locals()
        )

        # Simulation values
        sim_arr = df[sim_col].astype(float)

        # Observed values
        obs_arr = df[obs_col].astype(float)

        # Output
        numerator = ((sim_arr - obs_arr).pow(2)).sum()
        denominator = ((obs_arr - obs_arr.mean()).pow(2)).sum()
        output = float(1 - numerator / denominator)

        return output

    def compute_kge(
        self,
        df: pandas.DataFrame,
        sim_col: str,
        obs_col: str
    ) -> float:
        '''
        Calculate the [`Kling-Gupta Efficiency`](https://doi.org/10.1016/j.jhydrol.2009.08.003)
        metric between simulated and observed values

        Args:
            df (pandas.DataFrame): DataFrame containing at least two columns with simulated and observed values.

            sim_col (str): Name of the column containing simulated values.

            obs_col (str): Name of the column containing observed values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.compute_kge
            ),
            vars_values=locals()
        )

        # Simulation values
        sim_arr = df[sim_col].astype(float)

        # Observed values
        obs_arr = df[obs_col].astype(float)

        # Pearson correlation coefficient (r)
        r = sim_arr.corr(obs_arr)

        # Variability of prediction errors
        alpha = sim_arr.std() / obs_arr.std()

        # Bias
        beta = sim_arr.mean() / obs_arr.mean()

        # Output
        output = float(1 - pow(pow(r - 1, 2) + pow(alpha - 1, 2) + pow(beta - 1, 2), 0.5))

        return output

    def compute_mse(
        self,
        df: pandas.DataFrame,
        sim_col: str,
        obs_col: str
    ) -> float:
        '''
        Calculate the `Mean Squared Error` metric between simulated and observed values

        Args:
            df (pandas.DataFrame): DataFrame containing at least two columns with simulated and observed values.

            sim_col (str): Name of the column containing simulated values.

            obs_col (str): Name of the column containing observed values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.compute_mse
            ),
            vars_values=locals()
        )

        # Simulation values
        sim_arr = df[sim_col].astype(float)

        # Observed values
        obs_arr = df[obs_col].astype(float)

        # Output
        output = float(((sim_arr - obs_arr).pow(2)).mean())

        return output

    def compute_rmse(
        self,
        df: pandas.DataFrame,
        sim_col: str,
        obs_col: str
    ) -> float:
        '''
        Calculate the `Root Mean Squared Error` metric between simulated and observed values.

        Args:
            df (pandas.DataFrame): DataFrame containing at least two columns with simulated and observed values.

            sim_col (str): Name of the column containing simulated values.

            obs_col (str): Name of the column containing observed values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.compute_rmse
            ),
            vars_values=locals()
        )

        # computer MSE error
        mse_value = self.compute_mse(
            df=df,
            sim_col=sim_col,
            obs_col=obs_col
        )

        # Output
        output = float(pow(mse_value, 0.5))

        return output

    def compute_pbias(
        self,
        df: pandas.DataFrame,
        sim_col: str,
        obs_col: str
    ) -> float:
        '''
        Calculate the `Percent Bias` metric between simulated and observed values.

        Args:
            df (pandas.DataFrame): DataFrame containing at least two columns with simulated and observed values.

            sim_col (str): Name of the column containing simulated values.

            obs_col (str): Name of the column containing observed values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.compute_pbias
            ),
            vars_values=locals()
        )

        # Simulation values
        sim_arr = df[sim_col].astype(float)

        # Observed values
        obs_arr = df[obs_col].astype(float)

        # Output
        output = float(100 * (sim_arr - obs_arr).sum() / obs_arr.sum())

        return output

    def compute_mare(
        self,
        df: pandas.DataFrame,
        sim_col: str,
        obs_col: str
    ) -> float:
        '''
        Calculate the `Mean Absolute Relative Error` metric between simulated and observed values

        Args:
            df (pandas.DataFrame): DataFrame containing at least two columns with simulated and observed values.

            sim_col (str): Name of the column containing simulated values.

            obs_col (str): Name of the column containing observed values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.compute_mare
            ),
            vars_values=locals()
        )

        # Simulation values
        sim_arr = df[sim_col].astype(float)

        # Observed values
        obs_arr = df[obs_col].astype(float)

        # Output
        output = float(((obs_arr - sim_arr) / obs_arr).abs().mean())

        return output

    def scenario_indicators(
        self,
        sensim_file: str | pathlib.Path,
        df_name: str,
        sim_col: str,
        obs_file: str | pathlib.Path,
        date_format: str,
        obs_col: str,
        indicators: list[str],
        json_file: typing.Optional[str | pathlib.Path] = None
    ) -> dict[str, typing.Any]:
        '''
        Compute performance indicators for sample scenarios obtained using the method
        [`simulation_by_sample_parameters`](https://swat-model.github.io/pySWATPlus/api/sensitivity_analyzer/#pySWATPlus.SensitivityAnalyzer.simulation_by_sample_parameters).

        Before computing the indicators, simulated and observed values are normalized using the formula `(v - min_v) / (max_v - min_v)`,
        where `min_v` and `max_v` represent the minimum and maximum of all simulated and observed values combined.

        The method returns a dictionary with two keys:

        - `problem`: The definition dictionary passed to sampling.
        - `indicator`: A `DataFrame` containing the `Scenario` column and one column per indicator,
          with scenario indices and corresponding indicator values.

        Args:
            sensim_file (str | pathlib.Path): Path to the `sensitivity_simulation.json` file produced by `simulation_by_sobol_sample`.

            df_name (str): Name of the `DataFrame` within `sensitivity_simulation.json` from which to compute scenario indicators.

            sim_col (str): Name of the column in `df_name` containing simulated values.

            obs_file (str | pathlib.Path): Path to the CSV file containing observed data. The file must include a
                `date` column (used to merge simulated and observed data) and use a comma as the separator.

            date_format (str): Date format of the `date` column in `obs_file`, used to parse `datetime.date` objects from date strings.

            obs_col (str): Name of the column in `obs_file` containing observed data. All negative and `None` observed values are removed
                due to the normalization of observed and similated values before computing indicators.

            indicators (list[str]): List of performance indicators to compute. Available options:

                - `NSE`: Nash–Sutcliffe Efficiency
                - `KGE`: Kling–Gupta Efficiency
                - `MSE`: Mean Squared Error
                - `RMSE`: Root Mean Squared Error
                - `PBIAS`: Percent Bias
                - `MARE`: Mean Absolute Relative Error

            json_file (str | pathlib.Path, optional): Path to a JSON file for saving the output `DataFrame` containing indicator values.
                If `None` (default), the `DataFrame` is not saved.

        Returns:
            Dictionary with two keys, `problem` and `indicator`, and their corresponding values.
        '''

        # Check input variables type
        validators._variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.scenario_indicators
            ),
            vars_values=locals()
        )

        # Check valid name of metric
        abbr_indicator = self.indicator_names
        for indicator in indicators:
            if indicator not in abbr_indicator:
                raise ValueError(
                    f'Invalid name "{indicator}" in "indicatiors" list; expected names are {list(abbr_indicator.keys())}'
                )

        # Observed DataFrame
        obs_df = utils._df_observe(
            obs_file=pathlib.Path(obs_file).resolve(),
            date_format=date_format,
            obs_col=obs_col
        )
        obs_df.columns = ['date', 'obs']

        # Retrieve sensitivity output
        sensitivity_sim = utils._retrieve_sensitivity_output(
            sensim_file=pathlib.Path(sensim_file).resolve(),
            df_name=df_name,
            add_problem=True,
            add_sample=False
        )

        # Empty DataFrame to store scenario indicators
        inct_df = pandas.DataFrame(
            columns=indicators
        )

        # Iterate scenarios
        for key, df in sensitivity_sim['scenario'].items():
            df = df[['date', sim_col]]
            df.columns = ['date', 'sim']
            # Merge scenario DataFrame with observed DataFrame
            merge_df = df.merge(
                right=obs_df.copy(),
                how='inner',
                on='date'
            )
            # Normalized DataFrame
            norm_df = utils._df_normalize(
                df=merge_df[['sim', 'obs']]
            )
            # Iterate indicators
            for indicator in indicators:
                # Method from indicator abbreviation
                indicator_method = getattr(
                    self,
                    f'compute_{indicator.lower()}'
                )
                # indicator value
                key_indicator = indicator_method(
                    df=norm_df,
                    sim_col='sim',
                    obs_col='obs'
                )
                # Store error in DataFrame
                inct_df.loc[key, indicator] = key_indicator

        # Reset index to scenario column
        scnro_col = 'Scenario'
        inct_df = inct_df.reset_index(
            names=[scnro_col]
        )
        inct_df[scnro_col] = inct_df[scnro_col].astype(int)

        # Save DataFrame
        if json_file is not None:
            json_file = pathlib.Path(json_file).resolve()
            # Raise error for invalid JSON file extension
            validators._json_extension(
                json_file=json_file
            )
            # Write DataFrame to the JSON file
            inct_df.to_json(
                path_or_buf=json_file,
                orient='records',
                indent=4
            )

        # Output dictionary
        output = {
            'problem': sensitivity_sim['problem'],
            'indicator': inct_df
        }

        return output
