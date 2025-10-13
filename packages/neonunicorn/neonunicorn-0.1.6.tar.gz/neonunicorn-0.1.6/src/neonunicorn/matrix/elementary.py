# elementary.py
import torch

# Function to swap two rows in a matrix
def rowswap(matrix, row1, row2):
    """
    Swap row1 and row2 in the given PyTorch matrix.
    
    Args:
        matrix (torch.Tensor): Input 2D tensor
        row1 (int): Index of the first row
        row2 (int): Index of the second row
    
    Returns:
        torch.Tensor: New matrix with rows swapped
    """
    mat = matrix.clone()  # make a copy to avoid changing original
    mat[[row1, row2]] = mat[[row2, row1]]  # swap the rows
    return mat

# Example usage
if __name__ == "__main__":
    M = torch.tensor([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])
    
    print("Original matrix:\n", M)
    swapped = rowswap(M, 0, 2)
    print("After swapping row 0 and row 2:\n", swapped)
def rowscale(matrix, row_index, factor):
    mat = matrix.clone().float()
    mat[row_index] = mat[row_index] * factor
    return mat
def rowreplacement(matrix, target_row, source_row, j=1, k=1):
    mat = matrix.clone().float()
    mat[target_row] = j * mat[target_row] + k * mat[source_row]
    return mat


import torch

M = torch.tensor([[1,2,3],[4,5,6],[7,8,9]])
print("Original matrix:\n", M)

# Test rowscale
print("After scaling row 0 by 3:\n", rowscale(M, 0, 3))

# Test rowreplacement
print("After row replacement (2*R0 + 3*R1 on row 0):\n", rowreplacement(M, 0, 1, 2, 3))
# elementary.py
import torch

# 1. Swap rows
def rowswap(matrix, row1, row2):
    mat = matrix.clone()
    mat[[row1, row2]] = mat[[row2, row1]]
    return mat

# 2. Scale a row
def rowscale(matrix, row_index, factor):
    mat = matrix.clone().float()  # Ensure float for multiplication
    mat[row_index] = mat[row_index] * factor
    return mat

# 3. Row replacement: j*Ri + k*Rj -> Ri
def rowreplacement(matrix, target_row, source_row, j, k):
    mat = matrix.clone().float()
    # Scale rows
    scaled_target = rowscale(mat, target_row, j)
    scaled_source = rowscale(mat, source_row, k)
    # Combine rows
    mat[target_row] = scaled_target[target_row] + scaled_source[source_row]
    return mat

# Example usage:
if __name__ == "__main__":
    M = torch.tensor([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])

    print("Original matrix:\n", M)

    # Test rowswap
    M_swap = rowswap(M, 0, 2)
    print("\nAfter swapping row 0 and row 2:\n", M_swap)

    # Test rowscale
    M_scale = rowscale(M, 0, 3)
    print("\nAfter scaling row 0 by 3:\n", M_scale)

    # Test rowreplacement
    M_replace = rowreplacement(M, 0, 1, 2, 3)
    print("\nAfter row replacement (2*R0 + 3*R1 on row 0):\n", M_replace)
import torch

def rref(matrix):
    mat = matrix.clone().float()  # make a copy and float for division
    rows, cols = mat.shape
    pivot_row = 0

    for col in range(cols):
        if pivot_row >= rows:
            break  # finished all rows
        
        # If pivot is 0, try to swap with a row below
        if mat[pivot_row, col] == 0:
            for r in range(pivot_row + 1, rows):
                if mat[r, col] != 0:
                    mat = rowswap(mat, pivot_row, r)
                    break
        
        # If pivot is still 0, go to next column
        if mat[pivot_row, col] == 0:
            continue
        
        # Scale pivot to 1
        factor = 1 / mat[pivot_row, col]
        mat = rowscale(mat, pivot_row, factor)
        
        # Eliminate elements below pivot
        for r in range(pivot_row + 1, rows):
            mat = rowreplacement(mat, r, pivot_row, 1, -mat[r, col])
        
        pivot_row += 1
    
    return mat

# Example
M = torch.tensor([[2, 4, -2],
                  [4, 9, -3],
                  [-2, -3, 7]])

rref_M = rref(M)
print("Reduced Row Echelon Form:\n", rref_M)
import torch

def rref_full(matrix):
    mat = matrix.clone().float()  # Convert to float for division
    rows, cols = mat.shape
    
    pivot_row = 0
    for col in range(cols):
        if pivot_row >= rows:
            break
            
        # Find pivot in current column
        if mat[pivot_row, col] == 0:
            for r in range(pivot_row + 1, rows):
                if mat[r, col] != 0:
                    mat = rowswap(mat, pivot_row, r)
                    break
        
        if mat[pivot_row, col] == 0:
            continue
        
        # Scale pivot to 1
        factor = 1 / mat[pivot_row, col]
        mat = rowscale(mat, pivot_row, factor)
        
        # Eliminate elements below pivot
        for r in range(pivot_row + 1, rows):
            mat = rowreplacement(mat, r, pivot_row, 1, -mat[r, col])
        
        # Eliminate elements above pivot
        for r in range(0, pivot_row):
            mat = rowreplacement(mat, r, pivot_row, 1, -mat[r, col])
        
        pivot_row += 1
    
    return mat

# Example
M = torch.tensor([[2, 4, -2],
                  [4, 9, -3],
                  [-2, -3, 7]])

rref_M = rref_full(M)
print("Full Reduced Row Echelon Form:\n", rref_M)
if __name__ == "__main__":
    import torch

    # Step 8 input matrix
    M = torch.tensor([
        [1, 3, 0, 0, 3],
        [0, 0, 1, 0, 9],
        [0, 0, 0, 1, -4]
    ]).float()  # float is better for row operations

    print("Original Matrix:\n", M)

    # 1. R1 $ R2 using rowswap
    M1 = rowswap(M, 0, 1)
    print("\nAfter swapping R1 and R2:\n", M1)

    # 2. 1/3 * R1 using rowscale
    M2 = rowscale(M1, 0, 1/3)
    print("\nAfter scaling R1 by 1/3:\n", M2)

    # 3. R3 = -3 * R1 + R3 using rowreplacement
    M3 = rowreplacement(M2, 2, 0, 1, -3)
    print("\nAfter row replacement R3 = -3*R1 + R3:\n", M3)