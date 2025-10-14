import torch
from numbers import Real
def rowswap(m: torch.Tensor, sourceRow: int, targetRow: int):
        m[[sourceRow,targetRow]] = m[[targetRow, sourceRow]]


def rowscale(m: torch.Tensor, sourceRow: int, scaleFact: float) -> torch.Tensor:
    # for a matrix m = [n][m], we need to index:
    # tempMat[sourceRow][m] = tempMat[sourceRow][m] * scaleFact
    # we can also use this: [element * scaleFact for element in m[sourceRow]]

    tempMat = m.detach().clone()
    if isinstance(scaleFact, Real) == False:
         raise("Please use a real number for the scaleFact")
    for c in range(len(m.T)):
        tempMat[sourceRow][c] = tempMat[sourceRow][c] * scaleFact
    # print(tempMat.size())
    return tempMat

def rowreplacement(m: torch.Tensor, fRow: int, sRow: int, j: float, k: float):
    
    # scale the first row
    scaledFirstRow = rowscale(m, fRow, j)
    # print(scaledFirstRow)
    # scale the second row
    scaledSecondRow = rowscale(m, sRow, k)
    m += scaledFirstRow + scaledSecondRow

  
def rref(m: torch.Tensor):
    # We have to iterate over each row and check if they are non-zero.
    # If any are, we should:
    #   reduce them so that the leading row above has 1 in the pivot
    # We should swap the rows if any leading zeros are found, making sure all-zero rows stay at the bottom.
    nRows = m.shape[0]
    nCols = m.shape[1]
    pivotRow = 0
    # this is will go down the columns
    for col in range(nCols):
        for row in range(pivotRow, nRows):
          if m[row, col] != 0:
            # now we reduce the rows
            rowswap(m, pivotRow, row)
            # now make pivot one
            pivot_element = m[pivotRow, col]
            # divide by the floor of the pivot element
            m[pivotRow] //= pivot_element
            # elimenate below
            for row in range(pivotRow + 1, nRows):
              factor = m[row, col]
              m[row] -= factor * m[pivotRow]
            pivotRow += 1
