import pytest
from strain_relief.constants import MOL_KEY
from strain_relief.minimisation._mmff94 import MMFF94_min
from strain_relief.types import MolsDict


@pytest.mark.parametrize("fixture", ["mols", "mols_wo_bonds"])
@pytest.mark.parametrize("force_field", ["MMFF94", "MMFF94s"])
def test_MMFF94_min(request, fixture: MolsDict, force_field: str):
    mols = request.getfixturevalue(fixture)
    results, mols = MMFF94_min(
        mols=mols,
        method="MMFF94",
        MMFFGetMoleculeProperties={"mmffVariant": force_field},
        MMFFGetMoleculeForceField={},
        maxIters=1,
        fmax=0.05,
        fexit=250,
    )

    for id in mols.keys():
        conf_energies = results[id]
        assert len(conf_energies) == mols[id][MOL_KEY].GetNumConformers()
