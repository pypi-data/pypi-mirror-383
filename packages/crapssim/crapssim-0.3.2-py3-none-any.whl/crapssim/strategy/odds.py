import typing

from crapssim.bet import Bet, Come, DontCome, DontPass, Odds, PassLine
from crapssim.strategy.tools import Player, Strategy, Table


class OddsAmount(Strategy):
    """Strategy that takes places odds on a given number for a given bet type."""

    def __init__(
        self,
        base_type: typing.Type[PassLine | DontPass | Come | DontCome],
        odds_amounts: dict[int, typing.SupportsFloat],
        always_working: bool = False,
    ):
        self.base_type = base_type
        self.odds_amounts = odds_amounts
        self.always_working = always_working

    def completed(self, player: Player) -> bool:
        """Return True if there are no bets of base_type on the table.

        Parameters
        ----------
        player
            The player whose bets to check for.

        Returns
        -------
        True if there are no base type bets on the table, otherwise False.
        """
        return len([x for x in player.bets if isinstance(x, self.base_type)]) == 0

    def update_bets(self, player: Player) -> None:
        for number, amount in self.odds_amounts.items():
            bet = Odds(self.base_type, number, float(amount), self.always_working)
            if bet.is_allowed(player) and not player.already_placed(bet):
                player.add_bet(bet)

    def _get_always_working_repr(self) -> str:
        """Since the default is false, only need to print when True"""
        return (
            f", always_working={self.always_working})" if self.always_working else f")"
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(base_type={self.base_type}, "
            f"odds_amounts={self.odds_amounts}"
            f"{self._get_always_working_repr()}"
        )


class PassLineOddsAmount(OddsAmount):
    def __init__(
        self,
        bet_amount: typing.SupportsFloat,
        numbers: tuple[int] = (4, 5, 6, 8, 9, 10),
        always_working: bool = False,
    ):
        self.bet_amount = float(bet_amount)
        self.numbers = numbers
        super().__init__(PassLine, {x: bet_amount for x in numbers}, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(bet_amount={self.bet_amount}, numbers={self.numbers}"
            f"{self._get_always_working_repr()}"
        )


class DontPassOddsAmount(OddsAmount):
    def __init__(
        self,
        bet_amount: typing.SupportsFloat,
        numbers: tuple[int] = (4, 5, 6, 8, 9, 10),
        always_working: bool = False,
    ):
        self.bet_amount = float(bet_amount)
        self.numbers = numbers
        super().__init__(DontPass, {x: bet_amount for x in numbers}, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(bet_amount={self.bet_amount}, numbers={self.numbers}"
            f"{self._get_always_working_repr()}"
        )


class ComeOddsAmount(OddsAmount):
    def __init__(
        self,
        bet_amount: typing.SupportsFloat,
        numbers: tuple[int] = (4, 5, 6, 8, 9, 10),
        always_working: bool = False,
    ):
        self.bet_amount = float(bet_amount)
        self.numbers = numbers
        super().__init__(DontPass, {x: bet_amount for x in numbers}, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(bet_amount={self.bet_amount}, numbers={self.numbers}"
            f"{self._get_always_working_repr()}"
        )


class DontComeOddsAmount(OddsAmount):
    def __init__(
        self,
        bet_amount: typing.SupportsFloat,
        numbers: tuple[int] = (4, 5, 6, 8, 9, 10),
        always_working: bool = False,
    ):
        self.bet_amount = float(bet_amount)
        self.numbers = numbers
        super().__init__(DontCome, {x: bet_amount for x in numbers}, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(bet_amount={self.bet_amount}, numbers={self.numbers}"
            f"{self._get_always_working_repr()}"
        )


class OddsMultiplier(Strategy):
    """Strategy that takes an AllowsOdds object and places Odds on it given either a multiplier,
    or a dictionary of points and multipliers."""

    def __init__(
        self,
        base_type: typing.Type[PassLine | DontPass | Come | DontCome],
        odds_multiplier: dict[int, int] | int,
        always_working: bool = False,
    ):
        """Takes an AllowsOdds item (ex. PassLine, Come, DontPass) and adds a BaseOdds bet
        (either Odds or LayOdds) based on the odds_multiplier given.

        Parameters
        ----------
        base_type
            The bet that odds will be added to.
        odds_multiplier
            If odds_multiplier is an integer adds multiplier * base_bets amount to the odds.
            If the odds multiplier is a dictionary of integers, looks at the dictionary to
            determine what odds multiplier to use depending on the given point.
        """
        self.base_type = base_type
        self.always_working = always_working

        if isinstance(odds_multiplier, int):
            self.odds_multiplier = {x: odds_multiplier for x in (4, 5, 6, 8, 9, 10)}
        else:
            self.odds_multiplier = odds_multiplier

    @staticmethod
    def get_point_number(bet: Bet, table: "Table"):
        if isinstance(bet, (PassLine, DontPass)):
            return table.point.number
        elif isinstance(bet, (Come, DontCome)):
            return bet.number
        else:
            raise NotImplementedError

    def update_bets(self, player: Player) -> None:
        """Add an Odds bet to the given base_types in the amount determined by the odds_multiplier.

        Parameters
        ----------
        player
            The player to add the odds bet to.
        """
        for bet in [x for x in player.bets if isinstance(x, self.base_type)]:
            point = self.get_point_number(bet, player.table)

            if point in self.odds_multiplier:
                multiplier = self.odds_multiplier[point]
            else:
                return

            amount = bet.amount * multiplier
            OddsAmount(
                self.base_type, {point: amount}, self.always_working
            ).update_bets(player)

    def completed(self, player: Player) -> bool:
        """Return True if there are no bets of base_type on the table.

        Parameters
        ----------
        player
            The player whose bets to check for.

        Returns
        -------
        True if there are no base type bets on the table, otherwise False.
        """
        return len([x for x in player.bets if isinstance(x, self.base_type)]) == 0

    def _get_odds_multiplier_repr(self) -> int | dict[int, int]:
        """If the odds_multiplier has multiple values return a dictionary with the values,
        if all the multipliers are the same return an integer of the multiplier."""
        if all([x == self.odds_multiplier[4] for x in self.odds_multiplier.values()]):
            odds_multiplier: int | dict[int, int] = self.odds_multiplier[4]
        else:
            odds_multiplier = self.odds_multiplier
        return odds_multiplier

    def _get_always_working_repr(self) -> str:
        """Since the default is false, only need to print when True"""
        return (
            f", always_working={self.always_working})" if self.always_working else f")"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(base_type={self.base_type}, "
            f"odds_multiplier={self.get_odds_multiplier_repr()}"
            f"{self._get_always_working_repr()}"
        )


class PassLineOddsMultiplier(OddsMultiplier):
    """Strategy that adds an Odds bet to the PassLine bet. Equivalent to
    OddsMultiplier(PassLine, odds)."""

    def __init__(
        self,
        odds_multiplier: dict[int, int] | int | None = None,
        always_working: bool = False,
    ):
        """Add odds to PassLine bets with the multiplier specified by the odds_multiplier variable.

        Parameters
        ----------
        odds_multiplier
            If odds_multiplier is an integer the bet amount is the PassLine bet amount *
            odds_multiplier.  If it's a dictionary it uses the PassLine bet's point to determine
            the multiplier. Defaults to {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3} which are 345x odds.
        """
        if odds_multiplier is None:
            odds_multiplier = {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3}
        super().__init__(PassLine, odds_multiplier, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(odds_multiplier={self._get_odds_multiplier_repr()}"
            f"{self._get_always_working_repr()}"
        )


class DontPassOddsMultiplier(OddsMultiplier):
    """Strategy that adds a LayOdds bet to the DontPass bet. Equivalent to
    OddsMultiplier(DontPass, odds)"""

    def __init__(
        self,
        odds_multiplier: dict[int, int] | int | None = None,
        always_working: bool = False,
    ):
        """Add odds to DontPass bets with the multiplier specified by odds.

        Parameters
        ----------
        odds_multiplier
            If odds_multiplier is an integer the bet amount is the DontPass bet amount *
            odds_multiplier. If it's a dictionary it uses the DontPass bet's point to determine the
            multiplier. Defaults to 6.
        """
        if odds_multiplier is None:
            odds_multiplier = 6
        super().__init__(DontPass, odds_multiplier, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(odds_multiplier={self._get_odds_multiplier_repr()}"
            f"{self._get_always_working_repr()}"
        )


class ComeOddsMultiplier(OddsMultiplier):
    """Strategy that adds an Odds bet to the Come bet. Equivalent to
    OddsMultiplier(Come, odds)."""

    def __init__(
        self,
        odds_multiplier: dict[int, int] | int | None = None,
        always_working: bool = False,
    ):
        """Add odds to Come bets with the multiplier specified by the odds_multiplier variable.

        Parameters
        ----------
        odds_multiplier
            If odds_multiplier is an integer the bet amount is the Come bet amount *
            odds_multiplier.  If it's a dictionary it uses the Come bet's point to determine
            the multiplier. Defaults to {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3} which are 345x odds.
        """
        if odds_multiplier is None:
            odds_multiplier = {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3}
        super().__init__(Come, odds_multiplier, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(odds_multiplier={self._get_odds_multiplier_repr()}"
            f"{self._get_always_working_repr()}"
        )


class DontComeOddsMultiplier(OddsMultiplier):
    """Strategy that adds an Odds bet to the DontCome bet. Equivalent to
    OddsMultiplier(DontCome, odds)."""

    def __init__(
        self,
        odds_multiplier: dict[int, int] | int | None = None,
        always_working: bool = False,
    ):
        """Add odds to DontCome bets with the multiplier specified by the odds_multiplier variable.

        Parameters
        ----------
        odds_multiplier
            If odds_multiplier is an integer the bet amount is the Come bet amount *
            odds_multiplier.  If it's a dictionary it uses the Come bet's point to determine
            the multiplier. Defaults to 6.
        """
        if odds_multiplier is None:
            odds_multiplier = 6
        super().__init__(DontCome, odds_multiplier, always_working)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(odds_multiplier={self._get_odds_multiplier_repr()}"
            f"{self._get_always_working_repr()}"
        )
