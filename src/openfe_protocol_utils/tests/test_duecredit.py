import os
import importlib
import pytest

import openfe_protocol_utils


pytest.importorskip("duecredit")


@pytest.mark.skipif(
    (os.environ.get("DUECREDIT_ENABLE", "no").lower() in ("no", "0", "false")),
    reason="duecredit is disabled",
)
class TestDuecredit:

    @pytest.mark.parametrize(
        "module, dois",
        [
            [
                "openfe_protocol_utils.analysis.multistate_analysis",
                [
                    "10.5281/zenodo.596622",
                    "10.1063/1.2978177",
                    "10.1021/ct0502864",
                    "10.1021/acs.jctc.5b00784",
                    "10.5281/zenodo.596220",
                ],
            ],
        ],
    )
    def test_duecredit_protocol_collection(self, module, dois):
        importlib.import_module(module)
        for doi in dois:
            assert openfe_protocol_utils.due.due.citations[(module, doi)].cites_module

    def test_duecredit_active(self):
        assert openfe_protocol_utils.due.due.active
