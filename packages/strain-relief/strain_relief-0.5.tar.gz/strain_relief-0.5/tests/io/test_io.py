from pathlib import Path

import pandas as pd
import pytest
from rdkit import Chem
from strain_relief import test_dir
from strain_relief.constants import CHARGE_COL_NAME, SPIN_COL_NAME
from strain_relief.io._io import (
    _calculate_charge,
    _calculate_spin,
    load_parquet,
    to_mols_dict,
)


@pytest.mark.parametrize(
    "parquet_path, id_col_name",
    [
        (test_dir / "data" / "ligboundconf.parquet", None),
        (test_dir / "data" / "target.parquet", "SMILES"),
    ],
)
def test_load_parquet(parquet_path: Path, id_col_name: str | None):
    df = load_parquet(parquet_path=parquet_path, id_col_name=id_col_name, include_charged=True)
    assert len(df) > 0


def test_calculate_charge():
    df = pd.DataFrame({"mol": [Chem.MolFromSmiles("C"), Chem.MolFromSmiles("C[O-]")]})
    df = _calculate_charge(df, "mol", True)
    assert df[CHARGE_COL_NAME].to_list() == [0, -1]


def test_calculate_spin():
    df = pd.DataFrame({"mol": [Chem.MolFromSmiles("CC"), Chem.MolFromSmiles("C[CH]")]})
    df = _calculate_spin(df, "mol")
    assert df[SPIN_COL_NAME].to_list() == [1, 3]


def test_to_mols_dict():
    df = pd.DataFrame({"mol": [Chem.MolFromSmiles("C"), Chem.MolFromSmiles("C[O-]")], "id": [1, 2]})
    df = _calculate_charge(df, "mol", False)
    mols = to_mols_dict(df=df, mol_col_name="mol", id_col_name="id", include_charged=False)
    assert len(mols) == 1


@pytest.mark.skip(reason="Test not implemented")
def test_check_columns():
    pass


@pytest.mark.skip(reason="Test not implemented")
def test_save_data():
    pass
