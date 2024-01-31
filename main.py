from contest import Contest
import itertools
import copy
import matplotlib.pyplot as plt
import json
import numpy as np


def are_games_neighbors(game1, game2):
    are_games_neighbors = 0
    type = None
    reputation = None
    contests = []

    for contest_id in game1:

        if are_games_neighbors > 2:
            break

        game_1_contest_players = game1[contest_id]._players
        game_2_contest_players = game2[contest_id]._players

        for players_tuple_id in reversed(range(len(game_1_contest_players))):
            game_1_players_tuple = game_1_contest_players[players_tuple_id]
            game_2_players_tuple = game_2_contest_players[players_tuple_id]

            if abs(game_1_players_tuple["amount"] - game_2_players_tuple["amount"]) == 1:
                are_games_neighbors += 1
                type = game_1_players_tuple["type"]
                reputation = game_1_players_tuple["reputation"]
                contests.append(contest_id)
            elif abs(game_1_players_tuple["amount"] - game_2_players_tuple["amount"]) > 1:
                return None


    if are_games_neighbors == 2:
        return {"hash": str(type)+"_"+str(reputation), "contests": contests}
    else:
        return None


def zip_players_list(flat_players_list):
    player_creation_instructions = dict()

    for player in flat_players_list:
        if player in player_creation_instructions:
            player_creation_instructions[player]["amount"] += 1
        else:
            player_creation_instructions[player] = {"type": player, "amount": 1}

    return list(player_creation_instructions.values())


def is_game_in_equilibrium(game_to_test, games, neighbors_of_game, games_map, verbose = False):
    game = games[game_to_test]
    is_game_in_equilibrium_bool = True
    for game_id in range(len(neighbors_of_game)):
        # If this game is an actual neighbor (has only one player in one contest that moved)
        if neighbors_of_game[game_id] is not None:
            contest_one = neighbors_of_game[game_id]["contests"][0]
            contest_two = neighbors_of_game[game_id]["contests"][1]
            relevant_player = neighbors_of_game[game_id]["hash"]
            op_game = games[game_id]

            players_tuple_in_op_game_contest_one = next(player_tuple for player_tuple in op_game[contest_one]._players if str(player_tuple["type"])+"_"+str(player_tuple["reputation"]) == relevant_player)
            players_tuple_in_op_game_contest_two = next(player_tuple for player_tuple in op_game[contest_two]._players if str(player_tuple["type"])+"_"+str(player_tuple["reputation"]) == relevant_player)
            players_tuple_in_game_contest_one = next(player_tuple for player_tuple in game[contest_one]._players if str(player_tuple["type"])+"_"+str(player_tuple["reputation"]) == relevant_player)
            players_tuple_in_game_contest_two = next(player_tuple for player_tuple in game[contest_two]._players if str(player_tuple["type"])+"_"+str(player_tuple["reputation"]) == relevant_player)

            # If the player is in contest one in the neighbor game, the player is in contest two in current game
            if players_tuple_in_op_game_contest_one["amount"] > players_tuple_in_game_contest_one["amount"]:
                if op_game[contest_one]._contest_result is not None and relevant_player in op_game[contest_one]._contest_result:
                    if op_game[contest_one]._contest_result[relevant_player]["amount"] < players_tuple_in_op_game_contest_one["amount"]:
                        player_utility_in_op_game = 0
                    else:
                        player_utility_in_op_game = op_game[contest_one]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_op_game = 0

                if game[contest_two]._contest_result is not None and relevant_player in game[contest_two]._contest_result:
                    if game[contest_two]._contest_result[relevant_player]["amount"] < players_tuple_in_game_contest_two["amount"]:
                        player_utility_in_game = 0
                    else:
                        player_utility_in_game = game[contest_two]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_game = 0

            # If the player is in contest two in the neighbor game, the player is in contest one in current game
            else:
                if op_game[contest_two]._contest_result is not None and relevant_player in op_game[contest_two]._contest_result:
                    if op_game[contest_two]._contest_result[relevant_player]["amount"] < players_tuple_in_op_game_contest_two["amount"]:
                        player_utility_in_op_game = 0
                    else:
                        player_utility_in_op_game = op_game[contest_two]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_op_game = 0

                if game[contest_one]._contest_result is not None and relevant_player in game[contest_one]._contest_result:
                    if game[contest_one]._contest_result[relevant_player]["amount"] < players_tuple_in_game_contest_one["amount"]:
                        player_utility_in_game = 0
                    else:
                        player_utility_in_game = game[contest_one]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_game = 0

            if player_utility_in_game < player_utility_in_op_game:
                if verbose:
                    print(game_to_test, "<", game_id, "For player of type", relevant_player)
                if games_map.get(game_to_test) is None:
                    games_map[game_to_test] = []
                games_map[game_to_test].append(game_id)

                is_game_in_equilibrium_bool = False

    return is_game_in_equilibrium_bool

def find_inner_cycles(game_map, current_game_id, stack, games_with_loops):
    if current_game_id in games_with_loops:
        return

    following_games = game_map.get(current_game_id)

    if following_games is None:
        return

    for game in following_games:
        if game in stack:
            print("loop found! \n")

            stack.append(game)
            for game_in_stack in stack:
                games_with_loops.append(game_in_stack)

            print_stack(stack)
            stack.pop()
        else:
            stack.append(game)
            find_inner_cycles(game_map, game, stack, games_with_loops)
            stack.pop()

def print_stack(stack):
    result = ""
    for number in stack:
        result = result + str(number) + "->"
    print(result)
# initialize the game settings

# This tuple list represents the players in the game
# The first value is the player's type (the lower the type - the stronger the player)
# The second value is the amount of players of this type to compete in the game.
# NOTICE: the program assumes that the strong player shows first in the list of tuples

def run_simulation(config, verbose):
    player_creation_instructions = config["player_creation_instructions"]
    config["contests"]

    contests_count = len(config["contests"])
    arrangements = list()
    for player_tuple in player_creation_instructions:
        amount_of_players = player_tuple["amount"]
        rng = list(range(amount_of_players + 1)) * contests_count
        if len(arrangements) == 0:
            for perm in set(i for i in itertools.permutations(rng, contests_count) if sum(i) == amount_of_players):
                arrangement = dict()
                for contest in range(len(perm)):
                    arrangement[contest] = []
                    arrangement[contest].append({"type": player_tuple["type"], "amount": perm[contest], "reputation": player_tuple["reputation"], "score": player_tuple["score"]})
                arrangements.append(arrangement)
        else:
            new_arrangements = list()
            for arrangement in arrangements:
                for perm in set(i for i in itertools.permutations(rng, contests_count) if sum(i) == amount_of_players):
                    new_arrangement = copy.deepcopy(arrangement)
                    for contest in range(len(perm)):
                        new_arrangement[contest].append({"type": player_tuple["type"], "amount": perm[contest], "reputation": player_tuple["reputation"], "score": player_tuple["score"]})
                    new_arrangements.append(new_arrangement)
            arrangements = new_arrangements

    # Make sure that in each arrangement
    # For each arrangement
    for arrangement_id in reversed(range(len(arrangements))):
        is_arrangement_valid = True

        # Check the validity of each contest
        for contest_id in arrangements[arrangement_id]:

            # Sum the amount of players in the contest
            number_of_players_in_contest = 0
            for player_tuple in arrangements[arrangement_id][contest_id]:
                number_of_players_in_contest += player_tuple["amount"]

            if number_of_players_in_contest > config["contests"][contest_id]["maxAllowedPlayers"]:
                is_arrangement_valid = False
            else:
                for player_tuple in arrangements[arrangement_id][contest_id]:
                    if player_tuple["amount"] > 0 and player_tuple["score"] < config["contests"][contest_id]["minimum_score"]:
                        is_arrangement_valid = False
                 

        if not is_arrangement_valid:
            del arrangements[arrangement_id]

    games = list()

    for i in range(len(arrangements)):
        arrangement = arrangements[i]
        # We now needs to create contests.
        # Each arrangement is a game

        game = dict()
        for contest_id in arrangement:

            players = arrangement[contest_id]
            game[contest_id] = Contest(config["contests"][contest_id]["prize"])
            game[contest_id].add_players(players)
            game[contest_id].calculate_inner_equilibrium()
        games.append(game)
    games_effort = {}
    for game_id in range(len(games)):
        if verbose:
            print()
            print()
            print(game_id)
        sum_effort = 0
        game_effort = {}
        for contest_id in games[game_id]:
            if(games[game_id][contest_id]._contest_result is not None):
                total_effort_in_contest = sum(item['effort'] * item['amount'] for item in games[game_id][contest_id]._contest_result.values())                    
                sum_effort += total_effort_in_contest
                game_effort[contest_id] = total_effort_in_contest
            else:
               total_effort_in_contest = 0
                    
            if verbose:
                print(games[game_id][contest_id])
                print(games[game_id][contest_id]._contest_result)
                print()
                print("Total effort: ", total_effort_in_contest)

        game_effort["total_effort"] = sum_effort
        games_effort[game_id] = game_effort
       #clea if verbose:
            #print(sum_effort)


    games_utility = {}
    for game_id in range(len(games)):
        # if verbose:
        #     print(game_id)
        sum_utility = 0
        for contest_id in games[game_id]:
            # if verbose:
            #     print(games[game_id][contest_id])
            #     print(games[game_id][contest_id]._contest_result)
            if games[game_id][contest_id]._contest_result is not None:
                for player_type in games[game_id][contest_id]._contest_result:
                    player_type_tuple = games[game_id][contest_id]._contest_result[player_type]
                    sum_utility += player_type_tuple['utility']*player_type_tuple['amount']
        games_utility[game_id] = sum_utility
        # if verbose:
        #     print(games_utility)

    if verbose:
        print("\n")
    neighbors_matrix = []

    for game_id in range(len(games)):
        neighbors_matrix.append([])
        for j in range(len(games)):
            neighbors_matrix[game_id].append(are_games_neighbors(games[game_id], games[j]))

    games_in_equilibrium = []
    games_map = {}

    for game_id in range(len(neighbors_matrix)):
        game = games[game_id]
        neighbors_of_game = neighbors_matrix[game_id]
        if is_game_in_equilibrium(game_id, games, neighbors_of_game, games_map, verbose):
            games_in_equilibrium.append(game_id)
    if config['check_loops'] == 1:
        if verbose:
            print()
            print()
            print()
        games_without_loops = []
        for game in games_map:
            find_inner_cycles(games_map, game, [game], games_without_loops)

    if verbose:
        print()
        print()
        print()

    if verbose:
        print("Games in equilibrium: ")

        for game_id in games_in_equilibrium:

            print(game_id)
            for contest_id in games[game_id]:
                print(games[game_id][contest_id])
                print(games[game_id][contest_id]._contest_result)
            print("\n")


    max_utility = -1
    max_utility_game = -1
    for game_index in range(len(games_utility)):
        if max_utility < games_utility[game_index]:
            max_utility = games_utility[game_index]
            max_utility_game = game_index

    max_effort = -1
    max_effort_game = -1
    for game_index in range(len(games_effort)):
        if max_effort < games_effort[game_index]["total_effort"]:
            max_effort = games_effort[game_index]["total_effort"]
            max_effort_game = game_index

    min_effort = 99999999999999999
    min_effort_game = 9999999999999
    for game_index in range(len(games_effort)):
        if min_effort > games_effort[game_index]["total_effort"]:
            min_effort = games_effort[game_index]["total_effort"]
            min_effort_game = game_index

    no_equilibrium = False

    if len(games_in_equilibrium) == 0:
        no_equilibrium = True
        if verbose:
            print("No equilibrium")

    if verbose:
        print()
        print()
        print()


        for game_index in range(len(games_utility)):
            if max_utility == games_utility[game_index]:
                print("Max utility is in game: ", game_index, "with utility of ", max_utility)
                for contest_id in games[game_index]:
                    print(games[game_index][contest_id])
                    print(games[game_index][contest_id]._contest_result)

        print()
        print("Max effort is in game: ", max_effort_game , "with effort of ", max_effort)
        for contest_id in games[max_effort_game]:
            print(games[max_effort_game][contest_id])
            print(games[max_effort_game][contest_id]._contest_result)

        print

        print("Min effort is in game: ", min_effort_game , "with effort of ", min_effort)
        for contest_id in games[min_effort_game]:
            print(games[min_effort_game][contest_id])
            print(games[min_effort_game][contest_id]._contest_result)

    return no_equilibrium




def find_curve(config):
    result = []
    
    # Define the range of reputation values
    reputation_min = 3  # Minimum reputation value
    reputation_max = 20  # Maximum reputation value
    num_points = 50  # Number of points to consider

    # Iterate over the range of reputation values
    for i in range(num_points):
        reputation = reputation_min + (reputation_max - reputation_min) * (i / (num_points - 1))

        # Perform binary search for the minimum type value
        type_min = 0.1  # Minimum type value
        type_max = 10  # Maximum type value (adjust as needed)
        precision = 0.00001  # Desired precision

        while type_max - type_min > precision:
            curr_type = (type_min + type_max) / 2  # Midpoint of the range

            config["player_creation_instructions"][0]["type"] = curr_type
            config["player_creation_instructions"][0]["reputation"] = reputation
            
            no_equilibrium = run_simulation(config, False)
            
            if no_equilibrium: 
                # The condition is satisfied, move the upper bound down
                type_max = curr_type
            else:
                # The condition is not satisfied, move the lower bound up
                type_min = curr_type

        # Print the reputation and minimum type value for each reputation
        print(f"For reputation = {reputation}, Minimum type = {curr_type}")
        result.append({"reputation": reputation, "type": curr_type})

    return result

# def ccreate_graph(data):
#     reputations = [item["reputation"] for item in data]
#     types = [item["type"] for item in data]

#     plt.plot(reputations, types, '-o')
#     plt.xlabel("Reputation")
#     plt.ylabel("Marginal Cost")
#     plt.title("The minimum marginal cost for the h-type for equilibrium to exist")
#     plt.show()


# def create_graph(data):
#     reputations = [item["reputation"] for item in data]
#     types = [item["type"] for item in data]

#     # Curve
#     # Define the range for alpha_h (x-axis)
#     alpha_h = np.array(reputations)

#     # Define the range for c_h (y-axis)
#     c_h = np.linspace(3, 10, 100)

#     # Create a meshgrid for alpha_h and c_h
#     alpha_h, c_h = np.meshgrid(alpha_h, c_h)

#     # Define the equation
#     equation = ((alpha_h + 2) * (1 - 20 / (c_h + 20)) ** 2) / 3 - 1 / 4

#     # Create the plot without adding the label to the legend yet
#     plt.contour(alpha_h, c_h, equation, [0], colors='g')

#     # Extract the line created by the contour and manually add it to the legend
#     line_contour = plt.Line2D([], [], color='g', label='Negative cumulative effect ratio')
#     plt.gca().add_artist(line_contour)

#     # Scatter plot
#     plt.scatter(reputations, types, color='red', label='Equilibrium ratio')

#     plt.xlabel("h-type reputation")
#     plt.ylabel("h-type marginal cost")

#     # Display the legend
#     plt.legend()

#     plt.grid()
#     plt.show()

f = open('Config.json')

config = json.load(f)
# result = find_curve(config)

# create_graph(result)

run_simulation(config, True)