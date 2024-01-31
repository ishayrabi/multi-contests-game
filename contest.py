import copy


class Contest:

    # static counter of the contests that has been created
    contest_count = 0

    # Create a new contest
    def __init__(self, prize):
        # Increase the counter of the contests been created
        Contest.contest_count += 1

        self._players = None
        self._contest_result = None
        self._active_players = None
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
            active_player["utility"] = self.calculate_prize(relevant_players) #self._prize
            self._contest_result = {str(active_player["type"])+"_"+str(active_player["reputation"]): active_player}
            self._active_players = relevant_players
        else:
            # We will start by assuming all the players are active
            for i in range(len(relevant_players)):
                # Defining the active players
                active_players = copy.deepcopy(relevant_players[0:len(relevant_players) - i])

                #  Assuming that the active players' list is sorted, the weakest player will be last.
                weakest_player_tuple = active_players[len(active_players) - 1]
                arrived_an_equilibrium = False
                while not arrived_an_equilibrium and weakest_player_tuple["amount"] > 0:

                    # Calculating the number of active players and the sum of the types
                    sum_of_players_types = Contest.get_player_sum_types(active_players)
                    amount_of_players = Contest.get_players_amount(active_players)

                    # Calculate the total effort
                    total_effort = self.calculate_total_effort(active_players)

                    weakest_player_prob_of_winning = \
                        self.calculate_single_player_probability_of_winning(amount_of_players, sum_of_players_types,
                                                                            weakest_player_tuple["type"])
                    lowest_player_effort = self.calculate_single_player_effort(total_effort,
                                                                               weakest_player_prob_of_winning)

                    # If the effort is positive - we reached an equilibrium
                    if lowest_player_effort > 0:
                        contest_result = dict()
                        all_players_are_active = True
                        for active_player in list(active_players):
                            active_player["prob_of_winning"] = self.calculate_single_player_probability_of_winning(
                                amount_of_players, sum_of_players_types, active_player["type"])
                            
                            tmp_effort = self.calculate_single_player_effort(total_effort,
                                                                                          active_player[
                                                                                              "prob_of_winning"])
                            active_player["effort"] = tmp_effort
                            active_player["utility"] = self.calculate_prize(active_players) * active_player["prob_of_winning"]*active_player["prob_of_winning"]
                            contest_result[str(active_player["type"])+"_"+str(active_player["reputation"])] = active_player
                            if tmp_effort <= 0:
                                all_players_are_active = False
                        if all_players_are_active:
                            self._contest_result = contest_result
                            self._active_players = active_players
                            return contest_result

                    weakest_player_tuple["amount"] -= 1
        return self._contest_result

    def calculate_total_effort(self, relevant_players):
        return float((self.calculate_prize(relevant_players) * (self.get_players_amount(relevant_players) - 1)) /
                     float(self.get_player_sum_types(relevant_players)))

    @staticmethod
    def calculate_single_player_probability_of_winning(active_players_count, total_players_types, player_type):
        return 1 - ((active_players_count - 1) * player_type) / float(total_players_types)

    @staticmethod
    def calculate_single_player_effort(total_effort, probability_of_winning):
        return total_effort * probability_of_winning

    @staticmethod
    def get_players_amount(relevant_players_dict):
        amount_of_players = 0
        for relevant_players_tuple in relevant_players_dict:
            amount_of_players += relevant_players_tuple["amount"]

        return amount_of_players

    @staticmethod
    def get_player_sum_types(relevant_players_dict):
        sum_types = 0
        for relevant_players_tuple in relevant_players_dict:
            sum_types += relevant_players_tuple["amount"] * relevant_players_tuple["type"]

        return sum_types

    @staticmethod
    def get_player_sum_reputations(relevant_players_dict):
        sum_types = 0
        for relevant_players_tuple in relevant_players_dict:
            sum_types += relevant_players_tuple["amount"] * relevant_players_tuple["reputation"]

        return sum_types


    @staticmethod
    def get_average_player_reputation(relevant_players):
        return (Contest.get_player_sum_reputations(relevant_players) / Contest.get_players_amount(relevant_players))

    def calculate_prize_nominal(self, relevant_players):
        return self._prize

    def calculate_prize_additive(self, relevant_players):
        return self.calculate_prize_nominal(relevant_players) + Contest.get_average_player_reputation(relevant_players)

    def calculate_prize_multiply(self, relevant_players):
        return self.calculate_prize_nominal(relevant_players) * Contest.get_average_player_reputation(relevant_players)

    def calculate_prize(self, relevant_players):
        return self.calculate_prize_multiply(relevant_players)

    def __str__(self):
        prize = 0
        if self._active_players is not None:
            prize = self.calculate_prize(self._active_players)

        return "Content (" + str(self._contest_id) + ") with prize: " + str(prize) + " with players: " + str(
            self._players)

