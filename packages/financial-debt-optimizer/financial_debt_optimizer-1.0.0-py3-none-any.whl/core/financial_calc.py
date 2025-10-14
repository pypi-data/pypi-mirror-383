from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np
from enum import Enum
import calendar


class PaymentFrequency(Enum):
    """Supported payment frequencies."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi-weekly"
    SEMI_MONTHLY = "semi-monthly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi-annually"
    ANNUALLY = "annually"


class RecurrencePattern:
    """Handles calculation and generation of recurring date patterns.
    
    Supports all common recurrence frequencies including daily, weekly, bi-weekly,
    monthly, quarterly, semi-annually, and annually.
    """
    
    def __init__(self, frequency: str, start_date: date, end_date: Optional[date] = None):
        """Initialize a recurrence pattern.
        
        Args:
            frequency: One of the supported frequency types from PaymentFrequency enum
            start_date: The date when this pattern begins
            end_date: Optional end date for the pattern (None means no end)
        """
        self.frequency = frequency.lower()
        self.start_date = start_date
        self.end_date = end_date
        
        # Validate frequency
        valid_frequencies = [freq.value for freq in PaymentFrequency]
        if self.frequency not in valid_frequencies:
            raise ValueError(f"Frequency must be one of: {', '.join(valid_frequencies)}")
        
        # Ensure start_date is not after end_date
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
    
    def get_dates(self, range_start: date, range_end: date) -> List[date]:
        """Generate all occurrence dates within the given date range.
        
        Args:
            range_start: Start date of the range to generate dates for
            range_end: End date of the range to generate dates for
            
        Returns:
            List of dates on which the pattern occurs within the range
        """
        # Make sure we respect the pattern's own start and end dates
        effective_start = max(range_start, self.start_date)
        effective_end = range_end
        if self.end_date:
            effective_end = min(range_end, self.end_date)
        
        # Skip if the effective range is invalid
        if effective_start > effective_end:
            return []
            
        dates = []
        
        if self.frequency == PaymentFrequency.ONCE.value:
            # One-time event - only occurs on the start_date if it's in range
            if effective_start <= self.start_date <= effective_end:
                dates.append(self.start_date)
                
        elif self.frequency == PaymentFrequency.DAILY.value:
            current_date = effective_start
            delta = timedelta(days=1)
            
            while current_date <= effective_end:
                dates.append(current_date)
                current_date += delta
                
        elif self.frequency == PaymentFrequency.WEEKLY.value:
            # Start from effective_start, then iterate by 7 days
            current_date = effective_start
            delta = timedelta(days=7)
            
            while current_date <= effective_end:
                dates.append(current_date)
                current_date += delta
                
        elif self.frequency == PaymentFrequency.BI_WEEKLY.value:
            # Start from effective_start, then iterate by 14 days
            current_date = effective_start
            delta = timedelta(days=14)
            
            # Find the first date that matches the start_date's day of week and pattern
            days_difference = (effective_start - self.start_date).days
            # Adjust to find the next matching bi-weekly date
            days_to_add = (14 - (days_difference % 14)) % 14
            if days_to_add > 0:
                current_date = effective_start + timedelta(days=days_to_add)
            
            while current_date <= effective_end:
                dates.append(current_date)
                current_date += delta
                
        elif self.frequency == PaymentFrequency.SEMI_MONTHLY.value:
            # 1st and 15th of each month
            current_month = effective_start.month
            current_year = effective_start.year
            
            while True:
                # Try to add 1st of month if in range
                try:
                    first_of_month = date(current_year, current_month, 1)
                    if effective_start <= first_of_month <= effective_end:
                        dates.append(first_of_month)
                except ValueError:
                    pass
                
                # Try to add 15th of month if in range
                try:
                    fifteenth_of_month = date(current_year, current_month, 15)
                    if effective_start <= fifteenth_of_month <= effective_end:
                        dates.append(fifteenth_of_month)
                except ValueError:
                    pass
                
                # Move to next month
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
                
                # Check if we've gone past the end date
                if date(current_year, current_month, 1) > effective_end:
                    break
                    
        elif self.frequency == PaymentFrequency.MONTHLY.value:
            # Same day each month
            target_day = self.start_date.day
            current_month = effective_start.month
            current_year = effective_start.year
            
            # If effective_start is after the pattern day for current month,
            # skip to next month's occurrence
            if effective_start.day > target_day:
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
            
            while True:
                try:
                    current_date = date(current_year, current_month, target_day)
                    if effective_start <= current_date <= effective_end:
                        dates.append(current_date)
                except ValueError:
                    # Handle month lengths - use last day of month if target_day exceeds month length
                    last_day = calendar.monthrange(current_year, current_month)[1]
                    current_date = date(current_year, current_month, last_day)
                    if effective_start <= current_date <= effective_end:
                        dates.append(current_date)
                
                # Move to next month
                if current_month == 12:
                    current_month = 1
                    current_year += 1
                else:
                    current_month += 1
                
                # Check if we've gone past the end date
                if date(current_year, current_month, 1) > effective_end:
                    break
                    
        elif self.frequency == PaymentFrequency.QUARTERLY.value:
            # Same day every 3 months
            target_day = self.start_date.day
            target_month = self.start_date.month
            
            # Find the first quarterly occurrence in or after effective_start
            current_year = effective_start.year
            current_month = effective_start.month
            
            # Adjust to the next quarterly month from the pattern
            month_offset = (current_month - target_month) % 3
            if month_offset > 0:
                month_offset = 3 - month_offset
                current_month += month_offset
                if current_month > 12:
                    current_year += 1
                    current_month -= 12
            
            # If in the correct month but past the day, move to next quarter
            if month_offset == 0 and effective_start.day > target_day:
                current_month += 3
                if current_month > 12:
                    current_year += 1
                    current_month -= 12
            
            while True:
                try:
                    current_date = date(current_year, current_month, target_day)
                    if effective_start <= current_date <= effective_end:
                        dates.append(current_date)
                except ValueError:
                    # Handle month lengths
                    last_day = calendar.monthrange(current_year, current_month)[1]
                    current_date = date(current_year, current_month, last_day)
                    if effective_start <= current_date <= effective_end:
                        dates.append(current_date)
                
                # Move to next quarter
                current_month += 3
                if current_month > 12:
                    current_year += 1
                    current_month -= 12
                
                # Check if we've gone past the end date
                if date(current_year, current_month, 1) > effective_end:
                    break
                    
        elif self.frequency == PaymentFrequency.SEMI_ANNUALLY.value:
            # Same day every 6 months
            target_day = self.start_date.day
            target_month = self.start_date.month
            
            # Find the first semi-annual occurrence in or after effective_start
            current_year = effective_start.year
            current_month = effective_start.month
            
            # Adjust to the next semi-annual month from the pattern
            month_offset = (current_month - target_month) % 6
            if month_offset > 0:
                month_offset = 6 - month_offset
                current_month += month_offset
                if current_month > 12:
                    current_year += 1
                    current_month -= 12
            
            # If in the correct month but past the day, move to next semi-annual period
            if month_offset == 0 and effective_start.day > target_day:
                current_month += 6
                if current_month > 12:
                    current_year += 1
                    current_month -= 12
            
            while True:
                try:
                    current_date = date(current_year, current_month, target_day)
                    if effective_start <= current_date <= effective_end:
                        dates.append(current_date)
                except ValueError:
                    # Handle month lengths
                    last_day = calendar.monthrange(current_year, current_month)[1]
                    current_date = date(current_year, current_month, last_day)
                    if effective_start <= current_date <= effective_end:
                        dates.append(current_date)
                
                # Move to next semi-annual period
                current_month += 6
                if current_month > 12:
                    current_year += 1
                    current_month -= 12
                
                # Check if we've gone past the end date
                if date(current_year, current_month, 1) > effective_end:
                    break
                    
        elif self.frequency == PaymentFrequency.ANNUALLY.value:
            # Same month and day each year
            target_day = self.start_date.day
            target_month = self.start_date.month
            
            # Start from the first year in range
            current_year = effective_start.year
            
            # If effective_start is after the pattern date for current year,
            # skip to next year's occurrence
            if (effective_start.month > target_month or 
                (effective_start.month == target_month and effective_start.day > target_day)):
                current_year += 1
            
            while True:
                try:
                    current_date = date(current_year, target_month, target_day)
                    if current_date > effective_end:
                        break
                    if current_date >= effective_start:
                        dates.append(current_date)
                except ValueError:
                    # Handle February 29 in non-leap years
                    if target_month == 2 and target_day == 29 and not calendar.isleap(current_year):
                        current_date = date(current_year, target_month, 28)
                        if effective_start <= current_date <= effective_end:
                            dates.append(current_date)
                
                current_year += 1
        
        return sorted(dates)
    
    def get_monthly_frequency(self) -> float:
        """Calculate the monthly frequency (occurrences per month) of this pattern.
        
        Returns:
            Float representing the average number of occurrences per month
        """
        if self.frequency == PaymentFrequency.ONCE.value:
            return 0.0   # One-time events don't have a monthly frequency
        elif self.frequency == PaymentFrequency.DAILY.value:
            return 30.4  # Average days in a month
        elif self.frequency == PaymentFrequency.WEEKLY.value:
            return 4.35  # Average weeks in a month
        elif self.frequency == PaymentFrequency.BI_WEEKLY.value:
            return 2.17  # Average bi-weekly occurrences per month
        elif self.frequency == PaymentFrequency.SEMI_MONTHLY.value:
            return 2.0   # Exactly 2 times per month
        elif self.frequency == PaymentFrequency.MONTHLY.value:
            return 1.0   # Once per month
        elif self.frequency == PaymentFrequency.QUARTERLY.value:
            return 1/3   # Every 3 months
        elif self.frequency == PaymentFrequency.SEMI_ANNUALLY.value:
            return 1/6   # Twice per year
        elif self.frequency == PaymentFrequency.ANNUALLY.value:
            return 1/12  # Once per year
        else:
            raise ValueError(f"Unsupported frequency for monthly calculation: {self.frequency}")
    
    def __str__(self) -> str:
        """Return a human-readable representation of the pattern."""
        if self.end_date:
            return f"{self.frequency.capitalize()} from {self.start_date} to {self.end_date}"
        else:
            return f"{self.frequency.capitalize()} from {self.start_date} (no end date)"


@dataclass
class Debt:
    """Represents a debt with payment terms and current balance."""
    name: str
    balance: float
    minimum_payment: float
    interest_rate: float  # Annual percentage rate
    due_date: int  # Day of the month (1-31)

    def __post_init__(self):
        """Validate debt parameters after initialization."""
        if self.balance < 0:
            raise ValueError("Debt balance cannot be negative")
        if self.minimum_payment < 0:
            raise ValueError("Minimum payment cannot be negative")
        if self.interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if not 1 <= self.due_date <= 31:
            raise ValueError("Due date must be between 1 and 31")

    @property
    def monthly_interest_rate(self) -> float:
        """Calculate monthly interest rate from annual rate."""
        return self.interest_rate / 100 / 12

    def calculate_interest_charge(self, balance: float) -> float:
        """Calculate monthly interest charge on given balance."""
        return balance * self.monthly_interest_rate

    def calculate_principal_payment(self, total_payment: float, balance: float) -> float:
        """Calculate principal portion of a payment."""
        interest_charge = self.calculate_interest_charge(balance)
        return max(0, total_payment - interest_charge)

    def calculate_months_to_payoff(self, payment_amount: float) -> int:
        """Calculate months to pay off debt with fixed payment amount."""
        if payment_amount <= 0:
            return float('inf')
        
        monthly_rate = self.monthly_interest_rate
        if monthly_rate == 0:
            return int(np.ceil(self.balance / payment_amount))
        
        if payment_amount <= self.balance * monthly_rate:
            return float('inf')  # Payment doesn't cover interest
        
        months = -np.log(1 - (self.balance * monthly_rate) / payment_amount) / np.log(1 + monthly_rate)
        return int(np.ceil(months))


@dataclass
class Income:
    """Represents an income source with frequency and timing."""
    source: str
    amount: float
    frequency: str
    start_date: date

    def __post_init__(self):
        """Validate income parameters after initialization."""
        if self.amount <= 0:
            raise ValueError("Income amount must be positive")
        
        valid_frequencies = [freq.value for freq in PaymentFrequency]
        if self.frequency.lower() not in valid_frequencies:
            raise ValueError(f"Frequency must be one of: {valid_frequencies}")
        
        self.frequency = self.frequency.lower()

    def get_monthly_amount(self) -> float:
        """Convert income to monthly equivalent amount."""
        frequency_multipliers = {
            PaymentFrequency.WEEKLY.value: 52 / 12,
            PaymentFrequency.BI_WEEKLY.value: 26 / 12,
            PaymentFrequency.SEMI_MONTHLY.value: 2,
            PaymentFrequency.MONTHLY.value: 1,
            PaymentFrequency.QUARTERLY.value: 1 / 3,
            PaymentFrequency.ANNUALLY.value: 1 / 12,
        }
        return self.amount * frequency_multipliers[self.frequency]

    def get_payment_dates(self, start_date: date, end_date: date) -> List[date]:
        """Generate list of payment dates within the given date range."""
        dates = []
        today = date.today()
        
        # Start from the income start_date, but find the first payment on or after today
        current_date = self.start_date
        
        if self.frequency == PaymentFrequency.WEEKLY.value:
            delta = timedelta(days=7)
        elif self.frequency == PaymentFrequency.BI_WEEKLY.value:
            delta = timedelta(days=14)
        elif self.frequency == PaymentFrequency.SEMI_MONTHLY.value:
            # 1st and 15th of each month
            # Start from the month containing start_date or today, whichever is later
            month_start = max(start_date, today).replace(day=1)
            current_date = month_start
            
            while current_date <= end_date:
                # Add 1st of month
                first_of_month = current_date.replace(day=1)
                if first_of_month >= max(start_date, today) and first_of_month <= end_date:
                    dates.append(first_of_month)
                
                # Add 15th of month
                try:
                    mid_month = current_date.replace(day=15)
                    if mid_month >= max(start_date, today) and mid_month <= end_date:
                        dates.append(mid_month)
                except ValueError:
                    pass  # February with 28 days
                
                # Move to next month with year overflow protection
                try:
                    if current_date.month == 12:
                        new_year = current_date.year + 1
                        if new_year > 9999:
                            break
                        current_date = current_date.replace(year=new_year, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                except ValueError:
                    break
            
            return sorted(dates)
        elif self.frequency == PaymentFrequency.MONTHLY.value:
            delta = timedelta(days=30)  # Approximate, will adjust
        elif self.frequency == PaymentFrequency.QUARTERLY.value:
            delta = timedelta(days=90)  # Approximate
        elif self.frequency == PaymentFrequency.ANNUALLY.value:
            delta = timedelta(days=365)  # Approximate
        else:
            raise ValueError(f"Unsupported frequency: {self.frequency}")
        
        # For weekly, bi-weekly, monthly, quarterly, and annual frequencies
        # Find the first payment date on or after today
        while current_date < today:
            current_date += delta
        
        # Now generate payment dates starting from the first future date
        while current_date <= end_date:
            if current_date >= start_date:  # Only include if within the requested range
                dates.append(current_date)
            current_date += delta
        
        return dates


@dataclass
class RecurringExpense:
    """Represents a recurring expense like subscriptions, fees, etc."""
    description: str
    amount: float
    frequency: str  # monthly, quarterly, annually
    due_date: int   # Day of month when due (1-31)
    start_date: date

    def __post_init__(self):
        """Validate recurring expense parameters after initialization."""
        if self.amount <= 0:
            raise ValueError("Expense amount must be positive")
        
        valid_frequencies = ['bi-weekly', 'monthly', 'quarterly', 'annually']
        if self.frequency.lower() not in valid_frequencies:
            raise ValueError(f"Frequency must be one of: {valid_frequencies}")
        
        self.frequency = self.frequency.lower()
        
        if not (1 <= self.due_date <= 31):
            raise ValueError("Due date must be between 1 and 31")

    def get_payment_dates(self, start_date: date, end_date: date) -> List[date]:
        """Generate list of payment dates within the given date range."""
        dates = []
        today = date.today()
        
        # Handle bi-weekly frequency differently since it's not tied to month boundaries
        if self.frequency == 'bi-weekly':
            # Start from the expense start_date or today, whichever is later
            current_date = max(self.start_date, today)
            
            # Generate dates every 14 days
            while current_date <= end_date:
                if current_date >= start_date and current_date >= today:
                    dates.append(current_date)
                current_date += timedelta(days=14)
            
            return sorted(dates)
        
        # For monthly/quarterly/annual frequencies, use month-based logic
        current_date = max(self.start_date, start_date.replace(day=1))
        
        while current_date <= end_date:
            # Calculate payment date for this period
            try:
                payment_date = current_date.replace(day=self.due_date)
            except ValueError:
                # Handle cases where due_date doesn't exist in the month (e.g., Feb 30)
                try:
                    if current_date.month == 12:
                        new_year = current_date.year + 1
                        if new_year > 9999:
                            break
                        next_month = current_date.replace(year=new_year, month=1, day=1)
                    else:
                        next_month = current_date.replace(month=current_date.month + 1, day=1)
                    payment_date = (next_month - timedelta(days=1))  # Last day of month
                except ValueError:
                    break  # Stop on date calculation errors
            
            # Only include if payment date is on or after today and within range
            if payment_date >= today and start_date <= payment_date <= end_date:
                dates.append(payment_date)
            
            # Move to next period with year overflow protection
            try:
                if self.frequency == 'monthly':
                    if current_date.month == 12:
                        new_year = current_date.year + 1
                        if new_year > 9999:
                            break
                        current_date = current_date.replace(year=new_year, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                elif self.frequency == 'quarterly':
                    new_month = current_date.month + 3
                    if new_month > 12:
                        new_year = current_date.year + 1
                        if new_year > 9999:
                            break
                        current_date = current_date.replace(year=new_year, month=new_month - 12)
                    else:
                        current_date = current_date.replace(month=new_month)
                elif self.frequency == 'annually':
                    new_year = current_date.year + 1
                    if new_year > 9999:
                        break
                    current_date = current_date.replace(year=new_year)
            except ValueError:
                break  # Stop on date calculation errors
        
        return dates


@dataclass
class FutureIncome:
    """Represents future income events - both one-time and recurring.
    
    Can handle both one-time income events (bonuses, tax refunds) and 
    recurring income patterns (raises, new income streams).
    """
    description: str
    amount: float
    start_date: date
    frequency: Optional[str] = None  # If None, it's a one-time event
    end_date: Optional[date] = None  # If None and frequency is set, goes indefinitely
    
    # Legacy field for backward compatibility with one-time events
    date: Optional[date] = None

    def __post_init__(self):
        """Validate future income parameters after initialization."""
        if self.amount <= 0:
            raise ValueError("Income amount must be positive")
        
        # Handle backward compatibility - if 'date' is provided, use it as start_date for one-time event
        if self.date is not None:
            self.start_date = self.date
            self.frequency = None
            self.end_date = None
        
        # Validate dates
        if self.start_date <= date.today():
            raise ValueError("Future income start date must be in the future")
            
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Create recurrence pattern if frequency is specified
        self._pattern = None
        if self.frequency and self.frequency.lower() != 'once':
            self._pattern = RecurrencePattern(self.frequency, self.start_date, self.end_date)
        elif self.frequency and self.frequency.lower() == 'once':
            # 'once' is treated as a one-time event (no pattern needed)
            self._pattern = None
    
    def is_recurring(self) -> bool:
        """Check if this is a recurring income event."""
        return self.frequency is not None and self.frequency.lower() != 'once'
    
    def get_occurrences(self, range_start: date, range_end: date) -> List[Tuple[date, float]]:
        """Get all income occurrences within the specified date range.
        
        Args:
            range_start: Start date of the range
            range_end: End date of the range
            
        Returns:
            List of tuples containing (date, amount) for each occurrence
        """
        occurrences = []
        
        if self.is_recurring() and self._pattern:
            # Get all dates from the recurrence pattern
            dates = self._pattern.get_dates(range_start, range_end)
            for occurrence_date in dates:
                occurrences.append((occurrence_date, self.amount))
        else:
            # One-time event
            if range_start <= self.start_date <= range_end:
                occurrences.append((self.start_date, self.amount))
        
        return sorted(occurrences, key=lambda x: x[0])
    
    def get_total_amount_in_range(self, range_start: date, range_end: date) -> float:
        """Calculate total income amount within the specified date range.
        
        Args:
            range_start: Start date of the range
            range_end: End date of the range
            
        Returns:
            Total amount of income in the date range
        """
        occurrences = self.get_occurrences(range_start, range_end)
        return sum(amount for _, amount in occurrences)
    
    def get_monthly_average(self) -> float:
        """Calculate the average monthly income from this source.
        
        Returns:
            Average monthly income amount
        """
        if not self.is_recurring():
            # One-time events don't have a meaningful monthly average
            return 0.0
        
        return self.amount * self._pattern.get_monthly_frequency()
    
    def __str__(self) -> str:
        """Return a human-readable representation of the income."""
        if self.is_recurring():
            if self.end_date:
                return f"{self.description}: ${self.amount:.2f} {self.frequency} from {self.start_date} to {self.end_date}"
            else:
                return f"{self.description}: ${self.amount:.2f} {self.frequency} starting {self.start_date}"
        else:
            return f"{self.description}: ${self.amount:.2f} on {self.start_date}"


@dataclass
class FutureExpense:
    """Represents future expense events - both one-time and recurring.
    
    Can handle both one-time expense events (major purchases, repairs) and 
    recurring expense patterns (new subscriptions, insurance increases).
    """
    description: str
    amount: float
    start_date: date
    frequency: Optional[str] = None  # If None, it's a one-time event
    end_date: Optional[date] = None  # If None and frequency is set, goes indefinitely
    
    # Legacy field for backward compatibility with one-time events
    date: Optional[date] = None

    def __post_init__(self):
        """Validate future expense parameters after initialization."""
        if self.amount <= 0:
            raise ValueError("Expense amount must be positive")
        
        # Handle backward compatibility - if 'date' is provided, use it as start_date for one-time event
        if self.date is not None:
            self.start_date = self.date
            self.frequency = None
            self.end_date = None
        
        # Validate dates
        if self.start_date <= date.today():
            raise ValueError("Future expense start date must be in the future")
            
        if self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Create recurrence pattern if frequency is specified
        self._pattern = None
        if self.frequency and self.frequency.lower() != 'once':
            self._pattern = RecurrencePattern(self.frequency, self.start_date, self.end_date)
        elif self.frequency and self.frequency.lower() == 'once':
            # 'once' is treated as a one-time event (no pattern needed)
            self._pattern = None
    
    def is_recurring(self) -> bool:
        """Check if this is a recurring expense event."""
        return self.frequency is not None and self.frequency.lower() != 'once'
    
    def get_occurrences(self, range_start: date, range_end: date) -> List[Tuple[date, float]]:
        """Get all expense occurrences within the specified date range.
        
        Args:
            range_start: Start date of the range
            range_end: End date of the range
            
        Returns:
            List of tuples containing (date, amount) for each occurrence
        """
        occurrences = []
        
        if self.is_recurring() and self._pattern:
            # Get all dates from the recurrence pattern
            dates = self._pattern.get_dates(range_start, range_end)
            for occurrence_date in dates:
                occurrences.append((occurrence_date, self.amount))
        else:
            # One-time event
            if range_start <= self.start_date <= range_end:
                occurrences.append((self.start_date, self.amount))
        
        return sorted(occurrences, key=lambda x: x[0])
    
    def get_total_amount_in_range(self, range_start: date, range_end: date) -> float:
        """Calculate total expense amount within the specified date range.
        
        Args:
            range_start: Start date of the range
            range_end: End date of the range
            
        Returns:
            Total amount of expenses in the date range
        """
        occurrences = self.get_occurrences(range_start, range_end)
        return sum(amount for _, amount in occurrences)
    
    def get_monthly_average(self) -> float:
        """Calculate the average monthly expense from this source.
        
        Returns:
            Average monthly expense amount
        """
        if not self.is_recurring():
            # One-time events don't have a meaningful monthly average
            return 0.0
        
        return self.amount * self._pattern.get_monthly_frequency()
    
    def __str__(self) -> str:
        """Return a human-readable representation of the expense."""
        if self.is_recurring():
            if self.end_date:
                return f"{self.description}: ${self.amount:.2f} {self.frequency} from {self.start_date} to {self.end_date}"
            else:
                return f"{self.description}: ${self.amount:.2f} {self.frequency} starting {self.start_date}"
        else:
            return f"{self.description}: ${self.amount:.2f} on {self.start_date}"



def calculate_monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Calculate monthly payment for a loan with fixed terms."""
    if annual_rate == 0:
        return principal / months
    
    monthly_rate = annual_rate / 100 / 12
    return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def calculate_total_monthly_income(income_sources: List[Income]) -> float:
    """Calculate total monthly income from all sources."""
    return sum(income.get_monthly_amount() for income in income_sources)


def generate_amortization_schedule(
    debt: Debt, 
    payment_amount: float, 
    start_date: date
) -> pd.DataFrame:
    """Generate detailed amortization schedule for a debt."""
    schedule = []
    current_balance = debt.balance
    current_date = start_date
    
    month = 0
    max_months = 1200  # Maximum 100 years to prevent infinite loops
    
    # Check if payment is sufficient to make progress
    monthly_interest = debt.calculate_interest_charge(current_balance)
    if payment_amount <= monthly_interest:
        # Payment doesn't cover interest, create a single row showing this
        schedule.append({
            'month': 1,
            'date': current_date,
            'beginning_balance': current_balance,
            'payment': payment_amount,
            'principal': 0,
            'interest': monthly_interest,
            'ending_balance': current_balance + (monthly_interest - payment_amount),
            'debt_name': debt.name
        })
        return pd.DataFrame(schedule)
    
    while current_balance > 0.01 and month < max_months:  # Continue until debt is paid off
        month += 1
        
        interest_payment = debt.calculate_interest_charge(current_balance)
        principal_payment = min(payment_amount - interest_payment, current_balance)
        
        # Ensure we don't have negative principal payments
        if principal_payment < 0:
            principal_payment = 0
        
        new_balance = current_balance - principal_payment
        
        schedule.append({
            'month': month,
            'date': current_date,
            'beginning_balance': current_balance,
            'payment': min(payment_amount, current_balance + interest_payment),
            'principal': principal_payment,
            'interest': interest_payment,
            'ending_balance': max(0, new_balance),
            'debt_name': debt.name
        })
        
        current_balance = new_balance
        
        # Move to next month with year overflow protection
        try:
            if current_date.month == 12:
                new_year = current_date.year + 1
                if new_year > 9999:
                    break  # Stop if we would exceed reasonable year range
                current_date = current_date.replace(year=new_year, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        except ValueError:
            break  # Stop on date calculation errors
    
    return pd.DataFrame(schedule)


class DebtAnalyzer:
    """Utility class for analyzing debt scenarios."""
    
    
    @staticmethod
    def calculate_total_debt(debts: List[Debt]) -> float:
        """Calculate total debt balance."""
        return sum(debt.balance for debt in debts)
    
    @staticmethod
    def calculate_total_minimum_payments(debts: List[Debt]) -> float:
        """Calculate total minimum payments across all debts."""
        return sum(debt.minimum_payment for debt in debts)
    
    @staticmethod
    def calculate_weighted_average_rate(debts: List[Debt]) -> float:
        """Calculate weighted average interest rate across all debts."""
        total_balance = sum(debt.balance for debt in debts)
        if total_balance == 0:
            return 0
        
        weighted_sum = sum(debt.balance * debt.interest_rate for debt in debts)
        return weighted_sum / total_balance
    
    @staticmethod
    def rank_debts_by_avalanche(debts: List[Debt]) -> List[Debt]:
        """Rank debts by interest rate (highest first) for avalanche method."""
        return sorted(debts, key=lambda d: d.interest_rate, reverse=True)
    
    @staticmethod
    def rank_debts_by_snowball(debts: List[Debt]) -> List[Debt]:
        """Rank debts by balance (lowest first) for snowball method."""
        return sorted(debts, key=lambda d: d.balance)
    
    @staticmethod
    def calculate_payoff_order_impact(
        debts: List[Debt], 
        extra_payment: float,
        strategy: str = "avalanche"
    ) -> Dict[str, float]:
        """Calculate impact of different payoff strategies."""
        if strategy == "avalanche":
            ordered_debts = DebtAnalyzer.rank_debts_by_avalanche(debts)
        elif strategy == "snowball":
            ordered_debts = DebtAnalyzer.rank_debts_by_snowball(debts)
        else:
            raise ValueError("Strategy must be 'avalanche' or 'snowball'")
        
        total_interest = 0
        total_months = 0
        
        # Simplified calculation - distribute extra payment to priority debt
        for debt in ordered_debts:
            payment = debt.minimum_payment + extra_payment
            months = debt.calculate_months_to_payoff(payment)
            interest = (payment * months) - debt.balance
            
            total_interest += max(0, interest)
            total_months = max(total_months, months)
            
            # After first debt, extra payment becomes available
            extra_payment += debt.minimum_payment
        
        return {
            "total_interest": total_interest,
            "total_months": total_months,
            "strategy": strategy
        }