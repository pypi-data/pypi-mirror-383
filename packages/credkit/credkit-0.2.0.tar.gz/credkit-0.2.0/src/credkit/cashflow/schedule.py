"""Cash flow schedules for modeling loan payment streams."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterator, Self

from ..money import Money
from ..temporal import PaymentFrequency, Period
from .cashflow import CashFlow, CashFlowType
from .discount import DiscountCurve


@dataclass(frozen=True)
class CashFlowSchedule:
    """
    Represents an ordered collection of cash flows.

    Used to model complete loan payment schedules with principal, interest,
    and fee payments. Immutable by design to ensure schedule integrity.
    """

    cash_flows: tuple[CashFlow, ...]
    """Ordered tuple of cash flows (immutable)."""

    def __post_init__(self) -> None:
        """Validate schedule parameters."""
        if not isinstance(self.cash_flows, tuple):
            # Convert to tuple if not already
            object.__setattr__(self, "cash_flows", tuple(self.cash_flows))

        # Validate all items are CashFlow instances
        for i, cf in enumerate(self.cash_flows):
            if not isinstance(cf, CashFlow):
                raise TypeError(f"cash_flows[{i}] must be CashFlow, got {type(cf)}")

        # Validate all cash flows have same currency
        if len(self.cash_flows) > 0:
            first_currency = self.cash_flows[0].amount.currency
            for i, cf in enumerate(self.cash_flows[1:], start=1):
                if cf.amount.currency != first_currency:
                    raise ValueError(
                        f"All cash flows must have same currency. "
                        f"Found {first_currency} and {cf.amount.currency} at index {i}"
                    )

    @classmethod
    def from_list(cls, cash_flows: list[CashFlow], sort: bool = True) -> Self:
        """
        Create a schedule from a list of cash flows.

        Args:
            cash_flows: List of CashFlow instances
            sort: If True, sort chronologically by date

        Returns:
            CashFlowSchedule instance

        Example:
            >>> cf1 = CashFlow(date(2025, 1, 1), Money.from_float(1000), CashFlowType.PRINCIPAL)
            >>> cf2 = CashFlow(date(2025, 2, 1), Money.from_float(1000), CashFlowType.PRINCIPAL)
            >>> schedule = CashFlowSchedule.from_list([cf1, cf2])
        """
        if sort:
            sorted_flows = sorted(cash_flows, key=lambda cf: cf.date)
            return cls(cash_flows=tuple(sorted_flows))
        return cls(cash_flows=tuple(cash_flows))

    @classmethod
    def empty(cls, currency: "Currency" = None) -> Self:  # type: ignore
        """
        Create an empty schedule.

        Args:
            currency: Currency for the schedule (not enforced for empty schedule)

        Returns:
            Empty CashFlowSchedule
        """
        return cls(cash_flows=tuple())

    # Sequence protocol

    def __len__(self) -> int:
        """Number of cash flows in schedule."""
        return len(self.cash_flows)

    def __iter__(self) -> Iterator[CashFlow]:
        """Iterate over cash flows."""
        return iter(self.cash_flows)

    def __getitem__(self, index: int) -> CashFlow:
        """Get cash flow by index."""
        return self.cash_flows[index]

    def __bool__(self) -> bool:
        """Check if schedule is non-empty."""
        return len(self.cash_flows) > 0

    # Filtering methods

    def filter_by_type(self, *types: CashFlowType) -> Self:
        """
        Filter cash flows by type(s).

        Args:
            *types: One or more CashFlowType values to include

        Returns:
            New schedule with only matching cash flows

        Example:
            >>> schedule.filter_by_type(CashFlowType.PRINCIPAL, CashFlowType.INTEREST)
        """
        filtered = [cf for cf in self.cash_flows if cf.type in types]
        return CashFlowSchedule(cash_flows=tuple(filtered))

    def filter_by_date_range(self, start: date | None = None, end: date | None = None) -> Self:
        """
        Filter cash flows by date range.

        Args:
            start: Include flows on or after this date (None = no lower bound)
            end: Include flows on or before this date (None = no upper bound)

        Returns:
            New schedule with only cash flows in range

        Example:
            >>> schedule.filter_by_date_range(date(2025, 1, 1), date(2025, 12, 31))
        """
        filtered = []
        for cf in self.cash_flows:
            if start is not None and cf.date < start:
                continue
            if end is not None and cf.date > end:
                continue
            filtered.append(cf)
        return CashFlowSchedule(cash_flows=tuple(filtered))

    def get_principal_flows(self) -> Self:
        """Get only principal cash flows."""
        return self.filter_by_type(CashFlowType.PRINCIPAL, CashFlowType.PREPAYMENT, CashFlowType.BALLOON)

    def get_interest_flows(self) -> Self:
        """Get only interest cash flows."""
        return self.filter_by_type(CashFlowType.INTEREST)

    def get_fee_flows(self) -> Self:
        """Get only fee cash flows."""
        return self.filter_by_type(CashFlowType.FEE)

    # Aggregation methods

    def total_amount(self) -> Money:
        """
        Calculate total amount of all cash flows.

        Returns:
            Sum of all cash flow amounts

        Example:
            >>> schedule.total_amount()
            Money('10500.00', USD)
        """
        if len(self.cash_flows) == 0:
            from ..money import USD
            return Money.zero(USD)

        total = self.cash_flows[0].amount
        for cf in self.cash_flows[1:]:
            total = total + cf.amount
        return total

    def sum_by_type(self) -> dict[CashFlowType, Money]:
        """
        Sum cash flows grouped by type.

        Returns:
            Dictionary mapping CashFlowType to total Money amount

        Example:
            >>> schedule.sum_by_type()
            {CashFlowType.PRINCIPAL: Money('10000'), CashFlowType.INTEREST: Money('500')}
        """
        if len(self.cash_flows) == 0:
            return {}

        sums: dict[CashFlowType, Money] = {}
        for cf in self.cash_flows:
            if cf.type in sums:
                sums[cf.type] = sums[cf.type] + cf.amount
            else:
                sums[cf.type] = cf.amount
        return sums

    def aggregate_by_period(self, frequency: PaymentFrequency) -> Self:
        """
        Aggregate cash flows into periodic buckets.

        Combines all cash flows that fall within the same period,
        maintaining type classification where possible.

        Args:
            frequency: Payment frequency to aggregate by

        Returns:
            New schedule with aggregated cash flows

        Example:
            >>> # Aggregate daily flows into monthly buckets
            >>> monthly_schedule = daily_schedule.aggregate_by_period(PaymentFrequency.MONTHLY)
        """
        if len(self.cash_flows) == 0:
            return self

        # Group by (period_start_date, type)
        from collections import defaultdict
        period_groups: dict[tuple[date, CashFlowType], list[CashFlow]] = defaultdict(list)

        # Find first date to establish period boundaries
        first_date = min(cf.date for cf in self.cash_flows)

        for cf in self.cash_flows:
            # Calculate which period this cash flow belongs to
            # Count periods from first_date
            days_diff = (cf.date - first_date).days
            period_length_days = frequency.period.to_days(approximate=True)

            if period_length_days > 0:
                period_number = days_diff // period_length_days
                period_start = frequency.period.add_to_date(first_date) if period_number > 0 else first_date
                # Adjust for multiple periods
                for _ in range(period_number - 1):
                    period_start = frequency.period.add_to_date(period_start)
            else:
                period_start = first_date

            period_groups[(period_start, cf.type)].append(cf)

        # Aggregate each group
        aggregated_flows: list[CashFlow] = []
        for (period_date, cf_type), flows in period_groups.items():
            # Sum all amounts in this group
            total = flows[0].amount
            for cf in flows[1:]:
                total = total + cf.amount

            # Use the latest date in the period as the flow date
            latest_date = max(cf.date for cf in flows)

            # Create aggregated cash flow
            aggregated_flows.append(
                CashFlow(
                    date=latest_date,
                    amount=total,
                    type=cf_type,
                    description=f"Aggregated {cf_type.value} ({len(flows)} flows)"
                )
            )

        # Sort and return
        return CashFlowSchedule.from_list(aggregated_flows, sort=True)

    # Valuation methods

    def present_value(
        self,
        discount_curve: DiscountCurve,
        valuation_date: date | None = None,
    ) -> Money:
        """
        Calculate present value of all cash flows.

        Args:
            discount_curve: Curve to use for discounting
            valuation_date: Date to discount to (defaults to curve's valuation date)

        Returns:
            Total present value as Money

        Example:
            >>> curve = FlatDiscountCurve(InterestRate.from_percent(5.0), date(2024, 1, 1))
            >>> pv = schedule.present_value(curve)
        """
        if len(self.cash_flows) == 0:
            from ..money import USD
            return Money.zero(USD)

        val_date = valuation_date if valuation_date else discount_curve.valuation_date

        # Sum present values of all cash flows
        total_pv = self.cash_flows[0].present_value(discount_curve, val_date)
        for cf in self.cash_flows[1:]:
            total_pv = total_pv + cf.present_value(discount_curve, val_date)

        return total_pv

    def net_present_value(
        self,
        discount_curve: DiscountCurve,
        valuation_date: date | None = None,
    ) -> Money:
        """
        Alias for present_value().

        In consumer lending, NPV and PV are typically the same concept.
        """
        return self.present_value(discount_curve, valuation_date)

    # Utility methods

    def sort(self) -> Self:
        """
        Return new schedule sorted chronologically by date.

        Returns:
            New sorted CashFlowSchedule
        """
        return CashFlowSchedule.from_list(list(self.cash_flows), sort=True)

    def earliest_date(self) -> date | None:
        """Get earliest cash flow date, or None if empty."""
        if len(self.cash_flows) == 0:
            return None
        return min(cf.date for cf in self.cash_flows)

    def latest_date(self) -> date | None:
        """Get latest cash flow date, or None if empty."""
        if len(self.cash_flows) == 0:
            return None
        return max(cf.date for cf in self.cash_flows)

    def date_range(self) -> tuple[date, date] | None:
        """
        Get date range of schedule.

        Returns:
            Tuple of (earliest_date, latest_date), or None if empty
        """
        if len(self.cash_flows) == 0:
            return None
        return (self.earliest_date(), self.latest_date())  # type: ignore

    # String representation

    def __str__(self) -> str:
        if len(self.cash_flows) == 0:
            return "CashFlowSchedule(empty)"

        date_range = self.date_range()
        total = self.total_amount()
        return f"CashFlowSchedule({len(self.cash_flows)} flows, {date_range[0]} to {date_range[1]}, total={total})"

    def __repr__(self) -> str:
        return f"CashFlowSchedule({len(self.cash_flows)} flows)"
