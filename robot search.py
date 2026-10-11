import heapq
import time

MAP_A = [
    "S..#....",
    "##.#.##.",
    "....~~..",
    ".####.#.",
    "...~..#G",
]
MAP_B = [
    "S~~~~~~~G",
    ".#######.",
    ".........",
    ".#.#.#.#.",
    ".........",
]
MAP_C = [
    "S..#....",
    ".#.#.##.",
    "...#..#.",
    ".###.##.",
    "....#..G",
]

GRID = MAP_A  # change this to pick the map for the single run

COSTS = {'.': 1, '~': 3, 'S': 1, 'G': 1}      # cost of stepping INTO a cell
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]    # up, down, left, right


def find(grid, symbol):
    # look through the grid for S or G and return its (row, col)
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == symbol:
                return (r, c)


def get_moves(grid, cell):
    # every neighbour we can step to, with the cost of stepping there
    r, c = cell
    result = []
    for row_change, col_change in MOVES:
        next_row, next_col = r + row_change, c + col_change
        if 0 <= next_row < len(grid) and 0 <= next_col < len(grid[next_row]) and grid[next_row][next_col] != '#':
            result.append(((next_row, next_col), COSTS[grid[next_row][next_col]]))
    return result


def build_path(came_from, goal):
    # follow the "came from" links backwards from G to S, then flip it
    path = []
    cell = goal
    while cell is not None:
        path.append(cell)
        cell = came_from[cell]
    return path[::-1]


def dfs(grid, start, goal):
    stack = [start]
    came_from = {start: None}
    visited = set()
    expanded = 0

    while stack:
        cell = stack.pop()              # newest cell first = go deep
        if cell in visited:
            continue
        visited.add(cell)
        expanded += 1

        if cell == goal:
            return build_path(came_from, goal), expanded

        for next_cell, cost in get_moves(grid, cell):
            if next_cell not in visited:
                if next_cell not in came_from:
                    came_from[next_cell] = cell
                stack.append(next_cell)

    return None, expanded


def astar(grid, start, goal):
    def guess(cell):
        # manhattan distance to the goal
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

    count = 0  # breaks ties so heapq never has to compare two cells
    frontier = [(guess(start), count, 0, start)]   # (f, count, cost so far, cell)
    came_from = {start: None}
    best_cost = {start: 0}
    done = set()
    expanded = 0

    while frontier:
        f, _, cost_so_far, cell = heapq.heappop(frontier)   # lowest f first
        if cell in done:
            continue    # old entry, we already handled a cheaper one
        done.add(cell)
        expanded += 1

        if cell == goal:
            return build_path(came_from, goal), expanded

        for next_cell, step in get_moves(grid, cell):
            new_cost = cost_so_far + step
            # only keep this route if it's the cheapest we've found to that cell
            if next_cell not in best_cost or new_cost < best_cost[next_cell]:
                best_cost[next_cell] = new_cost
                came_from[next_cell] = cell
                count += 1
                heapq.heappush(frontier, (new_cost + guess(next_cell), count, new_cost, next_cell))

    return None, expanded


def run(name, algorithm, grid):
    start, goal = find(grid, 'S'), find(grid, 'G')

    t = time.perf_counter()
    path, expanded = algorithm(grid, start, goal)
    run_time_ms = (time.perf_counter() - t) * 1000

    cost = None
    if path:
        cost = sum(COSTS[grid[r][c]] for r, c in path[1:])   # S isn't counted
    return name, path, cost, expanded, run_time_ms


def show(grid, result):
    name, path, cost, expanded, run_time_ms = result
    print("Algorithm:", name)
    if path is None:
        print("No path found")
    else:
        print("Path:", path)
        print("Total cost:", cost)
        picture = [list(row) for row in grid]
        for r, c in path:
            if picture[r][c] not in 'SG':
                picture[r][c] = '*'
        for row in picture:
            print("".join(row))
    print("Nodes expanded:", expanded)
    print()


# single run on the chosen map
for name, algorithm in [("DFS", dfs), ("A*", astar)]:
    show(GRID, run(name, algorithm, GRID))

# table for all three maps
print(f"{'Map':<7}{'Algo':<6}{'Length':<8}{'Cost':<6}{'Expanded':<10}{'Time(ms)'}")
for map_name, grid in [("MAP_A", MAP_A), ("MAP_B", MAP_B), ("MAP_C", MAP_C)]:
    for name, algorithm in [("DFS", dfs), ("A*", astar)]:
        _, path, cost, expanded, run_time_ms = run(name, algorithm, grid)
        length = len(path) - 1 if path else "-"
        cost = cost if path else "-"
        print(f"{map_name:<7}{name:<6}{str(length):<8}{str(cost):<6}{expanded:<10}{run_time_ms:.3f}")
