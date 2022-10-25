import itertools
import numpy as np

ASSIGNED = 1
CROSSED = 2

# Subtract row minima
def step1(cost_matrix):
    h, w = cost_matrix.shape
    for i in range(h):
        min_v = cost_matrix[i, 0]
        for j in range(1, w):
            if cost_matrix[i, j] < min_v:min_v = cost_matrix[i, j]
        for j in range(w):cost_matrix[i, j]-=min_v
    return cost_matrix

# Subtract column minima
def step2(cost_matrix):
    h, w = cost_matrix.shape
    for j in range(w):
        min_v = cost_matrix[0, j]
        for i in range(1, h):
            if cost_matrix[i, j] < min_v:min_v = cost_matrix[i, j]
        for i in range(h):cost_matrix[i, j]-=min_v
    return cost_matrix

# Cover all zeros with a minimum number of lines
def step3(cost_matrix):

    def assign_target(matrix, mask_matrix, row_zeros, row, col):
        n = matrix.shape[0]

        for c in range(n):
            if matrix[row, c] == 0 and mask_matrix[row, c] == 0:
                mask_matrix[row, c] = CROSSED
        for r in range(n):
            if matrix[r, col] == 0 and mask_matrix[r, col] == 0:
                mask_matrix[r, col] = CROSSED
                row_zeros[r] -= 1
        mask_matrix[row, col] = ASSIGNED

    def assign_matrix(matrix, mask_matrix, row_marked, row_zeros, force_assign=False):
        n = matrix.shape[0]
        for r in range(n):
            if row_zeros[r] == 1 or (row_zeros[r] > 1 and force_assign):
                for c in range(n):
                    if matrix[r, c] == 0 and mask_matrix[r, c] == 0:
                        assign_target(matrix, mask_matrix, row_zeros, r, c)
                        row_zeros[r] = 0
                        row_marked[r] = False
                        return True
        return False

    n = cost_matrix.shape[0]
    mask_matrix = np.zeros_like(cost_matrix)
    row_marked, col_marked = [True] * n, [False] * n
    row_zeros = [0] * n
    for r in range(n):
        for c in range(n):
            if cost_matrix[r, c] == 0:row_zeros[r]+=1

    while True:
        update = assign_matrix(cost_matrix, mask_matrix, row_marked, row_zeros, force_assign=False)
        if not update:
            update = assign_matrix(cost_matrix, mask_matrix, row_marked, row_zeros, force_assign=True)
        if not update:break

    while True:
        update = False
        for r in range(n):
            if not row_marked[r]:continue
            for c in range(n):
                if not col_marked[c] and cost_matrix[r, c] == 0:
                    col_marked[c] = True
                    update = True
        if not update:break
        for c in range(n):
            if not col_marked[c]:continue
            for r in range(n):
                if not row_marked[r] and mask_matrix[r, c] == ASSIGNED:
                    row_marked[r] = True
                    update = True
        if not update:break

    rows, cols = list(range(n)), list(range(n))
    line_nums = 0
    for r in range(n):
        if not row_marked[r]:
            rows.remove(r)
            line_nums += 1
    for c in range(n):
        if col_marked[c]:
            cols.remove(c)
            line_nums += 1
    return line_nums, rows, cols, mask_matrix

# Create additional zeros
def step4(cost_matrix, rows, cols):
    h, w = cost_matrix.shape
    min_v = cost_matrix[rows[0], cols[0]]
    for i in rows:
        for j in cols:
            if cost_matrix[i, j] < min_v:min_v = cost_matrix[i, j]
    for i, j in itertools.product(range(h), range(w)):
        if i not in rows and j not in cols:
            cost_matrix[i, j] += min_v
        if i in rows and j in cols:
            cost_matrix[i, j] -= min_v
    return cost_matrix

def step5(mask_matrix, H, W):

    h, w = mask_matrix.shape
    res_rows, res_cols = [], []
    for r in range(h):
        for c in range(w):
            if mask_matrix[r, c] == ASSIGNED:
                if r < H and c < W:
                    res_rows.append(r)
                    res_cols.append(c)
                break
    return res_rows, res_cols

def munkres(cost_matrix):
    h, w = cost_matrix.shape
    nums = max(h, w)
    cost = np.zeros((nums, nums))
    for i in range(h):
        for j in range(w):
            cost[i,j] = cost_matrix[i,j]
    cost = step2(step1(cost))

    while True:
        line_nums, rows, cols, mask_matrix = step3(cost)
        if line_nums < nums:
            cost = step4(cost, rows, cols)
        else:
            return step5(mask_matrix, h, w)


if __name__ == '__main__':

    # https://www.hungarianalgorithm.com/solve.php
    cost_matrix = np.array([[4, 1, 3, 3, 4],
                            [2, 0, 5, 1, 5],
                            [3, 2, 2, 5, 2],
                            [2, 4, 1, 6, 3],
                            [1, 4, 6, 2, 3],
                            [0, 4, 2, 3, 5]])

    # cost_matrix = np.array([[0.4, 0.1, 0.3, 0.3, 0.4],
    #                         [0.2, 0.0, 0.5, 0.1, 0.5],
    #                         [0.3, 0.2, 0.2, 0.5, 0.2],
    #                         [0.2, 0.4, 0.1, 0.6, 0.3],
    #                         [0.1, 0.4, 0.6, 0.2, 0.3],
    #                         [0.0, 0.4, 0.2, 0.3, 0.5]])



    print(munkres(cost_matrix))