# initialize the game settings


from contest import Contest

# This tuple list represents the players in the game
# The first value is the player's type (the lower the type - the stronger the player)
# The second value is the amount of players of this type to compete in the game.
# NOTICE: the program assumes that the strong player shows first in the list of tuples
player_creation_instructions = [{"type": 1, "amount": 2}, {"type": 2, "amount": 2}, {"type": 3, "amount": 2}]

# The list of prizes in the game
# each item sets a contests, the value is the prize of winning the first place.
prizes = [10, 10]

contests = []

for i in range(len(prizes)):
    contests.append(Contest(prizes[i]))

# Assuming there is only one contest
contest = contests[0]

contest._players = player_creation_instructions
print contest.calculate_inner_equilibrium()