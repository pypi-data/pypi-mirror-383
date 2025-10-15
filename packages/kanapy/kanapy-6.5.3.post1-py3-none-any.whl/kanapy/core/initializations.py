"""
Classes for RVE and mesh initialization

Authors: Mahesh Prassad, Abhishek Biswas, Alexander Hartmaier
Ruhr University Bochum, Germany

March 2024
"""
import json
import os
import numpy as np
import logging
import itertools
from scipy.stats import lognorm, vonmises
from collections import defaultdict


def stat_names(legacy=False):
    if legacy:
        sig = 'std'
        loc = 'offs'
        scale = 'mean'
        kappa = 'kappa'
    else:
        sig = 'sig'
        loc = 'loc'
        scale = 'scale'
        kappa = 'kappa'
    return sig, loc, scale, kappa


class RVE_creator(object):
    r"""
    Creates an RVE based on user-defined statistics

    .. note:: 1. Input parameters provided by the user in the input file are:

                * Standard deviation for ellipsoid equivalent diameter (Log-normal distribution)
                * Mean value of ellipsoid equivalent diameter (Log-normal distribution)
                * Minimum and Maximum cut-offs for ellipsoid equivalent diameters
                * Mean value for aspect ratio
                * Mean value for ellipsoid tilt angles (Normal distribution)
                * Standard deviation for ellipsoid tilt angles (Normal distribution)
                * Side dimension of the RVE
                * Discretization along the RVE sides

              2. Particle, RVE and simulation data are written as JSON files in a folder in the current
                 working directory for later access.

                * Ellipsoid attributes such as Major, Minor, Equivalent diameters and its tilt angle.
                * RVE attributes such as RVE (Simulation domain) size, the number of voxels and the voxel resolution.
                * Simulation attributes such as periodicity and output unit scale (:math:`mm`
                  or :math:`\mu m`) for ABAQUS .inp file.

    Generates ellipsoid size distribution (Log-normal) based on user-defined statistics

    .. note:: 1. Input parameters provided by the user in the input file are:

                * Standard deviation for ellipsoid equivalent diameter (Normal distribution)
                * Mean value of ellipsoid equivalent diameter (Normal distribution)
                * Minimum and Maximum cut-offs for ellipsoid equivalent diameters
                * Mean value for aspect ratio
                * Mean value for ellipsoid tilt angles (Normal distribution)
                * Standard deviation for ellipsoid tilt angles (Normal distribution)
                * Side dimension of the RVE
                * Discretization along the RVE sides

              2. Particle, RVE and simulation data are written as JSON files in a folder in the current
                 working directory for later access.

                * Ellipsoid attributes such as Major, Minor, Equivalent diameters and its tilt angle.
                * RVE attributes such as RVE (Simulation domain) size, the number of voxels and the voxel resolution.
                * Simulation attributes such as periodicity and output unit scale (:math:`mm`
                  or :math:`\mu m`) for ABAQUS .inp file.

    """

    def __init__(self, stats_dicts, nsteps=1000, from_voxels=False, poly=None):
        """
        Create an RVE object.

        Parameters
        ----------
        stats_dicts
        nsteps
        from_voxels
        poly

        Attributes
        ----------
        packing_steps = nsteps  # max number of steps for packing simulation
        size = None  #  tuple of lengths along Cartesian axes
        dim = None  # tuple of number of voxels along Cartesian axes
        periodic = None  # Boolean for periodicity of RVE
        units = None  # Units of RVE dimensions, either "mm" or "um" (micron)
        nparticles = []  # list of particle numbers for each phase
        particle_data = []  # list of cits for statistical particle data for each grains
        phase_names = []  # list of names of phases
        phase_vf = []  # list of volume fractions of phases
        ialloy : int
            Number of alloy in ICAMS CP-UMAT
        """

        def init_particles(ip):
            """
            Extract statistical microstructure information from data dictionary
            and initalize particles for packing accordingly
            """

            def gen_data_basic(pdict):
                """Computes number of particles according to equivalent diameter distribution
                   and initializes particle ensemble with individual diameters approximating
                   this lognormal distribution.
                """
                # Compute the Log-normal CDF according to parameters for equiv. diameter distrib.
                xaxis = np.linspace(0.1, 200, 1000)
                ycdf = lognorm.cdf(xaxis, s=sig_ED, loc=loc_ED, scale=scale_ED)

                # Get the mean value for each pair of neighboring points as centers of bins
                xaxis = np.vstack([xaxis[1:], xaxis[:-1]]).mean(axis=0)

                # Based on the cutoff specified, get the restricted distribution
                index_array = np.where((xaxis >= dia_cutoff_min) & (xaxis <= dia_cutoff_max))
                eq_Dia = xaxis[index_array]  # Selected diameters within the cutoff

                # Compute the number fractions and extract them based on the cut-off
                number_fraction = np.ediff1d(ycdf)  # better use lognorm.pdf
                numFra_Dia = number_fraction[index_array]

                # Volume of each ellipsoid
                volume_array = (4 / 3) * np.pi * (0.5 * eq_Dia) ** 3

                # Volume fraction for each ellipsoid
                individualK = np.multiply(numFra_Dia, volume_array)
                K = individualK / np.sum(individualK)

                # Total number of ellipsoids for packing density given by volume fraction
                ip = pdict['Phase']
                num_f = np.divide(K * phase_vf[ip] * np.prod(self.size), volume_array)
                """print(f'Particle numbers: {num_f}')
                print(f'Total volume of particles: {np.sum(np.multiply(num_f, volume_array))}')"""
                # Rounding particle numbers to integer values keeping total volume constant
                num = np.zeros(len(num_f), dtype=int)
                rest = 0.0
                for i, val in enumerate(num_f):
                    v1 = np.rint(val).astype(int)
                    rest += v1 - val
                    if abs(rest) > 1.0:
                        sr = np.sign(rest).astype(int)
                        rest -= sr
                        v1 -= sr
                    num[i] = v1
                """print(f'Volume after rounding: {np.sum(np.multiply(num, volume_array))}')
                print(f'Particle numbers: {num}')
                print(f'Phase volume fraction: {phase_vf[ip]}')"""
                totalEllipsoids = int(np.sum(num))

                # Duplicate the diameter values
                eq_Dia = np.repeat(eq_Dia, num)

                # Raise value error in case the RVE side length is too small to fit grains inside.
                if len(eq_Dia) == 0:
                    raise ValueError(
                        'RVE volume too small to fit grains inside, please increase the RVE side length (or) ' +
                        'decrease the mean size for diameters!')

                # Voxel resolution : Smallest dimension of the smallest ellipsoid should contain at least 3 voxels
                voxel_size = np.divide(self.size, self.dim)

                # raise value error if voxel sizes along the 3 directions are not equal
                dif1 = np.abs(voxel_size[0] - voxel_size[1])
                dif2 = np.abs(voxel_size[1] - voxel_size[2])
                dif3 = np.abs(voxel_size[2] - voxel_size[0])
                if (dif1 > 1.e-5) or (dif2 > 1.e-5) or (dif3 > 1.e-5):
                    raise ValueError('Voxels are not cubic, voxel sizes must be identical in all directions.')

                # raise value error in case the grains are not voxelated well
                if voxel_size[0] >= np.amin(eq_Dia) / 3.:
                    logging.warning(" ")
                    logging.warning(f"    Grains with minimum size {np.amin(eq_Dia)} will not be voxelated well!")
                    logging.warning(f"    Voxel size is {voxel_size[0]}")
                    logging.warning("    Consider increasing the voxel numbers (OR) decreasing the RVE side lengths\n")
                    if voxel_size[0] > np.amin(eq_Dia):
                        raise ValueError(' Voxel size larger than minimum grain size.')

                # raise warning if large grain occur in periodic box
                if np.amax(eq_Dia) >= self.size[0] * 0.5 and self.periodic:
                    logging.warning("\n")
                    logging.warning("    Periodic box with grains larger than half of box width.")
                    logging.warning("    Check grain RVE carefully.")

                print(f'    Analyzed statistical data for phase {phase_names[-1]} ({ip})')
                print(f'    Total number of particles  = {totalEllipsoids}')
                pdict['Number'] = totalEllipsoids
                pdict['Equivalent_diameter'] = list(eq_Dia)
                return pdict

            def gen_data_elong(pdict):
                # Tilt angle statistics
                # Sample from Normal distribution: It takes mean and std of normal distribution
                tilt_angle = []
                num = pdict['Number']
                iter = 0
                while num > 0:
                    tilt = vonmises.rvs(kappa, loc=loc_ori, size=num)
                    index_array = np.where((tilt >= ori_cutoff_min) & (tilt <= ori_cutoff_max))
                    TA = tilt[index_array].tolist()
                    tilt_angle.extend(TA)
                    num = pdict['Number'] - len(tilt_angle)
                    iter += 1
                    if iter > 10000:
                        raise StopIteration('Iteration for tilt angles did not converge in 10000 iterations.'
                                            'Increase cutoff range to assure proper generation of particles.')

                # Aspect ratio statistics
                # Sample from lognormal or gamma distribution:
                # it takes mean, std and scale of the underlying normal distribution
                finalAR = []
                num = pdict['Number']
                iter = 0
                while num > 0:
                    ar = lognorm.rvs(sig_AR, loc=loc_AR, scale=scale_AR, size=num)
                    index_array = np.where((ar >= ar_cutoff_min) & (ar <= ar_cutoff_max))
                    AR = ar[index_array].tolist()
                    finalAR.extend(AR)
                    num = pdict['Number'] - len(finalAR)
                    iter += 1
                    if iter > 10000:
                        raise StopIteration('Iteration for aspect ratios did not converge in 10000 iterations.'
                                            'Increase cutoff range to assure proper generation of particles.')
                finalAR = np.array(finalAR)

                # Calculate the major, minor axes lengths for particles using:
                # (4/3)*pi*(r**3) = (4/3)*pi*(a*b*c) & b=c & a=AR*b
                minDia = pdict['Equivalent_diameter'] / finalAR ** (1 / 3)  # Minor axis length
                majDia = minDia * finalAR  # Major axis length
                minDia2 = minDia.copy()  # Minor2 axis length (assuming rotational shape)

                # Add data to dictionary to store the data generated
                pdict['Major_diameter'] = list(majDia)
                pdict['Minor_diameter1'] = list(minDia)
                pdict['Minor_diameter2'] = list(minDia2)
                pdict['Tilt angle'] = list(tilt_angle)
                return pdict

            # start of particle initialization
            # analyze information on grains in "stats" dictionary from outer scope
            # 1. Attributes for equivalent diameter
            if 'mean' in stats['Equivalent diameter'].keys():
                # load legacy names to ensure compatibility with previous versions
                sig, loc, scale, kappa = stat_names(legacy=True)
                logging.warning('Keys for descriptor parameters have changed.\n' +
                                'Please exchange std->sig, offs->loc, mean->scale')
            else:
                sig, loc, scale, kappa = stat_names(legacy=False)
            sig_ED = stats["Equivalent diameter"][sig]
            scale_ED = stats["Equivalent diameter"][scale]
            if loc in stats["Equivalent diameter"].keys():
                loc_ED = stats["Equivalent diameter"][loc]
            else:
                loc_ED = 0.0

            dia_cutoff_min = stats["Equivalent diameter"]["cutoff_min"]
            dia_cutoff_max = stats["Equivalent diameter"]["cutoff_max"]
            if dia_cutoff_min / dia_cutoff_max > 0.75:
                raise ValueError('Min/Max values for cutoffs of equiavalent diameter are too close: ' +
                                 f'Max: {dia_cutoff_max}, Min: {dia_cutoff_min}')
            # generate dict for basic particle data: number of particles and equiv. diameters
            pdict = gen_data_basic(dict({'Type': stats["Grain type"], 'Phase': ip}))

            # 2. Additional attributes for elongated or freely-defined grains
            if stats["Grain type"] == "Elongated":
                # Extract descriptors for aspect ratio distrib. from dict
                sig_AR = stats["Aspect ratio"][sig]
                scale_AR = stats["Aspect ratio"][scale]
                if loc in stats["Aspect ratio"].keys():
                    loc_AR = stats["Aspect ratio"][loc]
                else:
                    loc_AR = 0.0
                ar_cutoff_min = stats["Aspect ratio"]["cutoff_min"]
                ar_cutoff_max = stats["Aspect ratio"]["cutoff_max"]
                if ar_cutoff_min / ar_cutoff_max > 0.75:
                    raise ValueError('Min/Max values for cutoffs of aspect ratio are too close: ' +
                                     f'Max: {ar_cutoff_max}, Min: {ar_cutoff_min}')

                # Extract grain tilt angle statistics info from dict
                kappa = stats["Tilt angle"][kappa]
                loc_ori = stats["Tilt angle"][loc]
                ori_cutoff_min = stats["Tilt angle"]["cutoff_min"]
                ori_cutoff_max = stats["Tilt angle"]["cutoff_max"]
                if ori_cutoff_min / ori_cutoff_max > 0.75:
                    raise ValueError('Min/Max values for cutoffs of orientation of tilt axis are too close: ' +
                                     f'Max: {ori_cutoff_max}, Min: {ori_cutoff_min}')
                # Add attributes for elongated particle to dictionary
                pdict = gen_data_elong(pdict)
            elif stats["Grain type"] == "Free":
                try:
                    from kanapy.triple_surface import gen_data_free
                except:
                    raise ModuleNotFoundError('Free grain definitions are not available '
                                              'in the public version of Kanapy.')
                # Add attributes for elongated particle to dictionary
                pdict = gen_data_free(pdict, stats)
                return pdict
            return pdict

        # Start RVE generation
        if from_voxels:
            print('Creating an RVE from voxel input')
        else:
            print('Creating an RVE based on user defined statistics')
        # declare attributes of RVE object
        self.packing_steps = nsteps  # max number of steps for packing simulation
        self.size = None  # tuple of lengths along Cartesian axes
        self.dim = None  # tuple of number of voxels along Cartesian axes
        self.periodic = None  # Boolean for periodicity of RVE
        self.units = None  # Units of RVE dimensions, either "mm" or "um" (micron)
        self.ialloy = None  # Number of alloy in ICAMS CP-UMAT
        phase_names = []  # list of names of phases
        phase_vf = []  # list of volume fractions of phases
        ialloy = []
        if from_voxels:
            self.particle_data = None
            self.nparticles = None
        else:
            self.particle_data = []  # list of cits for statistical particle data for each grains
            self.nparticles = []  # List of article numbers for each phase

        # extract data from descriptors of individual phases
        for ip, stats in enumerate(stats_dicts):
            # Extract RVE side lengths and voxel numbers, must be provided for phase 0
            if 'RVE' in stats.keys():
                size = (stats["RVE"]["sideX"],
                        stats["RVE"]["sideY"],
                        stats["RVE"]["sideZ"])
                nvox = (int(stats["RVE"]["Nx"]),
                        int(stats["RVE"]["Ny"]),
                        int(stats["RVE"]["Nz"]))
                if self.size is None:
                    self.size = size
                else:
                    if self.size != size:
                        logging.warning(f'Conflicting RVE sizes in descriptors: {self.size}, {size}.' +
                                        'Using first value.')
                if self.dim is None:
                    self.dim = nvox
                else:
                    if self.dim != nvox:
                        logging.warning(f'Conflicting RVE voxel dimensions in descriptors: {self.dim}, {nvox}.' +
                                        'Using first value.')
                # Extract Alloy number for ICAMS CP-UMAT
                if "ialloy" in stats['RVE'].keys():
                    ialloy.append(stats['RVE']['ialloy'])
            elif ip == 0:
                raise ValueError('RVE properties must be specified in descriptors for first phase.')

            # Extract other simulation attributes, must be specified for phase 0
            if "Simulation" in stats.keys():
                peri = stats["Simulation"]["periodicity"]
                if type(peri) is bool:
                    periodic = peri
                else:
                    periodic = True if peri == 'True' else False
                if self.periodic is None:
                    self.periodic = periodic
                elif self.periodic != periodic:
                    logging.warning(f'Inconsistent values for periodicity. Using periodicity: {self.periodic}.')
                units = str(stats["Simulation"]["output_units"])
                # Raise ValueError if units are not specified as 'mm' or 'um'
                if units != 'mm' and units != 'um':
                    raise ValueError('Output units can only be "mm" or "um"!')
                if self.units is None:
                    self.units = units
                elif self.units != units:
                    logging.warning(f'Inconsistent values for units. Using units: {self.units}.')
            elif ip == 0:
                raise ValueError('Simulation attributes must be specified in descriptors for first phase.')

            # Extract phase information
            if "Phase" in stats.keys():
                phase_names.append(stats["Phase"]["Name"])
                phase_vf.append(stats["Phase"]["Volume fraction"])
            else:
                phase_names.append(f'Phase_{ip}')
                phase_vf.append(1. - np.sum(phase_vf))  # volume fraction can only be unspecified for last phase
            if np.sum(phase_vf) > 1.:
                raise ValueError(f"Sum of all phase fractions exceeds 1: {phase_vf}")

            # Extract grains shape attributes to initialize particles
            if not from_voxels:
                if stats["Grain type"] not in ["Elongated", "Equiaxed", "Free"]:
                    raise ValueError('The value for "Grain type" must be either "Equiaxed" or "Elongated".')
                part_dict = init_particles(ip)
                self.particle_data.append(part_dict)
                self.nparticles.append(part_dict['Number'])
        print('  RVE characteristics:')
        print(f'    RVE side lengths (X, Y, Z) = {self.size} ({self.units})')
        print(f'    Number of voxels (X, Y, Z) = {self.dim}')
        print(f'    Voxel resolution (X, Y, Z) = {np.divide(self.size, self.dim).round(4)}' +
              f'({self.units})')
        print(f'    Total number of voxels     = {np.prod(self.dim)}\n')
        print('\nConsidered phases (volume fraction): ')
        for ip, name in enumerate(phase_names):
            print(f'{ip}: {name} ({phase_vf[ip] * 100.}%)')
        print('\n')
        self.phase_names = phase_names
        self.phase_vf = phase_vf
        nall = len(ialloy)
        if nall > 0:
            if nall != len(phase_vf):
                logging.warning(f'{nall} values of "ialloy" provided, but only {len(phase_vf)} phases defined.')
            self.ialloy = ialloy
        return


class mesh_creator(object):
    def __init__(self, dim):
        """
        Create a mesh object.

        Parameters
        ----------
        dim: 3-tuple for dimensions of mesh (numbers of voxels in each Cartesian direction)

        Attributes
        ----------
        self.dim = dim  # dimension tuple: number of voxels in each Cartesian direction
        self.nvox = np.prod(dim)  # number of voxels
        self.phases = np.zeros(dim, dtype=int)  # field data with phase numbers
        self.grains = np.zeros(dim, dtype=int)  # field data with grain numbers
        self.voxel_dict = dict()  # stores nodes assigned to each voxel (key; voxel number:int)
        self.grain_dict = dict()  # stored voxels assigned to each grain (key: grain number:int
        self.nodes = None  # array of nodal positions
        self.nodes_smooth = None  # array of nodal positions after smoothening grain boundaries
        """

        if not (type(dim) is tuple and len(dim) == 3):
            raise ValueError(f"Dimension dim must be a 3-tuple, not {type(dim)}, {dim}")
        self.dim = dim  # dimension tuple: number of voxels in each Cartesian direction
        self.nvox = np.prod(dim)  # number of voxels
        self.grains = None
        self.phases = None
        self.grain_dict = dict()  # voxels assigned to each grain (key: grain number:int)
        self.grain_phase_dict = None  # phases per grain (key: grain number:int)
        self.grain_ori_dict = None  # orientations per grain (key: grain number:int)
        self.voxel_dict = defaultdict(list)  # dictionary to store list of node ids for each element
        self.vox_center_dict = dict()  # dictionary to store center of each voxel as 3-tupel
        self.nodes = None  # array of nodal positions
        self.nodes_smooth = None  # array of nodal positions after smoothening grain boundaries
        self.prec_vf_voxels = None  # actual volume fraction of precipitates in voxelated structure
        return

    def get_ind(self, addr):
        """
        Return the index in an array from a generic address.

        Parameters
        ----------
        addr

        Returns
        -------

        """
        if addr is None:
            ind = None
        elif len(addr) == 0:
            ind = addr
        elif len(addr) == 3:
            ind = addr[0] * self.dim[1] * self.dim[2] + addr[1] * self.dim[1] + addr[2]
        else:
            raise ValueError(f"Address must be a single int or a 3-tuple, not {type(addr)}, {addr}.")
        return ind

    def create_voxels(self, sim_box):
        """
        Generates voxels inside the defined RVE (Simulation box)

        :param sim_box: Simulation box representing RVE dimensions
        :type sim_box: :obj:`entities.Cuboid`

        :returns: * Node list containing coordinates.
                  * Element dictionary containing element IDs and nodal connectivities.
                  * Voxel dictionary containing voxel ID and center coordinates.
        :rtype: Tuple of Python dictionaries.
        """
        print('    Generating voxels inside RVE')
        # generate nodes of all voxels from RVE side dimensions
        lim_minX, lim_maxX = sim_box.left, sim_box.right
        lim_minY, lim_maxY = sim_box.top, sim_box.bottom
        lim_minZ, lim_maxZ = sim_box.front, sim_box.back  # define the cuboidal RVE limits

        # generate points within these limits
        pointsX = np.linspace(lim_minX, lim_maxX, num=self.dim[0] + 1, endpoint=True)
        pointsY = np.linspace(lim_minY, lim_maxY, num=self.dim[1] + 1, endpoint=True)
        pointsZ = np.linspace(lim_minZ, lim_maxZ, num=self.dim[2] + 1, endpoint=True)

        # duplicate neighbouring points
        pointsX_dup = [(first, second) for first, second in zip(pointsX, pointsX[1:])]
        pointsY_dup = [(first, second) for first, second in zip(pointsY, pointsY[1:])]
        pointsZ_dup = [(first, second) for first, second in zip(pointsZ, pointsZ[1:])]

        verticesDict = {}  # dictionary to store vertices
        node_count = 0
        elmt_count = 0
        # loop over the duplicate pairs
        for (mi, ni), (mj, nj), (mk, nk) in itertools.product(pointsX_dup, pointsY_dup, pointsZ_dup):

            # Find the center of each voxel and update the center dictionary
            elmt_count += 1
            self.vox_center_dict[elmt_count] = (0.5 * (mi + ni), 0.5 * (mj + nj), 0.5 * (mk + nk))

            # group the 8 nodes of an element and update node & element dictionary accordingly
            # C3D8 element connectivity is maintained by this list (DON'T change this order)
            vertices = [(ni, mj, nk), (ni, mj, mk), (mi, mj, mk), (mi, mj, nk),
                        (ni, nj, nk), (ni, nj, mk), (mi, nj, mk), (mi, nj, nk)]

            for coo in vertices:
                if coo not in verticesDict.keys():
                    node_count += 1
                    verticesDict[coo] = node_count
                    self.voxel_dict[elmt_count].append(node_count)
                else:
                    self.voxel_dict[elmt_count].append(verticesDict[coo])

        # nodal positions array
        self.nodes = np.zeros((node_count, 3))
        for pos, i in verticesDict.items():
            self.nodes[i - 1, :] = pos
        return


def set_stats(grains, ar=None, omega=None, deq_min=None, deq_max=None,
              asp_min=None, asp_max=None, omega_min=None, omega_max=None,
              size=100, voxels=60, gtype='Elongated', rveunit='um',
              periodicity=False, VF=None, phasename=None, phasenum=None,
              save_file=False):
    """
    grains = [sigma, loc , scale of lognorm distrib. of equiv. diameter]
    ar = [sigma, loc, scale of logorm distrib of aspect ratio]
    omega = [kappa, loc of von Mises distrib. of tilt angle]
    """

    # type of grains either 'Elongated' or 'Equiaxed'
    if not (gtype == 'Elongated' or gtype == 'Equiaxed'):
        raise ValueError('Wrong grain type given in set_stats: {}'
                         .format(gtype))
    if gtype == 'Elongated' and (ar is None or omega is None):
        raise ValueError('If elliptical grains are specified, aspect ratio ' +
                         '(ar) and orientation (omega) need to be given.')
    if gtype == 'Equiaxed' and (ar is not None or omega is not None):
        logging.warning('Equiaxed grains have been specified, but aspect ratio' +
                        ' (ar) and orientation (omega) have been provided. ' +
                        'Will change grain type to "Elongated".')
        gtype = 'Elongated'

    # define cutoff values
    # cutoff deq
    if deq_min is None:
        deq_min = 1.3 * grains[1]  # 316L: 8
    if deq_max is None:
        deq_max = grains[1] + grains[2] + 6. * grains[0]  # 316L: 30
    if gtype == 'Elongated':
        # cutoff asp
        if asp_min is None:
            asp_min = np.maximum(1., ar[1])  # 316L: 1
        if asp_max is None:
            asp_max = ar[2] + ar[0]  # 316L: 3
        # cutoff omega
        if omega_min is None:
            omega_min = -np.pi  # omega[1] - 2 * omega[0]
        if omega_max is None:
            omega_max = np.pi  # omega[1] + 2 * omega[0]

    # RVE box size
    lx = ly = lz = size  # size of box in each direction
    # number of voxels
    nx = ny = nz = voxels  # number of voxels in each direction
    # specify RVE info
    if type(periodicity) is bool:
        pbc = periodicity
    else:
        pbc = True if periodicity == 'True' else False

    # check grain type
    # create the corresponding dict with statistical grain geometry information
    sig, loc, scale, kappa = stat_names(legacy=False)
    ms_stats = {'Grain type': gtype,
                'Equivalent diameter':
                    {sig: grains[0], loc: grains[1], scale: grains[2],
                     'cutoff_min': deq_min, 'cutoff_max': deq_max},
                'RVE':
                    {'sideX': lx, 'sideY': ly, 'sideZ': lz,
                     'Nx': nx, 'Ny': ny, 'Nz': nz},
                'Simulation': {'periodicity': pbc,
                               'output_units': rveunit},
                'Phase': {'Name': phasename,
                          'Number': phasenum,
                          'Volume fraction': VF}}
    if gtype == 'Elongated':
        ms_stats['Aspect ratio'] = {sig: ar[0], loc: ar[1], scale: ar[2],
                                    'cutoff_min': asp_min, 'cutoff_max': asp_max}
        ms_stats['Tilt angle'] = {kappa: omega[0], loc: omega[1],
                                  'cutoff_min': omega_min, 'cutoff_max': omega_max}
    if save_file:
        cwd = os.getcwd()
        json_dir = cwd + '/json_files'  # Folder to store the json files
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        with open(json_dir + '/stat_info.json', 'w') as outfile:
            json.dump(ms_stats, outfile, indent=2)

    return ms_stats


class NodeSets(object):
    def __init__(self, nodes):
        self.F0yz = []  # left nodes
        self.F0yz_full = [] # left nodes copy

        self.F1yz = []  # right nodes
        self.F1yz_full = [] # right nodes copy

        self.Fx0z = []  # bottom nodes
        self.Fx0z_full = [] # bottom nodes copy

        self.Fx1z = []  # top nodes
        self.Fx1z_full = [] # top nodes copy

        self.Fxy0 = []  # rear nodes
        self.Fxy0_full = [] # rear nodes copy

        self.Fxy1 = []  # front nodes
        self.Fxy1_full = [] # front nodes copy

        self.surfSet = []  # nodes on any surface
        maxX = max(nodes[:, 0])
        minX = min(nodes[:, 0])
        maxY = max(nodes[:, 1])
        minY = min(nodes[:, 1])
        maxZ = max(nodes[:, 2])
        minZ = min(nodes[:, 2])
        # select all nodes on a surface and assign to face
        for i, coord in enumerate(nodes):
            surface = False
            if np.isclose(coord[0], maxX):
                surface = True
                self.F1yz.append(i)    # rightSet, nodes belong to the right face
                self.F1yz_full.append(i)
            if np.isclose(coord[0], minX):
                surface = True
                self.F0yz.append(i)    # leftSet, nodes belong to the left face
                self.F0yz_full.append(i)
            if np.isclose(coord[1], maxY):
                surface = True
                self.Fx1z.append(i)    # topSet, nodes belong to the top face
                self.Fx1z_full.append(i)
            if np.isclose(coord[1], minY):
                surface = True
                self.Fx0z.append(i)    # bottomSet, nodes belong to the bottom face
                self.Fx0z_full.append(i)
            if np.isclose(coord[2], maxZ):
                surface = True
                self.Fxy1.append(i)    # frontSet, nodes belong to the front face
                self.Fxy1_full.append(i)
            if np.isclose(coord[2], minZ):
                surface = True
                self.Fxy0.append(i)    # rearSet, nodes belong to the rear face
                self.Fxy0_full.append(i)
            if surface:
                self.surfSet.append(i) # set for all nodes that belong to the faces (includes all previous face sets)

        #########
        # EDGES #
        #########
        # top front edge
        E_T1 = np.intersect1d(self.Fxy1, self.Fx1z)
        self.Ex11_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_T1)
        self.Ex11 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_T1)
        # top back edge
        E_T3 = np.intersect1d(self.Fxy0, self.Fx1z)
        self.Ex10_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_T3)
        self.Ex10 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_T3)
        # top left edge
        E_T4 = np.intersect1d(self.F0yz, self.Fx1z)
        self.E01z_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_T4)
        self.E01z = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_T4)
        # top right edge
        E_T2 = np.intersect1d(self.F1yz, self.Fx1z)
        self.E11z_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_T2)
        self.E11z = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_T2)

        # bottom front edge
        E_B1 = np.intersect1d(self.Fxy1, self.Fx0z)
        self.Ex01_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_B1)
        self.Ex01 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_B1)
        # bottom rear edge
        E_B3 = np.intersect1d(self.Fxy0, self.Fx0z)
        self.Ex00_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_B3)
        self.Ex00 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 0], E_B3)
        # bottom left edge
        E_B4 = np.intersect1d(self.F0yz, self.Fx0z)
        self.E00z_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_B4)
        self.E00z = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_B4)
        # bottom right edge
        E_B2 = np.intersect1d(self.F1yz, self.Fx0z)
        self.E10z_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_B2)
        self.E10z = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 2], E_B2)

        # left front edge
        E_M1 = np.intersect1d(self.F0yz, self.Fxy1)
        self.E0y1_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M1)
        self.E0y1 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M1)
        # right front edge
        E_M2 = np.intersect1d(self.Fxy1, self.F1yz)
        self.E1y1_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M2)
        self.E1y1 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M2)
        # left rear edge
        E_M4 = np.intersect1d(self.Fxy0, self.F0yz)
        self.E0y0_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M4)
        self.E0y0 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M4)
        # right rear edge
        E_M3 = np.intersect1d(self.Fxy0, self.F1yz)
        self.E1y0_full = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M3)
        self.E1y0 = self.CreatePeriodicEdgeSets(self.surfSet, nodes[self.surfSet, 1], E_M3)

        ############
        # VERTICES #
        ############
        self.V001 = np.intersect1d(self.Ex01, self.E00z)[0]  # V1
        self.V101 = np.intersect1d(self.Ex01, self.E10z)[0]  # V2
        self.V000 = np.intersect1d(self.Ex00, self.E00z)[0]  # H1
        self.V100 = np.intersect1d(self.E10z, self.Ex00)[0]  # H2
        self.V111 = np.intersect1d(self.Ex11, self.E11z)[0]  # V3
        self.V110 = np.intersect1d(self.E11z, self.Ex10)[0]  # H3
        self.V011 = np.intersect1d(self.Ex11, self.E01z)[0]  # V4
        self.V010 = np.intersect1d(self.Ex10, self.E01z)[0]  # H4

        CORNERNODES = [self.V000, self.V100, self.V010, self.V001, self.V011, self.V101, self.V110, self.V111]

        #####################
        # CreateEdgeNodeset #
        #####################
        EdgeNodes = []
        EdgeNodes.extend(self.Ex11)
        EdgeNodes.extend(self.Ex10)
        EdgeNodes.extend(self.E01z)
        EdgeNodes.extend(self.E11z)
        EdgeNodes.extend(self.Ex01)
        EdgeNodes.extend(self.Ex00)
        EdgeNodes.extend(self.E00z)
        EdgeNodes.extend(self.E10z)
        EdgeNodes.extend(self.E0y1)
        EdgeNodes.extend(self.E1y1)
        EdgeNodes.extend(self.E0y0)
        EdgeNodes.extend(self.E1y0)

        # Remove Corner Nodes from Edge Nodesets
        self.Ex11P = self.RemoveItemInList(self.Ex11_full, CORNERNODES) # top front edge
        self.Ex10P = self.RemoveItemInList(self.Ex10_full, CORNERNODES) # top rear edge
        self.Ex01P = self.RemoveItemInList(self.Ex01_full, CORNERNODES) # bottom front edge
        self.Ex00P = self.RemoveItemInList(self.Ex00_full, CORNERNODES) # bottom rear edge
        self.E01zP = self.RemoveItemInList(self.E01z_full, CORNERNODES) # top left edge
        self.E00zP = self.RemoveItemInList(self.E00z_full, CORNERNODES) # bottom left edge
        self.E10zP = self.RemoveItemInList(self.E10z_full, CORNERNODES) # bottom right edge
        self.E11zP = self.RemoveItemInList(self.E11z_full, CORNERNODES) # top right edge
        self.E0y0P = self.RemoveItemInList(self.E0y0_full, CORNERNODES) # left rear edge
        self.E1y0P = self.RemoveItemInList(self.E1y0_full, CORNERNODES) # right rear edge
        self.E1y1P = self.RemoveItemInList(self.E1y1_full, CORNERNODES) # right front edge
        self.E0y1P = self.RemoveItemInList(self.E0y1_full, CORNERNODES) # left front edge

        ######### Sorts the Nodesets with respect to their coordinates
        # print('Pure surface nodes after deleting edge and corner nodes')

        # Pure BottomSet nodes without vertices and edges.
        self.Fx0zP = self.RemoveItemInList(self.Fx0z_full, CORNERNODES)
        self.Fx0zP = self.RemoveItemInList(self.Fx0zP, EdgeNodes)
        # print("Bottom Face: ", len(self.Fx0zP))

        # Pure TopSet nodes without vertices and edges.
        self.Fx1zP = self.RemoveItemInList(self.Fx1z_full, CORNERNODES)
        self.Fx1zP = self.RemoveItemInList(self.Fx1zP, EdgeNodes)
        # print("Top Face: ", len(self.Fx1zP))

        # Pure LeftSet nodes without vertices and edges.
        self.F0yzP = self.RemoveItemInList(self.F0yz_full, CORNERNODES)
        self.F0yzP = self.RemoveItemInList(self.F0yzP, self.Fx1zP)
        self.F0yzP = self.RemoveItemInList(self.F0yzP, self.Fx0zP)
        self.F0yzP = self.RemoveItemInList(self.F0yzP, EdgeNodes)
        # print("Left Face: ", len(self.F0yzP))

        # Pure RightSet nodes without vertices and edges.
        self.F1yzP = self.RemoveItemInList(self.F1yz_full, CORNERNODES)
        self.F1yzP = self.RemoveItemInList(self.F1yzP, self.Fx1zP)
        self.F1yzP = self.RemoveItemInList(self.F1yzP, self.Fx0zP)
        self.F1yzP = self.RemoveItemInList(self.F1yzP, EdgeNodes)
        # print("Right Face: ", len(self.F1yzP))

        # Pure FrontSet nodes without vertices and edges.
        self.Fxy1P = self.RemoveItemInList(self.Fxy1_full, CORNERNODES)
        self.Fxy1P = self.RemoveItemInList(self.Fxy1P, self.Fx1zP)
        self.Fxy1P = self.RemoveItemInList(self.Fxy1P, self.Fx0zP)
        self.Fxy1P = self.RemoveItemInList(self.Fxy1P, self.F0yzP)
        self.Fxy1P = self.RemoveItemInList(self.Fxy1P, self.F1yzP)
        self.Fxy1P = self.RemoveItemInList(self.Fxy1P, EdgeNodes)
        # print("Front Face: ", len(self.Fxy1P))

        # Pure RearSet nodes without vertices and edges.
        self.Fxy0P = self.RemoveItemInList(self.Fxy0_full, CORNERNODES)
        self.Fxy0P = self.RemoveItemInList(self.Fxy0P, self.Fx1zP)
        self.Fxy0P = self.RemoveItemInList(self.Fxy0P, self.Fx0zP)
        self.Fxy0P = self.RemoveItemInList(self.Fxy0P, self.F0yzP)
        self.Fxy0P = self.RemoveItemInList(self.Fxy0P, self.F1yzP)
        self.Fxy0P = self.RemoveItemInList(self.Fxy0P, EdgeNodes)
        # print("Rear Face: ", len(self.Fxy0P))

        # Order opposite surfaces in the same way so that corresponding nodes are directly at same position in nodeSet
        self.Fx0zP = self.CreatePeriodicNodeSets(self.surfSet, nodes[self.surfSet, 0],
                                                               nodes[self.surfSet, 2], self.Fx0zP) # BottomSet

        self.Fx1zP = self.CreatePeriodicNodeSets(self.surfSet, nodes[self.surfSet, 0],
                                                               nodes[self.surfSet, 2], self.Fx1zP) # TopSet

        self.F0yzP = self.CreatePeriodicNodeSets(self.surfSet, nodes[self.surfSet, 1],
                                                               nodes[self.surfSet, 2], self.F0yzP) # LeftSet

        self.F1yzP = self.CreatePeriodicNodeSets(self.surfSet, nodes[self.surfSet, 1],
                                                               nodes[self.surfSet, 2], self.F1yzP)  # RightSet

        self.Fxy1P = self.CreatePeriodicNodeSets(self.surfSet, nodes[self.surfSet, 0],
                                                               nodes[self.surfSet, 1], self.Fxy1P)  # FrontSet

        self.Fxy0P = self.CreatePeriodicNodeSets(self.surfSet, nodes[self.surfSet, 0],
                                                               nodes[self.surfSet, 1], self.Fxy0P)  # RearSet


    def CreatePeriodicNodeSets(self, Nodes, sortCoord1, sortCoord2, NodeSet):
        # Creates a List of Sorted Nodes with respect to sortCoord1 and sortCoord2 for faces
        # Input: Nodeset of surface nodes
        import operator
        startList = []
        sortedList = []
        for number in NodeSet:
            startList.append([number, sortCoord1[Nodes.index(number)], sortCoord2[Nodes.index(number)]])
        startList.sort(key=operator.itemgetter(1, 2))
        for item in range(len(startList)):
            sortedList.append(startList[item][0])

        return sortedList


    def CreatePeriodicEdgeSets(self, Nodes, sortCoord, NodeSet):
        # Creates a List of Sorted Nodes with respect to sortCoord for edges
        import operator
        startList = []
        sortedList = []
        for number in NodeSet:
            startList.append([number, sortCoord[Nodes.index(number)]])
        startList.sort(key=operator.itemgetter(1))
        for item in range(len(startList)):
            sortedList.append(startList[item][0])

        return sortedList

    def RemoveItemInList(self, NodeList, ReplaceNodeList):
        # remove set of nodes from list
        for item in ReplaceNodeList:
            try:
                NodeList.remove(item)
            except ValueError:
                pass

        return NodeList

