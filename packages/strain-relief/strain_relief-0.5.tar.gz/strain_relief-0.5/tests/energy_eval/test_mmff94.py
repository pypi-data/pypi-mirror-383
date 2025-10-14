import pytest
from strain_relief.constants import MOL_KEY
from strain_relief.energy_eval._mmff94 import MMFF94_energy, _MMFF94_energy
from strain_relief.types import MolPropertiesDict, MolsDict


@pytest.mark.parametrize("fixture", ["mols", "mols_wo_bonds"])
@pytest.mark.parametrize("force_field", ["MMFF94", "MMFF94s"])
def test_MMFF94_energy(request, fixture: MolsDict, force_field: str):
    mols = request.getfixturevalue(fixture)
    result = MMFF94_energy(
        mols=mols,
        method="MMFF94",
        MMFFGetMoleculeProperties={"mmffVariant": force_field},
        MMFFGetMoleculeForceField={},
    )
    assert result is not None
    assert isinstance(result, dict)
    assert len(result) == len(mols)

    for id, mol in result.items():
        assert isinstance(mol, dict)
        assert len(mol) == mols[id][MOL_KEY].GetNumConformers()

        for conf_id, energy in mol.items():
            assert isinstance(conf_id, int)
            assert isinstance(energy, float)


@pytest.mark.parametrize("force_field", ["MMFF94", "MMFF94s"])
def test__MMFF94_energy(mol_w_confs: MolPropertiesDict, force_field: str):
    mol = mol_w_confs
    result = _MMFF94_energy(
        mol=mol[MOL_KEY],
        id="id",
        MMFFGetMoleculeProperties={"mmffVariant": force_field},
        MMFFGetMoleculeForceField={},
    )
    assert result is not None
    assert isinstance(result, dict)
    assert len(result) == mol[MOL_KEY].GetNumConformers()

    for conf_id, energy in result.items():
        assert isinstance(conf_id, int)
        assert isinstance(energy, float)
