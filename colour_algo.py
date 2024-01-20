import networkx as nx
from collections import Counter
from random import choice
from graph import cg
from typing import Dict, List, Any
from pprint import pprint as print
# from json import dump

# colors represent the time slots available
# the key of this dict is the colour, and the value is the room list
coloring: Dict[int, List[Any]] = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
}

# maxNodePerColor is equal to number of rooms available for one time slot
maxNodePerColor = 2
# maxColors is equal to maximum number of time slots over two days
maxColors = 8
# maximum penalty allowed for node to be considered
maxPenalty = 5

# the main evaluation function
def evaluateColour(G:nx.Graph, node: int, selectedColor: int, day: int, colours: Dict[int, List[Any]]) -> int:
    clash_count = 0
    idle_count = 0
    room_change_count = 0
    # node being considered
    gNode = G.nodes[node]
    GNode = {
        "sv": gNode["supervisors"],
        "p": gNode["panels"],
        "color": selectedColor,
        "day": day
    }
    for k, evaluationNodes  in colours.items():
        for evaluationNode in evaluationNodes:
            # evaluationNode is the node used to evaluate coloring for node being considered 
            if evaluationNode != gNode:
                eNode = G.nodes[evaluationNode]
                eColor = lambda : eNode["color"] if eNode["color"] is not None else 0
                eDay = lambda : eNode["day"] if eNode["day"] is not None else 0
                ENode = {
                    "sv" : eNode["supervisors"],
                    "p" : eNode["panels"],
                    "color": eColor(),
                    "day": eDay()
                }
                if same_day(GNode, ENode):
                    # same color means same time slot
                    # clashing only happens when supervisor has to be a panel in a different room in the same time slot
                    if GNode["color"] == ENode["color"]:
                        clash = count_clash(GNode, ENode)
                        clash_count += clash
                    # checks for consecutive time slot
                    elif GNode["color"] - ENode["color"] == 1:
                        room_change = count_room_change(GNode, ENode)
                        room_change_count += room_change
                    idle_slots = count_idle_slot(GNode, ENode)
                    idle_count += idle_slots
    return 2 * clash_count + idle_count**2 + room_change_count

def count_clash(node: Any, eNode: Any) -> int:
    # count how many panels of current node is a supervisor in other node
    # also include clashes where a student share a supervisor in the same time slot
    combined_list = node['sv'] + node['p'] + eNode['sv'] + eNode['p']
    # Count unique occurrences using Counter
    unique_occurrences = Counter(combined_list)
    count = 0
    for sv, occurence in unique_occurrences.items():
        if occurence > 1:
            count += occurence // 2
    return count

def count_idle_slot(node: Dict[str, Any], eNode: Any) -> int:
    idle_slots = 0
    # check if current node has any panel in the checking node
    count = sum([i in node["p"] for i in eNode["p"]])
    if count > 0:
        for i in range(0, count):
        # count how many idle slots are there
        # idling can only happen once due to having only 4 slots per day
            diff = node["color"] - eNode["color"] - 1
            if diff > 0:
                idle_slots += diff
    return idle_slots

def count_room_change(node: Any, eNode: Any) -> int:
    # total panel that needs to swap place after one time slot
    count = sum([i in node["p"] for i in eNode["p"]])
    return 1 * count

def same_day(node: Any, eNode: Any) -> bool:
    # Check if the same day
    return node['day'] == eNode['day']

def get_day(color: int) -> int:
    # returns the day for each time slot
    if color <= 4:
        return 1
    else:
        return 2

def run(G: nx.Graph):
    # counter to track how many nodes have been coloured i.e. how many students have been assigned a time slot
    coloredNodes = 0
    totalNodes = G.number_of_nodes()

    for node in G.nodes():
        neighbours: list[int] = list(G.neighbors(node))
        # get neighbouring colors
        neighbourColors = [
            G.nodes[neighbour]["color"]
            if G.nodes[neighbour].get("color") is not None
            else 0
            for neighbour in neighbours
        ]
        # available colors should only include colors that are not used by neighbours
        # available colors should also only include colors that have only been used once. 
        # this is because colors that have been used twice means the time slot represented by the color has been filled.
        availableColors: list[int] = [
            i
            for i in range(1, maxColors + 1)
            if i not in neighbourColors and len(coloring[i]) < maxNodePerColor
        ]
        # check if availableColors include color that exceeds maximum color
        # if exceed, then the search is stopped prematurely
        if max(availableColors, default=0) > maxColors:
            print("Exceeded color limit")
            return
        # check if no colors are available
        # if no colors, then the search is stopped prematurely
        if len(availableColors) == 0:
            print("No solution is obtained")
            return
        # main loop to iterate through possible next node to be put into sequence
        while True:
            # this is needed to check if the loop is still unable to find available colors(slots) to be selected based on penalty
            if len(availableColors) == 0:
                print("No solution is obtained")
                return
            selectedColor = min(availableColors)
            day = get_day(selectedColor)
            penalty = evaluateColour(G, node, selectedColor, day, coloring)
            # print(f"Colour: {selectedColor} Penalty: {penalty}")
            if penalty <= maxPenalty:
                coloring[selectedColor].append(node)
                G.nodes[node]["color"] = selectedColor
                G.nodes[node]["day"] = day
                G.nodes[node]["penalty"] = penalty
                break
            # remove colors(slots) that the current node cannot select
            availableColors.remove(selectedColor)
        if coloredNodes == totalNodes:
            break

    fullResult = True
    print(f"{coloring}")
    print(f"Total penalty = {sum([G.nodes[node]["penalty"] for node in G.nodes()])}")
    if fullResult:
        for key, c in coloring.items():
            for i in c:
                color = {
                    "Day": G.nodes[i]["day"],
                    "Slot": key,
                    "Student": i,
                    "Supervisors": G.nodes[i]["supervisors"],
                    "Panels": G.nodes[i]["panels"],
                    "Penalty": G.nodes[i]["penalty"]
                }
                print(color, sort_dicts=False)
run(cg)
