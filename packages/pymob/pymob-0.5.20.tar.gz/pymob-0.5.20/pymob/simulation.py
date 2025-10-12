import os
import sys
import copy
import warnings
import textwrap
import tempfile
import importlib
from copy import deepcopy
from typing import Optional, List, Union, Literal, Any, Tuple, Sequence, Mapping
from types import ModuleType
import configparser
from functools import partial
from typing import Callable, Dict
from collections import OrderedDict
import logging
import numpy as np
from numpy.typing import NDArray
import xarray as xr
import arviz as az
import dpath as dp
from sklearn.preprocessing import MinMaxScaler

import pymob
from pymob.utils.config import lambdify_expression, lookup_args, get_return_arguments
from pymob.utils.errors import errormsg, import_optional_dependency, PymobError
from pymob.utils.store_file import parse_config_section, is_number
from pymob.utils.misc import benchmark
from pymob.sim.evaluator import Evaluator, create_dataset_from_dict, create_dataset_from_numpy
from pymob.sim.base import stack_variables
from pymob.sim.config import Config, ParameterDict, DataVariable, Param, NumericArray
from pymob.sim.plot import SimulationPlot
from pymob.sim.report import Report

config_deprecation = "Direct access of config options will be deprecated. Use `Simulation.config.OPTION` API instead"
MODULES = ["sim", "mod", "prob", "data", "plot"]

def is_iterable(x):
    try:
        iter(x)
        return True
    except TypeError:
        return False


def flatten_parameter_dict(model_parameter_dict, exclude_params=[]):
    """Takes a dictionary of key value pairs where the values may be
    floats or arrays. It flattens the arrays and adds indexes to the keys.
    In addition a function is returned that back-transforms the flattened
    parameters."""
    parameters = model_parameter_dict

    flat_params = {}
    empty_map = {}
    for par, value in parameters.items():
        if par in exclude_params:
            continue
        if is_iterable(value):
            empty_map.update({par: np.full_like(value, fill_value=np.nan)})
            for i, subvalue in enumerate(value):
                subpar = f"{par}___{i}"
                flat_params.update({subpar: subvalue})

        else:
            flat_params.update({par: value})

        if par not in empty_map:
            empty_map.update({par: np.nan})


    def reverse_mapper(parameters):
        param_dict = empty_map.copy()

        for subpar, value in parameters.items():
            subpar_list = subpar.split("___")

            if len(subpar_list) > 1:
                par, par_index = subpar_list
                param_dict[par][int(par_index)] = value
            elif len(subpar_list) == 1:
                par, = subpar_list
                param_dict[par] = value

        return param_dict
    
    return flat_params, reverse_mapper


def update_parameters_dict(config, x, parnames):
    for par, val, in zip(parnames, x):
        key_exist = dp.set(config, glob=par, value=val, separator=".")
        if key_exist != 1:
            raise KeyError(
                f"prior parameter name: {par} was not found in config. " + 
                "make sure parameter name was spelled correctly"
            )
    return config



class SimulationBase:
    """
    Construct a simulation directly to construct a new simulation instance, 
    use it with a config file for modifying or playing with existing simulations
    or use for subclassing.

    Components
    ----------

    model : Callable
        A python function that returns one or multiple numeric values or arrays
        The number and dimensionality of the output must be specified in the
        :class:`pymob.sim.config.Datastructure`, which takes 
        :class:`pymob.sim.config.DataVariable` as input.
    model_parameters : Dict['parameters': Dict[str, float|Array], 'y0': xarray.Dataset, 'x_in': xarray.Dataset]
        Model parameters is a dictionary containing 3 keys: 'parameters' (parameters), 
        'y0' (initial values), and 'x_in' (input that can be interpolated).
        Only 'theta' is a mandatory component.
        
    
    Direct use
    ----------

    In the direct use, {class}`pymob.simulation.SimulationBase` is instantiated
    and the relevant model attributes are set. Each simulation needs these 
    parameters
    
    >>> import xarray as xr
    >>> from pymob import SimulationBase
    >>> from pymob.examples import linear_model
    >>> from pymob.sim.solvetools import solve_analytic_1d

    Instantiate the model and assign the data. ALthough assigning data is
    not mandatory, it makes setting up a model easier, because the coordinates,
    and dimensions are simply taken from the observations dataset

    >>> sim = SimulationBase()
    >>> linreg, x, y, y_noise, parameters = linear_model(n=5)
    >>> obs = xr.DataArray(y_noise, coords={"x": x}).to_dataset(name="y")
    >>> sim.observations = obs
    MinMaxScaler(variable=y, min=-4.654415807935214, max=5.905355866673117)

    Parameterize the model    
    
    >>> sim.model = linreg
    >>> sim.solver = solve_analytic_1d
    >>> sim.config.model_parameters.a = Param(value=10, free=False)
    >>> sim.config.model_parameters.b = Param(value=3, free=True , prior="normal(loc=0,scale=10)") # type:ignore
    >>> sim.model_parameters["parameters"] = sim.config.model_parameters.value_dict

    Run the model
    
    >>> sim.dispatch_constructor()
    >>> evaluator = sim.dispatch(theta={"b":3})
    >>> evaluator()
    >>> evaluator.results
    <xarray.Dataset>
    Dimensions:  (x: 5)
    Coordinates:
      * x        (x) float64 -5.0 -2.5 0.0 2.5 5.0
    Data variables:
        y        (x) float64 -5.0 2.5 10.0 17.5 25.0

    
    Subclassing use
    ---------------

    Subclassing :class:`SimulationBase` makes sense if the Simulation is intended
    to be used with configuration files

    >>> class LotkaVolterraSimulation(SimulationBase):
    ...     def initialize(self, input):
    ...         self.observations = xr.load_dataset(os.path.join(self.data_path, self.config.case_study.observations))
    ...         y0 = self.parse_input("y0", drop_dims=["time"])
    ...         self.model_parameters["y0"] = y0
    ...         self.model_parameters["parameters"] = self.config.model_parameters.value_dict
    
    .. :code-block: python

       sim = LotkaVolterraSimulation(settings.cfg)
       sim.setup()

    :meth:`setup` calls initialize and a couple of other functions to set up the
    simulation. Afterwards methods like :meth:`dispatch` can be used. The idea is
    to automatize the regular setup steps for a simulation in the initialize 
    method. The reason why :meth:`setup` is called explicitely and not implicitly
    by the `__init__` method is to give the user the opportunity to change the 
    configuration before initializing, such as the name of the scenario 
    (`sim.config.case_study.scenario`), the results directory 
    (`sim.config.case_study.output`) or any other configuration of the simulation

    """
    Report = Report
    SimulationPlot = SimulationPlot
    model: Optional[Callable] = None
    solver: Optional[Callable] = None
    solver_post_processing: Optional[Callable] = None
    _mod: ModuleType
    _prob: ModuleType
    _data: ModuleType
    _plot: ModuleType

    def __init__(
        self, 
        config: Optional[Union[str,configparser.ConfigParser,Config]] = None, 
    ) -> None:
        
        if isinstance(config, Config):
            self.config = config
        else:
            self.config = Config(config=config)

        self.config.case_study.pymob_version = pymob.__version__

        self._observations: xr.Dataset = xr.Dataset()
        self._observations_copy: xr.Dataset = xr.Dataset()
        self._coordinates: Dict = {}
        self._scaler = {}

        self._model_parameters: Dict[Literal["parameters","y0","x_in"],Any] =\
            ParameterDict(parameters={}, callback=self._on_params_updated)
        # self.observations = None
        self._objective_names: str|List[str] = []
        self.indices: Dict = {}

        # seed gloabal RNG
        self._seed_buffer_size: int = self.config.multiprocessing.n_cores * 2
        self.RNG = np.random.default_rng(self.config.simulation.seed)
        self._random_integers = self.create_random_integers(n=self._seed_buffer_size)
     
        self.parameterize = partial(
            self.parameterize, 
            model_parameters=copy.deepcopy(dict(self.model_parameters))
        )

        self._report: Optional[Report] = None
        # simulation
        # self.setup()
        
    def setup(self, **evaluator_kwargs):
        """Simulation setup routine, when the following methods have been 
        defined:
        
        coords = self.set_coordinates(input=self.input_file_paths)
        self.coordinates = self.create_coordinates()
        self.var_dim_mapper = self.create_dim_index()
        init-methods
        ------------

        self.initialize --> may be replaced by self.set_observations

        """


        self.load_modules()

        self.config.create_directory(directory="results", force=True)
        self.config.create_directory(directory="scenario", force=True)

        self.set_logger()
        
        self.initialize(input=self.config.input_file_paths)
        self.coordinates = self.create_coordinates()
        self.validate()

        # TODO: set up logger
        self.parameterize = partial(
            self.parameterize, 
            model_parameters=copy.deepcopy(dict(self.model_parameters))
        )
        self.dispatch_constructor()

    @property
    def model_parameters(self) -> Dict[Literal["parameters","y0","x_in"],Any]:
        return self._model_parameters
    
    @model_parameters.setter
    def model_parameters(self, value: Dict[Literal["parameters","y0","x_in"],Any]):
        if "parameters" not in value:
            raise KeyError(
                "'model_parameters' must contain a 'parameters' key"
            )

        self._check_input_for_nans(model_parameters=value, key="x_in")
        self._check_input_for_nans(model_parameters=value, key="y0")
        
        if not isinstance(value["parameters"], dict):
            raise ValueError(
                f"`model_parameters['parameters'] = {value['parameters']}`, but "
                "must be of type dict."
            )
        self.parameterize = partial(
            self.parameterize, 
            model_parameters=copy.deepcopy(dict(self.model_parameters))
        )
        self._model_parameters = ParameterDict(value, callback=self._on_params_updated)

    def _on_params_updated(self, updated_dict):
        self.model_parameters = updated_dict

    def _check_input_for_nans(self, model_parameters, key):
        if key not in model_parameters:
            return

        for data_var, array in model_parameters[key].items():
            nans = array.isnull().sum([
                d for d in array.dims 
                if d == self.config.simulation.x_dimension
            ])
            nans = nans.where(nans, drop=True)

            if sum(nans.shape) > 0:
                batch_dim = self.config.simulation.batch_dimension
                raise PymobError(
                    f"The xarray passed to `sim.model_parameters['{key}']` contained "+
                    f"NaN values. They occur at the {batch_dim}-coordinates: "+
                    f"{nans.coords['id'].values}.\n\n"+
                    
                    "Why does this error occur?\n"+
                    "--------------------------\n"+
                    "Pymob uses y0 as initial conditions for a solver and uses x_in to "+
                    "provide interpolated values for any value of t. Having nan values "+
                    "in such components presents an unsolvable challenge to the solver.\n\n" +

                    "How can I fix this error?\n"+
                    "-------------------------\n"+
                    "General advice: Use sim.parse_input https://pymob.readthedocs.io/en/stable/api/pymob.html#pymob.simulation.SimulationBase.parse_input\n"
                    "* Problem with 'x_in': Check sim.observations and also check"+
                    "sim.config.simulations.x_in"
                    "You may need to take a decision how to interpolate "+
                    "your data. Check out the xarray documentation "+
                    "https://docs.xarray.dev/en/stable/generated/xarray.DataArray.interpolate_na.html" +
                    "or https://docs.xarray.dev/en/stable/generated/xarray.DataArray.ffill.html "+
                    "to replace nan values.\n"+ 
                    "* If you want to make sure your 'x_in' follows a rectangular interpolation you can use\n"+
                    "  >>> sim.parse_input('x_in', reference_data=sim.observations)\n"
                    "  >>> pymob.solvers.base.rect_interpolation(x_in)\n"
                    "* Problem with 'y0': Check sim.observations and also check "+
                    "sim.config.simulation.y0\n\n"

                    "Details\n"
                    "-------\n"
                    f"{key}: {model_parameters[key]}"
                )
        

    @property
    def observations(self):
        assert isinstance(self._observations, xr.Dataset), "Observations must be an xr.Dataset"
        return self._observations

    @observations.setter
    def observations(self, value: xr.Dataset):
        for k, v in value.data_vars.items():
            if k not in self.config.data_structure.data_variables:
                datavar = DataVariable(
                    dimensions=[str(d) for d in v.dims],
                    min=float(v.values.min()),
                    max=float(v.values.max()),
                )
                setattr(self.config.data_structure, k, datavar)
                warnings.warn(
                    f"`sim.config.data_structure.{k} = Datavariable({datavar})` has been "
                    "assumed from `sim.observations`. If the order of the dimensions "
                    f"should be different, specify `sim.config.data_structure.{k} "
                    "= DataVariable(dimensions=[...], ...)` manually."
                )
            else:
                datavar: DataVariable = getattr(self.config.data_structure, k)
                if np.isnan(datavar.min):
                    datavar.min = float(v.values.min())
                if np.isnan(datavar.max):
                    datavar.max = float(v.values.max())

                if set(datavar.dimensions) != set(v.dims):
                    raise KeyError(
                        f"Dimensions of the '{k}' DataVariable({datavar}) "
                        f"Did not match the definitions in the observations: "
                        f"dimensions={list(v.dims)}. "
                        "If you are unsure what to do, not specifying data variables"
                        "is a valid option."
                    )

        self._observations = value
        if sum(tuple(self._observations_copy.sizes.values())) == 0:
            self._observations_copy = copy.deepcopy(value)

        self.coordinates = self.create_coordinates()

        unobserved_keys = [
            k for k in self.config.data_structure.observed_data_variables 
            if k not in self.observations
        ]

        if len(unobserved_keys) > 0:
            raise KeyError(
                f"{unobserved_keys} were not found in the observations."
                f"Make sure any unobserved data variable is specified as "
                "'DataVariable(..., observed=False)' or make sure the "
                "observations include the data variable."
            )

        self.create_data_scaler()
        
    def save_observations(
        self, 
        filename="observations.nc", 
        directory=None, 
        force=False
    ):
        """Save observations to a NetCDF file.

        This function saves the observations data to a NetCDF file with a specified
        filename and directory. By default, it saves to the data path defined in the
        configuration. It prompts the user for confirmation before overwriting an
        existing file, unless the `force` flag is set.

        Parameters
        ----------
        filename : str, optional
            The name of the NetCDF file to save. Defaults to "observations.nc".
        directory : str, optional
            The directory to save the NetCDF file to. If None, the data path
            defined in the object's configuration is used. Defaults to None.
        force : bool, optional
            If True, overwrite the file without prompting. Defaults to False.

        Returns
        -------
        None

        Raises
        ------
        None

        Notes
        -----
        - The function updates the `observations` attribute in the object's
        configuration to reflect the saved filename.
        - The `drop_encoding()` method is called on the observations dataset
        before saving to remove any encoding information.  This is a common
        practice to ensure portability and avoid issues with different NetCDF
        readers.
        - The function uses `os.path.join()` to construct the full file path,
        ensuring correct path handling across different operating systems.
        - Before exporting attributes of the dataset are serialized to avoid
        export errors.
        - Creates a data directory if it does not exist
        
        Examples
        --------

        >>> # Create a simulation
        >>> sim = SimulationBase()
        >>> sim.config.case_study.name = "testing"

        >>> # Save observations to the default data path with the default filename
        >>> # 'case_studies/testing/data/observations.nc'
        >>> sim.save_observations() 
        >>> os.listdir("case_studies/testing/data/")
        ['observations.nc']

        >>> # Overwrite an existing file without prompting
        >>> sim.save_observations(force=True)
        >>> os.listdir("case_studies/testing/data/")
        ['observations.nc']

        >>> # Save observations to a specific directory with a custom filename
        >>> sim.save_observations(filename="my_obs.nc", directory="case_studies/testing/data_mod/")
        >>> os.listdir("case_studies/testing/data_mod/")
        ['my_obs.nc']

        """

        if directory is None:
            directory = self.data_path
            
        fp = os.path.join(directory, filename)
        if filename != self.config.case_study.observations:
            self.config.case_study.observations = filename

        self._serialize_attrs(self.observations)

        if not os.path.exists(os.path.dirname(fp)):
            os.makedirs(os.path.dirname(fp))

        if not os.path.exists(fp) or force:
            self.observations.drop_encoding().to_netcdf(fp)
        else:
            if input(f"Observations {fp} exist. Overwrite? [y/N]") == "y":
                self.observations.drop_encoding().to_netcdf(fp)

    @staticmethod
    def _serialize_attrs(observations):
        for key, dv in observations.items():
            dv.attrs = {
                k: str(v) for k, v in dv.attrs.items() 
            }

        return observations

    @property
    def coordinates(self):
        return self._coordinates

    @coordinates.setter
    def coordinates(self, value: Dict[str, np.ndarray] | List[np.ndarray] | Tuple[np.ndarray]):
        dims = self.config.data_structure.dimensions
        if len(dims) != len(value):
            raise AssertionError(
                f"number of dimensions {dims} ({len(dims)}), must match "
                f"the number of dimensions in the coordinate data "
                f"{len(value)}."
            )

        if isinstance(value, (tuple, list)):
            value = {dim: x_i for dim, x_i in zip(dims, value)}

        self._coordinates = value

    @property
    def free_model_parameters(self) -> List[Param]:
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        free_params = self.config.model_parameters.free.copy()
        for k, param in free_params.items():
            param.name = k
        return list(free_params.values())

    @property
    def fixed_model_parameters(self) -> Dict[str, Param]:
        return self.config.model_parameters.fixed

    @property
    def all_model_parameters(self) -> Dict[str, Param]:
        return self.config.model_parameters.all

    def __repr__(self) -> str:
        return (
            "Simulation(case_study={c}, scenario={s}, version={v})".format(
                c=self.config.case_study.name, 
                s=self.config.case_study.scenario,
                v=self.config.case_study.version
            )
        )

    def load_modules(self):
        """Loads modules from cases studies. If the case study is a regular 
        python package. It looks for the package associated with the Simulation 
        class and imports the typical modules [data, mod, plot, prob, sim]

        :meta private:
        """
        # test if the case study is installed as a package
        package = self.__module__.split(".")[0]
        spec = importlib.util.find_spec(package)
        if spec is not None and package != "pymob":
            p = importlib.import_module(package)
            self.config.case_study.version = p.__version__
            for module in MODULES:
                try:
                    # TODO: Consider importing modules as a nested dictionary 
                    # with the indexing key being the package. The package
                    # cannot be derived from the class, if a method, that is 
                    # executed on a lower level case-study, should target that 
                    # a module belonging to the same package, because if the
                    # object is used, it would resolve to the package of the
                    # higher level case-study
                    m = importlib.import_module(f"{package}.{module}")
                    setattr(self, f"_{module}", m)
                except ModuleNotFoundError:

                    # look in the base classes if modules cannot be imported from top-level
                    # module
                    base_classes = type(self).__bases__
                    assert len(base_classes) == 1
                    try:
                        parent_package = base_classes[0].__module__.split(".")[0]
                        m = importlib.import_module(f"{parent_package}.{module}")
                        setattr(self, f"_{module}", m)

                    except ModuleNotFoundError:
                        warnings.warn(
                            f"Module {module}.py not found in {package} or in {parent_package}. "
                            f"Missing modules can lead to unexpected behavior. "
                            f"Does your case study of the parent class have a {module}.py file? "
                            f"It should have the line `from PARENT_CASE_STUDY. "
                            f"{module} import *` to import all objects from "
                            "the parent case study."
                        )
            return

        # This branch is for case studies that are not installed (I guess)
        # append relevant paths to sys
        package = os.path.join(
            self.config.case_study.root, 
            self.config.case_study.package
        )
        if package not in sys.path:
            sys.path.insert(0, package)
            print(f"Inserted '{package}' into PATH at index=0")
    
        case_study = os.path.join(
            self.config.case_study.root, 
            self.config.case_study.package,
            self.config.case_study.name,
            # Account for package architecture 
            self.config.case_study.name,
        )
        if case_study not in sys.path:
            sys.path.insert(0, case_study)
            print(f"Inserted '{case_study}' into PATH at index=0")

        for module in MODULES:
            try:
                m = importlib.import_module(module, package=case_study)
                setattr(self, f"_{module}", m)
            except ModuleNotFoundError:
                warnings.warn(
                    f"Module {module}.py not found in {case_study}."
                    f"Missing modules can lead to unexpected behavior."
                )

    def set_logger(self):        
        self.logger = logging.getLogger(f"{type(self).__qualname__}")
        self.logger.setLevel(logging.DEBUG)

        # add a file handler
        handler = logging.FileHandler(f"{self.output_path}/log.txt", mode="w")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # add a stderr handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def create_coordinates(self) -> Dict[str, np.ndarray]:
        """
        :meta private:
        """
        coordinates = {}
        for dim in self.config.data_structure.dimensions:
            if dim in self.observations:
                coord = self.observations[dim].values
            else:
                # adds a dummy coordinate
                coord = np.array([0])

            coordinates.update({dim: coord})

        return coordinates

    def reset_coordinate(self, dim:str):
        self.coordinates[dim] = self.observations[dim].values

    def reset_data_variable(self, data_variable:str):
        self.observations[data_variable] = self._observations_copy[data_variable]

    def reset_all_coordinates(self):
        self.coordinates = self.create_coordinates()

    def create_interpolated_coordinates(self, dim):
        """Combines coordinates from observations and from interpolation"""
        if "x_in" not in self.model_parameters:
            warnings.warn(
                "No interpolated input available, coordinates will remain unchanged"
            )
            return

        # this resets the coordinates to observation coordinates
        self.reset_coordinate(dim=dim) 

        new_coord = np.unique(np.concatenate([
            self.coordinates[dim], 
            self.model_parameters["x_in"][dim].values
        ]))
        new_coord.sort()

        self.coordinates[dim] = new_coord

    def benchmark(self, n=100, **kwargs):
        evaluator = self.dispatch(theta=self.model_parameter_dict, **kwargs)
        evaluator(seed=1) 

        @benchmark
        def run_bench():
            for i in range(n):
                evaluator = self.dispatch(theta=self.model_parameter_dict, **kwargs)
                evaluator(seed=self.RNG.integers(100))
                evaluator.results

        print(f"\nBenchmarking with {n} evaluations")
        print("=================================")
        run_bench()
        print("=================================\n")
        
    def infer_ode_states(self) -> int:
        if self.config.simulation.n_ode_states == -1:
            try: 
                return_args = get_return_arguments(self.model)
                n_ode_states = len(return_args)
                warnings.warn(
                    "The number of ODE states was not specified in "
                    "the config file [simulation] > 'n_ode_states = <n>'. "
                    f"Extracted the return arguments {return_args} from the "
                    "source code. "
                    f"Setting 'n_ode_states={n_ode_states}."
                )
            except:  # noqa: E722
                warnings.warn(
                    "The number of ODE states was not specified in "
                    "the config file [simulation] > 'n_ode_states = <n>' "
                    "and could not be extracted from the return arguments."
                )
                n_ode_states = -1
        else:
            n_ode_states = self.config.simulation.n_ode_states

        return n_ode_states
        
    @staticmethod
    def validate_model_input(model_input) -> OrderedDict[str, Sequence[float]]:
        """Returns a copy of the model input. This means, the original model input
        will not be overwritten by any action.
        """
        if isinstance(model_input, xr.Dataset):
            model_input = {
                k: dv.values for k, dv in model_input.data_vars.items()
            }
            return OrderedDict(model_input) # type: ignore
        
        raise NotImplementedError(
            f"Model input of type {type(model_input)} "
            "is not implemented. Use an xr.Dataset"
        )

    def subset_by_batch_dimension(self, data):
        """
        FIXME
        Subset by batch dimension, seems to be a method that is not appropriate for
        dispatch; and rather for the dispatch constructor
        The feature of pymob was not used and is currently deactivated in sim.dispatch()
        A better use of the method would be the use during the call to dispatch_constructor
        """
        batch_dim = self.config.simulation.batch_dimension
        if batch_dim not in self.coordinates:
            return data
        
        if batch_dim not in data:
            raise KeyError(
                "Batch dimension not in input data"
            )
        mask = data[batch_dim].isin(self.coordinates[batch_dim])
        return data.where(mask, drop=True)

    @property
    def coordinates_input_vars(self) -> Dict[str, Dict[str, Dict[str, NDArray]]]:
        """TODO: Error source. dataset coordinates are unordered."""
        input_vars = ["x_in", "y0"]

        # This is a function that could replace the below, to return always
        # dictionaries for any possible input vars. Default: Empty dict
        coordinates = {}
        for k in input_vars:
            if k in self.model_parameters:
                dataset: xr.Dataset = self.model_parameters[k]
                data_var_coords = {}
                for var_name, var_data in dataset.data_vars.items():
                    var_coords = {ck: cv.values for ck, cv in var_data.coords.items()}
                    data_var_coords.update({var_name:var_coords})
            else:
                data_var_coords = {}

            coordinates.update({k: data_var_coords})
        return coordinates
        # return {
        #     k: {ck: cv.values for ck, cv in v.coords.items()} 
        #     for k, v in self.model_parameters.items() 
        #     if k in input_vars
        # }

    @property
    def dims_input_vars(self) -> Dict[str, Dict[str, Tuple[str, ...]]]:
        return {
            kiv: {
                k_var: tuple([k for k in v_var.keys()]) 
                for k_var, v_var in viv.items()
            } 
            for kiv, viv in self.coordinates_input_vars.items()
        }

    @property
    def coordinates_indices(self):
        return {
            idx_name: idx_val.coords[idx_name].values
            for idx_name, idx_val in self.indices.items() 
        }

    @property
    def parameter_dims(self) -> Dict[str, Tuple[str, ...]]:
        return {
            par_name: param.dims
            for par_name, param in self.config.model_parameters.all.items() 
        }

    @property
    def parameter_shapes(self) -> Dict[str, Tuple[int, ...]]:
        return {
            par_name: tuple([self.dimension_sizes[d] for d in param.dims])
            for par_name, param in self.config.model_parameters.all.items() 
        }

    def dispatch_constructor(self, **evaluator_kwargs):
        """Construct the dispatcher and pass everything to the evaluator that is 
        static."""

        if self.model is None:
            if self.config.simulation.model:
                if not hasattr(self, "_mod"):
                    self.load_modules()
                model = getattr(self._mod, self.config.simulation.model)
                self.model = model
            else: 
                raise ValueError(
                    "A model was not provided as a callable function nor was "
                    "it specified in 'config.simulation.model', please specify "
                    "Any of the two."
                )
        else:
            model = self.model

        self.n_ode_states = self.infer_ode_states()

        if self.solver is None:
            if self.config.simulation.solver:
                if not hasattr(self, "_mod"):
                    self.load_modules()
                try:
                    solver = getattr(self._mod, self.config.simulation.solver)
                except AttributeError:
                    try:
                        solver = getattr(pymob.solvers, self.config.simulation.solver)
                    except AttributeError:
                        raise AttributeError(
                            f"The solver {self.config.simulation.solver} "
                            f"could not be found in {self._mod} or {pymob.solvers} "
                            f"Define your own solver or callable or select an "
                            "implemented solver (e.g. JaxSolver)."
                        )
                self.solver = solver
            else: 
                raise ValueError(
                    "A solver was not provided directly to 'sim.solver' nor was "
                    "it specified in 'config.simulation.model', please specify "
                    "Any of the two."
                )
        else:
            solver = self.solver
        
        if self.solver_post_processing is None:
            if self.config.simulation.solver_post_processing is not None:
                post_processing = getattr(self._mod, self.config.simulation.solver_post_processing)
            else:
                def post_processing(results, time, interpolation):
                    return results
        else:
            post_processing = self.solver_post_processing

        stochastic = self.config.simulation.modeltype
            
        solver_options = {}
        if isinstance(solver, type):
            solver_classes = [solver] + [c for c in solver.__mro__ if c not in [solver, object]]

            for sc in solver_classes:
                try:
                    solver_options = getattr(self.config, sc.__name__.lower())
                    solver_options = solver_options.model_dump()
                    break
                except AttributeError:
                    continue

        self.evaluator = Evaluator(
            model=model,
            solver=solver,
            parameter_dims=self.parameter_dims,
            dimensions=self.dimensions,
            dimension_sizes=self.dimension_sizes,
            n_ode_states=self.config.simulation.n_ode_states,
            var_dim_mapper=self.var_dim_mapper,
            data_structure=self.data_structure,
            data_structure_and_dimensionality=self.data_structure_and_dimensionality,
            data_variables=self.data_variables,
            coordinates=self.coordinates,
            coordinates_input_vars=self.coordinates_input_vars,
            dims_input_vars=self.dims_input_vars,
            coordinates_indices=self.coordinates_indices,
            # TODO: pass the whole simulation settings section
            stochastic=True if stochastic == "stochastic" else False,
            indices=self.indices,
            post_processing=post_processing,
            batch_dimension=self.config.simulation.batch_dimension,
            solver_options=solver_options,
            **evaluator_kwargs
        )

        # return evaluator

    def dispatch(
            self, 
            theta: Mapping[str, float|NumericArray|Sequence[float]] = {}, 
            y0: Mapping[str, float|NumericArray|Sequence[float]] = {}, 
            x_in: Mapping[str, float|NumericArray|Sequence[float]] = {}, 
        ):
        """Dispatch an evaluator, which will compute the model for the parameters
        (theta), starting values (y0) and model input (x_in). 
        
        Evaluators are advantageous, because they are easier serialized
        than the whole simulation object. Comparison can then happen back in 
        the simulation.

        In addition, evaluators can be dispatched and seeded and evaluated in
        parallel, because they are decoupled from the simulation object

        Parameters
        ----------

        theta : Dict[float|Sequence[float]]
            Dictionary of model parameters that should be changed for dispatch.
            Unspecified model parameters will assume the default values, 
            specified under config.model_parameters.NAME.value

        y0 : Dict[float|Sequence[float]]
            Dictionary of initial values that should be changed for dispatch.
        
        x_in : Dict[float|Sequence[float]]
            Dictionary of model input values that should be changed for dispatch.
        
        """
        model_parameters = self.parameterize(dict(theta)) #type: ignore
        # can be initialized
        if "y0" in model_parameters:
            y0_ = self.validate_model_input(model_parameters["y0"])
            
            # update keys passed to y0
            y0_.update(y0)
            model_parameters["y0"] = y0_
        else:
            model_parameters["y0"] = OrderedDict({})
        
        if "x_in" in model_parameters:
            x_in_ = self.validate_model_input(model_parameters["x_in"])

            # update keys passed to x_in
            x_in_.update(x_in)
            model_parameters["x_in"] = x_in_
        else:
            model_parameters["x_in"] = OrderedDict({})
        
        evaluator = self.evaluator.spawn()
        evaluator.parameters = model_parameters
        return evaluator

    def parse_input(
        self, 
        input : Literal["y0", "x_in"], 
        reference_data: Optional[xr.Dataset]=None, 
        drop_dims: List[str]=[]
    ) -> xr.Dataset:
        """Parses a config string e.g. y=Array([0]) or a=b to a numpy array 
        and looks up symbols in the elements of data, where data items are
        key:value pairs of a dictionary, xarray items or anything of this form

        The values are broadcasted along the remaining dimensions in the obser-
        vations that have not been dropped. Input refers to the argument in
        the config file. 

        This method is useful to prepare y0s or x_in from observations or to broadcast
        starting values along batch dimensions.

        Parameters
        ----------

        input : Literal["y0", "x_in"]
            The key in config.simulation that contains the input mapping. The
            key must be contained in the data structure, otherwise an error
            will be raised. This is done to make sure there is no ambiguity in
            the applied dimensional broadcasting.
            
            Example:
            `sim.config.simulation.y0 = ['A=Array([0])', 'B=C']` 
            `reference_data = xr.Dataset()`

        reference_data : Optional[xr.Dataset]
    
        """
        if input == "y0":
            input_list = self.config.simulation.y0
        elif input == "x_in":
            input_list = self.config.simulation.x_in
        else:
            raise NotImplementedError(f"Input type {input}: is not implemented")

        input_dataset = xr.Dataset()
        for input_expression in input_list:
            key, expr = input_expression.split("=")
            
            if key not in self.config.data_structure.all:
                raise KeyError(
                    f"'{key}' was not found in the DataStructure and "
                    "reference_data. "
                    f"Set 'sim.config.data_structure.{key} = DataVariable(...) " 
                    f"Or Specify reference_data that contains '{key}' " 
                )
                

            func, args = lambdify_expression(expr)
            if len(args) > 0 and reference_data is None:
                raise AssertionError(
                    f"Pymob is trying to look up the values of {args} in the "+
                    "reference data, but `reference_data=None`. Provide "+
                    "reference data if necessary and check if the right input "+
                    f"key is used (currently: `input='{input}'`)."
                )
            kwargs = lookup_args(args, reference_data)
            value = func(**kwargs)
            
            # parse dims and coords
            if reference_data is None:
                try:
                    input_dims = {
                        k: len(self.coordinates[k]) for k 
                        in self.config.data_structure.all[key].dimensions
                        if k not in drop_dims
                    }
                except KeyError as err:
                    missing_dim, = err.args
                    if missing_dim not in self.coordinates:
                        raise KeyError(
                            f"Pymob cannot find the key '{missing_dim}' in "+
                            f"the coordinates: `sim.coordinates = {self.coordinates}`"
                        )
                    else:
                        raise KeyError(
                            f"Pymob cannot find the key '{missing_dim}' in "+
                            "the simulation data structure: "+
                            f"{self.config.data_structure.all.keys()}`. "
                            "Make sure all needed data variables are defined."
                        )
                input_coords = {k:self.coordinates[k] for k in input_dims}

            else:
                input_dims = {
                    k:v for k, v in reference_data.dims.items() 
                    if k not in drop_dims
                }
                input_coords = {k:reference_data.coords[k] for k in input_dims}
            
            # this asserts that new dims is in the right order
            new_dims = {
                k: input_dims[k] for k in self.config.data_structure.all[key].dimensions
                if k not in drop_dims
            }

            input_coords = {k: input_coords[k] for k in new_dims.keys()}

            if isinstance(value, xr.DataArray):
                value = value.values
                if value.ndim != len(input_coords):
                    raise KeyError(
                        f"Dimensions of the input array ({value.ndim}) and " +
                        "the specified dimensions on the data variable "+
                        f"'{key}(dimensions={self.config.data_structure.all[key].dimensions})' " +
                        "did not match. Is a dimension missing from "+
                        "the data variable? You can update it by using"+
                        f" `sim.config.data_structure.{key}.dimensions = [...]"
                    )
            else:
                if len(new_dims) == 0:
                    value = float(value)
                else:
                    value = np.broadcast_to(value, tuple(new_dims.values()))


            value = xr.DataArray(value, coords=input_coords)
            input_dataset[key] = value


        return input_dataset


    def reshape_observations(self, observations, reduce_dim):
        """This method reduces the dimensionality of the observations. 
        Compiling xarray datasets from multiple experiments with different 
        IDs and different endpoints, lead to blown up datasets where 
        all combinations (even though they were not tested) are filled with
        NaNs. Reducing such artificial dimensions by flattening the arrays
        is the aim of this method. 

        TODO: There should be tests, whether the method is applicable (this
        may be already caught with the assertion)

        TODO: The method should be generally applicable
        """

        raise NotImplementedError(
            "reshape_observations is an experimental method. "
            "Using this method may have unexpected results."
        )
        
        # currently the method is still based on the damage-proxy project
        substances = observations.attrs[reduce_dim]

        stacked_obs = stack_variables(
            ds=observations.copy(),
            variables=["cext_nom", "cext", "cint"],
            new_coordinates=substances,
            new_dim="substance",
            pattern=lambda var, coord: f"{var}_{coord}"
        ).transpose(*self.dimensions, reduce_dim)

        # reduce cext_obs
        cext_nom = stacked_obs["cext_nom"]
        assert np.all(
            (cext_nom == 0).sum(dim=reduce_dim) == len(substances) - 1
        ), "There are mixture treatments in the SingleSubstanceSim."


        # VECTORIZED INDEXING IS THE KEY
        # https://docs.xarray.dev/en/stable/user-guide/indexing.html#vectorized-indexing

        # Defining a function to reduce the "reduce_dim" dimension to length 1
        def index(array, axis=None, **kwargs):
            # Check that there is exactly one non-zero value in 'substance'
            non_zero_count = (array != 0).sum(axis=axis)
            
            if not (non_zero_count == 1).all():
                raise ValueError(f"Invalid '{reduce_dim}' dimension. It should have exactly one non-zero value.")
            
            return np.where(array != 0)[axis]


        # Applying the reduction function using groupby and reduce
        red_data = stacked_obs.cext_nom
        new_dims = [d for d in red_data.dims if d != reduce_dim]

        reduce_dim_idx = red_data\
            .groupby(*new_dims)\
            .reduce(index, dim=reduce_dim)\
            .rename(f"{reduce_dim}_index")
        
        if stacked_obs.dims[reduce_dim] == 1:
            reduce_dim_idx = reduce_dim_idx.squeeze()
        
        reduce_dim_id_mapping = stacked_obs[reduce_dim]\
            .isel({reduce_dim: reduce_dim_idx})\
            .drop(reduce_dim)\
            .rename(f"{reduce_dim}_id_mapping")
        
        reduce_dim_idx = reduce_dim_idx.assign_coords({
            f"{reduce_dim}": reduce_dim_id_mapping
        })

        # this works because XARRAY is amazing :)
        stacked_obs["cext_nom"] = stacked_obs["cext_nom"].sel({reduce_dim: reduce_dim_id_mapping})
        stacked_obs["cext"] = stacked_obs["cext"].sel({reduce_dim: reduce_dim_id_mapping})
        stacked_obs["cint"] = stacked_obs["cint"].sel({reduce_dim: reduce_dim_id_mapping})
        
        # drop old dimension and add dimension as inexed dimension
        # this is necessary, as the reduced dimension needs to disappear from
        # the coordinates.
        stacked_obs = stacked_obs.drop_dims(reduce_dim)
        stacked_obs = stacked_obs.assign_coords({
            f"{reduce_dim}": reduce_dim_id_mapping,
            f"{reduce_dim}_index": reduce_dim_idx,
        })
        
        indices = {
            reduce_dim: reduce_dim_idx
        }

        return stacked_obs, indices


    def evaluate(self, theta):
        """Wrapper around run to modify paramters of the model.
        """
        self.model_parameters = self.parameterize(theta) #type: ignore
        return self.run()
    
    def compute(self):
        """
        A wrapper around run, which catches errors, logs, does post processing
        """
        warnings.warn("Discouraged to use self.Y constructs. Instability suspected.", DeprecationWarning, 2)
        self.Y = self.evaluate(theta=self.model_parameter_dict)

    def interactive(self):
        # optional imports
        extra = "'interactive' dependencies can be installed with pip install pymob[interactive]"
        widgets = import_optional_dependency("ipywidgets", errors="raise", extra=extra)
        if widgets is not None:
            import ipywidgets as widgets
            from IPython.display import display, clear_output
        else:
            raise ImportError("ipywidgets is not available and needs to be installed")

        def interactive_output(func, controls):
            out = widgets.Output(layout={'border': '1px solid black'})
            def observer(change):
                theta={key:s.value for key, s in sliders.items()}
                widgets.interaction.show_inline_matplotlib_plots()
                with out:
                    clear_output(wait=True)
                    func(theta)
                    widgets.interaction.show_inline_matplotlib_plots()
            for k, slider in controls.items():
                slider.observe(observer, "value")
            widgets.interaction.show_inline_matplotlib_plots()
            observer(None)
            return out

        sliders = {}
        for key, par in self.config.model_parameters.free.items():
            s = widgets.FloatSlider(
                par.value, description=key, min=par.min, max=par.max,
                step=par.step
            )
            sliders.update({key: s})

        def func(theta):
            # extra = self.config.inference.extra_vars
            # extra = [extra] if isinstance(extra, str) else extra
            # extra_vars = {v: self.observations[v] for v in extra}
            evaluator = self.dispatch(theta=theta)
            evaluator()
            self.plot(results=evaluator.results)

        out = interactive_output(func=func, controls=sliders)

        display(widgets.HBox([widgets.VBox([s for _, s in sliders.items()]), out]))
    
    def set_inferer(self, backend: Literal["numpyro", "scipy", "pyabc", "pymoo"]):
        extra = (
            "set_inferer(backend='{0}') was not executed successfully, because "
            "'{0}' dependencies were not found. They can be installed with "
            "pip install pymob[{0}]. Alternatively:"
        )

        if backend == "pyabc":
            pyabc = import_optional_dependency(
                "pyabc", errors="raise", extra=extra.format("pyabc")
            )
            if pyabc is not None:
                from pymob.inference.pyabc_backend import PyabcBackend
            
            self.inferer = PyabcBackend(simulation=self)

        elif backend == "pymoo":
            pymoo = import_optional_dependency(
                "pymoo", errors="raise", extra=extra.format("pymoo2")
            )
            if pymoo is not None:
                from pymob.inference.pymoo_backend import PymooBackend

            self.inferer = PymooBackend(simulation=self)

        elif backend == "numpyro":
            numpyro = import_optional_dependency(
                "numpyro", errors="raise", extra=extra.format("numpyro")
            )
            if numpyro is not None:
                from pymob.inference.numpyro_backend import NumpyroBackend

            self.inferer = NumpyroBackend(simulation=self)
    
        elif backend == "scipy":
            numpyro = import_optional_dependency(
                "scipy", errors="raise", extra=extra.format("scipy")
            )
            if numpyro is not None:
                from pymob.inference.scipy_backend import ScipyBackend

            self.inferer = ScipyBackend(simulation=self)
    
    
    
        else:
            raise NotImplementedError(f"Backend: {backend} is not implemented.")

    def check_dimensions(self, dataarray):
        """Check if dataset dimensions match the specified dimensions.
        TODO: Name datasets for referencing them in errormessages
        """
        ds_dims = dataarray.dims
        specified_dims = self.config.data_structure[dataarray.name].dimensions
        in_dims = [k in specified_dims for k in ds_dims]
        assert all(in_dims), IndexError(
            "Not all dataset dimensions, were not found in specified dimensions. "
            f"Settings(dims={specified_dims}) != dataset(dims={ds_dims})"
        )
        
    def dataarray_to_1Darrayy(self, dataarray: xr.DataArray) -> xr.DataArray: 
        self.check_dimensions(dataarray=dataarray)
        arr_dims = self.config.data_structure[dataarray.name].dimensions
        array_1D = dataarray.stack(multiindex=arr_dims)
        return array_1D

    def array1D_to_dataarray(self, dataarray: xr.DataArray) -> xr.DataArray: 
        arr_dims = self.config.data_structure[dataarray.name].dimensions
        return dataarray.unstack().transpose(*arr_dims)

    def create_data_scaler(self):
        """Creates a scaler for the data variables of the dataset over all
        remaining dimensions.
        In addition produces a scaled copy of the observations
        """
        # make sure the dataset follows the order of variables specified in
        # the config file. This is important so also in the simulation results
        # the scalers are matched.
        
        for key in self.config.data_structure.observed_data_variables:
            obs_1D_array = self.dataarray_to_1Darrayy(dataarray=self.observations[key])

            # scaler = StandardScaler()
            scaler = MinMaxScaler()
            
            # add bounds to array of observations and fit scaler
            lower_bound = np.array(self.config.data_structure[key].min, ndmin=1)
            upper_bound = np.array(self.config.data_structure[key].max, ndmin=1)
            stacked_array = np.concatenate([lower_bound, upper_bound, obs_1D_array])
            scaler.fit(stacked_array.reshape((len(stacked_array), -1)))

            self._scaler.update({key: scaler})

        self.print_scaling_info()

        scaled_obs = self.scale_(self.observations)
        self.observations_scaled = scaled_obs

    def print_scaling_info(self):
        for key in self.config.data_structure.observed_data_variables:
            scaler = self._scaler[key]
            print(
                f"{type(scaler).__name__}(variable={key}, "
                f"min={scaler.data_min_[0]}, max={scaler.data_max_[0]})"
            )

    def scale_(self, dataset: xr.Dataset):
        obs_scaled = dataset.copy()
        for key in self.config.data_structure.observed_data_variables:
            obs_1D_array = self.dataarray_to_1Darrayy(dataarray=obs_scaled[key])
            x = obs_1D_array.values.reshape((len(obs_1D_array), -1))
            x_scaled = self._scaler[key].transform(x) 
            obs_1D_array.values = x_scaled.reshape((len(x_scaled)))
            obs_scaled[key] = self.array1D_to_dataarray(obs_1D_array)
        return obs_scaled

    @property
    def results(self):
        warnings.warn("Discouraged to use results property.", DeprecationWarning, 2)
        return self.create_dataset_from_numpy(
            Y=self.Y, 
            Y_names=self.config.data_structure.data_variables, 
            coordinates=self.coordinates
        )

    def results_to_df(self, results):
        if isinstance(results, xr.Dataset):
            return results
        elif isinstance(results, dict):
            return create_dataset_from_dict(
                Y=results, 
                coordinates=self.coordinates,
                data_structure=self.data_structure,
                var_dim_mapper=self.var_dim_mapper
            )
        elif isinstance(results, np.ndarray):
            return create_dataset_from_numpy(
                Y=results,
                Y_names=self.config.data_structure.data_variables,
                coordinates=self.coordinates,
            )
        else:
            raise NotImplementedError(
                "Results returned by the solver must be of type Dict or np.ndarray."
            )
    

    @property
    def results_scaled(self):
        scaled_results = self.scale_(self.results)
        # self.check_scaled_results_feasibility(scaled_results)
        return scaled_results

    def scale_results(self, Y):
        ds = self.create_dataset_from_numpy(
            Y=Y, 
            Y_names=self.config.data_structure.data_variables, 
            coordinates=self.coordinates
        )
        return self.scale_(ds)

    def check_scaled_results_feasibility(self, scaled_results):
        """Parameter inference or optimization over many variables can only succeed
        in reasonable time if the results that should be compared are on approximately
        equal scales. The Simulation class, automatically estimates the scales
        of result variables, when observations are provided. 

        Problems can occurr when observations are on very narrow ranges, but the 
        simulation results can take much larger or lower values for that variable.
        As a result the inference procedure will almost exlusively focus on the
        optimization of this variable, because it provides the maximal return.

        The function warns the user, if simulation results largely deviate from 
        the scaled minima or maxima of the observations. In this case manual 
        minima and maxima should be given
        """
        max_scaled = scaled_results.max()
        min_scaled = scaled_results.min()
        if isinstance(self._scaler, MinMaxScaler):
            for varkey, varval in max_scaled.variables.items():
                if varval > 2:
                    warnings.warn(
                        f"Scaled results for '{varkey}' are {float(varval.values)} "
                        "above the ideal maximum of 1. "
                        "You should specify explicit bounds for the results variable."
                    )

            for varkey, varval in min_scaled.variables.items():
                if varval < -1:
                    warnings.warn(
                        f"Scaled results for '{varkey}' are {float(varval.values)} "
                        "below the ideal minimum of 0. "
                        "You should specify explicit bounds for the results variable."
                    )

    def validate(self):
        # TODO: run checks if the simulation was set up correctly
        #       - do observation dimensions match the model output (run a mini
        #         simulation with reduced coordinates to verify)
        #       -
        if len(self.config.data_structure.data_variables) == 0:
            raise RuntimeError(
                "No data_variables were specified. "
                "Specify like sim.config.simulation.data_variables = ['a', 'b'] "
                "Or in the simulation section of the config file. "
                "Data variables track the state variables of the simulation. "
                "If you want to do inference, they must match the variables of "
                "the observations."
            )

                    
        if len(self.config.data_structure.dimensions) == 0:
            raise RuntimeError(
                "No dimensions of the simulation were specified. "
                "Which observations are you expecting? "
                "'time' or 'id' are reasonable choices. But it all depends on "
                "your data. Dimensions must match your data if you want to do "
                "Parameter inference."
            )

    @staticmethod
    def parameterize(free_parameters: Dict[str,float|str|int], model_parameters: Dict) -> Dict:
        """
        Optional. Set parameters and initial values of the model. 
        Must return a dictionary with the keys 'y0' and 'parameters'
        
        Can be used to define parameters directly in the script or from a 
        parameter file.

        Arguments
        ---------

        input: List[str] file paths of parameter/input files
        theta: List[Param] a list of Parameters. By default the parameters
            specified in the settings.cfg are used in this list. 

        returns
        -------

        tulpe: tuple of parameters, can have any length.
        """
        parameters = copy.deepcopy(model_parameters["parameters"])
        parameters.update(free_parameters)

        updated_model_parameters = dict(parameters=parameters)
        for k, v in model_parameters.items():
            if k == "parameters":
                continue
            
            updated_model_parameters[k] = v

        return updated_model_parameters

    def run(self):
        """
        Implementation of the forward simulation of the model. Needs to return
        X and Y

        returns
        -------

        X: np.ndarray | xr.DataArray
        Y: np.ndarray | xr.DataArray
        """
        raise NotImplementedError
    
    def objective_function(self, results, **kwargs):
        func = getattr(self, self.config.inference.objective_function)
        obj = func(results, **kwargs)

        if obj.ndim == 0:
            obj_value = float(obj)
            obj_name = "objective"
        elif obj.ndim == 1:
            obj_value = obj.values
            obj_name = list(obj.coords["variable"].values)
        else:
            raise ValueError("Objectives should be at most 1-dimensional.")

        if len(self._objective_names) == 0:
            self._objective_names = obj_name

        return obj_name, obj_value

    def total_average(self, results):
        """objective function returning the total MSE of the entire dataset"""
        
        diff = (self.scale_(self.results_to_df(results)) - self.observations_scaled).to_array()
        return (diff ** 2).mean()

    def prior(self):
        raise NotImplementedError

    def initialize(self, input):
        """
        initializes the simulation. Performs any extra work, not done in 
        parameterize or set_coordinates. 

        Overwrite in a case study simulation if special tasks are necessary
        """
        warnings.warn(
            "Using default initialize method, "+
            "(load observations, define 'y0', define 'x_in'). "+
            "This may be insufficient for more complex simulations.",
            category=UserWarning
        )

        obs_path = os.path.join(self.data_path, self.config.case_study.observations)
        if obs_path is not None:
            if os.path.exists(obs_path):
                self.observations = xr.load_dataset(obs_path)
            else:
                raise FileNotFoundError(
                    "Observations could not be found under the following path: "+
                    f"'{obs_path}'. Make sure it exists "+
                    "('sim.config.case_study.observations')"
                )
        else:
            warnings.warn(
                "'sim.config.case_study.observations' is undefined",
                category=UserWarning
            )

        if self.config.simulation.y0 is not None:
            self.model_parameters["y0"] = self.parse_input(
                input="y0", 
                reference_data=self.observations,
                drop_dims=[self.config.simulation.x_dimension]
            )
        else:
            warnings.warn(
                "'sim.config.simulation.y0' is undefined.",
                category=UserWarning
            )

        if self.config.simulation.x_in is not None:
            self.model_parameters["x_in"] = self.parse_input(
                input="x_in", 
                reference_data=self.observations,
                drop_dims=[]
            )
        else:
            warnings.warn(
                "'sim.config.simulation.x_in' is undefined.",
                category=UserWarning
            )

        self.model_parameters["parameters"] = self.config.model_parameters.value_dict
    
    def dump(self, results):
        pass
        
    
    def plot(self, results):
        pass

    @staticmethod
    def create_dataset_from_numpy(Y, Y_names, coordinates):
        warnings.warn(
            "Use `create_dataset_from_numpy` defined in sim.evaluator",
            category=DeprecationWarning
        )
        n_vars = Y.shape[-1]
        n_dims = len(Y.shape)
        assert n_vars == len(Y_names), errormsg(
            """The number of datasets must be the same as the specified number
            of data variables declared in the `settings.cfg` file.
            """
        )

        # transpose Y to put the variable dimension first, then add the
        # remaining dimensions in order
        Y_transposed = Y.transpose((n_dims - 1, *range(n_dims - 1)))

        data_arrays = []
        for y, y_name in zip(Y_transposed, Y_names):
            da = xr.DataArray(y, coords=coordinates, name=y_name)
            data_arrays.append(da)

        dataset = xr.merge(data_arrays)

        return dataset

    @staticmethod
    def option_as_list(opt):
        # TODO: Remove when all methods have been updated to the new config API
        if not isinstance(opt, (list, tuple)):
            opt_list = [opt]
        else:
            opt_list = opt

        return opt_list

    @property
    def input_file_paths(self):
        # TODO: Remove when all method has been updated to the new config API
        return self.config.input_file_paths

    # config as properties
    @property
    def dimensions(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.data_structure.dimensions

    @property
    def data_variables(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.data_structure.data_variables

    @property
    def n_ode_states(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.simulation.n_ode_states
    
    @n_ode_states.setter
    def n_ode_states(self, n_ode_state):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        self.config.simulation.n_ode_states = n_ode_state

    @property
    def input_files(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.simulation.input_files
  
    @property
    def case_study_path(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.package

    @property
    def root_path(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.root

    @property
    def case_study(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.name

    @property
    def scenario(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.scenario

    @property
    def scenario_path(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.scenario_path

    # TODO Outsource model parameters also to config (if it makes sense)
    @property
    def model_parameter_values(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return [p.value for p in self.config.model_parameters.free.values()]
    
    @property
    def model_parameter_names(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return list(self.config.model_parameters.free.keys())
    
    @property
    def n_free_parameters(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.model_parameters.n_free

    @property
    def model_parameter_dict(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.model_parameters.free_value_dict


    @property
    def output_path(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.output_path

    @property
    def data_path(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.case_study.data_path
       

    @property
    def data_variable_bounds(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        lower_bounds = self.config.data_structure.data_variables_min
        upper_bounds = self.config.data_structure.data_variables_max
        return lower_bounds, upper_bounds

    @property
    def objective(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.inference.objective_function

    @property
    def n_objectives(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.inference.n_objectives

    @property
    def objective_names(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.inference.objective_names

    @property
    def n_cores(self):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        return self.config.multiprocessing.n_cores
    
    @n_cores.setter
    def n_cores(self, value):
        # TODO: Remove when all method has been updated to the new config API
        warnings.warn(config_deprecation, DeprecationWarning)
        self.config.multiprocessing.cores = value

    def create_random_integers(self, n: int):
        return self.RNG.integers(low=0, high=int(1e18), size=n).tolist()
        
    def refill_consumed_seeds(self):
        n_seeds_left = len(self._random_integers)
        if n_seeds_left == self.config.multiprocessing.n_cores:
            n_new_seeds = self._seed_buffer_size - n_seeds_left
            new_seeds = self.create_random_integers(n=n_new_seeds)
            self._random_integers.extend(new_seeds)
            print(f"Appended {n_new_seeds} new seeds to sim.")
        
    def draw_seed(self):
        # return None       
        # the collowing has no multiprocessing stability when the simulation is
        # serialized directly
        self.refill_consumed_seeds()
        seed = self._random_integers.pop(0)
        return seed

    @property
    def error_model(self):
        em = parse_config_section(self.config._config["error-model"], method="strfloat")
        return em

    @property
    def evaluator_dim_order(self):
        return self.config.data_structure.evaluator_dim_order

    @property
    def var_dim_mapper(self) -> Dict[str, List[str]]:
        return self.config.data_structure.var_dim_mapper
    
    @property
    def data_structure(self):
        return self.config.data_structure.dimdict

    @property
    def data_structure_and_dimensionality(self):
        data_structure = {}
        for dv, dv_dims in self.config.data_structure.dimdict.items():
            dim_sizes = {}
            for dim in dv_dims:
                coord = self.coordinates[dim]
                dim_sizes.update({dim: len(coord)})
            data_structure.update({dv: dim_sizes})

        return data_structure

    @property
    def dimension_coords(self) -> Dict[str, Tuple[str|int, ...]]:
        """Goes through dimensions of data structure and adds coordinates,
        then goes through dimensions of parameters and searches in coordinates
        and indices to 
        """
        dim_coords = {}
        for dim in self.config.data_structure.dimensions:
            try:
                coord = self.coordinates[dim]   
            except KeyError:
                raise KeyError(
                    f"'{dim}' was specified in config.data_structure but is not "+
                    f"available in sim.coordinates['{dim}']. Provide observations "+
                    "that have coordinates specified for this dimension, or, "+
                    "if the dimension is unneeded, remove it from the definition "+
                    "of the data variable."
                )
            dim_coords.update({dim: tuple(coord)})

        for dim in self.config.model_parameters.dimensions:
            coord = self.coordinates.get(dim, None)

            if coord is None:
                coord = self.coordinates_indices.get(dim, None)
            
            if coord is None:
                raise KeyError(
                    "No coordinates have been defined for parameter dimension "+
                    f"{dim}. Use `sim.coordinates['{dim}'] = [...]` to define "+
                    "the coordinates." 
                )
            
            _, index = np.unique(coord, return_index=True)
            unique_coords = tuple(np.array(coord)[sorted(index)])

            if dim in dim_coords and unique_coords != dim_coords[dim]:
                raise ValueError(
                    "unique coordinates in sim.indices were not identical to "+
                    f"simulation coordinates of dimension '{dim}'"
                )

            dim_coords.update({dim: unique_coords})

        return dim_coords
    
    @property
    def dimension_sizes(self) -> Dict[str, int]:
        return {
            dim: len(coords) for dim, coords 
            in self.dimension_coords.items()
        }

    @staticmethod
    def index_coordinates(array):
        # Create a dictionary to map unique coordinates to indices
        # using np.unique thereby retains the order of the elements in
        # the order of their furst occurence
        # use an unsorted unique index
        unique_coordinates, index = np.unique(array, return_index=True)
        unique_coordinates = unique_coordinates[index.argsort()]
        string_to_index = {
            coord: index for index, coord 
            in enumerate(unique_coordinates)
        }

        # Convert the original array to a list of indices
        index_list = [string_to_index[string] for string in array]
        return index_list

    def create_index(self, coord):
        if coord not in self.observations.coords:
            raise KeyError(f"{coord} is not in {list(self.observations.coords)}")
        
        batch_dim = self.config.simulation.batch_dimension
        # TODO: There may be a problem, when batch dimension is not defined!

        return {coord: xr.DataArray(
                self.index_coordinates(self.observations[coord].values),
                dims=(batch_dim), 
                coords={
                    batch_dim: self.observations[batch_dim], 
                    coord: self.observations[coord]
                }, 
                name=f"{coord}_index"
            )
        }

    def reorder_dims(self, Y):
        results = {}
        for var, mapper in self.var_dim_mapper.items():
            results.update({
                var: Y[var][np.array(mapper)]
            })
    
        return results

    def prior_predictive_checks(self, **plot_kwargs):
        """OVERWRITE IF NEEDED.
        Placeholder method. Minimally plots the prior predictions of a 
        simulation.
        """

        idata = self.inferer.prior_predictions()

        checks = {}
        flag = self.inferer.check_prior_for_nans(idata=idata)
        checks.update({"NaN values in prior draws": flag})

        if not all(checks.values()):
            raise ValueError("Not all checks passed.")

        simplot = self.SimulationPlot(
            observations=self.observations,
            idata=idata,
            coordinates=self.dimension_coords,
            config=self.config,
            idata_groups=["prior_predictive"],
            **plot_kwargs
        )   

        simplot.plot_data_variables()
        simplot.save("prior_predictive.png")

    def posterior_predictive_checks(self, **plot_kwargs):
        """OVERWRITE IF NEEDED.
        Placeholder method. Minimally plots the posterior predictions of a 
        simulation.
        """

        simplot = self.SimulationPlot(
            observations=self.observations,
            idata=self.inferer.idata,
            coordinates=self.dimension_coords,
            config=self.config,
            idata_groups=["posterior_predictive"],
            **plot_kwargs
        )

        simplot.plot_data_variables()
        simplot.save("posterior_predictive.png")


    def report(self):
        """Creates a configurable report. To select which items to report and
        to fine-tune the report settings, modify the options in `config.report`.
        """
        self._report = self.Report(config=self.config, backend=type(self.inferer))

        if self.solver_post_processing is None:
            if self.config.simulation.solver_post_processing is not None:
                post_processing = getattr(self._mod, self.config.simulation.solver_post_processing)
            else:
                post_processing = None
        else:
            post_processing = self.solver_post_processing
        _ = self._report.model(self.model, post_processing)

        _ = self._report.parameters(self.model_parameters)
        
        self._report.table_parameter_estimates(
            posterior=self.inferer.idata.posterior,
            indices=self.indices
        )

        _ = self._report.goodness_of_fit(idata=self.inferer.idata)

        _ = self._report.diagnostics(idata=self.inferer.idata)

        _ = self._report.additional_reports(sim=self)

        self._report.compile_report()

        # TODO: find a good way to integrate posterior predictive and prior predictive 
        # into the report. I think their execution should be continued outside of the report,
        # but they could be linked (as images) inside the report. This way, the report
        # would just have to plot them if available.

    def export(
        self, 
        directory: Optional[str] = None,
        mode: Literal["export", "copy"] = "export",

    ):
        """Exports a SimulationBase object to disk. If directory is given, objects are
        exported to the directory, otherwise, exports are made to sim.output_path

        Parameters
        ----------

        directory : str
            Optional. Specifies the directory where the simulation should be exported to.
            Otherwise exports to output path
        mode : str
            If from_directory is used in 'import'-mode, the output, data and scenario
            paths are changed to take the path of the directory, which means that all
            output, data, etc. is directed to the directory. If mode='copy', the original
            paths read from the config file remain as they were. 
        
    
        Notes
        -----

        This method exports at least two files:
        - 'settings.cfg' 
        - 'observations.nc'. 
        
        If the inferer was already run, it additionally exports 
        - 'idata.nc'
        
        """
        if directory is None:
            directory = self.output_path

        os.makedirs(directory, exist_ok=True)

        data_path_backup = self.config.case_study.data
        output_path_backup = self.config.case_study.output
        scenario_path_backup = self.config.case_study.scenario_path_override
        
        self.config.case_study.data = directory
        # FIXME: Setting package to . did not work out with use of pymob infer
        #        Why did I do this? Make sure it checks out
        # self.config.case_study.package = "."
        self.save_observations(directory=directory, force=True)

        if hasattr(self, "inferer"):
            backend = type(self.inferer).__name__
        
            if backend == "NumpyroBackend":
                self.config.simulation.inferer = "numpyro"
            elif backend == "ScipyBackend":
                self.config.simulation.inferer = "scipy"
            elif backend == "PymooBackend":
                self.config.simulation.inferer = "pymoo"
            elif backend == "PyabcBackend":
                self.config.simulation.inferer = "pyabc"
            else:
                raise NotImplementedError(f"Backend: {backend} is not implemented.")


            if hasattr(self.inferer, "idata"):
                idata_path = os.path.join(directory, "idata.nc")
                # removes the existing file before attempting overwrite. Otherwise
                # this raises an OS Error
                if os.access(idata_path, os.W_OK):
                    os.remove(idata_path)
                self.inferer.idata.to_netcdf(idata_path)
            else:
                pass
        else:
            pass

        if mode == "copy":
            # under copy-mode, the exported scenario file should retain the original
            # data path. This is temporarily overwritten in from_directory(mode="copy")
            # and then reset
            self.config.case_study.data = data_path_backup
            self.config.save(fp=os.path.join(directory, "settings.cfg"), force=True)
        elif mode == "export":
            # under mode export, the data_path in the config file should reflect the 
            # export directory
            # output path and scenario paths are irrelevant because they are overwritten
            # using import mode of from_directory
            self.config.case_study.output = directory
            self.config.case_study.scenario_path_override = directory
            self.config.save(fp=os.path.join(directory, "settings.cfg"), force=True)
            self.config.case_study.data = data_path_backup
            self.config.case_study.output = output_path_backup
            self.config.case_study.scenario_path_override = scenario_path_backup

        else:
            raise PymobError(textwrap.dedent(
                """export only supports the modes 'copy' and 'export', please select 
                one of those options.
                """
            ))


    @classmethod
    def from_directory(
        cls, 
        directory: str,
        mode: Literal["import", "copy"] = "import",
    ) -> "SimulationBase":
        """Imports a SimulationBase from a directory where the simulation had been 
        exported to with sim.export()

        Parameters
        ----------
        directory : str
            The path to the directory, the required contents of the directory are:
            'settings.cfg' and 'observations.nc'. Optionally 'idata.nc' can be defined,
            which contains the posterior. From this a MempySim with completed inference
            can be initialized

        mode : str
            If from_directory is used in 'import'-mode, the output, data and scenario
            paths are changed to take the path of the directory, which means that all
            output, data, etc. is directed to the directory. If mode='copy', the original
            paths read from the config file remain as they were. 
        """
        cfg_file = os.path.join(directory, "settings.cfg")
        config = Config(config=cfg_file)

        if mode == "import":
            config.case_study.data = directory
            config.case_study.output = directory
            config.case_study.scenario_path_override = directory
        elif mode == "copy":
            data_path_backup = config.case_study.data
            config.case_study.data = directory            
        else:
            raise PymobError(textwrap.dedent(
                """from_directory only supports the modes 'copy' and 'import', please select 
                one of those options.
                """
            ))

        sim = cls(config)
        sim.setup()

        if hasattr(sim.config.simulation, "inferer"):
            sim.set_inferer(sim.config.simulation.inferer)
            idata = os.path.join(directory, "idata.nc")
            if os.path.exists(idata):
                # load transfers the idata object into memory, which is important
                # for decoupling it from the underlying file, which may be used
                # for 
                sim.inferer.idata = az.from_netcdf(idata).load()
            else:
                pass
        else:
            pass

        if mode == "copy":
            # reset the data path to its original value, so that the copied simulation
            # is equivalent to the original one.
            sim.config.case_study.data = data_path_backup

        return sim

    def copy(self):
        """Creates a copy of a SimulationBase object by exporting to a temporary directory
        in the output path and importing again from that directoy. The temporary directory
        is destroyed directly afterwards
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # create the tempdir in the output path, because a default temporary directory
            # may not have enough space. Using the output path here resolves any path issues.
            tmp_basedir = os.path.join(self.output_path, "_tmp")
            os.makedirs(tmp_basedir, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=tmp_basedir) as name:
                self.export(directory=name, mode="copy")
                sim_copy = type(self).from_directory(name, mode="copy")

        return sim_copy
