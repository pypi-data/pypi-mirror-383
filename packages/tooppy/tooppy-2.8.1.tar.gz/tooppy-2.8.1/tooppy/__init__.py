import numpy as np
from scipy.sparse import coo_matrix
import time
from sympy import symbols, Matrix, diff, expand
import itertools
import os
import pyvista

__version__ = "2.8.0"

def get_M_n(d:int, n:int, E=1, nu=1/3):
    return E / (1-(n - 1) * nu - (d - n) * n / (1 - max(0, d - n - 1) * nu) * nu ** 2)

def get_element_stiffness_matrix(
    E=1,  # Young's modulus
    nu=1/3,  # Poisson's ratio
    dimensional=2
):
    dof = dimensional * 2 ** dimensional
    M_1 = get_M_n(dimensional, 1, E=E, nu=nu)
    M_2 = get_M_n(dimensional, 2, E=E, nu=nu)
    G = E / (2 * (1 + nu))  # Modulus of rigidity

    C = np.zeros([dimensional + dimensional * (dimensional - 1) // 2] * 2)
    C[:dimensional, :dimensional] = np.eye(dimensional) * (M_1 * 2 - M_2) + np.ones([dimensional] * 2) * (M_2 - M_1)
    C[dimensional:, dimensional:] = np.eye(dimensional * (dimensional - 1) // 2) * G
    C = C.tolist()  # For certain versions of NumPy, if this line of code is not executed, then C = Matrix(C) will throw an error

    C = Matrix(C)  # Constitutive (material property) matrix:
    
    # Initialize SymPy symbols
    xs = ''
    for i in range(dimensional):
        xs += (' ' if i > 0 else '') + 'x' + str(i)
    xs = symbols(xs)

    Ns = []
    for I in itertools.product(*([[-1, 1]] * dimensional)):
        Ns.append(1)
        for j, i in enumerate(I):
            Ns[-1] *= 0.5 + i * xs[j]
        
    # Create strain-displacement matrix B:
    B = [[0] * dof for i in range(dimensional)]
    for i, x in enumerate(xs):
        for j, N in enumerate(Ns):
            B[i][j * dimensional + i] = diff(N, x)
    for i, x in enumerate(xs):
        for j, y in enumerate(xs):
            if j <= i:
                continue
            B.append([0] * dof)
            for k, N in enumerate(Ns):
                B[-1][k * dimensional + i] = diff(N, y)
                B[-1][k * dimensional + j] = diff(N, x)
    B = Matrix(B)

    dK = B.T * C * B

    # Because dK is symmetric, only need to integrate about half of it.
    K = np.zeros([dof] * 2)
    for i in range(dof):
        for j in range(0, i + 1):
            K[i, j] = expand(dK[i * dof + j]).integrate(*[[x, -0.5, 0.5] for x in xs])
    for i in range(dof):
        for j in range(i + 1, dof):
            K[i, j] = K[j, i]
    
    return K

def get_smoothen_kernel(
    rmin,
    resolution,
    mask=None,
    element_indices_flattened=None
):  # Generate kernel for smoothing a field
    iH = []
    jH = []
    sH = []
    for row, I in enumerate(itertools.product(*[range(e) for e in resolution])):
        if not element_indices_flattened is None and element_indices_flattened[row] == -1:
            continue
        KK1 = [int(np.maximum(i - (np.ceil(rmin) - 1), 0)) for i in I]
        KK2 = [int(np.minimum(i + np.ceil(rmin), nel)) for i, nel in zip(I, resolution)]
        for J in itertools.product(*[range(e_1, e_2) for e_1, e_2 in zip(KK1, KK2)]):
            col = 0
            for a, b in zip(J, resolution):
                col = col * b + a
            if not element_indices_flattened is None and element_indices_flattened[col] == -1:
                continue
            fac = rmin - np.sqrt(np.sum([(i - j) ** 2 for i, j in zip(I, J)]))
            if fac >= 0:
                if mask is None:
                    iH.append(row)
                    jH.append(col)
                else:
                    iH.append(element_indices_flattened[row])
                    jH.append(element_indices_flattened[col])
                sH.append(fac)
    if mask is None:
        H = coo_matrix((sH, (iH, jH)), shape=(np.prod(resolution), np.prod(resolution))).tocsc()
    else:
        H = coo_matrix((sH, (iH, jH)), shape=[np.sum(mask)] * 2).tocsc()
    H_row_sum = H.sum(1)
    H_row_sum[H_row_sum == 0] = 1
    H /= H_row_sum
    return H
    
def optimality_criteria(  # Used for updating the design variables
    x,  # Old value of the design variables
    dc,  # Sensitivity of the compliance (objective function) with respect to the design variables
    dv,  # Sensitivity of the volume with respect to the design variables
    sum_target
):
    l_low = 0  # Bounds for the Lagrange multiplier
    l_high = 1e9
    move = 0.2  # Maximum change allowed in the design variables in one iteration
    while (l_high - l_low) / (l_low + l_high) > 1e-3:
        l_mid = 0.5 * (l_high + l_low)
        x_new = np.clip(
            x * np.sqrt(-dc / dv / l_mid),
            np.maximum(0, x - move),
            np.minimum(1, x + move)
        )
        if np.sum(x_new) > sum_target :
            l_low = l_mid
        else:
            l_high = l_mid
    return x_new

def _indices_to_id(resolution, indices):
    id = 0
    for a, b in zip(resolution, indices):
        id = a * id + b
    return id

def solve(
    get_fixed,  # Inputs resolution, outputs an array defining which dofs are fixed
    get_load,  # Inputs resolution, outputs an array defining which dofs are applied force
    resolution,  # Resolution of the solution domain (counting elements, not vertices)
    volume_fraction,  # Volume fraction (target volume / solution domain volume)
    penal=3.0,  # Punish density value between 0 and 1, which is usually not allowed in reality. Min value is 1, which means no punishment. Can be of form float or [float, float] which defines start penal and end penal
    rmin=1.5,  # Larger values for smoother results
    ft=1,  # Solving mode. 0: sens, 1: dens
    E=1,  # Young's modulus
    nu=1 / 3,  # Poisson's ratio
    iterations=20,
    initial_guess=None,
    get_mask=None,  # Define where materials are allowed to be placed. If set to None, materials are allowed to be placed throughout the entire solution domain
    change_threshold=0,  # Terminate the iteration when the single-step update amount is less than this value
    initial_noise_strength=0,
    intermediate_results_saving_path=None,  # The path for saving intermediate results of iterations. If set to None, intermediate results will not be saved
    intermediate_results_start_index=1,
    element_stiffness_matrix_file_dir='./element_stiffness_matrices/',
    skip_calculating_element_stiffness_matrix_if_exists=True,
    linalg_solver='auto',  # Can be 'scipy', 'taichi' or 'auto'. Scipy usually has broader support and exhibits more consistent performance across different hardware and Python versions. Taichi is generally faster and supports GPU acceleration.
    taichi_arch='gpu'  # Can be 'cpu' or 'gpu'
):
    assert linalg_solver in ['auto', 'scipy', 'taichi']
    assert taichi_arch in ['cpu', 'gpu']

    t_2 = time.time()
    # t_0 = time.time()

    if not intermediate_results_saving_path is None:
        if not os.path.exists(intermediate_results_saving_path):
            os.makedirs(intermediate_results_saving_path)
    
    # Max and min stiffness
    density_min = 1e-9  # If set to 0, the linear system will become singular
    density_max = 1.0

    if type(penal) in [int, float]:
        penal = [penal] * 2
    
    # Degrees of freedom (DOFs) & mask
    if callable(get_mask):
        # Calculate location of vertices
        slices = [slice(0, e) for e in resolution]
        coordinates = np.mgrid[slices]
        coordinates = [e.flatten() + 0.5 for e in coordinates]
        mask = get_mask(resolution, np.prod(resolution), np.array(coordinates))
        mask = np.reshape(mask, resolution)
        element_num = np.sum(mask)

        vertex_mask = np.zeros([e + 1 for e in resolution], dtype=bool)
        for e in itertools.product(*[range(2) for _ in resolution]):
            pad_width = np.zeros([len(resolution), 2], dtype=int)
            for i in range(len(resolution)):
                pad_width[i, e[i]] = 1
            vertex_mask = np.logical_or(vertex_mask, np.pad(mask, pad_width=pad_width, mode='constant', constant_values=False))
        dof = len(resolution) * np.sum(vertex_mask)
        vertex_indices_flattened = np.zeros(np.prod(vertex_mask.shape), dtype=int) - 1  # -1 means a vertex is not used
        i = 0
        for j, e in enumerate(vertex_mask.flatten()):
            if e:
                vertex_indices_flattened[j] = i
                i += 1
    else:
        mask = None
        vertex_mask = None
        element_num = np.prod(resolution)
        dof = len(resolution) * np.prod([e + 1 for e in resolution])
    print('degrees of freedom =', dof)  # The time required for solution is usually proportional to the square of this value
    
    # Allocate design variables (as array), initialize and allocate sens.
    if initial_guess is None:
        x = volume_fraction / (1 if mask is None else np.mean(mask)) * np.ones(element_num, dtype=float)
    else:
        x = initial_guess.flatten()
    if initial_noise_strength != 0:
        x += (np.random.rand(element_num) * 2 - 1) * initial_noise_strength
    xPhys = x.copy()

    # print('Time escaped in the first part =', time.time() - t_0)
    
    # Calculate the element stiffness matrix or load it if cache exists
    if not os.path.exists(element_stiffness_matrix_file_dir):
        os.makedirs(element_stiffness_matrix_file_dir)
    element_stiffness_matrix_file_name = 'KE_' + str(len(resolution)) + 'd_' + str(E) + ',' + str(nu) + '.npy'
    if skip_calculating_element_stiffness_matrix_if_exists and os.path.exists(element_stiffness_matrix_file_dir + element_stiffness_matrix_file_name):
        K_element = np.load(element_stiffness_matrix_file_dir + element_stiffness_matrix_file_name)
    else:
        t_0 = time.time()
        K_element = get_element_stiffness_matrix(E=E, nu=nu, dimensional=len(resolution))  # Element Stiffness Matrix
        np.save(element_stiffness_matrix_file_dir + element_stiffness_matrix_file_name, K_element)
        print('Time escaped in calculating element stiffness matrix =', time.time() - t_0)
    
    t_0 = time.time()

    dof_per_element = len(resolution) * 2 ** len(resolution)

    element_dof_matrix = np.zeros((element_num, dof_per_element), dtype=int)  # The element at position (i, j) of this matrix represents the number of the j-th dof of freedom of the i-th element within the entire system's dofs
    if mask is None:
        for element_id, element_indices in enumerate(itertools.product(*[range(e) for e in resolution])):
            n1 = _indices_to_id([e + 1 for e in resolution], element_indices)  # The id of the first vertex of the element. It is different from the element id because the vertex has one more point in each dimension than the element
            indices = n1 * len(resolution) + np.arange(2 * len(resolution), dtype=int)
            j = len(resolution)
            for nel in resolution[-1:0:-1]:
                j *= nel + 1
                indices = list(indices) + list(np.array(indices) + j)
            element_dof_matrix[element_id] = indices
    else:  # Mask is applied
        element_id = 0
        for element_indices in itertools.product(*[range(e) for e in resolution]):
            if not mask[*element_indices]:
                continue
            indices = []
            for e in itertools.product(*[range(2) for _ in resolution]):
                element_indices_2 = np.array(element_indices)
                for i in range(len(resolution)):
                    element_indices_2[i] += e[i]
                n1 = _indices_to_id([e + 1 for e in resolution], element_indices_2)  # The id of the first vertex of the element. It is different from the element id because the vertex has one more point in each dimension than the element
                n1 = vertex_indices_flattened[n1]
                indices += list(n1 * len(resolution) + np.arange(len(resolution), dtype=int))
            element_dof_matrix[element_id] = indices

            element_id += 1
            
    # Construct the index pointers for the coo format
    iK = np.kron(element_dof_matrix, np.ones((dof_per_element, 1), dtype=np.int32)).flatten()  # Repeat each element dof_per_element times in the first dimension then flatten it
    jK = np.kron(element_dof_matrix, np.ones((1, dof_per_element), dtype=np.int32)).flatten()  # Repeat each element dof_per_element times in the second dimension then flatten it

    print('Time escaped in construction of edofMat =', time.time() - t_0)

    # Construct a kernel for smoothening the design variables for regularization
    t_0 = time.time()
    if mask is None:
        element_indices_flattened = None
    else:
        element_indices_flattened = np.zeros(np.prod(resolution), dtype=int) - 1  # -1 means a vertex is not used
        i = 0
        for j, e in enumerate(mask.flatten()):
            if e:
                element_indices_flattened[j] = i
                i += 1
    H = get_smoothen_kernel(rmin, resolution, mask=mask, element_indices_flattened=element_indices_flattened)
    print('Time escaped in construction of kernel for smoothening =', time.time() - t_0)
    
    t_0 = time.time()

    # Calculate location of vertices
    slices = [slice(0, e + 1) for e in resolution]
    coordinates = np.mgrid[slices]
    coordinates = np.array([e.flatten() for e in coordinates])

    # Boundary Conditions and support
    fixed = get_fixed(resolution, len(resolution) * np.prod([e + 1 for e in resolution]), coordinates)
    if mask is None:
        free = np.setdiff1d(np.arange(dof), fixed)
    else:
        free = np.stack([vertex_indices_flattened] * len(resolution), axis=1).flatten()
        free[fixed] = -1
        free = np.where((free != -1).reshape(np.prod([e + 1 for e in resolution]), len(resolution))[vertex_mask.flatten()].flatten())[0]

    # Manually process the coordinates of the sparse matrix to remove constrained dofs from sparse matrix
    free_mask = np.zeros(dof, dtype=bool)
    free_mask[free] = True
    sparse_matrix_element_mask = np.logical_and(free_mask[iK], free_mask[jK])  # This array can be huge
    iK = iK[sparse_matrix_element_mask]  # This array can be huge
    jK = jK[sparse_matrix_element_mask]  # This array can be huge
    for i in range(dof - 1, -1, -1):  # TODO: This might be accelerated by pre-calculating the mapping of row numbers
        if not free_mask[i]:
            iK[iK > i] -= 1
            jK[jK > i] -= 1
    del free_mask

    # Automatically choose linalg solver
    if linalg_solver == 'auto':
        linalg_solver = 'scipy' if len(free) < 15000 else 'taichi'

    if linalg_solver == 'scipy':
        from scipy.sparse.linalg import spsolve  # , cg, minres
    else:
        import taichi as ti
        from tooppy.taichi_cg_solver import sparse_linear_system
        ti.init(arch=ti.gpu if taichi_arch == 'gpu' else ti.cpu)
    
    if linalg_solver == 'taichi':
        linear_system = sparse_linear_system(len(free), iK, jK, np.zeros(len(iK)))

    # Set load
    f = get_load(resolution, len(resolution) * np.prod([e + 1 for e in resolution]), coordinates)
    if not mask is None:
        f = f.reshape(np.prod([e + 1 for e in resolution]), len(resolution), -1)
        f = f[vertex_mask.flatten()]
    f = f.reshape(dof, -1)  # Shape: (dof, number of different loads)
    if np.min(np.max(np.abs(f[free]), axis=0)) == 0:
        raise ValueError("No load found on free dofs.")

    del coordinates
    
    deformation = np.zeros(f.shape)

    print('Time escaped in preparing other things =', time.time() - t_0)
    
    t_0 = time.time()
    loop = 0
    change = 1
    penal_iter = iter(np.linspace(penal[0], penal[1], iterations))
    solutions_last_time = [None] * f.shape[1]
    while change > change_threshold and loop < iterations:
        loop += 1

        penal_in_iteration = next(penal_iter)
        
        # t_1 = time.time()

        # Setup and solve FE problem
        sK = (K_element.flatten()[np.newaxis].T * (density_min + xPhys ** penal_in_iteration * (density_max - density_min))).flatten(order='F')
        sK = sK[sparse_matrix_element_mask]

        # print('Time escaped in generating K =', time.time() - t_1)
        # t_1 = time.time()
        
        if linalg_solver == 'scipy':
            K_system = coo_matrix((sK, (iK, jK)), shape=(len(free), len(free))).tocsc()  # The rigid matrix of the entire system
            
            # Remove constrained dofs from matrix
            # K_system = K_system[free, :][:, free]

            # Solve linear system
            deformation[free, :] = np.reshape(spsolve(K_system, f[free]), [len(free), -1])
            # u[free, :] = np.reshape(cg(K, f[free])[0], [len(free), -1])
            # u[free, :] = np.reshape(minres(K, f[free])[0], [len(free), -1])
            # ml = pyamg.ruge_stuben_solver(K)
            # u[free, :] = np.reshape(ml.solve(f[free], tol=1e-8), [len(free), -1])
        else:
            # sK = np.array(sK)
            # sK = sK.copy()
            linear_system.replace_matrix_elements(sK)
            for i in range(f.shape[1]):
                if solutions_last_time[i] is None:
                    solution = linear_system.cg_solve(f[free, i], max_iter=int(len(free) * 1))[0]
                else:
                    solution = linear_system.cg_solve(f[free, i], x0=solutions_last_time[i], max_iter=int(len(free) * 0.1))[0]
                solutions_last_time[i] = solution
                deformation[free, i] = solution

        # print('Time escaped in solving the linear system =', time.time() - t_1)
        # t_1 = time.time()
        
        # Objective and sensitivity
        ce = np.zeros(element_num)
        for e in deformation.T:  # Traverse different types of forces
            deformation_element = e[element_dof_matrix].reshape(element_num, dof_per_element)
            energy_element = (np.dot(deformation_element, K_element) * deformation_element).sum(1)  # strain energy of an element
            ce = np.maximum(ce, energy_element)  # Compliance energy
        obj = ((density_min + xPhys ** penal_in_iteration * (density_max - density_min)) * ce).sum()  # Total strain energy
        dc = (-penal_in_iteration * xPhys ** (penal_in_iteration - 1) * (density_max - density_min)) * ce  # Ignore contribution of d ce /d obj
        dv = np.ones(element_num)
        
        # Sensitivity filtering
        if ft == 0:
            dc = np.asarray((H * (x * dc))[np.newaxis].T)[:, 0] / np.maximum(0.001, x)
        elif ft == 1:
            dc = np.asarray(H * (dc[np.newaxis].T))[:, 0]
            dv = np.asarray(H * (dv[np.newaxis].T))[:, 0]
            
        # Optimality criteria (Update design variables)
        xold = x
        x = optimality_criteria(x, dc, dv, volume_fraction * np.prod(resolution))

        # print('Time escaped in optimality criteria =', time.time() - t_1)
        # t_1 = time.time()
        
        # Regularize the design variables
        if ft == 0:
            xPhys = x
        elif ft == 1:  # Directly adjusts the design variables x themselves based on their average within a neighborhood defined by rmin.
            xPhys = np.asarray(H * x[np.newaxis].T)[:, 0]
        
        # Compute the change by the inf. norm
        change = np.linalg.norm(x.reshape(element_num, 1) - xold.reshape(element_num, 1), np.inf)

        if not intermediate_results_saving_path is None:
            if mask is None:
                data_to_save = xPhys
            else:
                data_to_save = np.zeros(np.prod(resolution))
                data_to_save[mask.flatten()] = xPhys
            np.save(f'{intermediate_results_saving_path}result_{len(resolution)}d_{loop + intermediate_results_start_index - 1}.npy', data_to_save.reshape(resolution))
        
        print(
            'iteration ', loop,
            ', loss = ', obj,
            ', change = ', change,
            sep=''
        )
    print('Time escaped in main loop =', time.time() - t_0)

    print('Time escaped totally =', time.time() - t_2)
    
    if mask is None:
        return xPhys.reshape(resolution)
    else:
        result = np.zeros(np.prod(resolution))
        result[mask.flatten()] = xPhys
        return result.reshape(resolution)

def get_indices_on_boundary_elements(resolution, axis_selection):
    indices = []
    for a, b in zip(resolution, axis_selection):
        if b is None:
            indices.append(range(a))
        else:
            indices.append(([0] if b[0] else []) + ([a - 1] if b[1] else []))
    indices = np.array(list(itertools.product(*indices)))
    indices *= [int(np.prod(resolution[i:])) for i in range(1, len(resolution) + 1)]
    return np.sum(indices, axis=-1)

def get_indices_on_face(resolution, axis, start=False, end=False):
    axis_selection = [None] * len(resolution)
    axis_selection[axis] = [start, end]
    
    return get_indices_on_boundary_elements(resolution, axis_selection)

def mirrow_first_axis(array):
    shape = list(array.shape)
    shape[0] *= 2
    result = np.zeros(shape, dtype=array.dtype)
    result[:array.shape[0]] = array[::-1]
    result[array.shape[0]:] = array
    return result

def mirror(
    array,
    mirror_x=False,
    mirror_y=False,
    mirror_z=False
):
    if mirror_x:
        array = mirrow_first_axis(array)
    array = np.transpose(array, [1, 2, 0])
    if mirror_y:
        array = mirrow_first_axis(array)
    array = np.transpose(array, [1, 2, 0])
    if mirror_z:
        array = mirrow_first_axis(array)
    array = np.transpose(array, [1, 2, 0])

    return array

# Visualize the result with pyvista
def plot_3d_array(
    array,
    mirror_x=False,
    mirror_y=False,
    mirror_z=False,
    volume_quality=5,
    additional_meshes=[],
    notebook=False
):
    array = mirror(array, mirror_x=mirror_x, mirror_y=mirror_y, mirror_z=mirror_z)

    plotter = pyvista.Plotter(notebook=notebook)

    grid = pyvista.ImageData()
    grid.dimensions = np.array(array.shape) + 1
    grid.spacing = [volume_quality] * 3
    grid.cell_data["values"] = array.flatten(order="F")

    plotter.add_volume(grid, opacity=[0, 1, 1], cmap='magma')

    for mesh in additional_meshes:
        mesh.points *= volume_quality
        plotter.add_mesh(mesh)

    plotter.show()
