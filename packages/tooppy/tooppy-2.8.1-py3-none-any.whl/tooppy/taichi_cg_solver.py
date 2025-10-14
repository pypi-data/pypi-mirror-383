import numpy as np
import taichi as ti
import time

@ti.kernel
def csr_matvec_kernel(row_ptr: ti.template(),  # type: ignore
                      cols: ti.template(),  # type: ignore
                      values: ti.template(),  # type: ignore
                      x: ti.template(),  # type: ignore
                      y: ti.template(),  # type: ignore
                      n: ti.i32):  # type: ignore
    """CSR格式稀疏矩阵向量乘法"""
    for i in range(n):
        temp: ti.float64 = 0.0  # type: ignore
        for idx in range(row_ptr[i], row_ptr[i + 1]):
            temp += values[idx] * x[cols[idx]]
        y[i] = temp

@ti.kernel
def vector_add_scaled(x: ti.template(),  # type: ignore
                      y: ti.template(),  # type: ignore
                      alpha: ti.f64,  # type: ignore
                      z: ti.template(),  # type: ignore
                      n: ti.i32):  # type: ignore
    """向量加法: z = x + alpha * y"""
    for i in range(n):
        z[i] = x[i] + alpha * y[i]

@ti.kernel
def vector_copy(src: ti.template(), dst: ti.template(), n: ti.i32):  # type: ignore
    """向量拷贝: dst = src"""
    for i in range(n):
        dst[i] = src[i]

@ti.kernel
def vector_sub_from_vector(b: ti.template(),  # type: ignore
                           Ax: ti.template(),  # type: ignore
                           result: ti.template(),  # type: ignore
                           n: ti.i32):  # type: ignore
    """向量减法: result = b - Ax"""
    for i in range(n):
        result[i] = b[i] - Ax[i]

@ti.kernel
def dot_product_reduce(x: ti.template(), y: ti.template()) -> ti.f64:  # type: ignore
    """向量点积 - 使用Taichi的reduction"""
    result: ti.float64 = 0.0  # type: ignore
    for i in range(x.shape[0]):
        result += x[i] * y[i]
    return result

def dense_to_csr(A):
    """将稠密矩阵转换为CSR格式"""
    rows, cols = [], []
    values = []
    
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if abs(A[i, j]) > 1e-15:
                rows.append(i)
                cols.append(j)
                values.append(A[i, j])
    
    rows = np.array(rows, dtype=np.int32)
    cols = np.array(cols, dtype=np.int32)
    values = np.array(values, dtype=np.float64)
    
    # 构建row_ptr
    n = A.shape[0]
    row_ptr = np.zeros(n + 1, dtype=np.int32)
    for i in range(len(rows)):
        row_ptr[rows[i] + 1] += 1
    row_ptr = np.cumsum(row_ptr)
    
    return row_ptr, cols, values

def coo_to_csr(row, col, data, shape, return_sort_indices=False):
    """
    将COO格式稀疏矩阵转换为CSR格式
    
    参数:
        row: COO格式的行索引数组
        col: COO格式的列索引数组
        data: COO格式的非零元素值数组
        shape: 矩阵形状 (n_rows, n_cols)
    
    返回:
        row_ptr: CSR格式的行指针数组
        col_indices: CSR格式的列索引数组
        values: CSR格式的非零元素值数组
    """
    # 转换为numpy数组
    row = np.array(row, dtype=np.int32)
    col = np.array(col, dtype=np.int32)
    data = np.array(data, dtype=np.float64)

    n_rows, n_cols = shape
    
    # 按行索引排序（相同行内按列索引排序）
    sort_indices = np.lexsort((col, row))
    row_sorted = row[sort_indices]
    col_sorted = col[sort_indices]
    start = time.time()
    data_sorted = data[sort_indices]
    end = time.time()
    # print(f"排列数据边际时间: {end - start:.4f} 秒")
    
    # 构建row_ptr数组
    row_ptr = np.zeros(n_rows + 1, dtype=np.int32)
    
    # 计算每行的非零元素个数
    for i in range(len(row_sorted)):
        row_ptr[row_sorted[i] + 1] += 1
    
    # 累加得到row_ptr
    row_ptr = np.cumsum(row_ptr)
    
    if return_sort_indices:
        return row_ptr, col_sorted, data_sorted, sort_indices
    else:
        return row_ptr, col_sorted, data_sorted

class sparse_linear_system():
    def __init__(self, n, rows, cols, data):
        """
        参数:
            row_ptr_np: CSR格式的行指针数组（numpy）
            cols_np: CSR格式的列索引数组（numpy）
            values_np: CSR格式的非零元素值数组（numpy）
        """
        self.n = n

        row_ptr, cols, values, sort_indices = coo_to_csr(rows, cols, data, (n, n), return_sort_indices=True)
        self.sort_indices = sort_indices
        nnz = len(values)
        
        # 创建Taichi fields for CSR格式数据（在GPU上）
        self.row_ptr_field = ti.field(dtype=ti.i32, shape=n + 1)
        self.cols_field = ti.field(dtype=ti.i32, shape=nnz)
        self.values_field = ti.field(dtype=ti.f64, shape=nnz)
        
        # 将CSR数据传输到GPU
        self.row_ptr_field.from_numpy(row_ptr)
        self.cols_field.from_numpy(cols)
        self.values_field.from_numpy(values)

    def cg_solve(self, b, x0=None, tol=1e-18, max_iter=None):
        """
        基于Taichi field的GPU加速共轭梯度法
        
        参数:
            b: 右端向量（numpy）
            x0: 初始解
            tol: 收敛容差
            max_iter: 最大迭代次数
        
        返回:
            x: 近似解（numpy数组）
            iterations: 实际迭代次数
        """
        n = self.n
        if max_iter is None:
            max_iter = n * 10
        
        # 转换为numpy数组（确保类型正确）
        b_np = np.array(b, dtype=np.float64)
        
        # 创建Taichi fields for 向量（在GPU上）
        x = ti.field(dtype=ti.f64, shape=n)
        r = ti.field(dtype=ti.f64, shape=n)
        p = ti.field(dtype=ti.f64, shape=n)
        Ap = ti.field(dtype=ti.f64, shape=n)
        temp = ti.field(dtype=ti.f64, shape=n)
        b_field = ti.field(dtype=ti.f64, shape=n)
        
        # 初始化b field
        b_field.from_numpy(b_np)
        
        # 初始化x
        if x0 is None:
            x.fill(0.0)
        else:
            x.from_numpy(np.array(x0, dtype=np.float64))
        
        # 计算初始残差 r = b - Ax
        csr_matvec_kernel(self.row_ptr_field, self.cols_field, self.values_field, x, temp, n)
        vector_sub_from_vector(b_field, temp, r, n)
        
        # p = r
        vector_copy(r, p, n)
        
        # rs_old = r^T * r
        rs_old = dot_product_reduce(r, r)
        
        if ti.sqrt(rs_old) < tol:
            return x.to_numpy(), 0
        for iteration in range(max_iter):
            
            # Ap = A * p
            csr_matvec_kernel(self.row_ptr_field, self.cols_field, self.values_field, p, Ap, n)
            
            # alpha = rs_old / (p^T * Ap)
            pAp = dot_product_reduce(p, Ap)
            alpha = rs_old / pAp
            
            # x = x + alpha * p
            vector_add_scaled(x, p, alpha, x, n)
            
            # r = r - alpha * Ap
            vector_add_scaled(r, Ap, -alpha, r, n)
            
            # rs_new = r^T * r
            rs_new = dot_product_reduce(r, r)
            
            if ti.sqrt(rs_new) < tol:
                return x.to_numpy(), iteration + 1
            
            # beta = rs_new / rs_old
            beta = rs_new / rs_old
            
            # p = r + beta * p
            vector_add_scaled(r, p, beta, p, n)
            
            rs_old = rs_new
        
        return x.to_numpy(), max_iter
    
    def replace_matrix_elements(self, data):  # 替换非零元的值，次序必须和初始化实例时完全一样
        data_sorted = data[self.sort_indices]
        self.values_field.from_numpy(data_sorted)
