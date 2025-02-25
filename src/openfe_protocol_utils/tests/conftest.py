# This code is part of OpenFE and is licensed under the MIT license.
# For details, see https://github.com/OpenFreeEnergy/openfe
import os
import importlib
import pytest
from importlib import resources
from rdkit import Chem
from rdkit.Chem import AllChem
from openff.units import unit
import pooch

import gufe
from gufe import SmallMoleculeComponent, LigandAtomMapping


class SlowTests:
    """Plugin for handling fixtures that skips slow tests

    Fixtures
    --------

    Currently two fixture types are handled:
      * `integration`:
        Extremely slow tests that are meant to be run to truly put the code
        through a real run.

      * `slow`:
        Unit tests that just take too long to be running regularly.


    How to use the fixtures
    -----------------------

    To add these fixtures simply add `@pytest.mark.integration` or
    `@pytest.mark.slow` decorator to the relevant function or class.


    How to run tests marked by these fixtures
    -----------------------------------------

    To run the `integration` tests, either use the `--integration` flag
    when invoking pytest, or set the environment variable
    `OFE_INTEGRATION_TESTS` to `true`. Note: triggering `integration` will
    automatically also trigger tests marked as `slow`.

    To run the `slow` tests, either use the `--runslow` flag when invoking
    pytest, or set the environment variable `OFE_SLOW_TESTS` to `true`
    """
    def __init__(self, config):
        self.config = config

    @staticmethod
    def _modify_slow(items, config):
        msg = ("need --runslow pytest cli option or the environment variable "
               "`OFE_SLOW_TESTS` set to `True` to run")
        skip_slow = pytest.mark.skip(reason=msg)
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    @staticmethod
    def _modify_integration(items, config):
        msg = ("need --integration pytest cli option or the environment "
               "variable `OFE_INTEGRATION_TESTS` set to `True` to run")
        skip_int = pytest.mark.skip(reason=msg)
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_int)

    def pytest_collection_modifyitems(self, items, config):
        if (config.getoption('--integration') or
            os.getenv("OFE_INTEGRATION_TESTS", default="false").lower() == 'true'):
            return
        elif (config.getoption('--runslow') or
              os.getenv("OFE_SLOW_TESTS", default="false").lower() == 'true'):
            self._modify_integration(items, config)
        else:
            self._modify_integration(items, config)
            self._modify_slow(items, config)


# allow for optional slow tests
# See: https://docs.pytest.org/en/latest/example/simple.html
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--integration", action="store_true", default=False,
        help="run long integration tests",
    )


def pytest_configure(config):
    config.pluginmanager.register(SlowTests(config), "slow")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line(
            "markers", "integration: mark test as long integration test")


@pytest.fixture(scope='session')
def benzene_modifications():
    files = {}
    with importlib.resources.files('openfe_protocol_utils.tests.data') as d:
        fn = str(d / 'benzene_modifications.sdf')
        supp = Chem.SDMolSupplier(str(fn), removeHs=False)
        for rdmol in supp:
            files[rdmol.GetProp('_Name')] = SmallMoleculeComponent(rdmol)
    return files


@pytest.fixture(scope='session')
def T4_protein_component():
    with resources.files('openfe_protocol_utils.tests.data') as d:
        fn = str(d / '181l_only.pdb')
        comp = gufe.ProteinComponent.from_pdb_file(fn, name="T4_protein")

    return comp


@pytest.fixture()
def eg5_ligands_sdf():
    with resources.files('openfe_protocol_utils.tests.data.eg5') as d:
        yield str(d / 'eg5_ligands.sdf')


@pytest.fixture()
def eg5_ligands(eg5_ligands_sdf) -> list[SmallMoleculeComponent]:
    return [SmallMoleculeComponent(m)
            for m in Chem.SDMolSupplier(eg5_ligands_sdf, removeHs=False)]


RFE_OUTPUT = pooch.create(
    path=pooch.os_cache("openfe_analysis"),
    base_url="doi:10.6084/m9.figshare.24101655",
    registry={
        "checkpoint.nc": "5af398cb14340fddf7492114998b244424b6c3f4514b2e07e4bd411484c08464",
        "db.json": "b671f9eb4daf9853f3e1645f9fd7c18150fd2a9bf17c18f23c5cf0c9fd5ca5b3",
        "hybrid_system.pdb": "07203679cb14b840b36e4320484df2360f45e323faadb02d6eacac244fddd517",
        "simulation.nc": "92361a0864d4359a75399470135f56642b72c605069a4c33dbc4be6f91f28b31",
        "simulation_real_time_analysis.yaml": "65706002f371fafba96037f29b054fd7e050e442915205df88567f48f5e5e1cf",
    }
)


@pytest.fixture
def simulation_nc():
    return RFE_OUTPUT.fetch("simulation.nc")
