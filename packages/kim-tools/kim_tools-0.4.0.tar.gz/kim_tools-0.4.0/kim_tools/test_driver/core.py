################################################################################
#
#  CDDL HEADER START
#
#  The contents of this file are subject to the terms of the Common Development
#  and Distribution License Version 1.0 (the "License").
#
#  You can obtain a copy of the license at
#  http:# www.opensource.org/licenses/CDDL-1.0.  See the License for the
#  specific language governing permissions and limitations under the License.
#
#  When distributing Covered Code, include this CDDL HEADER in each file and
#  include the License file in a prominent location with the name LICENSE.CDDL.
#  If applicable, add the following below this CDDL HEADER, with the fields
#  enclosed by brackets "[]" replaced with your own identifying information:
#
#  Portions Copyright (c) [yyyy] [name of copyright owner]. All rights reserved.
#
#  CDDL HEADER END
#
#  Copyright (c) 2017-2019, Regents of the University of Minnesota.
#  All rights reserved.
#
#  Contributor(s):
#     Ilia Nikiforov
#     Eric Fuemmler
#
################################################################################
"""
Helper classes for KIM Test Drivers

"""
import glob
import json
import logging
import os
import shutil
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import IO, Any, Dict, List, Optional, Union

import ase
import kim_edn
import numpy as np
import numpy.typing as npt
from ase import Atoms
from ase.build import bulk
from ase.calculators.calculator import Calculator
from ase.calculators.kim import get_model_supported_species
from ase.constraints import FixSymmetry
from ase.data import atomic_masses
from ase.filters import FrechetCellFilter, UnitCellFilter
from ase.optimize import LBFGSLineSearch
from ase.optimize.optimize import Optimizer
from kim_property import (
    get_properties,
    get_property_id_path,
    kim_property_create,
    kim_property_dump,
    kim_property_modify,
)
from kim_property.modify import STANDARD_KEYS_SCLAR_OR_WITH_EXTENT
from kim_query import raw_query

from ..aflow_util import (
    AFLOW,
    get_space_group_number_from_prototype,
    get_stoich_reduced_list_from_prototype,
    prototype_labels_are_equivalent,
)
from ..aflow_util.core import AFLOW_EXECUTABLE, get_atom_indices_for_each_wyckoff_orb
from ..ase import get_isolated_energy_per_atom
from ..kimunits import convert_list, convert_units
from ..symmetry_util import (
    cartesian_rotation_is_in_point_group,
    change_of_basis_atoms,
    get_cell_from_poscar,
    get_change_of_basis_matrix_to_conventional_cell_from_formal_bravais_lattice,
    get_formal_bravais_lattice_from_space_group,
)

logger = logging.getLogger(__name__)
logging.basicConfig(filename="kim-tools.log", level=logging.INFO, force=True)

__author__ = ["ilia Nikiforov", "Eric Fuemmeler"]
__all__ = [
    "KIMTestDriverError",
    "KIMTestDriver",
    "get_crystal_structure_from_atoms",
    "get_poscar_from_crystal_structure",
    "get_atoms_from_crystal_structure",
    "SingleCrystalTestDriver",
    "query_crystal_structures",
    "detect_unique_crystal_structures",
    "get_deduplicated_property_instances",
    "minimize_wrapper",
    "crystal_input_from_test_generator_line",
    "get_supported_lammps_atom_style",
]

# Force tolerance for the optional initial relaxation of the provided cell
FMAX_INITIAL = 1e-5
# Maximum steps for the optional initial relaxation of the provided cell
MAXSTEPS_INITIAL = 200
PROP_SEARCH_PATHS_INFO = (
    "- $KIM_PROPERTY_PATH (expanding globs including recursive **)\n"
    "- $PWD/local-props/**/\n"
    "- $PWD/local_props/**/"
)


def get_supported_lammps_atom_style(model: str) -> str:
    """
    Get the supported LAMMPS atom_style of a KIM model
    """
    from lammps import lammps

    candidate_atom_styles = ("atomic", "charge", "full")
    banned_species = "electron"  # Species in KIM models not understood by ASE
    supported_species = get_model_supported_species(model)
    test_species = None
    for species in supported_species:
        if species not in banned_species:
            test_species = species
            break
    if test_species is None:
        raise RuntimeError(
            "Model appears to only support species not understood by ASE:\n"
            + str(supported_species)
        )
    atoms = bulk(test_species, "fcc", 10.0)  # Very low-density FCC lattice
    for atom_style in candidate_atom_styles:
        with lammps(cmdargs=["-sc", "none"]) as lmp, NamedTemporaryFile() as f:
            lmp.command(f"kim init {model} metal unit_conversion_mode")
            atoms.write(f.name, format="lammps-data", atom_style=atom_style)
            try:
                lmp.command(f"read_data {f.name}")
                return atom_style
            except Exception as e:
                if str(e).startswith(
                    "ERROR: Incorrect format in Atoms section of data file:"
                ):
                    continue
                else:
                    msg = (
                        "The following unexpected exception was encountered when trying"
                        " to determine atom_style:\n" + repr(e)
                    )
                    print(msg)
                    raise e
    raise RuntimeError("Unable to determine supported atom type")


def _get_optional_source_value(property_instance: Dict, key: str) -> Any:
    """
    Function for getting an optional key's source-value, or None if the key
    doesn't exist, from a Property Instance that is a Dict
    """
    if key in property_instance:
        return property_instance[key]["source-value"]
    else:
        return None


def _update_optional_key_in_property_dict(
    property_instance: Dict, key: str, value: Any, unit: Optional[str] = None
) -> None:
    """
    In a Property Instance that's a Dict, update a key or erase it if
    None is provided
    """
    if value is None:
        if key in property_instance:
            property_instance.pop(key)
    else:
        property_instance[key] = {"source-value": value}
        if unit is not None:
            property_instance[key]["source-unit"] = unit


def minimize_wrapper(
    atoms: Atoms,
    fmax: float = FMAX_INITIAL,
    steps: int = MAXSTEPS_INITIAL,
    variable_cell: bool = True,
    logfile: Optional[Union[str, IO]] = "kim-tools.log",
    algorithm: type[Optimizer] = LBFGSLineSearch,
    cell_filter: type[UnitCellFilter] = FrechetCellFilter,
    fix_symmetry: Union[bool, FixSymmetry] = False,
    opt_kwargs: Dict = {},
    flt_kwargs: Dict = {},
) -> bool:
    """
    Use LBFGSLineSearch (default) to Minimize cell energy with respect to cell shape and
    internal atom positions.

    LBFGSLineSearch convergence behavior is as follows:

    - The solver returns True if it is able to converge within the optimizer
      iteration limits (which can be changed by the ``steps`` argument passed
      to ``run``), otherwise it returns False.
    - The solver raises an exception in situations where the line search cannot
      improve the solution, typically due to an incompatibility between the
      potential's values for energy, forces, and/or stress.

    This routine attempts to minimizes the energy until the force and stress
    reduce below specified tolerances given a provided limit on the number of
    allowed steps. The code returns when convergence is achieved or no
    further progress can be made, either due to reaching the iteration step
    limit, or a stalled minimization due to line search failures.

    Args:
        atoms:
            Atomic configuration to be minimized.
        fmax:
            Force convergence tolerance (the magnitude of the force on each
            atom must be less than this for convergence)
        steps:
            Maximum number of iterations for the minimization
        variable_cell:
            True to allow relaxation with respect to cell shape
        logfile:
            Log file. ``'-'`` means STDOUT
        algorithm:
            ASE optimizer algorithm
        CellFilter:
            Filter to use if variable_cell is requested
        fix_symmetry:
            Whether to fix the crystallographic symmetry. Can provide
            a FixSymmetry class here instead of detecting it on the fly
        opt_kwargs:
            Dictionary of kwargs to pass to optimizer
        flt_kwargs:
            Dictionary of kwargs to pass to filter (e.g. "scalar_pressure")

    Returns:
        Whether the minimization succeeded
    """
    existing_constraints = atoms.constraints
    if fix_symmetry is not False:
        if fix_symmetry is True:
            symmetry = FixSymmetry(atoms)
        else:
            symmetry = fix_symmetry
        atoms.set_constraint([symmetry] + existing_constraints)
    if variable_cell:
        supercell_wrapped = cell_filter(atoms, **flt_kwargs)
        opt = algorithm(supercell_wrapped, logfile=logfile, **opt_kwargs)
    else:
        opt = algorithm(atoms, logfile=logfile, **opt_kwargs)
    try:
        converged = opt.run(fmax=fmax, steps=steps)
        iteration_limits_reached = not converged
        minimization_stalled = False
    except Exception as e:
        minimization_stalled = True
        iteration_limits_reached = False
        logger.info("The following exception was caught during minimization:")
        logger.info(repr(e))

    logger.info(
        "Minimization "
        + (
            "stalled"
            if minimization_stalled
            else "stopped" if iteration_limits_reached else "converged"
        )
        + " after "
        + (
            ("hitting the maximum of " + str(steps))
            if iteration_limits_reached
            else str(opt.nsteps)
        )
        + " steps."
    )

    atoms.set_constraint(existing_constraints)

    if minimization_stalled or iteration_limits_reached:
        try:
            logger.info("Final forces:")
            logger.info(atoms.get_forces())
            logger.info("Final stress:")
            logger.info(atoms.get_stress())
        except Exception as e:
            logger.info(
                "The following exception was caught "
                "trying to evaluate final forces and stress:"
            )
            logger.info(repr(e))
        return False
    else:
        return True


def _add_property_instance(
    property_name: str,
    disclaimer: Optional[str] = None,
    property_instances: Optional[str] = None,
) -> str:
    """
    Initialize a new property instance in the serialized ``property_instances``. This
    wraps the ``kim_property.kim_property_create()`` function, with the simplification
    of setting "instance-id" automatically, as well as automatically searching for a
    definition file if ``property_name`` is not found.

    NOTE: Is there any need to allow Test Driver authors to specify an instance-id?

    Args:
        property_name:
            The property name, e.g.
            "tag:staff@noreply.openkim.org,2023-02-21:property/binding-energy-crystal"
            or "binding-energy-crystal"
        disclaimer:
            An optional disclaimer commenting on the applicability of this result, e.g.
            "This relaxation did not reach the desired tolerance."
        property_instances:
            A pre-existing EDN-serialized list of KIM Property instances to add to

    Returns:
            Updated EDN-serialized list of property instances
    """
    if property_instances is None:
        property_instances = "[]"
    # Get and check the instance-id to use.
    property_instances_deserialized = kim_edn.loads(property_instances)
    new_instance_index = len(property_instances_deserialized) + 1
    for property_instance in property_instances_deserialized:
        assert (
            property_instance["instance-id"] != new_instance_index
        ), "instance-id conflict"

    existing_properties = get_properties()
    property_in_existing_properties = False
    for existing_property in existing_properties:
        if (
            existing_property == property_name
            or get_property_id_path(existing_property)[3] == property_name
        ):
            property_in_existing_properties = True

    if not property_in_existing_properties:
        print(
            f"\nThe property name or id\n{property_name}\nwas not found in "
            "kim-properties.\n"
        )
        print(
            "I will now look for an .edn file containing its definition in the "
            f"following locations:\n{PROP_SEARCH_PATHS_INFO}\n"
        )

        property_search_paths = []

        # environment varible
        if "KIM_PROPERTY_PATH" in os.environ:
            property_search_paths += os.environ["KIM_PROPERTY_PATH"].split(":")

        # CWD
        property_search_paths.append(os.path.join(Path.cwd(), "local_props", "**"))
        property_search_paths.append(os.path.join(Path.cwd(), "local-props", "**"))

        # recursively search for .edn files in the paths, check if they are a property
        # definition with the correct name

        found_custom_property = False

        for search_path in property_search_paths:
            if found_custom_property:
                break
            else:
                # hack to expand globs in both absolute and relative paths
                if search_path[0] == "/":
                    base_path = Path("/")
                    search_glob = os.path.join(search_path[1:], "*.edn")
                else:
                    base_path = Path()
                    search_glob = os.path.join(search_path, "*.edn")

                for path in base_path.glob(search_glob):
                    if not os.path.isfile(
                        path
                    ):  # in case there's a directory named *.edn
                        continue
                    try:
                        path_str = str(path)
                        dict_from_edn = kim_edn.load(path_str)
                        if ("property-id") in dict_from_edn:
                            property_id = dict_from_edn["property-id"]
                            if (
                                property_id == property_name
                                or get_property_id_path(property_id)[3] == property_name
                            ):
                                property_name = path_str
                                found_custom_property = True
                                break
                    except Exception as e:
                        msg = (
                            "MESSAGE: Trying to load a property from the .edn file at\n"
                            f"{path}\n"
                            "failed with the following exception:\n"
                            f"{repr(e)}"
                        )
                        logger.info(msg)
                        print(msg)

        if not found_custom_property:
            raise KIMTestDriverError(
                f"\nThe property name or id\n{property_name}\nwas not found in "
                "kim-properties.\nI failed to find an .edn file containing a matching "
                '"property-id" key in the following locations:\n'
                + PROP_SEARCH_PATHS_INFO
            )

    return kim_property_create(
        new_instance_index, property_name, property_instances, disclaimer
    )


def _add_key_to_current_property_instance(
    property_instances: str,
    name: str,
    value: npt.ArrayLike,
    unit: Optional[str] = None,
    uncertainty_info: Optional[dict] = None,
) -> str:
    """
    Write a key to the last element of property_instances. This wraps
    ``kim_property.kim_property_modify()`` with a simplified (and more restricted)
    interface.

    Note: if the value is an array, this function will assume you want to write to the
    beginning of the array in every dimension.

    This function is intended to write entire keys in one go, and should not be used for
    modifying existing keys.

    WARNING! It is the developer's responsibility to make sure the array shape matches
    the extent specified in the property definition. This method uses fills the values
    of array keys as slices through the last dimension. If those slices are incomplete,
    kim_property automatically initializes the other elements in that slice to zero. For
    example, consider writing coordinates to a key with extent [":", 3]. The correct way
    to write a single atom would be to provide [[x, y, z]]. If you accidentally provide
    [[x], [y], [z]], it will fill the field with the coordinates
    [[x, 0, 0], [y, 0, 0], [z, 0, 0]]. This will not raise an error, only exceeding
    the allowed dimesnsions of the key will do so.

    Args:
        property_instances:
            An EDN-serialized list of dictionaries representing KIM Property Instances.
            The key will be added to the last dictionary in the list
        name:
            Name of the key, e.g. "cell-cauchy-stress"
        value:
            The value of the key. The function will attempt to convert it to a NumPy
            array, then use the dimensions of the resulting array. Scalars, lists,
            tuples, and arrays should work.
            Data type of the elements should be str, float, or int
        unit:
            The units
        uncertainty_info:
            dictionary containing any uncertainty keys you wish to include. See
            https://openkim.org/doc/schema/properties-framework/ for the possible
            uncertainty key names. These must be the same dimension as ``value``, or
            they may be scalars regardless of the shape of ``value``.

    Returns:
        Updated EDN-serialized list of property instances
    """

    def recur_dimensions(
        prev_indices: List[int],
        sub_value: npt.ArrayLike,
        modify_args: list,
        key_name: str = "source-value",
    ):
        sub_shape = sub_value.shape
        assert (
            len(sub_shape) != 0
        ), "Should not have gotten to zero dimensions in the recursive function"
        if len(sub_shape) == 1:
            # only if we have gotten to a 1-dimensional sub-array do we write stuff
            modify_args += [key_name, *prev_indices, "1:%d" % sub_shape[0], *sub_value]
        else:
            for i in range(sub_shape[0]):
                prev_indices.append(i + 1)  # convert to 1-based indices
                recur_dimensions(prev_indices, sub_value[i], modify_args, key_name)
                prev_indices.pop()

    value_arr = np.array(value)
    value_shape = value_arr.shape

    current_instance_index = len(kim_edn.loads(property_instances))
    modify_args = ["key", name]
    if len(value_shape) == 0:
        modify_args += ["source-value", value]
    else:
        prev_indices = []
        recur_dimensions(prev_indices, value_arr, modify_args)

    if unit is not None:
        modify_args += ["source-unit", unit]

    if uncertainty_info is not None:
        for uncertainty_key in uncertainty_info:
            if uncertainty_key not in STANDARD_KEYS_SCLAR_OR_WITH_EXTENT:
                raise KIMTestDriverError(
                    "Uncertainty key %s is not one of the allowed options %s."
                    % (uncertainty_key, str(STANDARD_KEYS_SCLAR_OR_WITH_EXTENT))
                )
            uncertainty_value = uncertainty_info[uncertainty_key]
            uncertainty_value_arr = np.array(uncertainty_value)
            uncertainty_value_shape = uncertainty_value_arr.shape

            if not (
                len(uncertainty_value_shape) == 0
                or uncertainty_value_shape == value_shape
            ):
                raise KIMTestDriverError(
                    f"The value {uncertainty_value_arr} provided for uncertainty key "
                    f"{uncertainty_key} has shape {uncertainty_value_shape}.\n"
                    f"It must either be a scalar or match the shape {value_shape} of "
                    "the source value you provided."
                )
            if len(uncertainty_value_shape) == 0:
                modify_args += [uncertainty_key, uncertainty_value]
            else:
                prev_indices = []
                recur_dimensions(
                    prev_indices, uncertainty_value_arr, modify_args, uncertainty_key
                )

    return kim_property_modify(property_instances, current_instance_index, *modify_args)


class KIMTestDriverError(Exception):
    def __init__(self, msg) -> None:
        # Call the base class constructor with the parameters it needs
        super(KIMTestDriverError, self).__init__(msg)
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class KIMTestDriver(ABC):
    """
    A base class for creating KIM Test Drivers. It has attributes that are likely
    to be useful to for most KIM tests

    Attributes:
        __kim_model_name (Optional[str]):
            KIM model name, absent if a non-KIM ASE calculator was provided
        __calc (:obj:`~ase.calculators.calculator.Calculator`):
            ASE calculator
        __output_property_instances (str):
            Property instances, possibly accumulated over multiple invocations of
            the Test Driver
    """

    class NonKIMModelError(Exception):
        """
        Raised when a KIM model name is requested but is absent. This is important
        to handle to inform users that they are trying to run a Test Driver that
        requires a KIM model (e.g. a LAMMPS TD) with a non-KIM Calculator
        """

    def __init__(
        self, model: Union[str, Calculator], suppr_sm_lmp_log: bool = False
    ) -> None:
        """
        Args:
            model:
                ASE calculator or KIM model name to use
            suppr_sm_lmp_log:
                Suppress writing a lammps.log
        """
        if isinstance(model, Calculator):
            self.__calc = model
            self.__kim_model_name = None
        else:
            from ase.calculators.kim.kim import KIM

            self.__kim_model_name = model
            self.__calc = KIM(self.__kim_model_name)
            if suppr_sm_lmp_log:
                if hasattr(self.__calc.parameters, "log_file"):
                    self.__calc.parameters.log_file = None

        self.__output_property_instances = "[]"

    def _setup(self, material, **kwargs) -> None:
        """
        Empty method, for optional overrides
        """
        pass

    @abstractmethod
    def _calculate(self, **kwargs) -> None:
        """
        Abstract calculate method
        """
        raise NotImplementedError("Subclasses must implement the _calculate method.")

    def __call__(self, material: Any = None, **kwargs) -> List[Dict]:
        """

        Main operation of a Test Driver:

            * Run :func:`~KIMTestDriver._setup` (the base class provides a barebones
              version, derived classes may override)
            * Call :func:`~KIMTestDriver._calculate` (implemented by each individual
              Test Driver)

        Args:
            material:
                Placeholder object for arguments describing the material to run
                the Test Driver on

        Returns:
            The property instances calculated during the current run
        """
        # count how many instances we had before we started
        previous_properties_end = len(kim_edn.loads(self.__output_property_instances))

        os.makedirs("output", exist_ok=True)

        # _setup is likely overridden by an derived class
        self._setup(material, **kwargs)

        # implemented by each individual Test Driver
        self._calculate(**kwargs)

        # The current invocation returns a Python list of dictionaries containing all
        # properties computed during this run
        return kim_edn.loads(self.__output_property_instances)[previous_properties_end:]

    def _add_property_instance(
        self, property_name: str, disclaimer: Optional[str] = None
    ) -> None:
        """
        Initialize a new property instance.
        NOTE: Is there any need to allow Test Driver authors to specify an instance-id?

        Args:
            property_name:
                The property name, e.g.
                "tag:staff@noreply.openkim.org,2023-02-21:property/binding-energy-crystal"
                or "binding-energy-crystal"
            disclaimer:
                An optional disclaimer commenting on the applicability of this result,
                e.g. "This relaxation did not reach the desired tolerance."
        """
        self.__output_property_instances = _add_property_instance(
            property_name, disclaimer, self.__output_property_instances
        )

    def _add_key_to_current_property_instance(
        self,
        name: str,
        value: npt.ArrayLike,
        unit: Optional[str] = None,
        uncertainty_info: Optional[dict] = None,
    ) -> None:
        """
        Add a key to the most recent property instance added with
        :func:`~kim_tools.test_driver.core.KIMTestDriver._add_property_instance`.
        If the value is an
        array, this function will assume you want to write to the beginning of the array
        in every dimension. This function is intended to write entire keys in one go,
        and should not be used for modifying existing keys.

        WARNING! It is the developer's responsibility to make sure the array shape
        matches the extent specified in the property definition. This method uses
        ``kim_property.kim_property_modify``, and fills the values of array keys as
        slices through the last dimension. If those slices are incomplete, kim_property
        automatically initializes the other elements in that slice to zero. For example,
        consider writing coordinates to a key with extent [":", 3]. The correct way to
        write a single atom would be to provide [[x, y, z]]. If you accidentally provide
        [[x], [y], [z]], it will fill the field with the coordinates
        [[x, 0, 0], [y, 0, 0], [z, 0, 0]]. This will not raise an error, only exceeding
        the allowed dimesnsions of the key will do so.

        Args:
            name:
                Name of the key, e.g. "cell-cauchy-stress"
            value:
                The value of the key. The function will attempt to convert it to a NumPy
                array, then use the dimensions of the resulting array. Scalars, lists,
                tuples, and arrays should work. Data type of the elements should be str,
                float, int, or bool
            unit:
                The units
            uncertainty_info:
                dictionary containing any uncertainty keys you wish to include. See
                https://openkim.org/doc/schema/properties-framework/ for the possible
                uncertainty key names. These must be the same dimension as ``value``, or
                they may be scalars regardless of the shape of ``value``.
        """
        self.__output_property_instances = _add_key_to_current_property_instance(
            self.__output_property_instances, name, value, unit, uncertainty_info
        )

    def _add_file_to_current_property_instance(
        self, name: str, filename: os.PathLike, add_instance_id: bool = True
    ) -> None:
        """
        add a "file" type key-value pair to the current property instance.

        Args:
            name:
                Name of the key, e.g. "restart-file"
            filename:
                The path to the filename. If it is not in  "$CWD/output/",
                the file will be moved there
            add_instance_id:
                By default, a numerical index will be added before the file extension or
                at the end of a file with no extension. This is to ensure files do not
                get overwritten when the _calculate method is called repeatedly.

        Raises:
            KIMTestDriverError:
                If the provided filename does not exist
        """
        if not os.path.isfile(filename):
            raise KIMTestDriverError("Provided file {filename} does not exist.")

        # all paths here should be absolute
        cwd_path = Path(os.getcwd())
        output_path = cwd_path / "output"
        filename_path = Path(filename).resolve()

        if output_path not in filename_path.parents:
            # Need to move file to output
            if cwd_path in filename_path.parents:
                # The file is somewhere under CWD,
                # so move it under CWD/output with
                # its whole directory structure
                final_dir = os.path.join(
                    output_path, os.path.relpath(filename_path.parent)
                )
                os.makedirs(final_dir, exist_ok=True)
            else:
                # We got a file that isn't even under CWD.
                # I can't really hope to suss out what they
                # were going for, so just move it to CWD/output
                final_dir = output_path
        else:
            # already under output, not moving anything
            final_dir = filename_path.parent

        input_name = filename_path.name
        if add_instance_id:
            current_instance_id = len(kim_edn.loads(self.__output_property_instances))
            root, ext = os.path.splitext(input_name)
            root = root + "-" + str(current_instance_id)
            final_name = root + ext
        else:
            final_name = input_name

        final_path = os.path.join(final_dir, final_name)

        assert final_path.startswith(str(output_path))

        shutil.move(filename, final_path)

        # Filenames are reported relative to $CWD/output
        self._add_key_to_current_property_instance(
            name, os.path.relpath(final_path, output_path)
        )

    def _get_supported_lammps_atom_style(self) -> str:
        """
        Return the atom_style that should be used when writing LAMMPS data files.
        This atom_style will be compatible with the KIM model this object
        was instantiated with.
        """
        return get_supported_lammps_atom_style(self.kim_model_name)

    @property
    def kim_model_name(self) -> Optional[str]:
        """
        Get the KIM model name, if present
        """
        if self.__kim_model_name is not None:
            return self.__kim_model_name
        else:
            raise self.NonKIMModelError(
                "A KIM model name is being requested, but the Test Driver "
                "is being run with a non-KIM calculator."
            )

    @property
    def property_instances(self) -> Dict:
        """
        Get all property instances accumulated over all calls to the Test Driver so far
        """
        return kim_edn.loads(self.__output_property_instances)

    @property
    def _calc(self) -> Optional[Calculator]:
        """
        Get the ASE calculator. Reinstantiate it if it's a KIM SM
        """
        if self.__kim_model_name is not None:
            reinst = False
            if hasattr(self.__calc, "clean"):
                self.__calc.clean()
                reinst = True
            if hasattr(self.__calc, "__del__"):
                self.__calc.__del__()
                reinst = True
            if reinst:
                from ase.calculators.kim.kim import KIM

                self.__calc = KIM(self.__kim_model_name)
        return self.__calc

    def _get_serialized_property_instances(self) -> str:
        """
        Get the property instances computed so far in serialized EDN format
        """
        return self.__output_property_instances

    def _set_serialized_property_instances(self, property_instances: str) -> None:
        """
        Set the property instances from a serialized EDN string
        """
        self.__output_property_instances = property_instances

    def write_property_instances_to_file(self, filename="output/results.edn") -> None:
        """
        Write internal property instances (possibly accumulated over several calls to
        the Test Driver) to a file at the requested path.

        Args:
            filename: path to write the file
        """
        filename_parent = Path(filename).parent.resolve()
        os.makedirs(filename_parent, exist_ok=True)
        kim_property_dump(self._get_serialized_property_instances(), filename)
        if filename_parent != Path("output").resolve():
            for file_in_output in glob.glob("output/*"):
                file_in_output_name = str(Path(file_in_output).name)
                for instance in self.property_instances:
                    for key in instance:
                        if isinstance(instance[key], dict):
                            if file_in_output_name == instance[key]["source-value"]:
                                shutil.move(file_in_output, filename_parent)
                            elif isinstance(instance[key]["source-value"], list):
                                for file_in_property in instance[key]["source-value"]:
                                    if file_in_output_name == file_in_property:
                                        shutil.move(file_in_output, filename_parent)

    def get_isolated_energy_per_atom(self, symbol: str) -> float:
        """
        Construct a non-periodic cell containing a single atom and compute its energy.

        Args
            symbol:
                The chemical species

        Returns:
            The isolated energy of a single atom
        """
        try:
            model = self.kim_model_name
        except self.NonKIMModelError:
            model = self._calc
        return get_isolated_energy_per_atom(model=model, symbol=symbol)


def _add_common_crystal_genome_keys_to_current_property_instance(
    property_instances: str,
    prototype_label: str,
    stoichiometric_species: List[str],
    a: float,
    a_unit: str,
    parameter_values: Optional[List[float]] = None,
    library_prototype_label: Optional[Union[List[str], str]] = None,
    short_name: Optional[Union[List[str], str]] = None,
    cell_cauchy_stress: Optional[List[float]] = None,
    cell_cauchy_stress_unit: Optional[str] = None,
    temperature: Optional[float] = None,
    temperature_unit: Optional[str] = "K",
    crystal_genome_source_structure_id: Optional[List[List[str]]] = None,
    aflow_executable: str = AFLOW_EXECUTABLE,
    omit_keys: Optional[List[str]] = None,
) -> str:
    """
    Write common Crystal Genome keys to the last element of ``property_instances``. See
    https://openkim.org/properties/show/crystal-structure-npt for definition of the
    input keys. Note that the "parameter-names" key is inferred from the
    ``prototype_label`` input and is not an input to this function.

    Args:
        property_instances:
            An EDN-serialized list of dictionaries representing KIM Property Instances.
            The key will be added to the last dictionary in the list
        aflow_executable:
            Path to the AFLOW executable
        omit_keys:
            Which keys to omit writing

    Returns:
        Updated EDN-serialized list of property instances
    """
    if omit_keys is None:
        omit_keys = []
    if "prototype-label" not in omit_keys:
        property_instances = _add_key_to_current_property_instance(
            property_instances, "prototype-label", prototype_label
        )
    if "stoichiometric-species" not in omit_keys:
        property_instances = _add_key_to_current_property_instance(
            property_instances, "stoichiometric-species", stoichiometric_species
        )
    if "a" not in omit_keys:
        property_instances = _add_key_to_current_property_instance(
            property_instances, "a", a, a_unit
        )

    # get parameter names
    aflow = AFLOW(aflow_executable=aflow_executable)
    aflow_parameter_names = aflow.get_param_names_from_prototype(prototype_label)
    if parameter_values is None:
        if len(aflow_parameter_names) > 1:
            raise KIMTestDriverError(
                "The prototype label implies that parameter_values (i.e. dimensionless "
                "parameters besides a) are required, but you provided None"
            )
    else:
        if len(aflow_parameter_names) - 1 != len(parameter_values):
            raise KIMTestDriverError(
                "Incorrect number of parameter_values (i.e. dimensionless parameters "
                "besides a) for the provided prototype"
            )
        if "parameter-names" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances, "parameter-names", aflow_parameter_names[1:]
            )
        if "parameter-values" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances, "parameter-values", parameter_values
            )

    if short_name is not None:
        if not isinstance(short_name, list):
            short_name = [short_name]
        if "short-name" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances, "short-name", short_name
            )

    if library_prototype_label is not None:
        if "library-prototype-label" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances, "library-prototype-label", library_prototype_label
            )

    if cell_cauchy_stress is not None:
        if len(cell_cauchy_stress) != 6:
            raise KIMTestDriverError(
                "Please specify the Cauchy stress as a 6-dimensional vector in Voigt "
                "order [xx, yy, zz, yz, xz, xy]"
            )
        if cell_cauchy_stress_unit is None:
            raise KIMTestDriverError("Please provide a `cell_cauchy_stress_unit`")
        if "cell-cauchy-stress" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances,
                "cell-cauchy-stress",
                cell_cauchy_stress,
                cell_cauchy_stress_unit,
            )

    if temperature is not None:
        if temperature_unit is None:
            raise KIMTestDriverError("Please provide a `temperature_unit`")
        if "temperature" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances, "temperature", temperature, temperature_unit
            )

    if crystal_genome_source_structure_id is not None:
        if "crystal-genome-source-structure-id" not in omit_keys:
            property_instances = _add_key_to_current_property_instance(
                property_instances,
                "crystal-genome-source-structure-id",
                crystal_genome_source_structure_id,
            )

    return property_instances


def _add_property_instance_and_common_crystal_genome_keys(
    property_name: str,
    prototype_label: str,
    stoichiometric_species: List[str],
    a: float,
    a_unit: str,
    parameter_values: Optional[List[float]] = None,
    library_prototype_label: Optional[Union[List[str], str]] = None,
    short_name: Optional[Union[List[str], str]] = None,
    cell_cauchy_stress: Optional[List[float]] = None,
    cell_cauchy_stress_unit: Optional[str] = None,
    temperature: Optional[float] = None,
    temperature_unit: Optional[str] = "K",
    crystal_genome_source_structure_id: Optional[List[List[str]]] = None,
    disclaimer: Optional[str] = None,
    property_instances: Optional[str] = None,
    aflow_executable: str = AFLOW_EXECUTABLE,
    omit_keys: Optional[List[str]] = None,
) -> str:
    """
    Initialize a new property instance to ``property_instances`` (an empty
    ``property_instances`` will be initialized if not provided). It will automatically
    get the an "instance-id" equal to the length of ``property_instances`` after it is
    added. Then, write the common Crystal Genome keys to it. See
    https://openkim.org/properties/show/crystal-structure-npt for definition of the
    input keys. Note that the "parameter-names" key is inferred from the
    ``prototype_label`` input and is not an input to this function.

    Args:
        property_name:
            The property name, e.g.
            "tag:staff@noreply.openkim.org,2023-02-21:property/binding-energy-crystal"
            or "binding-energy-crystal"
        disclaimer:
            An optional disclaimer commenting on the applicability of this result, e.g.
            "This relaxation did not reach the desired tolerance."
        property_instances:
            A pre-existing EDN-serialized list of KIM Property instances to add to
        aflow_executable:
            Path to the AFLOW executable
        omit_keys:
            Which keys to omit writing

    Returns:
            Updated EDN-serialized list of property instances
    """
    property_instances = _add_property_instance(
        property_name, disclaimer, property_instances
    )
    return _add_common_crystal_genome_keys_to_current_property_instance(
        property_instances=property_instances,
        prototype_label=prototype_label,
        stoichiometric_species=stoichiometric_species,
        a=a,
        a_unit=a_unit,
        parameter_values=parameter_values,
        library_prototype_label=library_prototype_label,
        short_name=short_name,
        temperature=temperature,
        temperature_unit=temperature_unit,
        crystal_genome_source_structure_id=crystal_genome_source_structure_id,
        cell_cauchy_stress_unit=cell_cauchy_stress_unit,
        cell_cauchy_stress=cell_cauchy_stress,
        aflow_executable=aflow_executable,
        omit_keys=omit_keys,
    )


def get_crystal_structure_from_atoms(
    atoms: Atoms,
    get_short_name: bool = True,
    prim: bool = True,
    aflow_np: int = 4,
    aflow_executable: str = AFLOW_EXECUTABLE,
) -> Dict:
    """
    By performing a symmetry analysis on an :class:`~ase.Atoms` object, generate a
    dictionary that is a subset of the
    `crystal-structure-npt <https://openkim.org/properties/show/crystal-structure-npt>`_
    property. See https://openkim.org/doc/schema/properties-framework/ for more
    information about KIM properties and how values and units are defined. The
    dictionary returned by this function does not necessarily constitute a complete KIM
    Property Instance, but the key-value pairs are in valid KIM Property format and can
    be inserted as-is into any single crystal Crystal Genome property.

    Args:
        atoms: Configuration to analyze. It is assumed that the length unit is angstrom
        get_short_name:
            whether to compare against AFLOW prototype library to obtain short-name
        prim: whether to primitivize the atoms object first
        aflow_np: Number of processors to use with AFLOW executable
        aflow_executable:
            Path to the AFLOW executable

    Returns:
        A dictionary that has the following Property Keys (possibly optionally) defined.
        See the
        `crystal-structure-npt
        <https://openkim.org/properties/show/crystal-structure-npt>`_
        Property Definition for their meaning:

        - "stoichiometric-species"
        - "prototype-label"
        - "a"
        - "parameter-names" (inferred from "prototype-label")
        - "parameter-values"
        - "short-name"

    """
    aflow = AFLOW(aflow_executable=aflow_executable, np=aflow_np)

    proto_des = aflow.get_prototype_designation_from_atoms(atoms, prim=prim)
    library_prototype_label, short_name = (
        aflow.get_library_prototype_label_and_shortname_from_atoms(atoms, prim=prim)
        if get_short_name
        else (None, None)
    )

    a = proto_des["aflow_prototype_params_values"][0]
    parameter_values = (
        proto_des["aflow_prototype_params_values"][1:]
        if len(proto_des["aflow_prototype_params_values"]) > 1
        else None
    )

    property_instances = _add_property_instance_and_common_crystal_genome_keys(
        property_name="crystal-structure-npt",
        prototype_label=proto_des["aflow_prototype_label"],
        stoichiometric_species=sorted(list(set(atoms.get_chemical_symbols()))),
        a=a,
        a_unit="angstrom",
        parameter_values=parameter_values,
        library_prototype_label=library_prototype_label,
        short_name=short_name,
        aflow_executable=aflow_executable,
    )

    return kim_edn.loads(property_instances)[0]


def get_poscar_from_crystal_structure(
    crystal_structure: Dict,
    output_file: Optional[str] = None,
    flat: bool = False,
    addtl_args: str = "--webpage ",
    aflow_executable: str = AFLOW_EXECUTABLE,
) -> Optional[str]:
    """
    Write a POSCAR coordinate file (or output it as a multiline string) from the AFLOW
    Prototype Designation obtained from a KIM Property Instance. The following keys from
    https://openkim.org/properties/show/2023-02-21/staff@noreply.openkim.org/crystal-structure-npt
    are used:

    - "stoichiometric-species"
    - "prototype-label"
    - "a"
    - "parameter-values"
      (if "prototype-label" defines a crystal with free parameters besides "a")

    Note that although the keys are required to follow the schema of a KIM Property
    Instance (https://openkim.org/doc/schema/properties-framework/), there is no
    requirement or check that the input dictionary is an instance of any specific KIM
    Property, only that the keys required to build a crystal are present.

    Args:
        crystal_structure:
            Dictionary containing the required keys in KIM Property Instance format
        output_file:
            Name of the output file. If not provided, the output is returned as a string
        flat:
            whether the input dictionary is flattened
        addtl_args:
            additional arguments to --proto
        aflow_executable:
            path to AFLOW executable
    Returns:
        If ``output_file`` is not provided, a string in POSCAR format containg the
        primitive unit cell of the crystal as defined in
        http://doi.org/10.1016/j.commatsci.2017.01.017. Lengths are always in angstrom.
    Raises:
        AFLOW.ChangedSymmetryException:
            if the symmetry of the atoms object is different from ``prototype_label``
    """
    if flat:
        prototype_label = crystal_structure["prototype-label.source-value"]
        a_unit = crystal_structure["a.source-unit"]
        a_value = crystal_structure["a.source-value"]
        parameter_values_key = "parameter-values.source-value"
        stoichiometric_species = crystal_structure[
            "stoichiometric-species.source-value"
        ]
    else:
        prototype_label = crystal_structure["prototype-label"]["source-value"]
        a_unit = crystal_structure["a"]["source-unit"]
        a_value = crystal_structure["a"]["source-value"]
        parameter_values_key = "parameter-values"
        stoichiometric_species = crystal_structure["stoichiometric-species"][
            "source-value"
        ]

    aflow = AFLOW(aflow_executable=aflow_executable)
    aflow_parameter_names = aflow.get_param_names_from_prototype(prototype_label)

    # Atoms objects are always in angstrom
    if a_unit == "angstrom":
        a_angstrom = a_value
    else:
        a_angstrom = convert_units(
            a_value,
            crystal_structure["a"]["source-unit"],
            a_unit,
            True,
        )

    aflow_parameter_values = [a_angstrom]

    if parameter_values_key in crystal_structure:
        if len(aflow_parameter_names) == 1:
            raise KIMTestDriverError(
                f'Prototype label {prototype_label} implies only "a" parameter, but '
                'you provided "parameter-values"'
            )
        if flat:
            aflow_parameter_values += crystal_structure[parameter_values_key]
        else:
            aflow_parameter_values += crystal_structure[parameter_values_key][
                "source-value"
            ]

    try:
        return aflow.write_poscar_from_prototype(
            prototype_label=prototype_label,
            species=stoichiometric_species,
            parameter_values=aflow_parameter_values,
            output_file=output_file,
            addtl_args=addtl_args,
        )
    except AFLOW.ChangedSymmetryException as e:
        # re-raise, just indicating that this function knows about this exception
        raise e


def get_atoms_from_crystal_structure(
    crystal_structure: Dict,
    flat: bool = False,
    aflow_executable: str = AFLOW_EXECUTABLE,
) -> Atoms:
    """
    Generate an :class:`~ase.Atoms` object from the AFLOW Prototype Designation obtained
    from a KIM Property Instance. The following keys from
    https://openkim.org/properties/show/2023-02-21/staff@noreply.openkim.org/crystal-structure-npt
    are used:

    - "stoichiometric-species"
    - "prototype-label"
    - "a"
    - "parameter-values" (if "prototype-label" defines a crystal with free parameters
      besides "a")

    Note that although the keys are required to follow the schema of a KIM Property
    Instance (https://openkim.org/doc/schema/properties-framework/),
    There is no requirement or check that the input dictionary is an instance of any
    specific KIM Property, only that the keys required to build a crystal are present.

    Args:
        crystal_structure:
            Dictionary containing the required keys in KIM Property Instance format
        flat:
            whether the dictionary is flattened
        aflow_executable:
            path to AFLOW executable

    Returns:
        Primitive unit cell of the crystal as defined in the
        `AFLOW prototype standard <http://doi.org/10.1016/j.commatsci.2017.01.017>`_.
        Lengths are always in angstrom

    Raises:
        AFLOW.ChangedSymmetryException:
            if the symmetry of the atoms object is different from ``prototype_label``
    """
    try:
        poscar_string = get_poscar_from_crystal_structure(
            crystal_structure, flat=flat, aflow_executable=aflow_executable
        )
    except AFLOW.ChangedSymmetryException as e:
        # re-raise, just indicating that this function knows about this exception
        raise e

    with NamedTemporaryFile(mode="w+") as f:
        f.write(poscar_string)
        f.seek(0)
        atoms = ase.io.read(f.name, format="vasp")
    atoms.wrap()
    return atoms


class SingleCrystalTestDriver(KIMTestDriver):
    """
    A KIM test that computes property(s) of a single nominal crystal structure

    Attributes:
        __nominal_crystal_structure_npt [Dict]:
            An instance of the
            `crystal-structure-npt
            <https://openkim.org/properties/show/crystal-structure-npt>`_
            property representing the nominal crystal structure and conditions of the
            current call to the Test Driver.
        aflow_executable [str]:
            Path to the AFLOW executable
    """

    def __init__(
        self,
        model: Union[str, Calculator],
        suppr_sm_lmp_log: bool = False,
        aflow_executable: str = AFLOW_EXECUTABLE,
    ) -> None:
        """
        Args:
            model:
                ASE calculator or KIM model name to use
            suppr_sm_lmp_log:
                Suppress writing a lammps.log
            aflow_executable:
                Path to AFLOW executable
        """
        self.aflow_executable = aflow_executable
        super().__init__(model, suppr_sm_lmp_log=suppr_sm_lmp_log)

    def _setup(
        self,
        material: Union[Atoms, Dict],
        cell_cauchy_stress_eV_angstrom3: Optional[List[float]] = None,
        temperature_K: float = 0,
        **kwargs,
    ) -> None:
        """
        TODO: Consider allowing arbitrary units for temp and stress?

        Args:
            material:
                An :class:`~ase.Atoms` object or a KIM Property Instance specifying the
                nominal crystal structure that this run of the test
                will use. Pass one of the two following types of objects:

                Atoms object:

                    :class:`~ase.Atoms` object to use as the initial configuration. Note
                    that a symmetry analysis will be performed on it and a primitive
                    cell will be generated according to the conventions in
                    http://doi.org/10.1016/j.commatsci.2017.01.017. This primitive cell
                    may be rotated and translated relative to the configuration you
                    provided.

                Property instance:

                    Dictionary containing information about the nominal input crystal
                    structure in KIM Property Instance format (e.g. from a query to the
                    OpenKIM.org database)
                    The following keys from
                    https://openkim.org/properties/show/2023-02-21/staff@noreply.openkim.org/crystal-structure-npt
                    are used:

                    - "stoichiometric-species"
                    - "prototype-label"
                    - "a"
                    - "parameter-values"
                      (if "prototype-label" defines a crystal with
                      free parameters besides "a")
                    - "short-name" (if present)
                    - "crystal-genome-source-structure-id" (if present)

                    Note that although the keys are required to follow the schema of a
                    KIM Property Instance
                    (https://openkim.org/doc/schema/properties-framework/),
                    There is no requirement or check that the input dictionary is an
                    instance of any specific KIM Property, only that
                    the keys required to build a crystal are present.

            cell_cauchy_stress_eV_angstrom3:
                Cauchy stress on the cell in eV/angstrom^3 (ASE units) in
                [xx, yy, zz, yz, xz, xy] format. This is a nominal variable, and this
                class simply provides recordkeeping of it. It is up to derived classes
                to implement actually imposing this stress on the system.
            temperature_K:
                The temperature in Kelvin. This is a nominal variable, and this class
                simply provides recordkeeping of it. It is up to derived classes to
                implement actually setting the temperature of the system.
        """

        if cell_cauchy_stress_eV_angstrom3 is None:
            cell_cauchy_stress_eV_angstrom3 = [0, 0, 0, 0, 0, 0]

        if isinstance(material, Atoms):
            crystal_structure = get_crystal_structure_from_atoms(
                atoms=material, aflow_executable=self.aflow_executable
            )
            aflow = AFLOW()
            atoms_rebuilt = get_atoms_from_crystal_structure(crystal_structure)
            _, self.__input_rotation, _, _ = (
                aflow.get_basistransformation_rotation_originshift_atom_map_from_atoms(
                    atoms_rebuilt,
                    material,
                )
            )
            msg = (
                "Rebuilding Atoms object in a standard setting defined by "
                "doi.org/10.1016/j.commatsci.2017.01.017. See log file or computed "
                "properties for the (possibly re-oriented) primitive cell that "
                "computations will be based on. To obtain the rotation of this "
                "cell relative to the Atoms object you provided, use "
                f"{self.__class__.__name__}.get_input_rotation()"
            )
            logger.info(msg)
            print()
            print(msg)
            print()
        else:
            self.__input_rotation = None
            crystal_structure = material

        # Pop the temperature and stress keys in case they came along with a query
        if "temperature" in crystal_structure:
            crystal_structure.pop("temperature")
        if "cell-cauchy-stress" in crystal_structure:
            crystal_structure.pop("cell-cauchy-stress")

        crystal_structure["temperature"] = {
            "source-value": temperature_K,
            "source-unit": "K",
        }
        crystal_structure["cell-cauchy-stress"] = {
            "source-value": cell_cauchy_stress_eV_angstrom3,
            "source-unit": "eV/angstrom^3",
        }
        if "meta" in crystal_structure:
            # Carrying 'meta' around doesn't really make sense since we may have already
            # modified things and will modify in the future
            crystal_structure.pop("meta")

        self.__nominal_crystal_structure_npt = crystal_structure

        # Warn if atoms appear unrelaxed
        atoms_tmp = self._get_atoms()
        force_max = np.max(atoms_tmp.get_forces())
        if force_max > FMAX_INITIAL:
            msg = (
                "The configuration you provided has a maximum force component "
                f"{force_max} eV/angstrom. Unless the Test Driver you are running "
                "provides minimization, you may wish to relax the configuration."
            )
            print(f"\nNOTE: {msg}\n")
            logger.info(msg)
        if cell_cauchy_stress_eV_angstrom3 == [0, 0, 0, 0, 0, 0]:
            stress_max = np.max(atoms_tmp.get_stress())
            if stress_max > FMAX_INITIAL:
                msg = (
                    "The configuration you provided has a maximum stress component "
                    f"{stress_max} eV/angstrom^3 even though the nominal state of the "
                    "system is unstressed. Unless the Test Driver you are running "
                    "provides minimization, you may wish to relax the configuration."
                )
                print(f"\nNOTE: {msg}\n")
                logger.info(msg)

    def _update_nominal_parameter_values(
        self,
        atoms: Atoms,
        max_resid: Optional[float] = None,
        cell_rtol: float = 0.01,
        rot_rtol: float = 0.01,
        rot_atol: float = 0.01,
        match_library_proto: bool = True,
    ) -> None:
        """
        Update the nominal parameter values of the nominal crystal structure from the
        provided :class:`~ase.Atoms` object. It is assumed that the crystallographic
        symmetry (space group + occupied Wyckoff positions) have not changed from the
        initially provided structure.

        The provided :class:`~ase.Atoms` object MUST be a primitive cell of the crystal
        as defined in http://doi.org/10.1016/j.commatsci.2017.01.017.
        The :class:`~ase.Atoms` object may be rotated, translated, and permuted, but the
        identity of the lattice vectors must be unchanged w.r.t. the crystallographic
        prototype. In other words, there must exist a permutation and translation of the
        fractional coordinates that enables them to match the equations defined by the
        prototype label.

        In practical terms, this means that this function is designed to take as input a
        relaxed or time-averaged from MD (and folded back into the original primitive
        cell) copy of the :class:`~ase.Atoms` object originally obtained from
        :func:`~kim_tools.test_driver.core.SingleCrystalTestDriver._get_atoms()`.

        If finding the parameter fails, this function will raise an exception. This
        probably indicates a phase transition to a different symmetry, which is a normal
        occasional occurrence if the original structure is not stable under the
        interatomic potential and prescribed conditions. These exceptions should not be
        handled and that run of the Test Driver should be allowed to fail.

        Args:
            atoms: Structure to analyze to get the new parameter values
            max_resid:
                Maximum residual allowed when attempting to match the fractional
                positions of the atoms to the crystallographic equations.
                If not provided, this is automatically set to 0.01*(minimum NN distance)
            cell_rtol:
                Relative tolerance on cell lengths and angles.
                Justification for default value: AFLOW uses 0.01*(minimum NN distance)
                as default tolerance.
            rot_rtol:
                Parameter to pass to :func:`numpy.allclose` for compariong fractional
                rotations. Default value chosen to be commensurate with AFLOW
                default distance tolerance of 0.01*(NN distance)
            rot_atol:
                Parameter to pass to :func:`numpy.allclose` for compariong fractional
                rotations. Default value chosen to be commensurate with AFLOW
                default distance tolerance of 0.01*(NN distance)
            match_library_proto:
                Whether to match to library prototypes

        Raises:
            AFLOW.FailedToMatchException:
                If the solution failed due to a failure to match two crystals that
                should be identical at some point in the solution process. This
                *usually* indicates a phase transformation
            AFLOW.ChangedSymmetryException:
                If a more definitive error indicating a phase transformation is
                encountered
        """
        aflow = AFLOW(aflow_executable=self.aflow_executable)
        try:
            if match_library_proto:
                (aflow_parameter_values, library_prototype_label, short_name) = (
                    aflow.solve_for_params_of_known_prototype(
                        atoms=atoms,
                        prototype_label=self.get_nominal_prototype_label(),
                        max_resid=max_resid,
                        cell_rtol=cell_rtol,
                        rot_rtol=rot_rtol,
                        rot_atol=rot_atol,
                    )
                )
            else:
                aflow_parameter_values = aflow.solve_for_params_of_known_prototype(
                    atoms=atoms,
                    prototype_label=self.get_nominal_prototype_label(),
                    max_resid=max_resid,
                    cell_rtol=cell_rtol,
                    rot_rtol=rot_rtol,
                    rot_atol=rot_atol,
                    match_library_proto=False,
                )
                library_prototype_label = None
                short_name = None
        except (AFLOW.FailedToMatchException, AFLOW.ChangedSymmetryException) as e:
            raise type(e)(
                "Encountered an error that MAY be the result of the nominal crystal "
                "being unstable under the given potential and conditions. Stopping "
                "execution."
            ) from e

        # Atoms objects always in angstrom
        self.__nominal_crystal_structure_npt["a"] = {
            "source-value": aflow_parameter_values[0],
            "source-unit": "angstrom",
        }
        if len(aflow_parameter_values) > 1:
            # If we detected new prototype values, old must have been
            # there and the same length as well
            old_param_values = self.__nominal_crystal_structure_npt["parameter-values"][
                "source-value"
            ]
            new_param_values = aflow_parameter_values[1:]
            assert len(old_param_values) == len(new_param_values)
            self.__nominal_crystal_structure_npt["parameter-values"] = {
                "source-value": new_param_values
            }
        _update_optional_key_in_property_dict(
            property_instance=self.__nominal_crystal_structure_npt,
            key="library-prototype-label",
            value=library_prototype_label,
        )
        _update_optional_key_in_property_dict(
            property_instance=self.__nominal_crystal_structure_npt,
            key="short-name",
            value=short_name,
        )

    def _verify_unchanged_symmetry(self, atoms: Atoms) -> bool:
        """
        Without changing the nominal state of the system, check if the provided Atoms
        object has the same symmetry as the nominal crystal structure associated with
        the current state of the Test Driver. This is defined as having the same
        prototype label, except for possible changes in Wyckoff letters as permitted by
        the space group normalizer.

        Args:
            atoms: The structure to compare to the current nominal structure of the Test
            Driver

        Returns:
            Whether or not the symmetry is unchanged

        """
        aflow = AFLOW(aflow_executable=self.aflow_executable)
        return prototype_labels_are_equivalent(
            aflow.get_prototype_designation_from_atoms(atoms)["aflow_prototype_label"],
            self.__nominal_crystal_structure_npt["prototype-label"]["source-value"],
        )

    def __add_poscar_to_curr_prop_inst(
        self,
        change_of_basis: Union[str, npt.ArrayLike],
        filename: os.PathLike,
        key_name: str,
    ) -> None:
        """
        Add a POSCAR file constructed from ``self.__nominal_crystal_structure_npt``
        to the current property instance.

        Args:
            change_of_basis:
                Passed to
                :meth:`kim_tools.test_driver.core.SingleCrystalTestDriver._get_atoms`
            filename:
                File to save to. Will be automatically moved and renamed,
                e.g. 'instance.poscar' -> 'output/instance-1.poscar'
            key_name:
                The property key to write to
        """

        # `_get_atoms` always returns in Angstrom
        atoms_tmp = self._get_atoms(change_of_basis)

        # will automatically be renamed
        # e.g. 'instance.poscar' -> 'output/instance-1.poscar'
        atoms_tmp.write(filename=filename, sort=True, format="vasp")
        self._add_file_to_current_property_instance(key_name, filename)

    def _add_property_instance_and_common_crystal_genome_keys(
        self,
        property_name: str,
        write_stress: Union[bool, List[float]] = False,
        write_temp: Union[bool, float] = False,
        stress_unit: Optional[str] = None,
        temp_unit: str = "K",
        disclaimer: Optional[str] = None,
        omit_keys: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize a new property instance to ``self.property_instances``. It will
        automatically get the an "instance-id" equal to the length of
        ``self.property_instances`` after it is added. Then, write the common Crystal
        Genome keys to it from the attributes of this class.

        Args:
            property_name:
                The property name, e.g.
                "tag:staff@noreply.openkim.org,2023-02-21:property/binding-energy-crystal"
                or "binding-energy-crystal"
            write_stress:
                What (if any) to write to the "cell-cauchy-stress" key.
                If True, write the nominal stress the Test Driver was initialized with.
                If a list of floats is given, write that value (it must be a length 6
                list representing a stress tensor in Voigt order xx,yy,zz,yz,xz,xy).
                If a list is specified, you must also specify `stress_unit`.
            write_temp:
                What (if any) to write to the "temperature" key.
                If True, write the nominal temperature the Test Driver was initialized
                with. If float is given, write that value.
            stress_unit:
                Unit of stress. Required if a stress tensor is specified in
                `write_stress`.
            temp_unit:
                Unit of temperature. Defaults to K.
            disclaimer:
                An optional disclaimer commenting on the applicability of this result,
                e.g. "This relaxation did not reach the desired tolerance."
            omit_keys:
                Which keys to omit writing
        """
        crystal_structure = self.__nominal_crystal_structure_npt

        a = crystal_structure["a"]["source-value"]

        a_unit = crystal_structure["a"]["source-unit"]

        prototype_label = crystal_structure["prototype-label"]["source-value"]

        stoichiometric_species = crystal_structure["stoichiometric-species"][
            "source-value"
        ]

        parameter_values = _get_optional_source_value(
            crystal_structure, "parameter-values"
        )

        library_prototype_label = _get_optional_source_value(
            crystal_structure, "library-prototype-label"
        )

        short_name = _get_optional_source_value(crystal_structure, "short-name")

        if write_stress is False:
            cell_cauchy_stress = None
            cell_cauchy_stress_unit = None
        elif write_stress is True:
            cell_cauchy_stress_stored = crystal_structure["cell-cauchy-stress"][
                "source-value"
            ]
            cell_cauchy_stress_unit_stored = crystal_structure["cell-cauchy-stress"][
                "source-unit"
            ]
            if (
                stress_unit is not None
                and stress_unit != cell_cauchy_stress_unit_stored
            ):
                cell_cauchy_stress_unit = stress_unit
                cell_cauchy_stress = convert_units(
                    cell_cauchy_stress_stored,
                    cell_cauchy_stress_unit_stored,
                    cell_cauchy_stress_unit,
                    True,
                )
            else:
                cell_cauchy_stress = cell_cauchy_stress_stored
                cell_cauchy_stress_unit = cell_cauchy_stress_unit_stored
        else:
            if len(write_stress) != 6:
                raise KIMTestDriverError(
                    "`write_stress` must be a boolean or an array of length 6"
                )
            cell_cauchy_stress = write_stress
            cell_cauchy_stress_unit = stress_unit

        if write_temp is False:
            temperature = None
            temperature_unit = None
        elif write_temp is True:
            temperature_stored = crystal_structure["temperature"]["source-value"]
            temperature_unit_stored = crystal_structure["temperature"]["source-unit"]
            if temp_unit != temperature_unit_stored:
                temperature_unit = temp_unit
                temperature = convert_units(
                    temperature_stored,
                    temperature_unit_stored,
                    temperature_unit,
                    True,
                )
            else:
                temperature = temperature_stored
                temperature_unit = temperature_unit_stored
        else:
            temperature = write_temp
            temperature_unit = temp_unit

        crystal_genome_source_structure_id = _get_optional_source_value(
            crystal_structure, "crystal-genome-source-structure-id"
        )

        super()._set_serialized_property_instances(
            _add_property_instance_and_common_crystal_genome_keys(
                property_name=property_name,
                prototype_label=prototype_label,
                stoichiometric_species=stoichiometric_species,
                a=a,
                a_unit=a_unit,
                parameter_values=parameter_values,
                library_prototype_label=library_prototype_label,
                short_name=short_name,
                cell_cauchy_stress=cell_cauchy_stress,
                cell_cauchy_stress_unit=cell_cauchy_stress_unit,
                temperature=temperature,
                temperature_unit=temperature_unit,
                crystal_genome_source_structure_id=crystal_genome_source_structure_id,
                disclaimer=disclaimer,
                property_instances=super()._get_serialized_property_instances(),
                aflow_executable=self.aflow_executable,
                omit_keys=omit_keys,
            )
        )

        if omit_keys is None:
            omit_keys = []
        if "coordinates-file" not in omit_keys:
            self.__add_poscar_to_curr_prop_inst(
                "primitive", "instance.poscar", "coordinates-file"
            )
        if "coordinates-file-conventional" not in omit_keys:
            self.__add_poscar_to_curr_prop_inst(
                "conventional",
                "conventional.instance.poscar",
                "coordinates-file-conventional",
            )

    def _get_temperature(self, unit: str = "K") -> float:
        """
        Get the nominal temperature

        Args:
            unit:
                The requested unit for the output. Must be understood by the GNU
                ``units`` utility
        """
        source_value = self.__nominal_crystal_structure_npt["temperature"][
            "source-value"
        ]
        source_unit = self.__nominal_crystal_structure_npt["temperature"]["source-unit"]
        if source_unit != unit:
            temp = convert_units(source_value, source_unit, unit, True)
        else:
            temp = source_value
        return temp

    def _get_cell_cauchy_stress(self, unit: str = "eV/angstrom^3") -> List[float]:
        """
        Get the nominal stress

        Args:
            unit:
                The requested unit for the output. Must be understood by the GNU
                ``units`` utility
        """
        source_value = self.__nominal_crystal_structure_npt["cell-cauchy-stress"][
            "source-value"
        ]
        source_unit = self.__nominal_crystal_structure_npt["cell-cauchy-stress"][
            "source-unit"
        ]
        if source_unit != unit:
            stress, _ = convert_list(source_value, source_unit, unit)
        else:
            stress = source_value
        return stress

    def _get_mass_density(self, unit: str = "amu/angstrom^3") -> float:
        """
        Get the mass density of the current nominal state of the system,
        according to the masses defined in :data:`ase.data.atomic_masses`

        Args:
            unit:
                The requested units

        Returns:
            The mass density of the crystal
        """
        atoms = self._get_atoms()  # always in angstrom
        vol_ang3 = atoms.get_volume()
        mass_amu = 0.0
        for atomic_number in atoms.get_atomic_numbers():
            mass_amu += atomic_masses[atomic_number]
        density_amu_ang3 = mass_amu / vol_ang3
        if unit != "amu/angstrom^3":
            density = convert_units(density_amu_ang3, "amu/angstrom^3", unit, True)
        else:
            density = density_amu_ang3

        return density

    def _get_nominal_crystal_structure_npt(self) -> Dict:
        """
        Get the dictionary returning the current nominal state of the system.

        Returns:
            An instance of the
            `crystal-structure-npt
            <https://openkim.org/properties/show/crystal-structure-npt>`_
            OpenKIM property containing a symmetry-reduced description of the nominal
            crystal structure.
        """
        return self.__nominal_crystal_structure_npt

    def deduplicate_property_instances(
        self,
        properties_to_deduplicate: Optional[List[str]] = None,
        allow_rotation: bool = False,
        aflow_np: int = 4,
        rot_rtol: float = 0.01,
        rot_atol: float = 0.01,
    ) -> None:
        """
        In the internally stored property instances,
        deduplicate any repeated crystal structures for each property id and merge
        their "crystal-genome-source-structure-id" keys.

        WARNING: Only the crystal structures are checked. If you for some reason have a
        property that can reasonably report different non-structural values for the
        same atomic configuration, this will delete the extras!

        Args:
            properties_to_deduplicate:
                A list of property names to pick out of ``property_instances`` to
                deduplicate. Each element can be the long or short name, e.g.
                "tag:staff@noreply.openkim.org,2023-02-21:property/binding-energy-crystal"
                or "binding-energy-crystal". If omitted, all properties will be
                deduplicated.
            allow_rotation:
                Whether or not structures that are rotated by a rotation that is not in
                the crystal's point group are considered identical
            aflow_np:
                Number of processors to use to run the AFLOW executable
            rot_rtol:
                Parameter to pass to :func:`numpy.allclose` for compariong fractional
                rotations. Default value chosen to be commensurate with AFLOW
                default distance tolerance of 0.01*(NN distance). Used only if
                `allow_rotation` is False
            rot_atol:
                Parameter to pass to :func:`numpy.allclose` for compariong fractional
                rotations. Default value chosen to be commensurate with AFLOW
                default distance tolerance of 0.01*(NN distance). Used only if
                `allow_rotation` is False
        """
        deduplicated_property_instances = get_deduplicated_property_instances(
            property_instances=self.property_instances,
            properties_to_deduplicate=properties_to_deduplicate,
            allow_rotation=allow_rotation,
            aflow_np=aflow_np,
            rot_rtol=rot_rtol,
            rot_atol=rot_atol,
            aflow_executable=self.aflow_executable,
        )
        logger.info(
            f"Deduplicated {len(self.property_instances)} Property Instances "
            f"down to {len(deduplicated_property_instances)}."
        )
        # Remove files
        for original_property_instance in self.property_instances:
            instance_id = original_property_instance["instance-id"]
            instance_id_still_there = False
            for deduplicated_property_instance in deduplicated_property_instances:
                if instance_id == deduplicated_property_instance["instance-id"]:
                    instance_id_still_there = True
                    break
            if not instance_id_still_there:
                for key in original_property_instance:
                    value_dict = original_property_instance[key]
                    if not isinstance(value_dict, dict):
                        continue
                    if "source-unit" in value_dict:
                        continue
                    value = value_dict["source-value"]
                    if isinstance(value, str):
                        # TODO: should really check the property def that this is a
                        # "file" type key, but come on, how incredibly unlikely is it
                        # that there just happends to be a string type property that
                        # happens to have a valid file path in it
                        candidate_filename = os.path.join("output", value)
                        if os.path.isfile(candidate_filename):
                            os.remove(candidate_filename)

        super()._set_serialized_property_instances(
            kim_edn.dumps(deduplicated_property_instances)
        )

    def _set_serialized_property_instances(self, property_instances) -> None:
        """
        An override to prevent SingleCrystalTestDriver derived classes from setting
        property instances directly
        """
        raise NotImplementedError(
            "Setting property instances directly not supported "
            "in Crystal Genome Test Drivers"
        )

    def _get_atoms(
        self, change_of_basis: Union[str, npt.ArrayLike] = "primitive"
    ) -> Atoms:
        """
        Get the atomic configuration representing the nominal crystal,
        with a calculator already attached.

        Args:
            change_of_basis:
                Specify the desired unit cell. The default, ``"primitive"``, gives
                the cell as defined in the `AFLOW prototype standard
                <http://doi.org/10.1016/j.commatsci.2017.01.017>`_. ``"conventional"``
                gives the conventional cell defined therein.

                Alternatively, provide an arbitrary change of basis matrix **P** as
                defined in ITA 1.5.1.2, with the above-defined primitive cell
                corresponding to the "old basis" and the returned ``Atoms`` object being
                in the "new basis".

                See the docstring for
                :func:`kim_tools.symmetry_util.core.change_of_basis_atoms` for
                more information on how to define the change of basis.

        Returns:
            Unit cell of the crystal.
            Lengths are always in angstrom
        """
        crystal_structure = self.__nominal_crystal_structure_npt
        atoms_prim = get_atoms_from_crystal_structure(
            crystal_structure, aflow_executable=self.aflow_executable
        )
        if isinstance(change_of_basis, str):
            if change_of_basis.lower() == "primitive":
                change_of_basis_matrix = None
            elif change_of_basis.lower() == "conventional":
                prototype_label = crystal_structure["prototype-label"]["source-value"]
                sgnum = get_space_group_number_from_prototype(prototype_label)
                formal_bravais_lattice = get_formal_bravais_lattice_from_space_group(
                    sgnum
                )
                change_of_basis_matrix = get_change_of_basis_matrix_to_conventional_cell_from_formal_bravais_lattice(  # noqa: E501
                    formal_bravais_lattice
                )
            else:
                raise KIMTestDriverError(
                    'Allowable string values for `change_of_basis` are "primitive" or '
                    f'"conventional". You provided f{change_of_basis}'
                )
        else:
            change_of_basis_matrix = change_of_basis

        if change_of_basis_matrix is None:
            atoms_tmp = atoms_prim
        else:
            atoms_tmp = change_of_basis_atoms(atoms_prim, change_of_basis_matrix)

        atoms_tmp.calc = self._calc
        return atoms_tmp

    def get_nominal_prototype_label(self) -> str:
        return self._get_nominal_crystal_structure_npt()["prototype-label"][
            "source-value"
        ]

    def get_nominal_space_group_number(self) -> int:
        return get_space_group_number_from_prototype(self.get_nominal_prototype_label())

    def get_nominal_stoichiometric_species(self) -> List[str]:
        return self._get_nominal_crystal_structure_npt()["stoichiometric-species"][
            "source-value"
        ]

    def get_nominal_stoichiometry(self) -> List[int]:
        return get_stoich_reduced_list_from_prototype(
            self.get_nominal_prototype_label()
        )

    def get_nominal_a(self) -> float:
        return self._get_nominal_crystal_structure_npt()["a"]["source-value"]

    def get_nominal_parameter_names(self) -> List[str]:
        return _get_optional_source_value(
            self._get_nominal_crystal_structure_npt(), "parameter-names"
        )

    def get_nominal_parameter_values(self) -> List[float]:
        return _get_optional_source_value(
            self._get_nominal_crystal_structure_npt(), "parameter-values"
        )

    def get_nominal_short_name(self) -> List[str]:
        return _get_optional_source_value(
            self._get_nominal_crystal_structure_npt(), "short-name"
        )

    def get_nominal_library_prototype_label(self) -> str:
        return _get_optional_source_value(
            self._get_nominal_crystal_structure_npt(), "library-prototype-label"
        )

    def get_atom_indices_for_each_wyckoff_orb(self) -> List[Dict]:
        """
        Get a list of dictionaries containing the atom indices of each Wyckoff
        orbit.

        Returns:
            The information is in this format --
            ``[{"letter":"a", "indices":[0,1]}, ... ]``
        """
        return get_atom_indices_for_each_wyckoff_orb(self.get_nominal_prototype_label())

    def get_input_rotation(self) -> Optional[npt.ArrayLike]:
        """
        Returns:
            If the Test Driver was called with an Atoms object, the nominal crystal
            structure may be rotated w.r.t. the input.
            This returns the Cartesian rotation to transform the Atoms input to the
            internal nominal crystal structure. I.e., if you want to get computed
            tensor properties in the same orientation as your input, you should
            rotate the reported tensors by the transpose of this rotation.
        """
        return self.__input_rotation


def query_crystal_structures(
    stoichiometric_species: List[str],
    prototype_label: Optional[str] = None,
    short_name: Optional[str] = None,
    cell_cauchy_stress_eV_angstrom3: Optional[List[float]] = None,
    temperature_K: float = 0,
    kim_model_name: Optional[str] = None,
) -> List[Dict]:
    """
    Query for all equilibrium parameter sets for this species combination and,
    optionally, crystal structure specified by ``prototype_label`` and/or ``short_name``
    in the KIM database. This is a utility function for running the test outside of the
    OpenKIM pipeline. In the OpenKIM pipeline, this information is delivered to the test
    driver through the ``runner`` script.

    Args:
        stoichiometric_species:
            List of unique species in the crystal. Required part of the Crystal Genome
            designation.
        short_name:
            short name of the crystal, e.g. "Hexagonal Close Packed". This will be
            searched as a case-insensitive regex, so partial matches will be returned.
            The list of possible shortnames is taken by postprocessing README_PROTO.TXT
            from the AFLOW software and packaged with kim-tools for reproducibility. To
            see the exact list of possible short names, call
            :func:`kim_tools.aflow_util.core.read_shortnames` and inspect the values of
            the returned
            dictionary. Note that a given short name corresponds to an exact set of
            parameters (with some tolerance), except the overall scale of the crystal.
            For example, "Hexagonal Close Packed" will return only structures with a
            c/a close to 1.63 (actually close packed), not any structure with the same
            symmetry as HCP as is sometimes colloquially understood.
            TODO: consider adding the same expanded logic we have on the website that
            searches for any crystal with the symmetry corresponding to a given
            shortname, i.e. invalidating the last caveat given above.
        prototype_label:
            AFLOW prototype label for the crystal.
        cell_cauchy_stress_eV_angstrom3:
            Cauchy stress on the cell in eV/angstrom^3 (ASE units) in
            [xx,yy,zz,yz,xz,xy] format
        temperature_K:
            The temperature in Kelvin
        kim_model_name:
            KIM model name. If not provided, RD will be queried instead

    Returns:
        List of kim property instances matching the query in the OpenKIM.org database
    """
    if cell_cauchy_stress_eV_angstrom3 is None:
        cell_cauchy_stress_eV_angstrom3 = [0, 0, 0, 0, 0, 0]

    stoichiometric_species.sort()

    # TODO: Some kind of generalized query interface for all tests, this is very
    # hand-made
    cell_cauchy_stress_Pa = [
        component * 1.6021766e11 for component in cell_cauchy_stress_eV_angstrom3
    ]

    query = {
        "meta.type": "rd" if kim_model_name is None else "tr",
        "property-id": (
            "tag:staff@noreply.openkim.org,2023-02-21:property/crystal-structure-npt"
        ),
        "stoichiometric-species.source-value": {
            "$size": len(stoichiometric_species),
            "$all": stoichiometric_species,
        },
        "cell-cauchy-stress.si-value": cell_cauchy_stress_Pa,
        "temperature.si-value": temperature_K,
    }

    if kim_model_name is not None:
        query["meta.subject.extended-id"] = kim_model_name

    if prototype_label is not None:
        query["prototype-label.source-value"] = prototype_label

    if short_name is not None:
        query["short-name.source-value"] = {"$regex": short_name, "$options": "$i"}

    raw_query_args = {
        "query": query,
        "database": "data",
        "limit": 0,
    }

    logger.info(f"Sending below query:\n{raw_query_args}")

    query_result = raw_query(**raw_query_args)

    len_msg = (
        f"Found {len(query_result)} equilibrium structures from "
        "query_crystal_genome_structures()"
    )
    logger.info(len_msg)
    logger.debug(f"Query result (length={len(query_result)}):\n{query_result}")

    print(f"\n!!! {len_msg} !!!\n")

    return query_result


def detect_unique_crystal_structures(
    crystal_structures: Union[List[Dict], Dict],
    allow_rotation: bool = False,
    aflow_np: int = 4,
    rot_rtol: float = 0.01,
    rot_atol: float = 0.01,
    aflow_executable=AFLOW_EXECUTABLE,
) -> Dict:
    """
    Detect which of the provided crystal structures is unique

    Args:
        crystal_structures:
            A list of dictionaries in KIM Property format, each containing the Crystal
            Genome keys required to build a structure, namely: "stoichiometric-species",
            "prototype-label", "a", and, if the prototype has free parameters,
            "parameter-values". These dictionaries are not required to be complete KIM
            Property Instances, e.g. the keys "property-id", "instance-id" and "meta"
            can be absent. Alternatively, this can be a dictionary of dictionaries with
            integers as indices, for the recursive call.
        allow_rotation:
            Whether or not structures that are rotated by a rotation that is not in the
            crystal's point group are considered identical
        aflow_np:
            Number of processors to use to run the AFLOW executable
        rot_rtol:
            Parameter to pass to :func:`numpy.allclose` for compariong fractional
            rotations. Default value chosen to be commensurate with AFLOW
            default distance tolerance of 0.01*(NN distance). Used only if
            `allow_rotation` is False
        rot_atol:
            Parameter to pass to :func:`numpy.allclose` for compariong fractional
            rotations. Default value chosen to be commensurate with AFLOW
            default distance tolerance of 0.01*(NN distance). Used only if
            `allow_rotation` is False
        aflow_executable:
            Path to AFLOW executable
    Returns:
        Dictionary with keys corresponding to indices of unique structures and values
        being lists of indices of their duplicates
    """
    if len(crystal_structures) == 0:
        return []

    aflow = AFLOW(aflow_executable=aflow_executable, np=aflow_np)

    with TemporaryDirectory() as tmpdirname:
        # I don't know if crystal_structurs is a list or a dict with integer keys
        for i in (
            range(len(crystal_structures))
            if isinstance(crystal_structures, list)
            else crystal_structures
        ):
            structure = crystal_structures[i]
            try:
                get_poscar_from_crystal_structure(
                    structure,
                    os.path.join(tmpdirname, str(i)),
                    aflow_executable=aflow_executable,
                )
            except AFLOW.ChangedSymmetryException:
                logger.info(
                    f"Comparison structure {i} failed to write a POSCAR due to a "
                    "detected higher symmetry"
                )

        comparison = aflow.compare_materials_dir(tmpdirname)

        unique_materials = {}
        for materials_group in comparison:
            i_repr = int(
                materials_group["structure_representative"]["name"].split("/")[-1]
            )
            unique_materials[i_repr] = []
            for structure_duplicate in materials_group["structures_duplicate"]:
                unique_materials[i_repr].append(
                    int(structure_duplicate["name"].split("/")[-1])
                )

        if not allow_rotation:
            for materials_group in comparison:
                # to preserve their ordering in the original input list, make this a
                # dictionary now
                repr_filename = materials_group["structure_representative"]["name"]
                rotated_structures = {}
                cell = get_cell_from_poscar(repr_filename)
                sgnum = materials_group["space_group"]
                for potential_rotated_duplicate in materials_group[
                    "structures_duplicate"
                ]:
                    cart_rot = potential_rotated_duplicate["rotation"]
                    if not cartesian_rotation_is_in_point_group(
                        cart_rot=cart_rot,
                        sgnum=sgnum,
                        cell=cell,
                        rtol=rot_rtol,
                        atol=rot_atol,
                    ):
                        i_rot_dup = int(
                            potential_rotated_duplicate["name"].split("/")[-1]
                        )
                        rotated_structures[i_rot_dup] = crystal_structures[i_rot_dup]
                        # Now that we know it's rotated, need to remove
                        # it from the list of duplicates
                        i_repr = int(repr_filename.split("/")[-1])
                        unique_materials[i_repr].remove(i_rot_dup)

                unique_materials.update(
                    detect_unique_crystal_structures(
                        crystal_structures=rotated_structures,
                        allow_rotation=False,
                        aflow_np=aflow_np,
                        rot_rtol=rot_rtol,
                        rot_atol=rot_atol,
                        aflow_executable=aflow_executable,
                    )
                )

    return unique_materials


def get_deduplicated_property_instances(
    property_instances: List[Dict],
    properties_to_deduplicate: Optional[List[str]] = None,
    allow_rotation: bool = False,
    aflow_np: int = 4,
    rot_rtol: float = 0.01,
    rot_atol: float = 0.01,
    aflow_executable: str = AFLOW_EXECUTABLE,
) -> List[Dict]:
    """
    Given a list of dictionaries constituting KIM Property instances,
    deduplicate any repeated crystal structures for each property id and merge
    their "crystal-genome-source-structure-id" keys.

    WARNING: Only the crystal structures are checked. If you for some reason have a
    property that can reasonably report different non-structural values for the
    same atomic configuration, this will delete the extras!

    Args:
        property_instances:
            The list of KIM Property Instances to deduplicate
        properties_to_deduplicate:
            A list of property names to pick out of ``property_instances`` to
            deduplicate. Each element can be the long or short name, e.g.
            "tag:staff@noreply.openkim.org,2023-02-21:property/binding-energy-crystal"
            or "binding-energy-crystal". If omitted, all properties will be
            deduplicated.
        allow_rotation:
            Whether or not structures that are rotated by a rotation that is not in the
            crystal's point group are considered identical
        aflow_np:
            Number of processors to use to run the AFLOW executable
        rot_rtol:
            Parameter to pass to :func:`numpy.allclose` for compariong fractional
            rotations. Default value chosen to be commensurate with AFLOW
            default distance tolerance of 0.01*(NN distance). Used only if
            `allow_rotation` is False
        rot_atol:
            Parameter to pass to :func:`numpy.allclose` for compariong fractional
            rotations. Default value chosen to be commensurate with AFLOW
            default distance tolerance of 0.01*(NN distance). Used only if
            `allow_rotation` is False
        aflow_executable:
            Path to aflow executable

    Returns:
        The deduplicated property instances
    """
    if properties_to_deduplicate is None:
        properties_set = set()
        for property_instance in property_instances:
            properties_set.add(property_instance["property-id"])
        properties_to_deduplicate = list(properties_set)

    property_instances_deduplicated = []
    for property_name in properties_to_deduplicate:
        # Pick out property instances with the relevant name
        property_instances_curr_name = []
        for property_instance in property_instances:
            property_id = property_instance["property-id"]
            if (
                property_id == property_name
                or get_property_id_path(property_id)[3] == property_name
            ):
                property_instances_curr_name.append(deepcopy(property_instance))
        if len(property_instances_curr_name) == 0:
            raise KIMTestDriverError(
                "The property you asked to deduplicate "
                "is not in the property instances you provided"
            )

        # Get unique-duplicate dictionary
        unique_crystal_structures = detect_unique_crystal_structures(
            crystal_structures=property_instances_curr_name,
            allow_rotation=allow_rotation,
            aflow_np=aflow_np,
            rot_rtol=rot_rtol,
            rot_atol=rot_atol,
            aflow_executable=aflow_executable,
        )

        # Put together the list of unique instances for the current
        # name only
        property_instances_curr_name_deduplicated = []
        for i_unique in unique_crystal_structures:
            property_instances_curr_name_deduplicated.append(
                property_instances_curr_name[i_unique]
            )
            # Put together a list of "crystal-genome-source-structure-id"
            # to gather into the deduplicated structure
            additional_source_structure_id = []
            for i_dup in unique_crystal_structures[i_unique]:
                source_structure_id = _get_optional_source_value(
                    property_instances_curr_name[i_dup],
                    "crystal-genome-source-structure-id",
                )
                if source_structure_id is not None:
                    # "crystal-genome-source-structure-id" is a 2D list
                    # but only the first row should be populated
                    additional_source_structure_id += source_structure_id[0]

            if len(additional_source_structure_id) != 0:
                if (
                    "crystal-genome-source-structure-id"
                    not in property_instances_curr_name_deduplicated[-1]
                ):
                    property_instances_curr_name_deduplicated[-1][
                        "crystal-genome-source-structure-id"
                    ] = [[]]
                property_instances_curr_name_deduplicated[-1][
                    "crystal-genome-source-structure-id"
                ]["source-value"][0] += additional_source_structure_id

        property_instances_deduplicated += property_instances_curr_name_deduplicated

    # Add any instances of properties that weren't deduplicated
    for property_instance in property_instances:
        property_id = property_instance["property-id"]
        if (
            property_id not in properties_to_deduplicate
            and get_property_id_path(property_id)[3] not in properties_to_deduplicate
        ):
            property_instances_deduplicated.append(deepcopy(property_instance))

    property_instances_deduplicated.sort(key=lambda a: a["instance-id"])

    return property_instances_deduplicated


def crystal_input_from_test_generator_line(
    test_generator_line: str, kim_model_name: str
) -> List[Dict]:
    """
    Produce a list of dictionaries of kwargs for a Crystal Genome Test Driver invocation
    from a line in its ``test_generator.json``
    """
    test_generator_dict = json.loads(test_generator_line)
    stoichiometric_species = test_generator_dict["stoichiometric_species"]
    prototype_label = test_generator_dict["prototype_label"]
    cell_cauchy_stress_eV_angstrom3 = test_generator_dict.get(
        "cell_cauchy_stress_eV_angstrom3"
    )
    temperature_K = test_generator_dict.get("temperature_K")
    crystal_genome_test_args = test_generator_dict.get("crystal_genome_test_args")
    equilibria = query_crystal_structures(
        stoichiometric_species=stoichiometric_species,
        prototype_label=prototype_label,
        kim_model_name=kim_model_name,
    )
    inputs = []
    for equilibrium in equilibria:
        inputs.append(
            {
                "material": equilibrium,
            }
        )
        if cell_cauchy_stress_eV_angstrom3 is not None:
            inputs[-1][
                "cell_cauchy_stress_eV_angstrom3"
            ] = cell_cauchy_stress_eV_angstrom3
        if temperature_K is not None:
            inputs[-1]["temperature_K"] = temperature_K
        if crystal_genome_test_args is not None:
            inputs[-1].update(crystal_genome_test_args)

    return inputs
