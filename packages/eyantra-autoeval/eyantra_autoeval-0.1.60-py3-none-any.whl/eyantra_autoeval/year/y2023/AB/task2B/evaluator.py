"""
evaluator.py

This file is used as an utility in task 2B of AstroTinker Bot theme.
It generates the dump_txt.txt file which is used in the simulation.

"""
# standard imports
import os
import heapq

# graph map for our theme
graph_map = {
    "0":  [ "1"],
    "1":  [ "0",  "2", "29"],
    "2":  [ "1",  "3",  "8"],
    "3":  [ "2",  "4", "28"],
    "4":  [ "3",  "5",  "6"],
    "5":  [ "4"],
    "6":  [ "4",  "7"],
    "7":  [ "6",  "8"],
    "8":  [ "2",  "7",  "9", "12"],
    "9":  [ "8", "10", "11"],
    "11": [ "9"],
    "10": [ "9"],
    "12": [ "8", "13", "19"],
    "13": ["12", "14"],
    "14": ["13", "15", "16"],
    "15": ["14"],
    "16": ["14", "17", "18"],
    "17": ["16"],
    "18": ["16", "19"],
    "19": ["12", "18", "20"],
    "20": ["19", "21", "24", "29"],
    "21": ["20", "22", "23"],
    "22": ["21"],
    "23": ["21"],
    "24": ["20", "25"],
    "25": ["24", "26"],
    "26": ["25", "27", "28"],
    "27": ["26"],
    "28": [ "3", "26", "29"],
    "29": [ "1", "20", "28"]
}

# Dijkstra Algorithm
def dijkstra(graph, start, end):
    # Initialize distances and predecessors
    distances = {node: float('inf') for node in graph}
    predecessors = {node: None for node in graph}
    distances[start] = 0

    # Priority queue for nodes to visit
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in graph[current_node]:
            distance = current_distance + 1  # Assuming all edges have equal weight of 1

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the path from end to start
    path = []
    while end is not None:
        path.insert(0, end)
        end = predecessors[end]

    return path


# Find all the paths connected between two points
def find_all_paths(graph, start, end):

    # Find path using recursion
    def recursive_find_paths(current, path):
        if current == end:
            paths.append(path)
        else:
            for neighbor in graph[current]:
                if neighbor not in path:
                    recursive_find_paths(neighbor, path + [neighbor])

    paths = []
    recursive_find_paths(start, [start])

    return paths

# Function Evaluate
def evaluate():

    # Set path to generate dump file
    directory_path = "/simulation/modelsim/"

    try: # Exception Handling
        if os.path.isdir(os.getcwd() + directory_path):
            # Read user input
            SP = input("Enter Start Point (0 <= SP < 30): ")
            EP = input("Enter End Point   (0 <= EP < 30): ")
            print()

            if SP in graph_map and EP in graph_map:
                # Find the shortest path
                shortest_path = dijkstra(graph_map, SP, EP)

                if not shortest_path:
                    print("No path found between SP and EP.")
                else:
                    # Find all possible paths connecting two points
                    all_paths = find_all_paths(graph_map, SP, EP)

                    i = 1
                    if all_paths:
                        all_paths.insert(0, shortest_path)
                        for path in all_paths:
                            print("Path " + str(i)+ " -> " + str(path))
                            i += 1

                    print("\nChoose the path same as the path given by your t1b_path_planner.c.")

                    print("Path Number ranges from 1 to " + str(i-1))
                    path_no = int(input("Enter the path Number : "))

                    if 0 < path_no < i:
                        print("Path selected is " + str(all_paths[path_no-1]))
                        with open('simulation/modelsim/dump_txt.txt', 'w') as f:
                            for i in all_paths[path_no-1]:
                                f.write(i + '\n')
                        print("File dump_txt.txt has been created.")
                    else:
                        print("Enter Valid Path Number")

            else:
                print("Invalid start or end point!")

        else:
            print(f"The directory '{directory_path}' does not exist.")

    except Exception as e:
        print(f"An error occurred: {e}")

    # Do not generate JSON file
    result = {}
    result["generate"] = False
    return result
