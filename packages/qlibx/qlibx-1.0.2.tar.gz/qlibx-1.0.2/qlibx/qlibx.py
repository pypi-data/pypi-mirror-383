import numpy as np

class Ket:
    def __init__(self, coef):
        self.coef = np.array(coef, dtype=complex)

        # to represent real values as real vector
        t=0
        for a in coef:
            if np.imag(a) == 0:
                t=0
            else:
                t=1
                break
        if t==0:
            self.coef = np.array(coef, dtype=float)
    
    def __add__(self, other):
        if not isinstance(other, Ket):
            raise ValueError("Can only add another Ket.")
        return Ket(self.coef + other.coef)
    
    def __sub__(self, other):
        if not isinstance(other, Ket):
            raise ValueError("Can only subtract another Ket.")
        return Ket(self.coef - other.coef)

    def __mul__(self, scalar):
        return Ket(scalar * self.coef)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __repr__(self):
        return f'Ket({self.coef})'
    
    def dagger(self):
        return Bra(np.conjugate(self.coef))
    
    def inner_product(self, another):
        if not isinstance(another, Bra):
            raise ValueError('Inner Product can only be taken with Bra')
        else:
            return np.dot(self.coef, another.coef)
        
    def outer_product(self, another):
        if not isinstance(another, Bra):
            raise ValueError('Outer Product can only be taken with Bra')
        else:
            return np.outer(self.coef,another.coef)
        
    def tensor(self, *args):
        result = self.coef
        for another in args:
            if not isinstance(another, Ket):
                raise ValueError("Tensor product can only be performed with Kets.")
            result = np.kron(result, another.coef)
        return Ket(result)


    
    
 
class Bra:
    def __init__(self,coef):
        self.coef = np.array(coef, dtype=complex).T

        # to represent real values as real vector
        t=0
        for a in coef:
            if np.imag(a) == 0:
                t=0
            else:
                t=1
                break
        if t==0:
            self.coef = np.array(coef, dtype=float)

    def __add__(self, other):
        if not isinstance(other, Bra):
            raise ValueError("Can only add another Bra.")
        return Bra(self.coef + other.coef)
    
    def __sub__(self, other):
        if not isinstance(other, Bra):
            raise ValueError("Can only subtract another Bra.")
        return Bra(self.coef - other.coef)

    def __mul__(self, scalar):
        return Ket(scalar * self.coef)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __repr__(self):
        return f'Bra({self.coef})'
    
    def dagger(self):
        return Ket(np.conjugate(self.coef))
    
    def inner_product(self, another):
        if not isinstance(another, Ket):
            raise ValueError('Inner Product can only be taken with Ket')
        else:
            return np.dot(self.coef, another.coef)
        
    def outer_product(self, another):
        if not isinstance(another, Ket):
            raise ValueError('Outer Product can only be taken with Ket')
        else:
            return np.outer(self.coef,another.coef)
        
    def tensor(self, *args):
        result = self.coef
        for another in args:
            if not isinstance(another, Bra):
                raise ValueError("Tensor product can only be performed with Bras.")
            result = np.kron(result, another.coef)
        return Bra(result)


class Operator:
    def __init__(self, matrix):
        self.matrix = np.array(matrix)

    def __add__(self, another):
        return Operator(self.matrix + another.matrix)
    
    def __sub__(self, another):
        return Operator(self.matrix - another.matrix)
    
    def __mul__(self, scalar):
        return Operator(scalar * np.array(self.matrix))
    
    def __rmul__(self, scalar):
        return Operator(self.__mul__(scalar))
    
    def __matmul__(self,another):
        return Operator(np.matmul(self.matrix , another.matrix))

    def op(self, another):
        if not isinstance(another,Ket):
            raise ValueError('Cannot Operate')
        else:
            return Ket(self.matrix@another.coef)
        
    def dagger(self):
        return Operator(np.conjugate(self.matrix).T)
    
    def hermitian(self):
        return np.array_equal(self.matrix,self.dagger().matrix)
    
    def antihermitian(self):
        return np.array_equal(self.matrix,-self.dagger().matrix)
    
    def normal(self):
        return np.array_equal(self.matrix@self.dagger().matrix,self.dagger().matrix@self.matrix)
        
    def unitary(self):
        if self.matrix.shape[0]==self.matrix.shape[1]:
            return np.array_equal(np.matmul(self.matrix,self.dagger().matrix),np.identity(np.shape(self.matrix)[0]))
        else:
            raise ValueError("It is not a square Matrix")
        
    def tensor(self, *args):
        result = self.matrix
        for another in args:
            if not isinstance(another, Operator):
                raise ValueError("Tensor product can only be performed with Operators.")
            result = np.kron(result, another.matrix)
        return Operator(result)
        
    def commutator(self, another):
        if not isinstance(another, Operator):
            raise ValueError("Commutator can only be computed with another Operator.")
        return Operator(self.matrix @ another.matrix - another.matrix @ self.matrix)
    
    def anti_commutator(self, another):
        if not isinstance(another, Operator):
            raise ValueError("Anti-commutator can only be computed with another Operator.")
        return Operator(self.matrix @ another.matrix + another.matrix @ self.matrix)
    
    def spectral_decom(self):
        if not np.array_equal(self.matrix, self.dagger().matrix):
            raise ValueError("Not an Hermitian operators.")
        
        eigenvalues, eigenvectors = np.linalg.eigh(self.matrix)
        decomposition = []
        for i in range(len(eigenvalues)):
            eigenvalue = eigenvalues[i]
            eigenvector = eigenvectors[:, i]
            decomposition.append((eigenvalue, eigenvector))
        return decomposition

        
    def __repr__(self):
        return f'Operator({self.matrix})'
    
    def partial_trace(self, dims, subsystem):
        if not isinstance(dims, (list, tuple)) or not isinstance(subsystem, int):
            raise ValueError("Invalid dimensions or subsystem index.")

        if subsystem < 0 or subsystem >= len(dims):
            raise ValueError("Subsystem index out of range.")

        if np.prod(dims) != self.matrix.shape[0]:
            raise ValueError("Dimensions do not match the size of the matrix.")

        dim_A = dims[subsystem]
        dim_B = int(self.matrix.shape[0] / dim_A)

        reshaped_matrix = self.matrix.reshape([dim_A, dim_B, dim_A, dim_B])
        traced_matrix = np.trace(reshaped_matrix, axis1=0, axis2=2)

        return Operator(traced_matrix)
        
    def von_neumann_entropy(self):
        if not np.array_equal(self.matrix, self.dagger().matrix):
            raise ValueError("Von Neumann entropy can only be calculated for Hermitian operators.")

        eigenvalues = np.linalg.eigvalsh(self.matrix)
        eigenvalues = eigenvalues[eigenvalues > 0]
        entropy = -np.sum(eigenvalues * np.log(eigenvalues))
        return entropy
    

    pauli_x = [[0, 1], [1, 0]]
    pauli_y = [[0, -1j], [1j, 0]]
    pauli_z = [[1, 0], [0, -1]]
    identity = [[1, 0], [0, 1]]




