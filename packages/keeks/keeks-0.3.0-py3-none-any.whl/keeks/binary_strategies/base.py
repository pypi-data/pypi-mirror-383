import abc

__author__ = "willmcginnis"


class BaseStrategy(abc.ABC):
    """
    Abstract base class for all binary betting strategies.

    This class defines the interface that all binary betting strategies must implement.
    Concrete strategy implementations should inherit from this class and implement
    the evaluate method.
    """

    def __init__(self, payoff: float, loss: float, transaction_cost: float = 0):
        """
        Initialize the strategy.

        Parameters
        ----------
        payoff : float
            The payoff multiplier for winning.
        loss : float
            The loss multiplier for losing.
        transaction_cost : float, optional
            The transaction cost as a fraction of the bet, by default 0.

        Raises
        ------
        ValueError
            If payoff is not positive, loss is negative, or loss + transaction_cost is not positive.
        """
        if payoff <= 0:
            raise ValueError("Payoff must be greater than 0")
        if loss < 0:
            raise ValueError("Loss must be non-negative")
        if transaction_cost < 0:
            raise ValueError("Transaction cost must be non-negative")
        if loss + transaction_cost <= 0:
            raise ValueError(
                "Total cost (loss + transaction_cost) must be greater than 0"
            )

        self.payoff = payoff
        self.loss = loss
        self.transaction_cost = transaction_cost

    def get_max_safe_bet(self, current_bankroll: float) -> float:
        """
        Calculate the maximum safe bet size based on current bankroll.

        Parameters
        ----------
        current_bankroll : float
            The current bankroll to use for calculations.

        Returns
        -------
        float
            The maximum safe bet size as a proportion of bankroll.
        """
        # Calculate maximum bet that won't result in negative bankroll
        # after accounting for loss multiplier and transaction costs
        max_bet = current_bankroll / (self.loss + self.transaction_cost)
        return min(1.0, max_bet / current_bankroll)

    def calculate_max_entry_price(self, outcomes, probabilities, current_wealth,
                                  tolerance=0.01, max_search_fraction=0.5):
        """
        Calculate maximum price willing to pay for a one-time gamble.

        This method is only implemented for strategies derived from utility theory
        (e.g., KellyCriterion, MertonShare). For heuristic strategies without
        underlying utility functions, this method raises NotImplementedError.

        Parameters
        ----------
        outcomes : array-like
            The possible payoffs from the gamble
        probabilities : array-like
            The probability of each outcome (must sum to ≤ 1)
        current_wealth : float
            Current wealth before the gamble
        tolerance : float, default=0.01
            Convergence tolerance for binary search
        max_search_fraction : float, default=0.5
            Maximum fraction of wealth to consider as upper bound

        Returns
        -------
        float
            Maximum price willing to pay for the gamble

        Raises
        ------
        NotImplementedError
            If the strategy does not have a utility-theoretic basis for
            calculating indifference prices.

        Notes
        -----
        This method answers: "What's the maximum I'd pay to participate in this
        one-time gamble?" It's fundamentally different from evaluate(), which
        answers: "How much should I bet in a repeated betting scenario?"

        Only strategies with underlying utility functions can meaningfully answer
        the entry price question. Heuristic strategies (e.g., FixedFraction, CPPI)
        don't have utility functions to derive indifference prices from.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support one-time entry price "
            "calculation. This method is only available for utility-based strategies "
            "like KellyCriterion and MertonShare.\n\n"
            "Heuristic strategies (FixedFraction, CPPI, Dynamic, etc.) don't have "
            "underlying utility functions to derive indifference prices from."
        )

    @abc.abstractmethod
    def evaluate(self, probability: float, current_bankroll: float) -> float:
        """
        Evaluate the strategy for a given probability.

        Parameters
        ----------
        probability : float
            The probability of winning.
        current_bankroll : float
            The current bankroll to use for calculations.

        Returns
        -------
        float
            The proportion of the bankroll to bet.
        """
        pass
