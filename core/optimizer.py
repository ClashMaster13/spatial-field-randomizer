import math
import random

def get_adj_plots(r, c, max_r, max_c):
    adj = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < max_r and 0 <= nc < max_c:
                adj.append((nr, nc))
    return adj

def calc_penalty(grids, r_count, c_count):
    pen = 0
    reps = len(grids)

    # 1. Column overlap check
    for c in range(c_count):
        col_lines = [grids[rep][r][c] for rep in range(reps) for r in range(r_count)]
        if len(col_lines) != len(set(col_lines)):
            pen += (len(col_lines) - len(set(col_lines))) * 5000

    # 2. Alley boundary check
    for rep in range(1, reps):
        top_prev = grids[rep - 1][-1]
        bot_curr = grids[rep][0]
        for c in range(c_count):
            if bot_curr[c] == top_prev[c]: pen += 10000
            if c > 0 and bot_curr[c] == top_prev[c - 1]: pen += 10000
            if c < c_count - 1 and bot_curr[c] == top_prev[c + 1]: pen += 10000

    # 3. Neighbor pair check
    pairs = {}
    for rep in range(reps):
        for r in range(r_count):
            for c in range(c_count):
                g1 = grids[rep][r][c]
                for nr, nc in get_adj_plots(r, c, r_count, c_count):
                    if (nr > r) or (nr == r and nc > c):
                        g2 = grids[rep][nr][nc]
                        p = tuple(sorted((g1, g2)))
                        pairs[p] = pairs.get(p, 0) + 1

    for count in pairs.values():
        if count > 1: pen += (count - 1) * 200

    # 4. Lateral edges (Col 1 and Col N only)
    edges = {}
    for rep in range(reps):
        for r in range(r_count):
            for c in [0, c_count - 1]:
                g = grids[rep][r][c]
                edges[g] = edges.get(g, 0) + 1

    for count in edges.values():
        if count > 1: pen += (count - 1) * 3000

    return pen

def run_sa_optimization(lines, num_reps, r_count, c_count, progress_callback=None):
    # Rep 1 is fixed serpentine
    r1 = [[None] * c_count for _ in range(r_count)]
    i = 0
    for r in range(r_count):
        cols = range(c_count) if r % 2 == 0 else range(c_count - 1, -1, -1)
        for c in cols:
            r1[r][c] = lines[i]
            i += 1

    all_grids = [r1]
    make_grid = lambda lst: [lst[i * c_count : (i + 1) * c_count] for i in range(r_count)]
    rep_lines = []
    
    for _ in range(1, num_reps):
        temp_lines = lines[:]
        random.shuffle(temp_lines)
        all_grids.append(make_grid(temp_lines))
        rep_lines.append(temp_lines)

    score = calc_penalty(all_grids, r_count, c_count)
    best_grids = [[row[:] for row in g] for g in all_grids]
    best_score = score

    t, alpha, iters = 400.0, 0.99995, 200000

    for step in range(iters):
        if best_score == 0: break
        
        if progress_callback and step % 20000 == 0:
            progress_callback(step / iters)

        target_rep = random.randint(1, num_reps - 1)
        idx1, idx2 = random.sample(range(len(lines)), 2)

        # swap
        rep_lines[target_rep - 1][idx1], rep_lines[target_rep - 1][idx2] = rep_lines[target_rep - 1][idx2], rep_lines[target_rep - 1][idx1]
        all_grids[target_rep] = make_grid(rep_lines[target_rep - 1])

        new_score = calc_penalty(all_grids, r_count, c_count)
        diff = new_score - score

        if diff < 0 or random.random() < math.exp(-diff / max(t, 1e-6)):
            score = new_score
            if score < best_score:
                best_score = score
                best_grids = [[row[:] for row in g] for g in all_grids]
        else:
            # revert
            rep_lines[target_rep - 1][idx1], rep_lines[target_rep - 1][idx2] = rep_lines[target_rep - 1][idx2], rep_lines[target_rep - 1][idx1]
            all_grids[target_rep] = make_grid(rep_lines[target_rep - 1])

        t *= alpha
        
    if progress_callback:
        progress_callback(1.0)
    return best_grids, best_score