import copy

class Contest:
    # static counter of the contests that hs been created
    contest_count = 0

    def __init__(self, prize):
        # Increase the counter of the contests been created
        Contest.contest_count += 1

        self._players = None
        self._contest_result = None
        self._prize = prize
        self._contest_id = Contest.contest_count

    def add_players(self, players):
        self._players = players

    def calculate_inner_equilibrium(self):
        """
        Calculate the tullock inner equilibrium
        :rtype: List fo tuples with the player's type, the number of players and the effort of a
                single player of type
        """

        relevant_players = []

        for player_tuple in self._players:
            if player_tuple["amount"] != 0:
                relevant_players.append(player_tuple)

        if len(relevant_players) == 0:
            return;

        elif len(relevant_players) == 1 and relevant_players[0]["amount"] == 1:
            active_player = copy.deepcopy(relevant_players[0])
            active_player["prob_of_winning"] = 1
            active_player["effort"] = 0
            active_player["utility"] = self._prize
            self._contest_result = {active_player["type"]: active_player}
        else:
            # We will start by assuming all the players are active
            for i in range(len(relevant_players)):
                # Defining te active players
                active_players = copy.deepcopy(relevant_players[0:len(relevant_players) - i])

                #  Assuming that the active players' list is sorted, the weakest player will be last.
                weakest_player_tuple = active_players[len(active_players) - 1]
                lowest_player_effort = -1
                while lowest_player_effort <= 0 and weakest_player_tuple["amount"] > 0:

                    # Calculating the number of active players and the sum of the types
                    sum_of_players_types = 0
                    amount_of_players = 0
                    for active_players_tuple in active_players:
                        amount_of_players += active_players_tuple["amount"]
                        sum_of_players_types += active_players_tuple["amount"] * active_players_tuple["type"]

                    # Calculate the total effort
                    total_effort = self.calculate_total_effort(amount_of_players, sum_of_players_types)

                    weakest_player_prob_of_winning = \
                        self.calculate_single_player_probability_of_winning(amount_of_players, sum_of_players_types,
                                                                            weakest_player_tuple["type"])
                    lowest_player_effort = self.calculate_single_player_effort(total_effort, weakest_player_prob_of_winning)

                    # If the effort is positive - we reached an equilibrium
                    if lowest_player_effort > 0:
                        contest_result = dict()
                        for active_player in list(active_players):
                            active_player["prob_of_winning"] = self.calculate_single_player_probability_of_winning(
                                amount_of_players, sum_of_players_types, active_player["type"])
                            active_player["effort"] = self.calculate_single_player_effort(total_effort,
                                                                                          active_player["prob_of_winning"])
                            active_player["utility"] = self._prize * active_player["prob_of_winning"] - active_player[
                                "effort"] * active_player["type"]
                            contest_result[active_player["type"]] = active_player
                        self._contest_result = contest_result
                        return contest_result
                    else:
                        weakest_player_tuple["amount"] -= 1
        return self._contest_result

    def calculate_total_effort(self, number_of_players, sum_of_players_types):
        return float((self._prize * (number_of_players - 1)) / float(sum_of_players_types))

    @staticmethod
    def calculate_single_player_probability_of_winning(active_players_count, total_players_types, player_type):
        return 1 - ((active_players_count - 1) * player_type) / float(total_players_types)

    @staticmethod
    def calculate_single_player_effort(total_effort, probability_of_winning):
        return total_effort * probability_of_winning

    def __str__(self):
        return "Content (" + str(self._contest_id) + ") with prize: " + str(self._prize) + " with players: " + str(
            self._players)
