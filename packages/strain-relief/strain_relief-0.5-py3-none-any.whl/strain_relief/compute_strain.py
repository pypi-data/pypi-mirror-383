####################################################################################################
# This is the script for StrainRelief calculate ligand strain using a given force field            #
#                                                                                                  #
# ALGORITHM:                                                                                       #
# 1. Read in molecules(s) from df                                                                  #
# 2. Calculate the local minimum conformer by minimising the docked pose with a loose convergence  #
#    criteria                                                                                      #
# 2. Generate n conformers for each molecule                                                       #
# 3. Minimise each conformation and choose the lowest as an approximation for the global minimum   #
# 4. (ONLY IF USING A DIFFFERENT FF FOR ENERGIES) Predict energy of each conformation              #
# 5. Calculate ligand strain between local and global minimum and apply threshold                  #
#####################################################################################################

from collections.abc import Sequence
from copy import deepcopy
from timeit import default_timer as timer

import pandas as pd
import rich
import rich.syntax
import rich.tree
from loguru import logger as logging
from omegaconf import DictConfig, OmegaConf
from rdkit import Chem

from strain_relief.conformers import generate_conformers
from strain_relief.energy_eval import predict_energy
from strain_relief.io import save_parquet, to_mols_dict
from strain_relief.minimisation import minimise_conformers
from strain_relief.types import MolsDict


def compute_strain(
    cfg: DictConfig,
    df: pd.DataFrame | None = None,
    mols: Sequence[Chem.Mol | bytes] | None = None,
    ids: Sequence[int | str] | None = None,
) -> pd.DataFrame:
    """Calculate ligand strain energies using rkdit conformer generation.

    One (and only one) of df or mols must be provided. If mols are provided they must
    be all RDKit Mol objects or all bytes (Mol.ToBinary()).

    Parameters
    ----------
    cfg: DictConfig
        DictConfig object containing the hydra configuration.
    df: pd.DataFrame [Optional]
        Input dataframe without rdkit.Mol objects.
    mols: Sequence[Chem.Mol|bytes] [Optional]
        List of molecules (RDKit.Mol or bytes).
    ids: Sequence[int|str] [Optional]
        List of unique molecule ids.

    Returns
    -------
    pd.DataFrame
        Dataframe with strain energies and other metadata.
    """
    start = timer()
    _print_config_tree(cfg)

    if (
        cfg.local_min.method in ["MACE", "FAIRChem"]
        or cfg.global_min.method in ["MACE", "FAIRChem"]
        or cfg.energy_eval.method in ["MACE", "FAIRChem"]
    ) and cfg.model.model_paths is None:
        raise ValueError("Model path must be provided if using a NNP")

    df = _parse_args(df=df, mols=mols, ids=ids)

    # Load data
    docked: MolsDict = to_mols_dict(df, **cfg.io.input)
    local_minima: MolsDict = {id: deepcopy(mol) for id, mol in docked.items()}
    global_minimia: MolsDict = {id: deepcopy(mol) for id, mol in docked.items()}

    # Find the local minimum using a looser convergence criteria
    logging.info("Minimising docked conformer...")
    local_minima = minimise_conformers(local_minima, **cfg.local_min)

    # Generate conformers from the docked conformer
    global_minimia = generate_conformers(global_minimia, **cfg.conformers)

    # Find approximate global minimum from generated conformers
    logging.info("Minimising generated conformers...")
    global_minimia = minimise_conformers(global_minimia, **cfg.global_min)

    # Predict single point energies (if using a different method from minimisation)
    if (
        cfg.local_min.method != cfg.energy_eval.method
        or cfg.global_min.method != cfg.energy_eval.method
    ):
        logging.info("Predicting energies of local minima poses...")
        local_minima = predict_energy(local_minima, **cfg.energy_eval)
        logging.info("Predicting energies of generated conformers...")
        global_minimia = predict_energy(global_minimia, **cfg.energy_eval)

    # Save torsional strains
    md = save_parquet(df, docked, local_minima, global_minimia, cfg.threshold, **cfg.io.output)

    end = timer()
    logging.info(f"Ligand strain calculations took {end - start:.2f} seconds. \n")

    return md


def _parse_args(
    df: pd.DataFrame | None = None,
    mols: Sequence[Chem.Mol | bytes] | None = None,
    ids: Sequence[int | str] | None = None,
) -> pd.DataFrame:
    """Normalise input into a dataframe with columns ['id', 'mol_bytes'].

     Precedence:
    1. If df is provided it is copied and returned (mols / ids ignored).
    2. Otherwise mols must be provided and be homogeneous (all Chem.Mol or all bytes).
       If ids not supplied they are auto-generated (0..n-1). RDKit Mol objects are
       converted to binary via Mol.ToBinary().
    """
    if df is None and mols is None:
        raise ValueError("Either df or mols must be provided")

    if df is not None:  # prevents input df from being updated
        if mols is not None:
            logging.warning("compute_strain received both df and mols; using df and ignoring mols.")
        return df.copy()

    if not ids:
        ids = list(range(len(mols)))

    mol_types = set(type(mol) for mol in mols)
    if len(mol_types) > 1:
        raise ValueError("All molecules must be of the same type (Chem.Mol or bytes)")

    if Chem.Mol in mol_types:
        mols = [mol.ToBinary() for mol in mols]

    return pd.DataFrame({"id": ids, "mol_bytes": mols})


def _print_config_tree(
    cfg: DictConfig,
    resolve: bool = False,
) -> None:
    """Prints content of DictConfig using Rich library and its tree structure.

    Parameters
    ----------
    cfg: DictConfig
        The configuration to be printed.
    resolve: bool
        Whether to resolve interpolations in the configuration.
    """
    style = "dim"
    tree = rich.tree.Tree("CONFIG", style=style, guide_style=style)

    # Generate config tree
    for field in cfg:
        branch = tree.add(field, style=style, guide_style=style)

        config_group = cfg[field]
        if isinstance(config_group, DictConfig):
            branch_content = OmegaConf.to_yaml(config_group, resolve=resolve)
        else:
            branch_content = str(config_group)

        branch.add(rich.syntax.Syntax(branch_content, "yaml"))

    # Print config tree
    rich.print(tree)
