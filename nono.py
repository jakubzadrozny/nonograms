from queue import *
import sys
sys.setrecursionlimit(11000)

MEM = dict()

def opt_dist(v, d):
    h = hash((tuple(v), tuple(d)))
    if h in MEM:
        return MEM[h]

    n, m = len(v), len(d)
    black, white = [0] * (n+1), n + 1
    for i in range(1, n + 1):
        black[i] = black[i-1] + (v[i-1] == 1)
        if v[i-1] == 2:
            white = min(white, i - 1)

    ok = [ [0] * (m+1) for i in range(n+1) ]
    ok[0][0] = 1
    for i in range(1, n+1):
        ok[i][0] = i - 1 < white
        for j in range(1, m+1):
            block = d[j-1]
            if i < block:
                continue
            elif i > block:
                optB = (black[i] == black[i-block]) * (v[i-block-1] != 2) * ok[i-block-1][j-1]
            else:
                optB = (black[i] == 0) * ok[0][j-1]
            optA = ok[i-1][j] * (v[i-1] != 2)
            ok[i][j] = optA + optB

    MEM[h] = ok[n][m]
    return ok[n][m]

def revise_line(line):
    x, type = line
    changed, check = [], []
    if type == 'row':
        lines, opts, k = rows, row_opts, m
        linepix = pixels[x]
    else:
        lines, opts, k = cols, col_opts, n
        linepix = [ pixels[i][x] for i in range(n) ]

    for i in range(k):
        if linepix[i] < 3:
            continue

        linepix[i] = 1
        optA = opt_dist(linepix, lines[x])
        linepix[i] = 2
        if optA == 0:
            dom = 2
        else:
            optB = opt_dist(linepix, lines[x])
            dom = 1 | 2*(optB > 0)

        linepix[i] = dom
        if dom == 0:
            break
        elif dom < 3:
            if type == 'row':
                pixels[x][i] = dom
                changed.append((x, i))
            else:
                pixels[i][x] = dom
                changed.append((i, x))

    if type == 'row':
        check = [ (p[1], 'col') for p in changed ]
    else:
        check = [ (p[0], 'row') for p in changed ]

    opts[x] = opt_dist(linepix, lines[x])

    return opts[x] > 0, changed, check

def full(pix = -1):
    q = Queue()
    if pix == -1:
        for x in range(n):
            q.put((x, 'row'))
        for x in range(m):
            q.put((x, 'col'))
    else:
        x, y = pix
        q.put((x, 'row'))
        q.put((y, 'col'))

    changed = []
    while not q.empty():
        line = q.get()
        succ, _changed, check = revise_line(line)
        changed += _changed
        if succ:
            for x in check:
                q.put(x)
        else:
            return False, changed

    return True, changed

f = open('zad_input.txt')
n, m = [int(x) for x in f.readline().strip().split()]

rows, cols = [], []
for i in range(n):
    row = [int(x) for x in f.readline().strip().split()]
    rows.append(row)
for i in range(m):
    col = [int(x) for x in f.readline().strip().split()]
    cols.append(col)

pixels = [ [3] * m for i in range(n) ]
row_opts, col_opts = [0] * n, [0] * m

full()

# BACKTRACK

s = set([ (x, y) for x in range(n) for y in range(m) if pixels[x][y] == 3])

def backtrack():
    if len(s) == 0:
        return True

    x, y = min(s, key=lambda a: min(row_opts[a[0]], col_opts[a[1]]))
    s.remove((x, y))

    global row_opts, col_opts
    row_cp, col_cp = row_opts[:], col_opts[:]

    pixels[x][y] = 1
    succ, changed = full((x, y))
    if succ:
        for p in changed:
            s.remove(p)
        if backtrack():
            return True

    row_opts, col_opts = row_cp, col_cp
    for px, py in changed:
        pixels[px][py] = 3
        s.add((px, py))

    pixels[x][y] = 2
    succ, changed = full((x, y))
    if succ:
        for p in changed:
            s.remove(p)
        if backtrack():
            return True

    row_opts, col_opts = row_cp, col_cp
    for px, py in changed:
        pixels[px][py] = 3
        s.add((px, py))
    pixels[x][y] = 3
    s.add((x, y))
    return False

backtrack()

with open('zad_output.txt', 'w') as f:
    for x in range(n):
        for y in range(m):
            if pixels[x][y] == 1:
                print('.', end='', file=f)
            else:
                print('#', end='', file=f)
        print(file=f)
