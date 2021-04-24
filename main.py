from contest import Contest
import itertools
import copy


def flatten_players_list(player_creation_instructions):
    flatten_players_list = list()

    for player_creation_instruction in player_creation_instructions:
        for player in range(player_creation_instruction["amount"]):
            flatten_players_list.append(player_creation_instruction["type"])

    return flatten_players_list


def are_games_neighbors(game1, game2):
    are_games_neighbors = 0
    type = None
    contests = []

    for contest_id in game1:

        if are_games_neighbors > 2:
            break

        game_1_contest_players = game1[contest_id]._players
        game_2_contest_players = game2[contest_id]._players

        for players_tuple_id in range(len(game_1_contest_players)):
            game_1_players_tuple = game_1_contest_players[players_tuple_id]
            game_2_players_tuple = game_2_contest_players[players_tuple_id]

            if abs(game_1_players_tuple["amount"] - game_2_players_tuple["amount"]) == 1:
                are_games_neighbors += 1
                type = game_1_players_tuple["type"]
                contests.append(contest_id)

    if are_games_neighbors == 2:
        return {"type": type, "contests": contests}
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


def is_game_in_equilibrium(game_to_test, games, neighbors_of_game):
    game = games[game_to_test]
    for game_id in range(len(neighbors_of_game)):
        # If this game is an actual neighbor (has only one player in one contest that moved)
        if neighbors_of_game[game_id] is not None:
            contest_one = neighbors_of_game[game_id]["contests"][0]
            contest_two = neighbors_of_game[game_id]["contests"][1]
            relevant_player = neighbors_of_game[game_id]["type"]
            op_game = games[game_id]

            players_tuple_in_op_game_contest_one = next (player_tuple for player_tuple in op_game[contest_one]._players if player_tuple["type"] == relevant_player)

            player_utility_in_op_game = 0
            player_utility_in_game = 0

            # If the player is in contest one in the neighbor game, the player is in contest two in current game
            if players_tuple_in_op_game_contest_one["amount"] > next(player_tuple for player_tuple in game[contest_one]._players if player_tuple["type"] == relevant_player)["amount"]:
                if op_game[contest_one]._contest_result is not None and relevant_player in op_game[contest_one]._contest_result:
                    player_utility_in_op_game = op_game[contest_one]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_op_game = 0

                if game[contest_two]._contest_result is not None and relevant_player in game[contest_two]._contest_result:
                    player_utility_in_game = game[contest_two]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_game = 0

            # If the player is in contest two in the neighbor game, the player is in contest one in current game
            else:
                if op_game[contest_two]._contest_result is not None and relevant_player in op_game[contest_two]._contest_result:
                    player_utility_in_op_game = op_game[contest_two]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_op_game = 0

                if game[contest_one]._contest_result is not None and relevant_player in game[contest_one]._contest_result:
                    player_utility_in_game = game[contest_one]._contest_result[relevant_player]["utility"]
                else:
                    player_utility_in_game = 0

            if player_utility_in_game < player_utility_in_op_game:
                print game_to_test, "<", game_id
                return False

    return True


# initialize the game settings

# This tuple list represents the players in the game
# The first value is the player's type (the lower the type - the stronger the player)
# The second value is the amount of players of this type to compete in the game.
# NOTICE: the program assumes that the strong player shows first in the list of tuples
player_creation_instructions = [{"type": 1, "amount": 2}, {"type": 2, "amount": 2}]

# The list of prizes in the game
# each item sets a contests, the value is the prize of winning the first place.
prizes = [10, 5.624]

# Flatten the problem
flatt_players_list = flatten_players_list(player_creation_instructions)

contests_count = len(prizes)
arrangements = list()
for player_tuple in player_creation_instructions:
    amount_of_players = player_tuple["amount"]
    rng = list(range(amount_of_players + 1)) * contests_count
    if len(arrangements) == 0:
        for perm in set(i for i in itertools.permutations(rng, contests_count) if sum(i) == amount_of_players):
            arrangement = dict()
            for contest in range(len(perm)):
                arrangement[contest] = []
                arrangement[contest].append({"type": player_tuple["type"], "amount": perm[contest]})
            arrangements.append(arrangement)
    else:
        new_arrangements = list()
        for arrangement in arrangements:
            for perm in set(i for i in itertools.permutations(rng, contests_count) if sum(i) == amount_of_players):
                new_arrangement = copy.deepcopy(arrangement)
                for contest in range(len(perm)):
                    new_arrangement[contest].append({"type": player_tuple["type"], "amount": perm[contest]})
                new_arrangements.append(new_arrangement)
        arrangements = new_arrangements

games = list()

for i in range(len(arrangements)):
    arrangement = arrangements[i]
    # We now needs to create contests.
    # Each arrangement is a game

    game = dict()
    for contest_id in arrangement:

        players = arrangement[contest_id]
        game[contest_id] = Contest(prizes[contest_id])
        game[contest_id].add_players(players)
        game[contest_id].calculate_inner_equilibrium()
    games.append(game)

for game_id in range(len(games)):
    print game_id
    for contest_id in games[game_id]:
        print games[game_id][contest_id]
        print games[game_id][contest_id]._contest_result

print "\n\n\n"
neighbors_matrix = []

for game_id in range(len(games)):
    neighbors_matrix.append([])
    for j in range(len(games)):
        neighbors_matrix[game_id].append(are_games_neighbors(games[game_id], games[j]))

games_in_equilibrium = []

for game_id in range(len(neighbors_matrix)):
    game = games[game_id]
    neighbors_of_game = neighbors_matrix[game_id]
    if is_game_in_equilibrium(game_id, games, neighbors_of_game):
        games_in_equilibrium.append(game_id)

for game_id in games_in_equilibrium:
    print game_id

