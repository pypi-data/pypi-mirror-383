import numpy as np
import tuna_scf as scf
import sys, time
from tuna_util import *
from tuna_integrals import tuna_integral as ints
import tuna_postscf as postscf
import tuna_mp as mp
import tuna_cc as cc
import tuna_molecule as plot
import tuna_ci as ci
import tuna_molecule as mol







def log_convergence_acceleration(calculation, silent=False):

    """
    
    Logs information about convergence acceleration.

    Args:
        calculation (Calculation): Calculation object
        silent (bool, optional): Should anything be printed
    
    """

    DIIS = calculation.DIIS
    damping = calculation.damping
    damping_factor = calculation.damping_factor
    level_shift = calculation.level_shift


    if DIIS:

        log(f" Using DIIS, storing {calculation.max_DIIS_matrices} matrices, for convergence acceleration", calculation, silent=silent, end="")

        if damping:
            
            if damping_factor: 
                
                log(f", with static damping.", calculation, silent=silent)

            else: 
                
                log(f", with dynamic damping.", calculation, silent=silent)

        else:

            log(f".", calculation, silent=silent)
            
    else:

        if damping:
            
            if damping_factor: 

                log(f" Using static damping for convergence acceleration.", calculation, silent=silent)

            else:
                
                log(f" Using dynamic damping for convergence acceleration.", calculation, silent=silent)


    if level_shift:

        log(f" Using level shift for convergence acceleration with parameter {calculation.level_shift_parameter:.2f}.", calculation, silent=silent)

    if not DIIS and not damping and not level_shift:

        log(" No convergence acceleration used.", calculation, 1, silent=silent)


    log("", calculation, silent=silent)


    return








def calculate_extrapolated_energy(basis, E_SCF_2, E_SCF_3, E_corr_2, E_corr_3):

    """
    
    Calculates the extrapolated energy, from input energies.

    Args:
        basis (str): Basis to extrapolate
        E_SCF_2 (float): SCF Energy from double-zeta basis
        E_SCF_3 (float): SCF Energy from triple-zeta basis
        E_corr_2 (float): Correlation energy from double-zeta basis
        E_corr_3 (float): Correlation energy from triple-zeta basis
    
    Returns:
        E_extrapolated (float): Extrapolated energy
        E_SCF_extrapolated (float): Extrapolated SCF energy
        E_corr_extrapolated (float): Extrapolated correlation energy
    
    
    """

    # Values from ORCA manual
    alpha_values = {

        "CC-PVDZ" : 4.42,
        "AUG-CC-PVDZ" : 4.30,
        "PC-1": 7.02,
        "DEF2-SVP" : 10.39,
        "DEF2-SVPD" : 10.39,
        "ANO-PVDZ" : 5.41,
        "AUG-ANO-PVDZ": 5.12
    }

    beta_values = {

        "CC-PVDZ" : 2.46,
        "AUG-CC-PVDZ" : 2.51,
        "PC-1": 2.01,
        "DEF2-SVP" : 2.40,
        "DEF2-SVPD" : 2.40,
        "ANO-PVDZ" : 2.43,
        "AUG-ANO-PVDZ" : 2.41
    }

    alpha = alpha_values.get(basis)
    beta = beta_values.get(basis)

    # Same SCF extrapolation as used in ORCA
    E_SCF_extrapolated = E_SCF_2 + (E_SCF_3 - E_SCF_2) / (1 - np.exp(alpha * (np.sqrt(2) - np.sqrt(3))))

    # Same correlation energy extrapolation as used in ORCA
    E_corr_extrapolated = (2 ** beta * E_corr_2 - 3 ** beta  * E_corr_3) / (2 ** beta - 3 ** beta)

    E_extrapolated = E_SCF_extrapolated + E_corr_extrapolated

    return E_extrapolated, E_SCF_extrapolated, E_corr_extrapolated










def extrapolate_energy(calculation, atomic_symbols, coordinates, P_guess=None, P_guess_alpha=None, P_guess_beta=None, E_guess=None, silent=False, terse=False):
    
    """
    
    Calculates the extrapolated energy, from two energy calculations.

    Args:
        calculation (Calculation): Calculation object
        atomic_symbols (list): List of atomic symbols
        coordinates (array): Coordinates
        P_guess (array, optional): Guess density matrix
        P_guess_alpha (array, optional): Guess alpha density matrix
        P_guess_beta (array, optional): Guess beta density matrix
        E_guess (float, optional): Guess energy
        silent (bool, optional): Should anything be printed
        terse (bool, optional): Should properties be calculated

    Returns:
        SCF_output_2 (Output): Double-zeta SCF output
        molecule_2 (Molecule): Double-zeta Molecule object
        E_extrapolated (float): Extrapolated total energy
        P_2 (array): Double-zeta density matrix

    """

    basis_pairs = {

        "CC-PVDZ" : "CC-PVTZ",
        "AUG-CC-PVDZ" : "AUG-CC-PVTZ",
        "PC-1": "PC-2",
        "DEF2-SVP" : "DEF2-TZVPP",
        "DEF2-SVPD" : "DEF2-TZVPPD",
        "ANO-PVDZ" : "ANO-PVTZ",
        "AUG-ANO-PVDZ" : "AUG-ANO-PVTZ"
    }

    # Takes out original and secondary basis set
    first_basis = calculation.original_basis
    second_basis = basis_pairs.get(first_basis)

    if not second_basis: error(f"Basis set extrapolation is not available for \"{first_basis}\". Check the manual for compatible basis sets!")


    log(f"\nBeginning basis set extrapolation with double- and triple- zeta basis sets...", calculation, 1, silent=silent)
    log(f"Double-zeta basis is {basis_types.get(first_basis)}, triple-zeta basis is {basis_types.get(second_basis)}.", calculation, 1, silent=silent)

    log_spacer(calculation, silent=silent, start="\n")
    log(f"               Double-zeta Calculation", calculation, 1, silent=silent, colour="white")
    log_spacer(calculation, silent=silent)

    calculation.basis = first_basis

    # Calculates the energy with the first basis, using the guess densities
    SCF_output_2, molecule_2, E_total_2, P_2  = calculate_energy(calculation, atomic_symbols, coordinates, P_guess=P_guess, P_guess_alpha=P_guess_alpha, P_guess_beta=P_guess_beta, E_guess=E_guess, terse=terse, silent=silent)

    calculation.basis = second_basis

    log_spacer(calculation, silent=silent, start="\n")
    log(f"               Triple-zeta Calculation", calculation, 1, silent=silent, colour="white")
    log_spacer(calculation, silent=silent)

    # Calculates the energy with the second basis
    SCF_output_3, _, E_total_3, _  = calculate_energy(calculation, atomic_symbols, coordinates, terse=terse, silent=silent)

    E_SCF_2 = SCF_output_2.energy
    E_SCF_3 = SCF_output_3.energy

    E_corr_2 = E_total_2 - E_SCF_2
    E_corr_3 = E_total_3 - E_SCF_3

    # Extrapolates the energies
    E_extrapolated, E_SCF_extrapolated, E_corr_extrapolated = calculate_extrapolated_energy(first_basis, E_SCF_2, E_SCF_3, E_corr_2, E_corr_3)

    log_spacer(calculation, silent=silent, start="\n")
    log(f"              Basis Set Extrapolation", calculation, 1, silent=silent, colour="white")
    log_spacer(calculation, silent=silent)

    log(f"  Double-zeta SCF energy:          {E_SCF_2:16.10f}", calculation, 1, silent=silent)
    log(f"  Triple-zeta SCF energy:          {E_SCF_3:16.10f}", calculation, 1, silent=silent)

    if calculation.method not in ["RHF", "HF", "UHF"]:

        log(f"\n  Double-zeta correlation energy:  {E_corr_2:16.10f}", calculation, 1, silent=silent)
        log(f"  Triple-zeta correlation energy:  {E_corr_3:16.10f}", calculation, 1, silent=silent)

    log(f"\n  Extrapolated SCF energy:         {E_SCF_extrapolated:16.10f}", calculation, 1, silent=silent)

    if calculation.method not in ["RHF", "HF", "UHF"]:
        
        log(f"  Extrapolated correlation energy: {E_corr_extrapolated:16.10f}", calculation, 1, silent=silent)

    log(f"  Extrapolated total energy:       {E_extrapolated:16.10f}", calculation, 1, silent=silent)

    log_spacer(calculation, silent=silent)


    return SCF_output_2, molecule_2, E_extrapolated, P_2
    










def calculate_one_electron_integrals(atoms, n_basis, basis_functions, centre_of_mass):

    """"
    
    Calculates one-electron integrals.

    Args:
        atoms (list): List of atoms
        n_basis (int): Number of basis functions
        basis_functions (array): Basis functions
        centre_of_mass (float): Z-coordinate of centre of mass
    
    """

    S = np.zeros((n_basis, n_basis)) 
    V = np.zeros((n_basis, n_basis)) 
    T = np.zeros((n_basis, n_basis)) 
    M = np.zeros((3, n_basis, n_basis)) 

    for i in range(n_basis):
        for j in range(i + 1):

            S[i, j] = S[j, i] = ints.S(basis_functions[i], basis_functions[j])

            T[i, j] = T[j, i] = ints.T(basis_functions[i], basis_functions[j])

            # This only takes the z-components of the dipole (the others are always zero for diatomics)
            M[2, i, j] = M[2, j, i] = ints.Mu(basis_functions[i], basis_functions[j], np.array([0, 0, centre_of_mass]), "z")

            for atom in atoms:

                V[i, j] += -atom.charge * ints.V(basis_functions[i], basis_functions[j], atom.origin)

            V[j, i] = V[i, j]


    return S, T, V, M[2]








def calculate_two_electron_integrals(n_basis, basis_functions):

    """"
    
    Calculates two-electron integrals.

    Args:
        n_basis (int): Number of basis functions
        basis_functions (array): Basis functions
    
    """

    ERI_AO = np.zeros((n_basis, n_basis, n_basis, n_basis))  

    ERI_AO = ints.doERIs(n_basis, ERI_AO, basis_functions)
    ERI_AO = np.asarray(ERI_AO)

    return ERI_AO








def calculate_nuclear_repulsion(charges, coordinates):
    
    """

    Calculates nuclear repulsion energy.

    Args:
        charges (array): Nuclear charges
        coordinates (array): Atomic coordinates

    Returns:
        V_NN (float): Nuclear-nuclear repulsion energy

    """

    V_NN = np.prod(charges) / np.linalg.norm(coordinates[1] - coordinates[0])
    
    return V_NN
    







def calculate_Fock_transformation_matrix(S):

    """

    Diagonalises the overlap matrix to find its square root, then inverts this as X = S^-1/2.

    Args:
        S (array): Overlap matrix in AO basis

    Returns:
        X (array): Fock transformation matrix

    """

    S_vals, S_vecs = np.linalg.eigh(S)
    S_sqrt = S_vecs * np.sqrt(S_vals) @ S_vecs.T
    
    smallest_S_eigenvalue = np.min(S_vals)

    X = np.linalg.inv(S_sqrt)

    return X, smallest_S_eigenvalue








def check_S_eigenvalues(smallest_S_eigenvalue, calculation, silent=False):

    """

    Checks the smallest eigenvalue of the overlap matrix against a threshold, raising an error if it is too small.

    Args:
        smallest_S_eigenvalue (float): Smallest eigenvalue of the overlap matrix
        calculation (Calculation): Calculation object
        silent (bool, optional): Should output be printed

    """

    log(f"\n Smallest overlap matrix eigenvalue is {smallest_S_eigenvalue:.8f}, threshold is {calculation.S_eigenvalue_threshold:.8f}.", calculation, 2, silent=silent)

    if smallest_S_eigenvalue < calculation.S_eigenvalue_threshold:

        error("An overlap matrix eigenvalue is too small! Change the basis set or decrease the threshold with STHRESH.")
    
    elif smallest_S_eigenvalue < 10 * calculation.S_eigenvalue_threshold:

        warning(f"Smallest overlap matrix eigenvalue is close to the threshold, at {smallest_S_eigenvalue:.8f} \n",space=1)

    return








def rotate_molecular_orbitals(molecular_orbitals, n_occ, theta):
    
    """

    Rotates HOMO and LUMO of molecular orbitals by given angle theta to break the symmetry.

    Args:
        molecular_orbitals (array): Molecular orbital array in AO basis
        n_occ (int): Number of occupied molecular orbitals
        theta (float): Angle in radians to rotate orbitals

    Returns:
        rotated_molecular_orbitals (array): Molecular orbitals with HOMO and LUMO rotated

    """

    # Converts to radians
    theta *= np.pi / 180.0

    homo_index = n_occ - 1
    lumo_index = n_occ

    dimension = len(molecular_orbitals)
    rotation_matrix = np.eye(dimension)

    # Makes sure there is a HOMO and a LUMO to rotate, builds rotation matrix using sine and cosine of the requested angle, at the HOMO and LUMO indices
    try:
        
        rotation_matrix[homo_index:lumo_index + 1, homo_index:lumo_index + 1] = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta),  np.cos(theta)]])
    
    except: error("Basis set too small to rotate initial guess orbitals! Use a larger basis or the NOROTATE keyword.")

    # Rotates molecular orbitals with this matrix
    rotated_molecular_orbitals = molecular_orbitals @ rotation_matrix


    return rotated_molecular_orbitals






def setup_initial_guess(P_guess, P_guess_alpha, P_guess_beta, E_guess, reference, T, V_NE, X, n_doubly_occ, n_alpha, n_beta, rotate_guess_mos, no_rotate_guess_mos, calculation, silent=False):

    """

    Either calculates or passes on the guess energy and density.

    Args:
        P_guess (array): Density matrix from previous step in AO basis
        P_guess_alpha (array): Alpha density matrix from previous step in AO basis
        P_guess_beta (array): Beta density matrix from previous step in AO basis
        E_guess (float): Final energy from previous step
        reference (str): Either RHF or UHF
        T (array): Kinetic energy integral matrix in AO basis
        V_NE (array): Nuclear-electron attraction integral matrix in AO basis
        X (array): Fock transformation matrix
        n_doubly_occ (int): Number of doubly occupied orbitals
        n_alpha (int): Number of alpha electrons
        n_beta (int): Number of beta electrons
        rotate_guess_mos (bool): Force rotation of guess molecular orbitals
        no_rotate_guess_mos (bool): Force no rotation of guess molecular orbitals
        calculation (Calculation): Calculation object
        silent (bool, optional): Should output be printed

    Returns:
        E_guess (float): Guess energy
        P_guess (array): Guess density matrix in AO basis
        P_guess_alpha (array): Guess alpha density matrix in AO basis
        P_guess_beta (array): Guess beta density matrix in AO basis
        guess_epsilons (array): Guess one-electron Fock matrix eigenvalues
        guess_mos (array): Guess one-electron Fock matrix eigenvectors

    """
    
    H_core = T + V_NE

    guess_epsilons = []
    guess_mos = []

    if reference == "RHF":
        
        # If there's a guess density, just use that
        if P_guess is not None: log("\n Using density matrix from previous step for guess. \n", calculation, 1, silent=silent)

        else:
            
            log("\n Calculating one-electron density for guess...  ", calculation, end="", silent=silent); sys.stdout.flush()

            # Diagonalise core Hamiltonian for one-electron guess, then build density matrix (2 electrons per orbital) from these guess molecular orbitals
            guess_epsilons, guess_mos = scf.diagonalise_Fock_matrix(H_core, X)

                 
            P_guess = scf.construct_density_matrix(guess_mos, n_doubly_occ, 2)

            # Take lowest energy guess epsilon for guess energy
            E_guess = guess_epsilons[0]       

            log("[Done]\n", calculation, silent=silent)


    elif reference == "UHF":    

        # If there's a guess density, just use that
        if P_guess_alpha is not None and P_guess_beta is not None: log("\n Using density matrices from previous step for guess. \n", calculation, silent=silent)

        else:

            log("\n Calculating one-electron density for guess...   ", calculation, end="", silent=silent)

            # Only rotate guess MOs if there's an even number of electrons, and it hasn't been overridden by NOROTATE
            rotate_guess_mos = True if (n_alpha + n_beta) % 2 == 0 and not no_rotate_guess_mos else False

            # Diagonalise core Hamiltonian for one-electron guess
            guess_epsilons, guess_mos = scf.diagonalise_Fock_matrix(H_core, X)

            # Rotate the alpha MOs if this is requested, otherwise take the alpha guess to equal the beta guess
            guess_mos_alpha = rotate_molecular_orbitals(guess_mos, n_alpha, calculation.theta) if rotate_guess_mos else guess_mos

            # Construct density matrices (1 electron per orbital) for the alpha and beta guesses
            P_guess_alpha = scf.construct_density_matrix(guess_mos_alpha, n_alpha, 1)
            P_guess_beta = scf.construct_density_matrix(guess_mos, n_beta, 1)

            # Take lowest energy guess epsilon for guess energy
            E_guess = guess_epsilons[0]

            # Add together alpha and beta densities for total density
            P_guess = P_guess_alpha + P_guess_beta

            log("[Done]\n", calculation, silent=silent)

            if rotate_guess_mos: 
                
                log(f" Initial guess density uses molecular orbitals rotated by {(calculation.theta):.1f} degrees.\n", calculation, silent=silent)


    return E_guess, P_guess, P_guess_alpha, P_guess_beta, guess_epsilons, guess_mos






def calculate_D2_energy(atoms, bond_length):

    """

    Calculates the D2 semi-empirical dispersion energy.

    Args:
        atoms (list(Atom)): List of atoms
        bond_length (float): Distance between two atoms

    Returns:
        E_D2 (float): D2 semi-empirical dispersion energy

    """

    # These parameters were chosen to match the implementation of Hartree-Fock in ORCA
    s6 = 1.2 
    damping_factor = 20
    
    C6 = np.sqrt(atoms[0].C6 * atoms[1].C6)
    vdw_sum = atoms[0].vdw_radius + atoms[1].vdw_radius

    f_damp = 1 / (1 + np.exp(-1 * damping_factor * (bond_length / (vdw_sum) - 1)))
    
    # Uses conventional dispersion energy expression, with damping factor to account for short bond lengths
    E_D2 = -1 * s6 * C6 / (bond_length ** 6) * f_damp
    
    return E_D2
        







def calculate_one_electron_energy(method, reference, basis_functions, atoms, n_basis, centre_of_mass, calculation, silent=False):

    """

    Calculates the energy of a one-electron system.

    Args:
        method (str): Electronic structure method
        reference (str): Either UHF or RHF
        atomic_orbitals (array): Atomic orbitals
        charges (list): Nuclear charges
        coordinates (array): Atomic coordinates in 3D
        centre_of_mass (float): Distance from first atom of centre of mass
        calculation (Calculation): Calculation object
        silent (bool, optional): Should anything be printed

    Returns:
        E (float): One-electron energy
        P (array): One-electron density matrix in AO basis
        epsilons (array): Energy levels of one-electron system
        molecular_orbitals (array): Molecular orbitals of one-electron system in AO basis
        D (array): Dipole integral matrix
        S (array): Overlap matrix
        ERI_AO (array): Electron repulsion integrals in AO basis
        T (array): Kinetic energy matrix in AO basis
        V_NE (array): Nuclear-electron matrix in AO basis

    """

    if method not in ["HF", "RHF", "UHF", "CIS", "UCIS", "CIS[D]", "UCIS[D]"]: error("A correlated calculation has been requested on a one-electron system!")
    elif method in ["CIS", "UCIS", "CIS[D]", "UCIS[D]"]: error("An excited state calculation has been requested on a one-electron system!")

    # Calculates one-electron integrals
    log(" Calculating one-electron integrals...       ", calculation, 1, end="", silent=silent); sys.stdout.flush()

    S, T, V_NE, D = calculate_one_electron_integrals(atoms, n_basis, basis_functions, centre_of_mass)

    log("[Done]", calculation, 1, silent=silent)
 
    ERI_AO = np.zeros((n_basis, n_basis, n_basis, n_basis))
    
    # Calculates Fock transformation matrix from overlap matrix
    log(" Constructing Fock transformation matrix...  ", calculation, 1, end="", silent=silent)
    
    X, smallest_S_eigenvalue = calculate_Fock_transformation_matrix(S)
    
    log("[Done]", calculation, 1, silent=silent)

    check_S_eigenvalues(smallest_S_eigenvalue, calculation, silent=silent)

    # Builds initial guess, which is the final answer for the one-electron case
    E, P, P_alpha, P_beta, epsilons, molecular_orbitals = setup_initial_guess(None, None, None, None, reference, T, V_NE, X, 1, 1, 0, calculation.rotate_guess, calculation.no_rotate_guess, calculation, silent=silent)

    return E, P, epsilons, molecular_orbitals, D, S, ERI_AO, T, V_NE









def calculate_energy(calculation, atomic_symbols, coordinates, P_guess=None, P_guess_alpha=None, P_guess_beta=None, E_guess=None, terse=False, silent=False):
 


    log("\n Setting up molecule...  ", calculation, 1, end="", silent=silent); sys.stdout.flush()

    # Builds molecule object using calculation and atomic parameters
    molecule = mol.Molecule(atomic_symbols, coordinates, calculation)
    
    # Unpacking of various useful calculation quantities
    method = calculation.method
    reference = calculation.reference

    # Unpacking of various useful molecular properties
    atomic_symbols = molecule.atomic_symbols
    atoms = molecule.atoms
    charges = molecule.charges
    n_basis = molecule.n_basis
    basis_functions = molecule.basis_functions
    coordinates = molecule.coordinates
    bond_length = molecule.bond_length
    centre_of_mass = molecule.centre_of_mass
    n_doubly_occ = molecule.n_doubly_occ
    n_occ = molecule.n_occ
    n_SO = molecule.n_SO
    n_virt = molecule.n_virt
    n_electrons = molecule.n_electrons
    n_alpha = molecule.n_alpha
    n_beta = molecule.n_beta


    if reference == "RHF":

        n_occ_print = n_occ // 2
        n_virt_print = n_virt // 2

    else:

        n_occ_print = n_occ
        n_virt_print = n_virt


    log("[Done]\n", calculation, 1, silent=silent)

    log(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", calculation, 1, silent=silent)
    log("    Molecule and Basis Information", calculation, 1, silent=silent, colour="white")
    log(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", calculation, 1, silent=silent)
    log("  Molecular structure: " + molecule.molecular_structure, calculation, 1, silent=silent)
    log("\n  Number of basis functions: " + str(len(basis_functions)), calculation, 1, silent=silent)
    log("  Number of primitive Gaussians: " + str(np.sum(molecule.primitive_Gaussians)), calculation, 1, silent=silent)
    log("\n  Charge: " + str(molecule.charge), calculation, 1, silent=silent)
    log("  Multiplicity: " + str(molecule.multiplicity), calculation, 1, silent=silent)
    log("  Number of electrons: " + str(n_electrons), calculation, 1, silent=silent)
    log("  Number of alpha electrons: " + str(n_alpha), calculation, 1, silent=silent)
    log("  Number of beta electrons: " + str(n_beta), calculation, 1, silent=silent)
    log("  Number of occupied orbitals: " + str(n_occ_print), calculation, 1, silent=silent)
    log("  Number of virtual orbitals: " + str(n_virt_print), calculation, 1, silent=silent)
    log(f"\n  Point group: {molecule.point_group}", calculation, 1, silent=silent)
    if len(atomic_symbols) == 2: log(f"  Bond length: {bohr_to_angstrom(bond_length):.5f} ", calculation, 1, silent=silent)

    for atom in atoms:

        if len(atoms) == 2 and atoms[0].basis_charge == atoms[1].basis_charge and atom == atoms[1]: break

        log(f"\n  Basis set for {atom.symbol_formatted} :\n", calculation, 3, silent=silent)

        values = molecule.basis_data[atom.basis_charge]

        for orbital, params in values:

            log(f"   {orbital}", calculation, 3, silent=silent)

            for exponent, coefficient in params:

                log(f"      {exponent:15.7f}     {coefficient:10.7f}", calculation, 3, silent=silent)

    log(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", calculation, 1, silent=silent)




    # Nuclear repulsion and dispersion energy are only calculated if there are two real atoms present
    if len(atomic_symbols) == 2 and not any(atom.ghost for atom in atoms):

        #Calculates nuclear repulsion energy
        log(" Calculating nuclear repulsion energy...  ", calculation, 1, end="", silent=silent)

        V_NN = calculate_nuclear_repulsion(charges, coordinates)

        log(f"[Done]\n\n Nuclear repulsion energy: {V_NN:.10f}\n", calculation, 1, silent=silent)
        
        # Calculates D2 dispersion energy if requested
        if calculation.D2:  

            log(" Calculating semi-empirical dispersion energy...  ", calculation, 1, end="", silent=silent)

            E_D2 = calculate_D2_energy(atoms, bond_length)

            log(f"[Done]\n\n Dispersion energy (D2): {E_D2:.10f}\n", calculation, 1, silent=silent)
            
        else: E_D2 = 0
        
    else: V_NN = 0; E_D2 = 0
        

    if n_electrons < 0: error("Negative number of electrons specified!")

    elif n_electrons == 0: error("Zero electrons specified!")


    elif n_electrons == 1: 

        log(" Beginning Hartree-Fock calculation...  \n", calculation, 1, silent=silent)

        # Calculates the one-electron energy, exact within the basis set
        E, P, epsilons, molecular_orbitals, D, S, ERI_AO, T, V_NE = calculate_one_electron_energy(method, reference, basis_functions, atoms, n_basis, centre_of_mass, calculation, silent=silent)

        J = np.einsum('ijkl,kl->ij', ERI_AO, P, optimize=True)
        K = np.einsum('ilkj,kl->ij', ERI_AO, P, optimize=True)

        final_energy = E + V_NN
        P_alpha = P / 2
        P_beta = P / 2

        kinetic_energy, nuclear_electron_energy, coulomb_energy, exchange_energy = scf.calculate_energy_components(P_alpha, P_beta, T, V_NE, None, None, None, None, P, J, K, "RHF")
        if not silent: postscf.print_energy_components(nuclear_electron_energy, kinetic_energy, exchange_energy, coulomb_energy, V_NN, calculation)

        # Builds energy output object with all the calculated quantities from the one-electron guess
        SCF_output = Output(final_energy, S, P, P_alpha, P_beta, molecular_orbitals, molecular_orbitals, None, epsilons, epsilons, None, kinetic_energy, nuclear_electron_energy, coulomb_energy, exchange_energy)

        # No beta electrons for the one-electron case exists
        epsilons_alpha = epsilons
        epsilons_beta = None
        molecular_orbitals_alpha = molecular_orbitals
        molecular_orbitals_beta = None
        
        SCF_output.D = D


    elif n_electrons > 1:

        if reference == "RHF": log(" Beginning restricted Hartree-Fock calculation...  \n", calculation, 1, silent=silent)
        else: log(" Beginning unrestricted Hartree-Fock calculation...  \n", calculation, 1, silent=silent)

        log(" Calculating one-electron integrals...  ", calculation, 1, end="", silent=silent); sys.stdout.flush()
   
        S, T, V_NE, D = calculate_one_electron_integrals(atoms, n_basis, basis_functions, centre_of_mass)

        log("[Done]", calculation, 1, silent=silent)

        log(" Calculating two-electron integrals...  ", calculation, 1, end="", silent=silent); sys.stdout.flush()

        try:

            ERI_AO = calculate_two_electron_integrals(n_basis, basis_functions)

        except np._core._exceptions._ArrayMemoryError:

            error("Not enough memory to build two-electron integrals array! Uh oh!")
        
        log("[Done]", calculation, 1, silent=silent)

        calculation.integrals_time = time.perf_counter()
        log(f"\n Time taken for integrals:  {calculation.integrals_time - calculation.start_time:.2f} seconds", calculation, 3, silent=silent)


        # Calculates Fock transformation matrix from overlap matrix
        log("\n Constructing Fock transformation matrix...  ", calculation, 1, end="", silent=silent); sys.stdout.flush()

        X, smallest_S_eigenvalue = calculate_Fock_transformation_matrix(S)

        log("[Done]", calculation, 1, silent=silent)

        check_S_eigenvalues(smallest_S_eigenvalue, calculation, silent=silent)

        # Calculates one-electron density for initial guess
        E_guess, P_guess, P_guess_alpha, P_guess_beta, _, _ = setup_initial_guess(P_guess, P_guess_alpha, P_guess_beta, E_guess, reference, T, V_NE, X, n_doubly_occ, n_alpha, n_beta, calculation.rotate_guess, calculation.no_rotate_guess, calculation, silent=silent)

        log(" Beginning self-consistent field cycle...\n", calculation, 1, silent=silent)

        # Prints convergence criteria specified
        log(f" Using \"{calculation.SCF_conv["name"]}\" SCF convergence criteria.", calculation, 1, silent=silent)

        # Prints the chosen SCF convergence acceleration options
        log_convergence_acceleration(calculation, silent=silent)

        # Starts SCF cycle for two-electron energy
        SCF_output = scf.run_SCF(molecule, calculation, T, V_NE, ERI_AO, V_NN, S, X, E_guess, P=P_guess, P_alpha=P_guess_alpha, P_beta=P_guess_beta, silent=silent)
        
        calculation.SCF_time = time.perf_counter()
        log(f" Time taken for SCF iterations:  {calculation.SCF_time - calculation.integrals_time:.2f} seconds\n", calculation, 3, silent=silent)

        # Extracts useful quantities from SCF output object
        molecular_orbitals = SCF_output.molecular_orbitals
        molecular_orbitals_alpha = SCF_output.molecular_orbitals_alpha  

        molecular_orbitals_beta = SCF_output.molecular_orbitals_beta   
        epsilons = SCF_output.epsilons
        epsilons_alpha = SCF_output.epsilons_alpha
        epsilons_beta = SCF_output.epsilons_beta
        P = SCF_output.P
        P_alpha = SCF_output.P_alpha
        P_beta = SCF_output.P_beta
        final_energy = SCF_output.energy
        kinetic_energy = SCF_output.kinetic_energy
        nuclear_electron_energy = SCF_output.nuclear_electron_energy
        coulomb_energy = SCF_output.coulomb_energy
        exchange_energy = SCF_output.exchange_energy

        # Packs dipole integrals into SCF output object
        SCF_output.D = D


        if reference == "UHF": 
            
            # Calculates UHF spin contamination and prints to the console
            postscf.calculate_spin_contamination(P_alpha, P_beta, n_alpha, n_beta, S, calculation, reference, silent=silent)

            if calculation.natural_orbitals and not calculation.no_natural_orbitals: 
                    
                mp.calculate_natural_orbitals(P, X, calculation, silent=silent)
                log(" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n", calculation, 1, silent=silent)


        if not silent: 

            # Prints the individual components of the total SCF energy
            postscf.print_energy_components(nuclear_electron_energy, kinetic_energy, exchange_energy, coulomb_energy, V_NN, calculation)

        # If a Moller-Plesset calculation is requested, calculates the energy and density matrices
        if "MP" in method: 

            E_MP2, E_MP3, E_MP4, P, P_alpha, P_beta = mp.calculate_Moller_Plesset(method, molecule, SCF_output, ERI_AO, calculation, X, T + V_NE, V_NN, silent=silent)
            postscf.calculate_spin_contamination(P_alpha, P_beta, n_alpha, n_beta, S, calculation, "MP2", silent=silent)

        # If a coupled-cluster calculation is requested, calculates the energy
        elif "CC" in method or "CEPA" in method or "QCISD" in method:

            E_CC, E_CCSD_T, P, P_alpha, P_beta = cc.begin_coupled_cluster_calculation(method, molecule, SCF_output, ERI_AO, X, T + V_NE, calculation, silent=silent)
            
            postscf.calculate_spin_contamination(P_alpha, P_beta, n_alpha, n_beta, S, calculation, "Coupled cluster", silent=silent)

        if method in correlated_methods:

            calculation.correlation_time = time.perf_counter()
            log(f"\n Time taken for correlated calculation:  {calculation.correlation_time - calculation.SCF_time:.2f} seconds", calculation, 3, silent=silent)



    # Prints post SCF information, as long as its not an optimisation that hasn't finished yet
    if not terse and not silent:
        
        postscf.post_SCF_output(molecule, calculation, epsilons, molecular_orbitals, P, S, molecule.partition_ranges, D, P_alpha, P_beta, epsilons_alpha, epsilons_beta, molecular_orbitals_alpha, molecular_orbitals_beta)
    
    if method in ["CIS", "UCIS", "CIS[D]", "UCIS[D]"]:

        log("\n\n Beginning excited state calculation...", calculation, 1, silent=silent)

        if n_virt <= 0: error("Excited state calculation requested on system with no virtual orbitals!")


        E_CIS, E_transition, P, P_alpha, P_beta = ci.run_CIS(ERI_AO, n_occ, n_virt, n_SO, calculation, SCF_output, molecule, silent=silent)
        
        calculation.excited_state_time = time.perf_counter()
        log(f"\n Time taken for excited state calculation:  {calculation.excited_state_time - calculation.SCF_time:.2f} seconds", calculation, 3, silent=silent)

        if calculation.additional_print: 
           
           # Optionally uses CIS density for dipole moment and population analysis
           postscf.post_SCF_output(molecule, calculation, epsilons, molecular_orbitals, P, S, molecule.partition_ranges, D, P_alpha, P_beta, epsilons_alpha, epsilons_beta, molecular_orbitals_alpha, molecular_orbitals_beta)

    # Prints Hartree-Fock energy
    if reference == "RHF": log("\n Restricted Hartree-Fock energy:   " + f"{final_energy:16.10f}", calculation, 1, silent=silent)
    else: log("\n Unrestricted Hartree-Fock energy: " + f"{final_energy:16.10f}", calculation, 1, silent=silent)



    # Adds up and prints MP2 energies
    if method in ["MP2", "SCS-MP2", "UMP2", "USCS-MP2", "OMP2", "UOMP2", "OOMP2", "UOOMP2"]: 
        
        space = " " * max(0, 8 - len(method))

        final_energy += E_MP2

        log(f" Correlation energy from {method}: {space}" + f"{E_MP2:16.10f}\n", calculation, 1, silent=silent)


    # Adds up and prints MP3 energies
    elif method in ["MP3", "UMP3", "SCS-MP3", "USCS-MP3"]:
        
        final_energy += E_MP2 + E_MP3

        if method == "SCS-MP3":

            log(f" Correlation energy from SCS-MP2:  " + f"{E_MP2:16.10f}", calculation, 1, silent=silent)
            log(f" Correlation energy from SCS-MP3:  " + f"{E_MP3:16.10f}\n", calculation, 1, silent=silent)

        else:

            log(f" Correlation energy from MP2:      " + f"{E_MP2:16.10f}", calculation, 1, silent=silent)
            log(f" Correlation energy from MP3:      " + f"{E_MP3:16.10f}\n", calculation, 1, silent=silent)


    elif method in ["MP4", "MP4[SDQ]", "MP4[DQ]", "MP4[SDTQ]"]:
        
        final_energy += E_MP2 + E_MP3 + E_MP4

        log(f" Correlation energy from MP2:      " + f"{E_MP2:16.10f}", calculation, 1, silent=silent)
        log(f" Correlation energy from MP3:      " + f"{E_MP3:16.10f}", calculation, 1, silent=silent)

        if method == "MP4" or method == "MP4[SDTQ]":

            log(f" Correlation energy from MP4:      " + f"{E_MP4:16.10f}\n", calculation, 1, silent=silent)

        elif method == "MP4[SDQ]":

            log(f" Correlation energy from MP4(SDQ): " + f"{E_MP4:16.10f}\n", calculation, 1, silent=silent)

        elif method == "MP4[DQ]":

            log(f" Correlation energy from MP4(DQ):  " + f"{E_MP4:16.10f}\n", calculation, 1, silent=silent)
 



    elif "CC" in method or "CEPA" in method or "QC" in method:

        final_energy += E_CC + E_CCSD_T


        if "CCSD[T]" in method:

            log(f" Correlation energy from CCSD:     " + f"{E_CC:16.10f}", calculation, 1, silent=silent)
            log(f" Correlation energy from CCSD(T):  " + f"{E_CCSD_T:16.10f}\n", calculation, 1, silent=silent)
        
        elif "QCISD[T]" in method:

            log(f" Correlation energy from QCISD:    " + f"{E_CC:16.10f}", calculation, 1, silent=silent)
            log(f" Correlation energy from QCISD(T): " + f"{E_CCSD_T:16.10f}\n", calculation, 1, silent=silent)

        else:
            
            space = " " * max(0, 8 - len(method))

            log(f" Correlation energy from {method}:{space} " + f"{E_CC:16.10f}\n", calculation, 1, silent=silent)



    # Prints CIS energy of state of interest
    elif method in excited_state_methods:

        final_energy = E_CIS

        method = method.replace("[", "(").replace("]", ")")
        space = " " * max(0, 8 - len(method))

        log(f"\n Excitation energy is the energy difference to excited state {calculation.root}.", calculation, 1, silent=silent)
        
        log(f"\n Excitation energy from {method}:  {space}" + f"{E_transition:16.10f}", calculation, 1, silent=silent)
    
    
    log(" Final single point energy:        " + f"{final_energy:16.10f}", calculation, 1, silent=silent)

    # Adds on D2 energy, and prints this as dispersion-corrected final energy
    if calculation.D2:
    
        final_energy += E_D2

        log("\n Semi-empirical dispersion energy: " + f"{E_D2:16.10f}", calculation, 1, silent=silent)
        log(" Dispersion-corrected final energy:" + f"{final_energy:16.10f}", calculation, 1, silent=silent)
    


    return SCF_output, molecule, final_energy, P


    





def scan_coordinate(calculation, atomic_symbols, starting_coordinates):

    """

    Loops through a number of scan steps and increments bond length, calculating enery each time.

    Args:
        calculation (Calculation): Calculation object
        atomic_symbols (list): List of atomic symbols
        starting_coordinates (array): Atomic coordinates to being coordinate scan calculation in 3D

    Returns:
        None: Nothing is returned

    """

    coordinates = starting_coordinates
    bond_length = np.linalg.norm(coordinates[1] - coordinates[0])

    # Unpacks useful quantities
    number_of_steps = calculation.scan_number
    step_size = angstrom_to_bohr(calculation.scan_step)

    log(f"Initialising a {number_of_steps} step coordinate scan in {step_size:.4f} angstrom increments.", calculation, 1) 
    log(f"Starting at a bond length of {bohr_to_angstrom(bond_length):.4f} angstroms.\n", calculation, 1)
    
    bond_lengths = [] 
    energies = []   
    
    P_guess = None
    E_guess = None 
    P_guess_alpha = None 
    P_guess_beta = None


    for step in range(1, number_of_steps + 1):
        
        bond_length = np.linalg.norm(coordinates[1] - coordinates[0])

        log_big_spacer(calculation, start="\n",space="")
        log(f"Starting scan step {step} of {number_of_steps} with bond length of {bohr_to_angstrom(bond_length):.5f} angstroms...", calculation, 1)
        log_big_spacer(calculation,space="")
        
        #Calculates the energy at the coordinates (in bohr) specified
        if calculation.extrapolate:

            SCF_output, _, energy, _ = extrapolate_energy(calculation, atomic_symbols, coordinates, P_guess, P_guess_alpha, P_guess_beta, E_guess, terse=True)

        else:
            
            SCF_output, _, energy, _  = calculate_energy(calculation, atomic_symbols, coordinates, P_guess, P_guess_alpha, P_guess_beta, E_guess, terse=True)


        #If MOREAD keyword is used, then the energy and densities are used for the next calculation
        if calculation.MO_read: 
            
            P_guess = SCF_output.P
            E_guess = energy 
            P_guess_alpha = SCF_output.P_alpha 
            P_guess_beta = SCF_output.P_beta

        # Appends energies and bond lengths to lists
        energies.append(energy)
        bond_lengths.append(bond_length)

        # Builds new coordinates by adding step size on
        coordinates = np.array([coordinates[0], [0, 0, bond_length + step_size]])
        
    log_big_spacer(calculation, start="\n",space="")    
    
    log("\nCoordinate scan calculation finished!\n\n Printing energy as a function of bond length...\n", calculation, 1)
    log_spacer(calculation)
    log("                    Coordinate Scan", calculation, 1, colour="white")
    log_spacer(calculation)
    log("  Step         Bond Length               Energy", calculation, 1)
    log_spacer(calculation)

    # Prints a table of bond lengths and corresponding energies
    for i, (energy, bond_length) in enumerate(zip(energies, bond_lengths)):
        
        step = i + 1

        log(f" {step:4.0f}            {bohr_to_angstrom(bond_length):.5f}             {energy:13.10f}", calculation, 1)

    log_spacer(calculation)
    
    # If SCANPLOT keyword is used, plots and shows a matplotlib graph of the data
    if calculation.scan_plot: 
        
        plot.scan_plot(calculation, bohr_to_angstrom(np.array(bond_lengths)), energies)

