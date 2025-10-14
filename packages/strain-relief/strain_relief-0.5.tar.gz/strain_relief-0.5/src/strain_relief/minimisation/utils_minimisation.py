import ase
import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator
from loguru import logger as logging
from rdkit import Chem

from strain_relief.constants import CHARGE_KEY, MOL_KEY, SPIN_KEY
from strain_relief.io import ase_to_rdkit, rdkit_to_ase
from strain_relief.minimisation.utils_bfgs import StrainReliefBFGS
from strain_relief.types import (
    ConfEnergiesDict,
    ConformerASEList,
    EnergiesDict,
    MolPropertiesDict,
    MolsDict,
)


def method_min(
    mols: MolsDict,
    calculator: ase.calculators,
    maxIters: int,
    fmax: float,
    fexit: float,
    conversion_factor: float = 1,
) -> tuple[EnergiesDict, MolsDict]:
    """Minimise all conformers of a Chem.Mol using the given calculator.

    Parameters
    ----------
    mols : MolsDict
        Dictionary of molecules to minimise.
    calculator : ase.calculators
        The ASE calculator to use for energy calculation.
    maxIters : int
        Maximum number of iterations for the minimisation.
    fmax : float
        Convergence criteria, converged when max(forces) < fmax.
    fexit : float
        Exit criteria, exit when max(forces) > fexit.
    conversion_factor: float
        Scale factor to convert energy to kcal/mol.

    energies, mols : EnergiesDict, MolsDict
        energies is a dict of final energy of each molecular conformer in eV (i.e. 0 = converged).
        mols contains the dictionary of molecules with the conformers minimised.

        energies = {
            "mol_id": {
                "conf_id": energy
            }
        }
    """
    energies: EnergiesDict = {}
    for id, mol_properties in mols.items():
        energies[id], mols[id] = _method_min(
            mol_properties, id, calculator, maxIters, fmax, fexit, conversion_factor
        )
    return energies, mols


def _method_min(
    mol_properties: MolPropertiesDict,
    id: str,
    calculator: ase.calculators,
    maxIters: int,
    fmax: float,
    fexit: float,
    conversion_factor: float,
) -> ConfEnergiesDict:
    """Minimise conformers of a single molecule using the given calculator.

    Parameters
    ----------
    mol_properties : MolPropertiesDict
        Dict of molecule to minimise and their properties.
    calculator : ase.calculators
        The ASE calculator to use for energy calculation.
    maxIters : int
        The maximum number of iterations for the minimisation.
    fmax : float
        Convergence criteria, converged when max(forces) < fmax.
    fexit : float
        Exit criteria, exit when max(forces) > fexit.
    conversion_factor: float
        Scale factor to convert energy to kcal/mol.

    Returns
    -------
    ConfEnergiesDict
        The final energy of each sucessfully converged conformer in the molecule in kcal/mol.
        {conf_id, energy}
    """
    results = []
    conf_id_and_conf_min: ConformerASEList = []

    mol: Chem.Mol = mol_properties[MOL_KEY]
    charge: int = mol_properties[CHARGE_KEY]
    spin: int = mol_properties[SPIN_KEY]

    conf_id_and_conf = rdkit_to_ase(mol)

    for conf_id, conf in conf_id_and_conf:
        conf.info = {"charge": charge, "spin": spin}
        new_conf, converged, energy = run_minimisation(conf, calculator, maxIters, fmax, fexit)
        results.append(tuple([converged, energy]))
        conf_id_and_conf_min.append(tuple([conf_id, new_conf]))

    mol = ase_to_rdkit(conf_id_and_conf_min)
    mol_properties[MOL_KEY] = mol

    energies = [E * conversion_factor for (converged, E) in remove_non_converged(mol, id, results)]
    energies = {conf.GetId(): E for conf, E in zip(mol.GetConformers(), energies)}

    return energies, mol_properties


def remove_non_converged(
    mol: Chem.Mol, id: str, results: list[tuple[int, float]]
) -> list[tuple[int, float]]:
    """Remove non-converged conformers from a molecule.

    Parameters
    ----------
    mol : Chem.Mol
        Molecule to remove non-converged conformers from.
    id : str
        ID of the molecule. Used for logging.
    results : list[tuple[int, float]]
        A binary not_converged flag and the final energy of the molecule in kcal/mol
        (i.e. 0 = converged) for each conformer.

    Results
    -------
    np.array[tuple[int, float]]
    """
    not_converged = np.array(
        [True if not_converged == 1 else False for (not_converged, _) in results]
    )
    if not_converged.sum() == 0:
        logging.debug(f"All conformers converged sucessfully for {id}")
    else:
        logging.debug(
            f"{mol.GetNumConformers() - not_converged.sum()}/{mol.GetNumConformers()} "
            f"conformers converged sucessfully for {id}"
        )
    confs_to_remove = np.array([conf.GetId() for conf in mol.GetConformers()])[not_converged]
    for conf_id in confs_to_remove:
        mol.RemoveConformer(int(conf_id))

    results = np.array(results)[~not_converged]
    return results


def run_minimisation(
    atoms: Atoms,
    calculator: Calculator,
    maxIters: int,
    fmax: float = 0.05,
    fexit: float = 250,
) -> tuple[Atoms, int, float]:
    """Run the minimisation of a single conformer using the given calculator.

    Parameters
    ----------
    atoms : ase.Atoms
        The ASE Atoms object to minimise.
    calculator : ase.calculators
        The ASE calculator to use for energy calculation.
    maxIters : int
        The maximum number of iterations for the minimisation.
    fmax : float
        Convergence criteria, converged when max(forces) < fmax.
    fexit : float
        Exit criteria, exit when max(forces) > fexit.

    Returns
    -------
    atoms : ase.Atoms
        The ASE Atoms object after minimisation.
    int
        The convergence status of the minimisation (0 = converged).
    float
        The final energy of the minimised conformer
    """
    atoms.calc = calculator
    dyn = StrainReliefBFGS(atoms)
    converged = dyn.run(fmax=fmax, fexit=fexit, steps=maxIters)
    return (
        atoms,
        int(not converged),
        atoms.get_potential_energy(),
    )  # doesn't have to recalculate energy
