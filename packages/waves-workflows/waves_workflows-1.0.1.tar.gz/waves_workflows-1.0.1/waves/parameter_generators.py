"""Provide build system compatible parameter generators for use as an external API module.

Will raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import collections
import copy
import hashlib
import itertools
import pathlib
import string
import sys
import typing
import warnings
from abc import ABC, abstractmethod

import numpy
import SALib
import scipy.stats
import SCons.Environment
import xarray
import yaml

from waves import _settings, _utilities
from waves._settings import _hash_coordinate_key, _set_coordinate_key
from waves.exceptions import ChoicesError, MutuallyExclusiveError, SchemaValidationError

_exclude_from_namespace = set(globals().keys())

#: The set name coordinate used in WAVES parameter study Xarray Datasets
SET_COORDINATE_KEY: typing.Final[str] = _set_coordinate_key

#: The set hash coordinate used in WAVES parameter study Xarray Datasets
HASH_COORDINATE_KEY: typing.Final[str] = _hash_coordinate_key


class ParameterGenerator(ABC):
    """Abstract base class for parameter study generators.

    Parameters must be scalar valued integers, floats, strings, or booleans

    :param parameter_schema: The YAML loaded parameter study schema dictionary, e.g.
        ``{parameter_name: schema_value}``.  Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param require_previous_parameter_study: Raise a ``RuntimeError`` if the previous parameter study file is missing.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    """

    def __init__(
        self,
        parameter_schema: dict,
        output_file_template: str | None = _settings._default_output_file_template,
        output_file: str | pathlib.Path | None = _settings._default_output_file,
        output_file_type: _settings._allowable_output_file_typing = _settings._default_output_file_type_api,
        set_name_template: str = _settings._default_set_name_template,
        previous_parameter_study: str | pathlib.Path | None = _settings._default_previous_parameter_study,
        require_previous_parameter_study: bool = _settings._default_require_previous_parameter_study,
        overwrite: bool = _settings._default_overwrite,
        write_meta: bool = _settings._default_write_meta,
        **kwargs,
    ) -> None:
        self.parameter_schema = parameter_schema
        self.output_file_template = (
            _utilities._AtSignTemplate(output_file_template) if output_file_template is not None else None
        )
        self.output_file = pathlib.Path(output_file) if output_file is not None else None
        self.output_file_type = output_file_type
        self.set_name_template = _utilities._AtSignTemplate(set_name_template)
        self.previous_parameter_study = (
            pathlib.Path(previous_parameter_study) if previous_parameter_study is not None else None
        )
        self.require_previous_parameter_study = require_previous_parameter_study
        self.overwrite = overwrite
        self.write_meta = write_meta

        if self.output_file_template is not None and self.output_file is not None:
            raise MutuallyExclusiveError(
                "The options 'output_file_template' and 'output_file' are mutually exclusive. "
                "Please specify one or the other."
            )

        if self.output_file_type not in _settings._allowable_output_file_types:
            raise ChoicesError(
                f"Unsupported 'output_file_type': '{self.output_file_type}'. "
                f"The 'output_file_type' must be one of {_settings._allowable_output_file_types}"
            )

        if self.previous_parameter_study is not None and not self.previous_parameter_study.is_file():
            message = f"Previous parameter study file '{self.previous_parameter_study}' does not exist."
            if self.require_previous_parameter_study:
                raise RuntimeError(message)
            else:
                warnings.warn(message)

        # Override set name template if output name template is provided.
        self.provided_output_file_template = False
        if self.output_file_template is not None:
            self.provided_output_file_template = True
            # Append the set number placeholder if missing
            output_file_template_string = self.output_file_template.safe_substitute()
            if _settings._template_placeholder not in output_file_template_string:
                self.output_file_template = _utilities._AtSignTemplate(
                    f"{output_file_template_string}{_settings._template_placeholder}"
                )
            self.set_name_template = self.output_file_template

        # Infer output directory from output file template if provided. Set to PWD otherwise.
        if self.output_file_template is not None:
            self.output_directory = pathlib.Path(self.output_file_template.safe_substitute()).parent
        else:
            self.output_directory = pathlib.Path.cwd()
        self.parameter_study_meta_file = self.output_directory / _settings._parameter_study_meta_file

        # Help mypy determine types of attributes set in semi-private function calls
        # TODO: make these return values from _validate and assign directly in __init__?
        self._parameter_names: list[str]
        self._validate()

        # Help mypy determine types of attributes set in semi-private function calls
        # TODO: make ``parameter_study`` a return values from _generate and assign directly in __init__, dropping
        # intermediate working variables?
        self._samples: numpy.ndarray
        self._set_hashes: list[str]
        self._set_names: dict[str, str]
        self.parameter_study: xarray.Dataset
        self._generate(**kwargs)

    @abstractmethod
    def _validate(self) -> None:
        """Process parameter study input to verify schema.

        Must set the class attributes:

        * ``self._parameter_names``: list of strings containing the parameter study's parameter names

        Minimum necessary work example:

        .. code-block::

           # Work unique to the parameter generator schema. Example matches CartesianProduct schema.
           self._parameter_names = list(self.parameter_schema.keys())
        """

    @abstractmethod
    def _generate(self, **kwargs) -> None:
        """Generate the parameter study definition.

        All implemented class method should accept kwargs as ``_generate(self, **kwargs)``. The ABC class accepts, but
        does not use any ``kwargs``.

        Must set the class attributes:

        * ``self._samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets,
            number of parameters). If it's possible that the samples may be of mixed type,
            ``numpy.array(..., dtype=object)`` should be used to preserve the original Python types.
        * ``self._set_hashes``: list of parameter set content hashes created by calling
          ``self._create_set_hashes`` after populating the ``self._samples`` parameter study values.
        * ``self._set_names``: Dictionary mapping parameter set hash to parameter set name strings created by
            calling ``self._create_set_names`` after populating ``self._set_hashes``.
        * ``self.parameter_study``: The Xarray Dataset parameter study object, created by calling
          ``self._create_parameter_study()`` after defining ``self._samples``.

        Minimum necessary work example:

        .. code-block::

           # Work unique to the parameter generator schema and set generation
           set_count = 5  # Normally set according to the parameter schema
           parameter_count = len(self._parameter_names)
           self._samples = numpy.zeros((set_count, parameter_count))

           # Work performed by common ABC methods
           super()._generate()
        """
        self._create_set_hashes()
        self._create_set_names()
        self._create_parameter_study()
        if self.previous_parameter_study is not None and self.previous_parameter_study.is_file():
            self._merge_parameter_studies()

    def write(
        self,
        output_file_type: _settings._allowable_output_file_typing | None = None,
        dry_run: bool = _settings._default_dry_run,
    ) -> None:
        """Write the parameter study to STDOUT or an output file.

        Writes to STDOUT by default. Requires non-default ``output_file_template`` or ``output_file`` specification to
        write to files.

        If printing to STDOUT, print all parameter sets together. If printing to files, overwrite when contents of
        existing files have changed. If overwrite is specified, overwrite all parameter set files.
        If a dry run is requested print file-content associations for files that would have been written.

        Writes parameter set files in YAML syntax by default. Output formatting is controlled by
        ``output_file_type``.

        .. code-block::

           parameter_1: 1
           parameter_2: a

        :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
        :param dry_run: Print contents of new parameter study output files to STDOUT and exit

        :raises waves.exceptions.ChoicesError: If an unsupported output file type is requested
        """
        if output_file_type is None:
            output_file_type = self.output_file_type

        self.output_directory.mkdir(parents=True, exist_ok=True)

        if self.write_meta and self.provided_output_file_template:
            self._write_meta()

        # Remove (or refactor away) from these complex types
        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/812
        parameter_study_object: dict | xarray.Dataset
        parameter_study_iterator: collections.abc.ItemsView | xarray.core.groupby.DatasetGroupBy
        conditional_write_function: (
            collections.abc.Callable[[pathlib.Path, dict], None]
            | collections.abc.Callable[[pathlib.Path, xarray.Dataset], None]
        )
        if output_file_type == "h5":
            parameter_study_object = self.parameter_study
            parameter_study_iterator = parameter_study_object.groupby(_set_coordinate_key)
            conditional_write_function = self._conditionally_write_dataset
        elif output_file_type == "yaml":
            parameter_study_object = self.parameter_study_to_dict()
            parameter_study_iterator = parameter_study_object.items()
            conditional_write_function = self._conditionally_write_yaml
        else:
            raise ChoicesError(
                f"Unsupported 'output_file_type': '{self.output_file_type}. "
                f"The 'output_file_type' must be one of {_settings._allowable_output_file_types}"
            )
        self._write(
            parameter_study_object,
            parameter_study_iterator,
            conditional_write_function,
            dry_run=dry_run,
        )

    def _scons_write(self, target: list, source: list, env: SCons.Environment.Environment) -> None:  # noqa: ARG002
        """`SCons Python build function`_ wrapper for the parameter generator's write() function.

        Reference: https://scons.org/doc/production/HTML/scons-user/ch17s04.html

        Searches for following keyword arguments in the task construction environment and passes to the write function:

        * ``output_file_type``

        :param target: The target file list of strings
        :param source: The source file list of SCons.Node.FS.File objects
        :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object
        """
        kwargs = {}
        if "output_file_type" in env:
            kwargs.update({"output_file_type": env["output_file_type"]})
        self.write(**kwargs)

    # Consolidate (or refactor away) the complex write/_write logic
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/812
    def _write(
        self,
        parameter_study_object: dict | xarray.Dataset,
        parameter_study_iterator: collections.abc.ItemsView | xarray.core.groupby.DatasetGroupBy,
        conditional_write_function: (
            collections.abc.Callable[[pathlib.Path, dict], None]
            | collections.abc.Callable[[pathlib.Path, xarray.Dataset], None]
        ),
        dry_run: bool = _settings._default_dry_run,
    ) -> None:
        """Write parameter study formatted output to STDOUT, separate set files, or a single file.

        Behavior as specified in :meth:`waves.parameter_generators.ParameterGenerator.write`
        """
        # If no output file template is provided, printing to stdout or single file. Prepend set names.
        if not self.provided_output_file_template:
            # If no output file template is provided, printing to stdout or a single file
            output_text = (
                yaml.safe_dump(parameter_study_object)
                if isinstance(parameter_study_object, dict)
                else f"{parameter_study_object}\n"
            )
            if self.output_file and not dry_run:
                # Remove (or refactor away) from this static type checking skip
                # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/812
                conditional_write_function(self.output_file, parameter_study_object)  # type: ignore[arg-type]
            elif self.output_file and dry_run:
                sys.stdout.write(f"{self.output_file.resolve()}\n{output_text}")
            else:
                sys.stdout.write(output_text)
        # If output file template is provided, writing to parameter set files
        else:
            for set_file, parameters in parameter_study_iterator:
                set_path = pathlib.Path(set_file)
                text = yaml.safe_dump(parameters) if isinstance(parameters, dict) else f"{parameters}\n"
                if self.overwrite or not set_path.is_file():
                    # If dry run is specified, print the files that would have been written to stdout
                    if dry_run:
                        sys.stdout.write(f"{set_path.resolve()}\n{text}")
                    else:
                        # Remove (or refactor away) from this static type checking skip
                        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/812
                        conditional_write_function(set_path, parameters)  # type: ignore[arg-type]

    def _conditionally_write_dataset(
        self,
        existing_parameter_study: pathlib.Path,
        parameter_study: xarray.Dataset,
    ) -> None:
        """Write NetCDF file over previous study if the datasets have changed or self.overwrite is True.

        :param existing_parameter_study: A relative or absolute file path to a previously created parameter
            study Xarray Dataset
        :param parameter_study: Parameter study xarray dataset
        """
        write = True
        if not self.overwrite and existing_parameter_study.is_file():
            with xarray.open_dataset(existing_parameter_study, engine="h5netcdf") as existing_dataset:
                if parameter_study.equals(existing_dataset):
                    write = False
        if write:
            existing_parameter_study.parent.mkdir(parents=True, exist_ok=True)
            parameter_study.to_netcdf(path=existing_parameter_study, mode="w", format="NETCDF4", engine="h5netcdf")

    def _conditionally_write_yaml(
        self,
        output_file: str | pathlib.Path,
        parameter_dictionary: dict,
    ) -> None:
        """Write YAML file over previous study if the datasets have changed or self.overwrite is True.

        :param output_file: A relative or absolute file path to the output YAML file
        :param parameter_dictionary: dictionary containing parameter set data
        """
        write = True
        if not self.overwrite and pathlib.Path(output_file).is_file():
            # FIXME: simplify class API/attributes type handling to avoid the explict type cast
            with pathlib.Path(output_file).open(mode="r") as existing_file:
                existing_yaml_object = yaml.safe_load(existing_file)
                if existing_yaml_object == parameter_dictionary:
                    write = False
        if write:
            # FIXME: simplify class API/attributes type handling to avoid the explict type cast
            with pathlib.Path(output_file).open(mode="w") as outfile:
                outfile.write(yaml.dump(parameter_dictionary))

    def _write_meta(self) -> None:
        """Write the parameter study meta data file.

        The parameter study meta file is always overwritten. It should *NOT* be used to determine if the parameter study
        target or dependee is out-of-date. Parameter study file paths are written as absolute paths.
        """
        set_files = [pathlib.Path(set_name) for set_name in self.parameter_study.coords[_set_coordinate_key].values]
        # Always overwrite the meta data file to ensure that *all* parameter file names are included.
        with self.parameter_study_meta_file.open(mode="w") as meta_file:
            if self.output_file:
                meta_file.write(f"{self.output_file.resolve()}\n")
            else:
                for set_file in set_files:
                    meta_file.write(f"{set_file.resolve()}\n")

    def _create_set_hashes(self) -> None:
        """Construct unique, repeatable parameter set content hashes from ``self._samples``.

        Creates an md5 hash from the concatenated string representation of parameter ``name:value`` associations.

        requires:

        * ``self._samples``: The parameter study samples. Rows are sets. Columns are parameters.
        * ``self._parameter_names``: parameter names used as columns of parameter study

        creates attribute:

        * ``self._set_hashes``: parameter set content hashes identifying rows of parameter study
        """
        self._set_hashes = _calculate_set_hashes(self._parameter_names, self._samples)

    def _create_set_names(self) -> None:
        """Construct parameter set names from the set name template and number of parameter sets in ``self._samples``.

        Creates the class attribute ``self._set_names`` required to populate the ``_generate()`` method's
        parameter study Xarray dataset object.

        requires:

        * ``self._set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self.set_name_template``: Parameter set name template. Overridden by ``output_file_template``, if provided

        creates attribute:

        * ``self._set_names``: Dictionary mapping parameter set hash to parameter set name
        """
        self._set_names = _create_set_names(self._set_hashes, self.set_name_template)

    def _create_set_names_array(self) -> xarray.DataArray:
        """Create an Xarray DataArray with the parameter set names using parameter set hashes as the coordinate.

        :return: set_names_array
        """
        return xarray.DataArray(
            list(self._set_names.values()),
            coords=[list(self._set_names.keys())],
            dims=[_hash_coordinate_key],
            name=_set_coordinate_key,
        )

    def _merge_set_names_array(self) -> None:
        """Merge the parameter set names array into the parameter study dataset as a non-index coordinate."""
        set_names_array = self._create_set_names_array()
        self.parameter_study = xarray.merge(
            [self.parameter_study.reset_coords(), set_names_array], join="outer", compat="no_conflicts"
        ).set_coords(_set_coordinate_key)

    def _create_parameter_study(self) -> None:
        """Create the standard structure for the parameter study dataset.

        requires:

        * ``self._set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self._parameter_names``: parameter names used as columns of parameter study
        * ``self._samples``: The parameter study samples. Rows are sets. Columns are parameters.

        creates attribute:

        * ``self.parameter_study``
        """
        sample_arrays = [
            xarray.DataArray(
                _coerce_values(list(values), name),
                name=name,
                dims=[_hash_coordinate_key],
                coords={_hash_coordinate_key: self._set_hashes},
            )
            for name, values in zip(self._parameter_names, self._samples.T, strict=True)
        ]
        self.parameter_study = xarray.merge(sample_arrays, join="outer", compat="no_conflicts")
        self._merge_set_names_array()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})

    def _parameter_study_to_numpy(self) -> numpy.ndarray:
        """Return the parameter study data as a 2D numpy array.

        :return: data
        """
        return _parameter_study_to_numpy(self.parameter_study)

    def parameter_study_to_dict(self) -> dict[str, dict[str, typing.Any]]:
        """Return parameter study as a dictionary.

        Used for iterating on parameter sets in an SCons workflow with parameter substitution dictionaries, e.g.

        .. code-block::

           >>> for set_name, parameters in parameter_generator.parameter_study_to_dict().items():
           ...     print(f"{set_name}: {parameters}")
           ...
           parameter_set0: {'parameter_1': 1, 'parameter_2': 'a'}
           parameter_set1: {'parameter_1': 1, 'parameter_2': 'b'}
           parameter_set2: {'parameter_1': 2, 'parameter_2': 'a'}
           parameter_set3: {'parameter_1': 2, 'parameter_2': 'b'}

        :return: parameter study sets and samples as a dictionary: {set_name: {parameter: value}, ...}
        """
        parameter_study_dictionary = {}
        for set_name, parameters in self.parameter_study.groupby(_set_coordinate_key):
            parameter_dict = {str(key): array.values.item() for key, array in parameters.items()}
            parameter_study_dictionary[str(set_name)] = parameter_dict
        return parameter_study_dictionary

    def _merge_parameter_studies(self) -> None:
        """Merge the current parameter study into a previous parameter study.

        When merging across identical parameter spaces, preserves the previous parameter study set name to set
        contents associations by dropping the new studies' set names during merge. If the parameter spaces are unique
        across studies, this method will use ``_propagate_parameter_space()`` to resolve the parameter spaces and break
        the set name to set contents associations of the previous study.

        Resets attributes:

        * ``self.parameter_study``
        * ``self._samples``
        * ``self._set_hashes``
        * ``self._set_names``

        :raises RuntimeError: If the ``self.previous_parameter_study`` attribute is None
        """
        if self.previous_parameter_study is None:
            raise RuntimeError("Called without a previous parameter study")

        previous_parameter_study = _open_parameter_study(self.previous_parameter_study)
        self.parameter_study = _merge_parameter_studies(
            [previous_parameter_study, self.parameter_study], self.set_name_template
        )
        self.parameter_study = self.parameter_study.swap_dims({_set_coordinate_key: _hash_coordinate_key})
        previous_parameter_study.close()

        # Recover parameter study numpy array(s) to match merged study
        self._samples = self._parameter_study_to_numpy()

        # Recalculate attributes with lengths matching the number of parameter sets
        self._set_hashes = list(self.parameter_study.coords[_hash_coordinate_key].values)
        self._set_names = self.parameter_study[_set_coordinate_key].to_series().to_dict()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})


class _ScipyGenerator(ParameterGenerator, ABC):
    sampler_class: str = ""

    def __init__(self, *args, **kwargs) -> None:
        """Require concrete child classes to set the ``self.sampler_class`` attribute to a string.

        :raises TypeError: if the ``self.sampler_class`` attribute is not overridden
        """
        if not self.sampler_class:
            raise ValueError("_ScipyGenerator subclasses must set ``sampler_class`` to a non-empty string")
        super().__init__(*args, **kwargs)

    def _validate(self) -> None:
        """Validate the parameter distribution schema. Executed by class initiation.

        .. code-block::

           parameter_schema = {
               'num_simulations': 4,  # Required key. Value must be an integer.
               'parameter_1': {
                   'distribution': 'norm',  # Required key. Value must be a valid scipy.stats
                   'loc': 50,               # distribution name.
                   'scale': 1
               },
               'parameter_2': {
                   'distribution': 'skewnorm',
                   'a': 4,
                   'loc': 30,
                   'scale': 2
               }
           }

        :raises waves.exceptions.SchemaValidationError:

            * Parameter schema is not a dictionary
            * Parameter schema ``num_simulations`` key is not an integer
            * Parameter definition distribution value is not a valid Python identifier
            * Parameter definition key(s) is not a valid Python identifier
            * Parameter schema does not have a ``num_simulations`` key
            * Parameter definition does not contain a ``distribution`` key
        """
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        if "num_simulations" not in self.parameter_schema:
            raise SchemaValidationError("Parameter schema is missing the required 'num_simulations' key")
        elif not isinstance(self.parameter_schema["num_simulations"], int):
            raise SchemaValidationError("Parameter schema 'num_simulations' must be an integer.")
        self._create_parameter_names()
        for name in self._parameter_names:
            parameter_keys = self.parameter_schema[name].keys()
            parameter_definition = self.parameter_schema[name]
            if "distribution" not in parameter_keys:
                raise SchemaValidationError(f"Parameter '{name}' does not contain the required 'distribution' key")
            elif (
                not isinstance(parameter_definition["distribution"], str)
                or not parameter_definition["distribution"].isidentifier()
            ):
                raise SchemaValidationError(
                    f"Parameter '{name}' distribution '{parameter_definition['distribution']}' "
                    "is not a valid Python identifier"
                )
            else:
                for key in parameter_keys:
                    if not isinstance(key, str) or not key.isidentifier():
                        raise SchemaValidationError(
                            f"Parameter '{name}' keyword argument '{key}' is not a valid Python identifier"
                        )
        # TODO: Raise an exception if the current parameter distributions don't match the previous_parameter_study
        self.parameter_distributions = self._generate_parameter_distributions()

    def _generate(self, **kwargs) -> None:
        set_count = self.parameter_schema["num_simulations"]
        parameter_count = len(self._parameter_names)
        override_kwargs = {"d": parameter_count}
        if kwargs:
            kwargs.update(override_kwargs)
        else:
            kwargs = override_kwargs
        sampler = getattr(scipy.stats.qmc, self.sampler_class)(**kwargs)
        self._generate_distribution_samples(sampler, set_count, parameter_count)
        super()._generate()

    def _generate_parameter_distributions(self) -> dict:
        """Return dictionary containing the {parameter name: scipy.stats distribution} defined by the parameter schema.

        :return: parameter_distributions
        """
        parameter_dictionary = copy.deepcopy({key: self.parameter_schema[key] for key in self._parameter_names})
        parameter_distributions = {}
        for parameter, attributes in parameter_dictionary.items():
            distribution_name = attributes.pop("distribution")
            parameter_distributions[parameter] = getattr(scipy.stats, distribution_name)(**attributes)
        return parameter_distributions

    def _generate_distribution_samples(
        self,
        sampler: (
            scipy.stats.qmc.Halton
            | scipy.stats.qmc.LatinHypercube
            | scipy.stats.qmc.PoissonDisk
            | scipy.stats.qmc.Sobol
        ),
        set_count: int,
        parameter_count: int,
    ) -> None:
        """Create parameter distribution samples.

        Requires attibrutes:

        * ``self.parameter_distributions``: dictionary containing the {parameter name: scipy.stats distribution} defined
          by the parameter schema. Set by
          :meth:`waves.parameter_generators._ScipyGenerator._generate_parameter_distributions`.

        Sets attribute(s):

        * ``self._samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets,
            number of parameters).
        """
        self._samples = numpy.zeros((set_count, parameter_count))
        quantiles = sampler.random(set_count)
        for i, distribution in enumerate(self.parameter_distributions.values()):
            self._samples[:, i] = distribution.ppf(quantiles[:, i])

    def _create_parameter_names(self) -> None:
        """Construct the parameter names from a distribution parameter schema."""
        self._parameter_names = [key for key in self.parameter_schema if key != "num_simulations"]


class CartesianProduct(ParameterGenerator):
    """Builds a cartesian product parameter study.

    Parameters must be scalar valued integers, floats, strings, or booleans

    :param parameter_schema: The YAML loaded parameter study schema dictionary - ``{parameter_name: schema value}``
        CartesianProduct expects "schema value" to be an iterable. For example, when read from a YAML file "schema
        value" will be a Python list. Each parameter's values must have a consistent data type, but data type may vary
        between parameters.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param require_previous_parameter_study: Raise a ``RuntimeError`` if the previous parameter study file is missing.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * Parameter schema is not a dictionary
        * Parameter key is not a supported iterable: set, tuple, list

    Example:

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'parameter_1': [1, 2],
       ...     'parameter_2': ['a', 'b']
       ... }
       >>> parameter_generator = waves.parameter_generators.CartesianProduct(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:       (set_hash: 4)
       Coordinates:
           set_hash      (set_hash) <U32 'de3cb3eaecb767ff63973820b2...
         * set_name      (set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1   (set_hash) object 1 1 2 2
           parameter_2   (set_hash) object 'a' 'b' 'a' 'b'

    """

    def _validate(self) -> None:
        """Validate the Cartesian Product parameter schema. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        self._parameter_names = list(self.parameter_schema.keys())
        # List, sets, and tuples are the supported PyYAML iterables that will support expected behavior
        for name in self._parameter_names:
            if not isinstance(self.parameter_schema[name], list | set | tuple):
                raise SchemaValidationError(f"Parameter '{name}' is not one of list, set, or tuple")

    def _generate(self, **kwargs) -> None:  # noqa: ARG002
        """Generate the Cartesian Product parameter sets."""
        self._samples = numpy.array(list(itertools.product(*self.parameter_schema.values())), dtype=object)
        super()._generate()


class LatinHypercube(_ScipyGenerator):
    """Builds a Latin-Hypercube parameter study from the `scipy Latin Hypercube`_ class.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param parameter_schema: The YAML loaded parameter study schema dictionary - ``{parameter_name: schema value}``
        LatinHypercube expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param require_previous_parameter_study: Raise a ``RuntimeError`` if the previous parameter study file is missing.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_distributions: A dictionary mapping parameter names to the `scipy.stats`_ distribution
    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``

    To produce consistent Latin Hypercubes on repeat instantiations, the ``**kwargs`` must include ``{'seed': <int>}``.
    See the `scipy Latin Hypercube`_ ``scipy.stats.qmc.LatinHypercube`` class documentation for details The ``d``
    keyword argument is internally managed and will be overwritten to match the number of parameters defined in the
    parameter schema.

    Example:

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'num_simulations': 4,  # Required key. Value must be an integer.
       ...     'parameter_1': {
       ...         'distribution': 'norm',  # Required key. Value must be a valid scipy.stats
       ...         'loc': 50,               # distribution name.
       ...         'scale': 1
       ...     },
       ...     'parameter_2': {
       ...         'distribution': 'skewnorm',
       ...         'a': 4,
       ...         'loc': 30,
       ...         'scale': 2
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.LatinHypercube(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:       (set_hash: 4)
       Coordinates:
           set_hash      (set_hash) <U32 '1e8219dae27faa5388328e225a...
         * set_name      (set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1   (set_hash) float64 0.125 ... 51.15
           parameter_2   (set_hash) float64 0.625 ... 30.97

    """

    def __init__(self, *args, **kwargs) -> None:
        self.sampler_class = "LatinHypercube"
        super().__init__(*args, **kwargs)

    def _generate(self, **kwargs) -> None:
        """Generate the Latin Hypercube parameter sets."""
        super()._generate(**kwargs)


class OneAtATime(ParameterGenerator):
    """Build a parameter study with single-value changes from a nominal parameter set.

    The nominal parameter set is created from the first value of every parameter iterable.

    Parameters must be scalar valued integers, floats, strings, or booleans

    The nominal parameter set will always be the first parameter set, e.g. ``parameter_set0`` for the default
    ``set_name_template``.

    :param parameter_schema: The YAML loaded parameter study schema dictionary - ``{parameter_name: schema value}``
        OneAtATime expects "schema value" to be an ordered iterable. For example, when read from a YAML file "schema
        value" will be a Python list. Each parameter's values must have a consistent data type, but data type may vary
        between parameters.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param require_previous_parameter_study: Raise a ``RuntimeError`` if the previous parameter study file is missing.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * Parameter schema is not a dictionary
        * Parameter key is not a supported iterable: tuple, list
        * Parameter key is empty

    Example:

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'parameter_1': [1.0],
       ...     'parameter_2': ['a', 'b'],
       ...     'parameter_3': [5, 3, 7]
       ... }
       >>> parameter_generator = waves.parameter_generators.OneAtATime(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:         (set_name: 4)
       Coordinates:
           set_hash        (set_name) <U32 '375a9b0b7c00d01bced92d9c5a6d302c' ....
         * set_name        (set_name) <U14 'parameter_set0' ... 'parameter_set3'
           parameter_sets  (set_name) <U14 'parameter_set0' ... 'parameter_set3'
       Data variables:
           parameter_1     (set_name) float64 32B 1.0 1.0 1.0 1.0
           parameter_2     (set_name) <U1 16B 'a' 'b' 'a' 'a'
           parameter_3     (set_name) int64 32B 5 5 3 7

    """

    def _validate(self) -> None:
        """Validate the One-at-a-Time parameter schema. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        self._parameter_names = list(self.parameter_schema.keys())
        # List and tuples are the supported PyYAML ordered iterables that will support expected behavior
        for name in self._parameter_names:
            if not isinstance(self.parameter_schema[name], list | tuple):
                raise SchemaValidationError(f"Parameter '{name}' is not a list or tuple")
            if len(self.parameter_schema[name]) < 1:
                raise SchemaValidationError(f"Parameter '{name}' must have at least one value")

    def _generate(self, **kwargs) -> None:  # noqa: ARG002
        """Generate the parameter sets from the user provided parameter values."""
        # Count how many total sets will be generated (= nominal set + number of off-nominal values)
        set_count = 1 + numpy.sum([len(self.parameter_schema[name]) - 1 for name in self._parameter_names])
        # Generate the nominal set, assuming that the first entry of each parameter is the nominal parameter
        nominal_set = numpy.array([[self.parameter_schema[name][0] for name in self._parameter_names]], dtype=object)
        # Generate the off-nominal sets, assuming that the first entry of each parameter is the nominal parameter
        all_sets = numpy.repeat([nominal_set[0]], set_count, axis=0)
        parameter_set_index = 1  # Start at 1 since we don't change the nominal set
        for parameter_name_index, name in enumerate(self._parameter_names):
            if len(self.parameter_schema[name]) > 1:
                for value in self.parameter_schema[name][1:]:  # Skip nominal value
                    all_sets[parameter_set_index][parameter_name_index] = value
                    parameter_set_index += 1
        # Combine the studies, preserving the nominal set as first set, e.g. "parameter_set0" by default.
        # This is not possible with super()._generate()
        nominal_study = CustomStudy(
            {"parameter_samples": nominal_set, "parameter_names": self._parameter_names},
            set_name_template=self.set_name_template.template,
        ).parameter_study
        off_nominal_study = CustomStudy(
            {"parameter_samples": all_sets, "parameter_names": self._parameter_names},
            set_name_template=self.set_name_template.template,
        ).parameter_study
        self.parameter_study = _merge_parameter_studies([nominal_study, off_nominal_study], self.set_name_template)
        self.parameter_study = self.parameter_study.sortby(_set_coordinate_key)
        # Do work normally performed by super()._generate(). Must re-calculate semi-private variables
        self.parameter_study = self.parameter_study.swap_dims({_set_coordinate_key: _hash_coordinate_key})
        self._samples = self._parameter_study_to_numpy()
        self._set_hashes = list(self.parameter_study.coords[_hash_coordinate_key].values)
        self._set_names = self.parameter_study[_set_coordinate_key].to_series().to_dict()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})
        if self.previous_parameter_study is not None and self.previous_parameter_study.is_file():
            self._merge_parameter_studies()


class CustomStudy(ParameterGenerator):
    """Builds a custom parameter study from user-specified values.

    Parameters must be scalar valued integers, floats, strings, or booleans

    :param parameter_schema: Dictionary with two keys: ``parameter_samples`` and ``parameter_names``.
        Parameter samples in the form of a 2D array with shape M x N, where M is the number of parameter sets and N is
        the number of parameters. Parameter names in the form of a 1D array with length N. When creating a
        `parameter_samples` array with mixed type (e.g. string and floats) use `dtype=object` to preserve the mixed
        types and avoid casting all values to a common type (e.g. all your floats will become strings). Each parameter's
        values must have a consistent data type, but data type may vary between parameters.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param require_previous_parameter_study: Raise a ``RuntimeError`` if the previous parameter study file is missing.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * Parameter schema is not a dictionary
        * Parameter schema does not contain the ``parameter_names`` key
        * Parameter schema does not contain the ``parameter_samples`` key
        * The ``parameter_samples`` value is an improperly shaped array

    Example:

    .. code-block::

       >>> import waves
       >>> import numpy
       >>> parameter_schema = dict(
       ...     parameter_samples = numpy.array([[1.0, 'a', 5], [2.0, 'b', 6]], dtype=object),
       ...     parameter_names = numpy.array(['height', 'prefix', 'index']))
       >>> parameter_generator = waves.parameter_generators.CustomStudy(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:       (set_hash: 2)
       Coordinates:
           set_hash      (set_hash) <U32 '50ba1a2716e42f8c4fcc34a90a...
         * set_name      (set_hash) <U14 'parameter_set0' 'parameter...
       Data variables:
           height        (set_hash) object 1.0 2.0
           prefix        (set_hash) object 'a' 'b'
           index         (set_hash) object 5 6

    """

    def _validate(self) -> None:
        """Validate the Custom Study parameter samples and names. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        try:
            self._parameter_names = self.parameter_schema["parameter_names"]
        except KeyError as err:
            raise SchemaValidationError("parameter_schema must contain the key: parameter_names") from err
        if "parameter_samples" not in self.parameter_schema:
            raise SchemaValidationError("parameter_schema must contain the key: parameter_samples")
        # Always convert to numpy array for shape check and _generate()
        else:
            self.parameter_schema["parameter_samples"] = numpy.array(
                self.parameter_schema["parameter_samples"], dtype=object
            )
        if (
            self.parameter_schema["parameter_samples"].ndim != 2
            or len(self._parameter_names) != self.parameter_schema["parameter_samples"].shape[1]
        ):
            raise SchemaValidationError(
                "The parameter samples must be an array of shape MxN, where N is the number of parameters."
            )
        return

    def _generate(self, **kwargs) -> None:  # noqa: ARG002
        """Generate the parameter study dataset from the user provided parameter array."""
        # Converted to numpy array by _validate. Simply assign to correct attribute
        self._samples = self.parameter_schema["parameter_samples"]
        super()._generate()


class SobolSequence(_ScipyGenerator):
    """Builds a Sobol sequence parameter study from the `scipy Sobol`_ class ``random`` method.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param parameter_schema: The YAML loaded parameter study schema dictionary - ``{parameter_name: schema value}``
        SobolSequence expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_distributions: A dictionary mapping parameter names to the ``scipy.stats`` distribution
    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``

    To produce consistent Sobol sequences on repeat instantiations, the ``**kwargs`` must include either
    ``scramble=False`` or ``seed=<int>``. See the `scipy Sobol`_ ``scipy.stats.qmc.Sobol`` class documentation for
    details.  The ``d`` keyword argument is internally managed and will be overwritten to match the number of parameters
    defined in the parameter schema.

    Example:

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'num_simulations': 4,  # Required key. Value must be an integer.
       ...     'parameter_1': {
       ...         'distribution': 'uniform',  # Required key. Value must be a valid scipy.stats
       ...         'loc': 0,                   # distribution name.
       ...         'scale': 10
       ...     },
       ...     'parameter_2': {
       ...         'distribution': 'uniform',
       ...         'loc': 2,
       ...         'scale': 3
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.SobolSequence(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:       (set_name: 4)
       Coordinates:
           set_hash      (set_name) <U32 'c1fa74da12c0991379d1df6541c421...
         * set_name      (set_name) <U14 'parameter_set0' ... 'parameter...
       Data variables:
           parameter_1   (set_name) float64 0.0 0.5 ... 7.5 2.5
           parameter_2   (set_name) float64 0.0 0.5 ... 4.25

    """

    def __init__(self, *args, **kwargs) -> None:
        self.sampler_class = "Sobol"
        super().__init__(*args, **kwargs)

    def _generate(self, **kwargs) -> None:
        """Generate the parameter study dataset from the user provided parameter array."""
        super()._generate(**kwargs)


class ScipySampler(_ScipyGenerator):
    """Builds a scipy sampler parameter study from a `scipy.stats.qmc`_ ``sampler_class``.

    Samplers must use the ``d`` parameter space dimension keyword argument. The following samplers are tested for
    parameter study shape and merge behavior:

    * Halton
    * LatinHypercube
    * PoissonDisk
    * Sobol

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param sampler_class: The `scipy.stats.qmc`_ sampler class name. Case sensitive.
    :param parameter_schema: The YAML loaded parameter study schema dictionary - ``{parameter_name: schema value}``
        ScipySampler expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_distributions: A dictionary mapping parameter names to the ``scipy.stats`` distribution
    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``

    Keyword arguments for the ``scipy.stats.qmc`` ``sampler_class``. The ``d`` keyword argument is internally managed
    and will be overwritten to match the number of parameters defined in the parameter schema.

    Example:

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'num_simulations': 4,  # Required key. Value must be an integer.
       ...     'parameter_1': {
       ...         'distribution': 'norm',  # Required key. Value must be a valid scipy.stats
       ...         'loc': 50,               # distribution name.
       ...         'scale': 1
       ...     },
       ...     'parameter_2': {
       ...         'distribution': 'skewnorm',
       ...         'a': 4,
       ...         'loc': 30,
       ...         'scale': 2
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.ScipySampler("LatinHypercube", parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:       (set_hash: 4)
       Coordinates:
           set_hash      (set_hash) <U32 '1e8219dae27faa5388328e225a...
         * set_name      (set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1   (set_hash) float64 0.125 ... 51.15
           parameter_2   (set_hash) float64 0.625 ... 30.97

    """

    def __init__(self, sampler_class: str, *args, **kwargs) -> None:
        self.sampler_class = sampler_class
        super().__init__(*args, **kwargs)

    def _generate(self, **kwargs) -> None:
        """Generate the `scipy.stats.qmc`_ ``sampler_class`` parameter sets."""
        super()._generate(**kwargs)


class SALibSampler(ParameterGenerator, ABC):
    """Builds a SALib sampler parameter study from a `SALib.sample`_ ``sampler_class``.

    Samplers must use the ``N`` sample count argument. Note that in `SALib.sample`_ ``N`` is *not* always equivalent to
    the number of simulations. The following samplers are tested for parameter study shape and merge behavior:

    * fast_sampler
    * finite_diff
    * latin
    * sobol
    * morris

    .. warning::

       For small numbers of parameters, some SALib generators produce duplicate parameter sets. These duplicate sets are
       removed during parameter study generation. This may cause the SALib analyze method(s) to raise errors related to
       the expected parameter set count.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param sampler_class: The `SALib.sample`_ sampler class name. Case sensitive.
    :param parameter_schema: The YAML loaded parameter study schema dictionary - ``{parameter_name: schema value}``
        SALibSampler expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset. If a previous parameter study exists, it is merged into the current study upon generation.
        Set name to content associations of the previous study are preserved when the parameter spaces between the
        previous and current study are identical. If the parameter spaces are unique, the current study will propagate
        the parameter spaces to resolve them. This will break set name to content associations of the previous study.
    :param overwrite: Overwrite existing output files
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * If the `SALib sobol`_ or `SALib morris`_ sampler is specified and there are fewer than 2 parameters.
        * ``N`` is not a key of ``parameter_schema``
        * ``problem`` is not a key of ``parameter_schema``
        * ``names`` is not a key of ``parameter_schema['problem']``
        * ``parameter_schema`` is not a dictionary
        * ``parameter_schema['N']`` is not an integer
        * ``parameter_schema['problem']`` is not a dictionary
        * ``parameter_schema['problem']['names']`` is not a YAML compliant iterable (list, set, tuple)

    Keyword arguments for the `SALib.sample`_ ``sampler_class`` ``sample`` method.

    *Example*

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     "N": 4,  # Required key. Value must be an integer.
       ...     "problem": {  # Required key. See the SALib sampler interface documentation
       ...         "num_vars": 3,
       ...         "names": ["parameter_1", "parameter_2", "parameter_3"],
       ...         "bounds": [[-1, 1], [-2, 2], [-3, 3]]
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.SALibSampler("sobol", parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:       (set_name: 32)
       Coordinates:
           set_hash      (set_name) <U32 'e0cb1990f9d70070eaf5638101dcaf...
         * set_name      (set_name) <U15 'parameter_set0' ... 'parameter...
       Data variables:
           parameter_1   (set_name) float64 -0.2029 ... 0.187
           parameter_2   (set_name) float64 -0.801 ... 0.6682
           parameter_3   (set_name) float64 0.4287 ... -2.871
    """

    def __init__(self, sampler_class: str, *args, **kwargs) -> None:
        self.sampler_class = sampler_class
        super().__init__(*args, **kwargs)

    def _validate(self) -> None:
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        if "N" not in self.parameter_schema:
            raise SchemaValidationError("Parameter schema is missing the required 'N' key")
        elif not isinstance(self.parameter_schema["N"], int):
            raise SchemaValidationError("Parameter schema 'N' must be an integer.")
        # Check the SALib owned "problem" dictionary for necessary WAVES elements
        if "problem" not in self.parameter_schema:
            raise SchemaValidationError("Parameter schema is missing the required 'problem' key")
        elif not isinstance(self.parameter_schema["problem"], dict):
            raise SchemaValidationError("'problem' must be a dictionary")
        if "names" not in self.parameter_schema["problem"]:
            raise SchemaValidationError("Parameter schema 'problem' dict is missing the required 'names' key")
        if not isinstance(self.parameter_schema["problem"]["names"], list | set | tuple):
            raise SchemaValidationError("Parameter 'names' is not one of list, set, or tuple")
        self._create_parameter_names()
        # Sampler specific validation
        self._sampler_validation()

    def _sampler_validation(self) -> None:
        """Call campler specific schema validation check methods.

        * sobol requires at least two parameters

        Requires attributes:

        * ``self._sampler_class`` set by class initiation
        * ``self._parameter_names`` set by ``self._create_parameter_names()``

        :raises waves.exceptions.SchemaValidationError: A sobol or morris sampler contains fewer than two parameters
        """
        parameter_count = len(self._parameter_names)
        if self.sampler_class == "sobol" and parameter_count < 2:
            raise SchemaValidationError("The SALib Sobol sampler requires at least two parameters")
        if self.sampler_class == "morris" and parameter_count < 2:
            raise SchemaValidationError("The SALib Morris sampler requires at least two parameters")

    def _sampler_overrides(self, override_kwargs: dict | None = None) -> dict:
        """Provide sampler specific kwarg override dictionaries.

        * sobol produces duplicate parameter sets for two parameters when ``calc_second_order`` is ``True``. Override
          this kwarg to be ``False`` if there are only two parameters.

        :param override_kwargs: any common kwargs to include in the override dictionary

        :return: override kwarg dictionary
        """
        if override_kwargs is None:
            override_kwargs = {}
        parameter_count = len(self._parameter_names)
        if self.sampler_class == "sobol" and parameter_count == 2:
            override_kwargs = {**override_kwargs, "calc_second_order": False}
        return override_kwargs

    def _create_parameter_names(self) -> None:
        """Construct the parameter names from a distribution parameter schema."""
        self._parameter_names = self.parameter_schema["problem"]["names"]

    def _generate(self, **kwargs) -> None:
        """Generate the `SALib.sample`_ ``sampler_class`` parameter sets."""
        N = self.parameter_schema["N"]  # noqa: N806
        override_kwargs = self._sampler_overrides()
        if kwargs:
            kwargs.update(override_kwargs)
        else:
            kwargs = override_kwargs
        __import__("SALib.sample", fromlist=[self.sampler_class])
        sampler = getattr(SALib.sample, self.sampler_class)
        problem = self.parameter_schema["problem"]
        self._samples = sampler.sample(problem, N, **kwargs)
        self._samples = numpy.unique(self._samples, axis=0)
        super()._generate()


def _calculate_set_hash(parameter_names: collections.abc.Sequence[str], set_samples: collections.abc.Sequence) -> str:
    """Calculate the unique, repeatable parameter set content hash for a single parameter set.

    :param parameter_names: list of parameter names in matching order with parameter samples
    :param set_samples: list of parameter set sample values in matching order with parameter names

    :returns: unique parameter set hash/identifier

    :raises RuntimeError: if the number of parameter names doesn't match the number of set sample values
    """
    if len(parameter_names) != len(set_samples):
        raise RuntimeError("Expected length of parameter names to match number of sample values")
    set_samples_array = numpy.array(set_samples, dtype=object)
    sorted_contents = sorted(zip(parameter_names, set_samples_array, strict=True))
    set_catenation = "\n".join(f"{name}:{sample!r}" for name, sample in sorted_contents)
    set_hash = hashlib.md5(set_catenation.encode("utf-8"), usedforsecurity=False).hexdigest()
    return set_hash


def _calculate_set_hashes(parameter_names: list[str], samples: numpy.ndarray) -> list[str]:
    """Calculate the unique, repeatable parameter set content hashes from a :class:`ParameterGenerator` object.

    The object must have a populated ``self._samples`` attribute.

    Expects parameter names to correspond to the columns of the samples array

    :param parameter_generator: A parameter generator object with at least partially complete attributes

    :returns: list of parameter set hashes
    """
    return [_calculate_set_hash(parameter_names, set_samples) for set_samples in samples]


def _parameter_study_to_numpy(parameter_study: xarray.Dataset) -> numpy.ndarray:
    """Return the parameter study data as a 2D numpy array.

    :param parameter_study: A :class:`ParameterGenerator` parameter study Xarray Dataset

    :return: data
    """
    data = []
    for _set_hash, data_row in parameter_study.groupby(_hash_coordinate_key):
        data.append([data_row[key].item() for key in data_row])
    return numpy.array(data, dtype=object)


def _verify_parameter_study(parameter_study: xarray.Dataset) -> None:
    """Verify the contents of a parameter study.

    :param parameter_study: A :class:`ParameterGenerator` parameter study Xarray Dataset

    Intended to verify parameter studies read from user supplied files. Currently the only check implemented in the set
    hash/set content consistency. Implies checking for the hash coordinate key and consistent data variable
    column/parameter names.

    :raises RuntimeError: if mandatory coordinate names are missing: ``set_name``, ``set_hash``
    :raises RuntimeError: if data variables and ``set_hash`` do not have the ``set_name`` dimension
    :raises RuntimeError: if parameter set hash values do not match the calculated hash from
        :meth:`_calculate_set_hash`.
    """
    # Check for mandatory coordinate keys
    coordinates = list(parameter_study.coords)
    if _set_coordinate_key not in coordinates:
        raise RuntimeError(f"Parameter study coordinate '{_set_coordinate_key}' missing")
    if _hash_coordinate_key not in coordinates:
        raise RuntimeError(f"Parameter study coordinate '{_hash_coordinate_key}' missing")

    # Check for the assigned dimensions
    if _set_coordinate_key not in parameter_study.dims:
        raise RuntimeError(f"Parameter study missing dimension '{_set_coordinate_key}'")
    keys = [*list(parameter_study.keys()), _hash_coordinate_key]
    for key in keys:
        if _set_coordinate_key not in parameter_study[key].dims:
            raise RuntimeError(f"Parameter study key '{key}' missing dimension '{_set_coordinate_key}'")

    # Check for parameter set hash values against parameter set name/content
    parameter_names = [str(key) for key in parameter_study]
    file_hashes = [str(set_hash) for set_hash in parameter_study[_hash_coordinate_key].values]
    samples = _parameter_study_to_numpy(parameter_study)
    calculated_hashes = _calculate_set_hashes(parameter_names, samples)
    if set(file_hashes) != set(calculated_hashes):
        raise RuntimeError(
            f"Parameter study set hashes not equal to calculated set hashes: \n"
            f"file:          {file_hashes}\n"
            f"calculated:    {calculated_hashes}"
        )


def _return_dataset_types(original_dataset: xarray.Dataset, update_dataset: xarray.Dataset) -> dict:
    """Return the union of data variables ``{name: dtype}``.

    :param original_dataset: Xarray Dataset with original types
    :param update_dataset: Xarray Dataset with override types. Types in this dataset overwrite types in
    ``original_dataset``

    :return: Dictionary with entries of type ``{name: dtype}`` constructed from ``original_dataset`` and
    ``update_dataset``

    :raises RuntimeError: if data variables with matching names have different types
    """
    # TODO: Accept an arbitrarily long list of positional arguments
    original_types = {key: original_dataset[key].dtype for key in original_dataset}
    update_types = {key: update_dataset[key].dtype for key in update_dataset}
    matching_keys = set(original_types.keys()) & set(update_types.keys())
    for key in matching_keys:
        original_type = original_types[key]
        update_type = update_types[key]
        if original_type != update_type:
            raise RuntimeError(f"Different types for '{key}': '{original_type}' and '{update_type}'")
    original_types.update(update_types)
    return original_types


def _open_parameter_study(parameter_study_file: pathlib.Path | str) -> xarray.Dataset:
    """Return a :class:`ParameterGenerator` parameter study xarray Dataset after verifying contents.

    :param parameter_study_file: Xarray parameter study file to open

    :return: A verified :class:`ParameterGenerator` parameter study xarray Dataset

    :raises RuntimeError: if file path is not found or is not a file
    :raises RuntimeError: if parameter study verification raises a RuntimeError
    """
    path = pathlib.Path(parameter_study_file)
    if not path.is_file():
        raise RuntimeError("File '{parameter_study_file}' is not a file")
    parameter_study = xarray.open_dataset(parameter_study_file, engine="h5netcdf")

    try:
        _verify_parameter_study(parameter_study)
    except RuntimeError as err:
        raise RuntimeError(
            f"Error opening '{parameter_study_file}'\n{err}\n"
            "Was the parameter study file modified by hand? "
            "Was the parameter study file generated on a system with differing machine precision? "
            f"Was the parameter study file generated by an older version of {_settings._project_name_short}?"
        ) from err
    return parameter_study


def _coerce_values(values: typing.Iterable, name: str | None = None) -> numpy.ndarray:
    """Coerces values of an iterable into a single datatype. Warns the user if coercion was necessary.

    :param values: list of values
    :param name: optional name of the parameter

    :return: 1D numpy array of a consistent datatype
    """
    datatypes = {type(value) for value in values}
    values_coerced = numpy.array(values)
    if len(datatypes) > 1:
        warnings.warn(
            f"Found mixed datatypes in parameter '{name}': '{datatypes}'. Parameter values will be unified to datatype:"
            f" '{type(values_coerced[0])}'."
        )
    return values_coerced


def _assess_parameter_spaces(studies: list[xarray.Dataset]) -> dict[str, list[xarray.Dataset]]:
    """From a list of parameter studies, separate studies into unique parameter spaces.

    This function generates a dictionary split by parameter space, with each space containing studies belonging to a
    shared unique parameter space.

    :param studies: list of parameter study xarray Datasets where the first study is considered the 'base' study

    :return: dictionary, with keys corresponding to the unique hash of the parameter space names and the values are
        a list of parameter study datasets with shared parameter space

    :raises RuntimeError: if input studies contain partially overlapping parameter spaces
    """
    # Group studies by parameter space hash
    parameter_spaces = collections.defaultdict(list)
    for study in studies:
        parameters = list(study.data_vars)
        parameter_space_hash = _calculate_set_hash(parameters, parameters)
        parameter_spaces[parameter_space_hash].append(study)

    # Verify no partial overlapping studies
    spaces = list(parameter_spaces.keys())
    for index, space in enumerate(spaces):
        parameters = list(parameter_spaces[space][0].data_vars)
        for space_other in spaces[index + 1 :]:
            parameters_other = list(parameter_spaces[space_other][0].data_vars)
            shared_parameters = set(parameters) & set(parameters_other)
            unshared_parameters = set(parameters) ^ set(parameters_other)
            if any(shared_parameters) and any(unshared_parameters):
                raise RuntimeError(
                    f"Found study containing partially overlapping parameter space during attempted merge operation.\n"
                    f"Unshared parameter(s): '{unshared_parameters}'\n"
                    f"Shared parameters :'{shared_parameters}'"
                )

    return parameter_spaces


def _propagate_parameter_space(study_base: xarray.Dataset, study_other: xarray.Dataset) -> xarray.Dataset:
    """Propagate unique parameters from a new study into the base study, creating a new study using CustomStudy.

    Assumes that the parameter studies do not share any parameters. The incoming studies should have set name as the
    active dimension.

    This function breaks set_name-to-content associations of the input studies, including the base study. This is due
    to new set hashes calculated for each expanded parameter set.

    :param study_base: A :class:`ParameterGenerator` parameter study Xarray Dataset
    :param study_other: A :class:`ParameterGenerator` parameter study Xarray Dataset with unique parameters compared
        to `study_base`

    :return: :class:`CustomStudy` parameter study xarray Dataset
    """
    # Calculate parameter sets (ROWS) in the samples matrix
    num_parameter_sets_base = len(study_base[_set_coordinate_key])
    num_parameter_sets_other = len(study_other[_set_coordinate_key])
    total_parameter_sets = num_parameter_sets_base * num_parameter_sets_other

    # Calculate parameters (COLUMNS) in the samples/parameters matrix
    num_parameters_base = len(study_base.data_vars)
    num_parameters_other = len(study_other.data_vars)
    total_parameters = num_parameters_base + num_parameters_other

    # Populate matrices for the propagated CustomStudy
    propagated_study_samples = numpy.full((total_parameter_sets, total_parameters), numpy.nan, dtype=object)
    propagated_study_parameters = numpy.full(total_parameters, numpy.nan, dtype=object)

    # Parameter values will need to be repeated by some factor to fill out the sample space
    repeats_base = int(numpy.ceil(total_parameter_sets / num_parameter_sets_base))
    repeats_other = int(numpy.ceil(total_parameter_sets / num_parameter_sets_other))

    # Construct the parameter names vector
    propagated_study_parameters[0:num_parameters_base] = study_base.data_vars
    propagated_study_parameters[num_parameters_base:] = study_other.data_vars

    # Construct the samples matrix
    for set_index in range(num_parameter_sets_base):
        for repeat_index in range(repeats_base):
            row = set_index * repeats_base + repeat_index
            for column, parameter in enumerate(study_base.data_vars):
                # Populate each entry of the samples matrix using the values of each parameter set at each parameter
                propagated_study_samples[row, column] = study_base.isel(set_name=set_index)[parameter].to_numpy().item()
    for repeat_index in range(repeats_other):
        for set_index in range(num_parameter_sets_other):
            row = repeat_index * num_parameter_sets_other + set_index
            for column_index, parameter in enumerate(study_other.data_vars):
                column = column_index + num_parameters_base
                propagated_study_samples[row, column] = (
                    study_other.isel(set_name=set_index)[parameter].to_numpy().item()
                )

    parameter_schema = {
        "parameter_samples": propagated_study_samples,
        "parameter_names": propagated_study_parameters.flatten(),
    }
    propagated_study = CustomStudy(parameter_schema).parameter_study
    return propagated_study


def _merge_parameter_space(studies: list[xarray.Dataset], template: string.Template | None = None) -> xarray.Dataset:
    """Merge a list of parameter studies with the same parameter space into one study.

    Studies should have set hash as the active dimension.

    Preserves the first given parameter study set name to set contents associations by dropping subsequent studies'
    set names during merge.

    :param studies: list of parameter study xarray Datasets with identical parameter spaces where the first
        study is considered the 'base' study.
    :param template: parameter set naming :class:`string.Template`. If none is provided, fetch the default template
        using the ``@`` delimiter from the WAVES settings.

    :return: parameter study xarray Dataset
    """
    # Verify type equality and record types prior to merge
    study_base = studies[0]
    types_dictionary = {}
    studies_other = []
    for study_other in studies[1:]:
        coerce_types = _return_dataset_types(study_base, study_other)
        types_dictionary.update(coerce_types)
        studies_other.append(study_other.drop_vars(_set_coordinate_key))

    # Combine all studies after dropping set names from all but `study_base`
    merged_study = xarray.merge([study_base, *studies_other], join="outer", compat="no_conflicts")

    # Coerce types back to their original type. Especially necessary for ints, which xarray.merge converts to float
    for parameter, old_dtype in types_dictionary.items():
        new_dtype = merged_study[parameter].dtype
        if new_dtype != old_dtype:
            merged_study[parameter] = merged_study[parameter].astype(old_dtype)

    merged_study = merged_study.sortby(_hash_coordinate_key)
    # Recalculate attributes with lengths matching the number of parameter sets
    merged_study = _update_set_names(merged_study, template)
    return merged_study


def _merge_parameter_studies(studies: list[xarray.Dataset], template: string.Template | None = None) -> xarray.Dataset:
    """Merge a list of parameter studies into one study.

    When merging across identical parameter spaces, uses :func:`_merge_parameter_space()` to preserve the first given
    parameter study set name to set contents associations by dropping subsequent studies' set names during merge. If
    the parameter spaces are unique across studies, this function will use :func:`_propagate_parameter_space()` to
    resolve the spaces and break the set name to set contents associations of the base study.

    :param studies: list of parameter study xarray Datasets where the first study is considered the 'base' study
    :param template: parameter set naming :class:`string.Template`. If none is provided, fetch the default template
        using the ``@`` delimiter from the WAVES settings.

    :return: parameter study xarray Dataset

    :raises RuntimeError: if fewer than two parameter studies are in the input parameter `studies`
    """
    if len(studies) < 2:
        raise RuntimeError("Not enough parameter studies provided for merge operation")

    # Swap dimensions from the set name to the set hash to merge identical sets
    swap_to_hash_index = {_set_coordinate_key: _hash_coordinate_key}
    studies = [study.swap_dims(swap_to_hash_index) for study in studies]

    parameter_spaces = _assess_parameter_spaces(studies)

    # Merge studies in each parameter space. Preserves the set names of the first study in each space
    merged_parameter_spaces = [_merge_parameter_space(studies, template) for studies in parameter_spaces.values()]

    # If multiple parameter spaces, propagate into one combined study. Breaks all set name associations
    swap_to_set_index = {_hash_coordinate_key: _set_coordinate_key}
    studies = [study.swap_dims(swap_to_set_index) for study in merged_parameter_spaces]
    study_combined = studies.pop(0)
    for study_other in studies:
        study_combined = _propagate_parameter_space(study_combined, study_other)

    return study_combined


def _create_set_names(set_hashes: list[str], template: string.Template | None = None) -> dict:
    """Construct parameter set names from the set name template and number of parameter set hashes.

    Set names are assigned to set hashes in hash ascending alphabetical order.

    :param set_hashes: parameter set content hashes identifying rows of parameter study
    :param template: parameter set naming :class:`string.Template`. If none is provided, fetch the default template
        using the ``@`` delimiter from the WAVES settings.

    :return: Dictionary mapping parameter set hash to parameter set name
    """
    if not template:
        template = _utilities._AtSignTemplate(_settings._default_set_name_template)

    set_names = {}
    set_hashes = sorted(set_hashes)
    for number, set_hash in enumerate(set_hashes):
        set_names[set_hash] = template.substitute({"number": number})

    return set_names


def _update_set_names(parameter_study: xarray.Dataset, template: string.Template | None = None) -> xarray.Dataset:
    """Update the parameter set names after a parameter study dataset merge operation.

    Hashes that are missing set names are assigned a new set name in hash ascending alphabetical order.

    :param parameter_study: A :class:`ParameterGenerator` parameter study Xarray Dataset with swapped set hash and set
        name dimensions
    :param template: parameter set naming :class:`string.Template`. If none is provided upon call, fetch the default
        template using the ``@`` delimiter from the WAVES settings.

    :return: parameter study xarray Dataset

    :raises RuntimeError: if the new set name assignment has a shape mismatch, e.g. when the set name template doesn't
        match the existing set names in the parameter study.
    """
    parameter_study = parameter_study.sortby(_hash_coordinate_key)
    set_hashes = list(parameter_study.coords[_hash_coordinate_key].values)
    set_names = _create_set_names(set_hashes, template)
    new_set_names = [
        set_name
        for set_name in set_names.values()
        if set_name not in parameter_study.coords[_set_coordinate_key].values
    ]
    null_set_names = parameter_study.coords[_set_coordinate_key].isnull()
    if any(null_set_names):
        try:
            parameter_study.coords[_set_coordinate_key][null_set_names] = new_set_names
        except ValueError as err:
            raise RuntimeError(
                "Could not fill merged parameter set names. Does the parameter set naming convention match?"
            ) from err

    return parameter_study


_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
