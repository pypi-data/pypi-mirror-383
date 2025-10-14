"""Validation utilities for financial data and inputs."""

from typing import Any, Dict, List, Tuple

from .financial_calc import Debt, Income, RecurringExpense


class ValidationError(ValueError):
    """Custom exception for validation errors."""

    pass


def validate_debt_data(debt_data) -> List[str]:
    """Validate debt data - can handle both dictionaries and lists of Debt objects.

    Args:
        debt_data: Dictionary containing debt information or list of Debt objects

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Handle list of Debt objects
    if isinstance(debt_data, list):
        for i, debt in enumerate(debt_data):
            if isinstance(debt, Debt):
                # Since the Debt object was created successfully, it passed __post_init__ validation
                # Just check for any logical issues
                try:
                    if not debt.name or debt.name.strip() == "":
                        errors.append(f"Debt {i+1}: Name cannot be empty")
                    # Additional validation can go here if needed
                except Exception:
                    errors.append(f"Debt {i+1}: Invalid debt data")
            else:
                errors.append(f"Item {i+1}: Expected Debt object, got {type(debt)}")
        return errors

    # Handle dictionary format (original functionality)
    if not isinstance(debt_data, dict):
        errors.append("Debt data must be a dictionary or list of Debt objects")
        return errors

    # Required fields
    required_fields = [
        "name",
        "balance",
        "minimum_payment",
        "interest_rate",
        "due_date",
    ]
    for field in required_fields:
        if field not in debt_data or debt_data[field] is None:
            errors.append(f"Missing required field: {field}")

    # Validate numeric fields
    if "balance" in debt_data:
        try:
            balance = float(debt_data["balance"])
            if balance < 0:
                errors.append("Balance cannot be negative")
        except (ValueError, TypeError):
            errors.append("Balance must be a valid number")

    if "minimum_payment" in debt_data:
        try:
            min_payment = float(debt_data["minimum_payment"])
            if min_payment < 0:
                errors.append("Minimum payment cannot be negative")
        except (ValueError, TypeError):
            errors.append("Minimum payment must be a valid number")

    if "interest_rate" in debt_data:
        try:
            interest_rate = float(debt_data["interest_rate"])
            if interest_rate < 0 or interest_rate > 100:
                errors.append("Interest rate must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("Interest rate must be a valid number")

    if "due_date" in debt_data:
        try:
            due_date = int(debt_data["due_date"])
            if due_date < 1 or due_date > 31:
                errors.append("Due date must be between 1 and 31")
        except (ValueError, TypeError):
            errors.append("Due date must be a valid integer")

    return errors


def validate_income_data(income_data) -> List[str]:
    """Validate income data - can handle both dictionaries and lists of Income objects.

    Args:
        income_data: Dictionary containing income information or list of Income objects

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Handle list of Income objects
    if isinstance(income_data, list):
        for i, income in enumerate(income_data):
            if isinstance(income, Income):
                # Income objects have their own validation in __post_init__
                try:
                    if not income.source or income.source.strip() == "":
                        errors.append(f"Income {i+1}: Source cannot be empty")
                    if income.amount <= 0:
                        errors.append(f"Income {i+1}: Amount must be positive")
                except Exception:
                    errors.append(f"Income {i+1}: Invalid income data")
            else:
                errors.append(f"Item {i+1}: Expected Income object, got {type(income)}")
        return errors

    # Handle dictionary format (original functionality)
    if not isinstance(income_data, dict):
        errors.append("Income data must be a dictionary or list of Income objects")
        return errors

    # Required fields
    required_fields = ["source", "amount", "frequency"]
    for field in required_fields:
        if field not in income_data or income_data[field] is None:
            errors.append(f"Missing required field: {field}")

    # Validate amount
    if "amount" in income_data:
        try:
            amount = float(income_data["amount"])
            if amount <= 0:
                errors.append("Income amount must be positive")
        except (ValueError, TypeError):
            errors.append("Income amount must be a valid number")

    # Validate frequency
    if "frequency" in income_data:
        valid_frequencies = ["weekly", "bi-weekly", "monthly", "quarterly", "annually"]
        frequency = str(income_data["frequency"]).lower().strip()
        if frequency not in valid_frequencies:
            errors.append(
                f"Invalid frequency. Must be one of: {', '.join(valid_frequencies)}"
            )

    return errors


def validate_expense_data(expense_data) -> List[str]:
    """Validate expense data - can handle both dictionaries and lists of RecurringExpense objects.

    Args:
        expense_data: Dictionary containing expense information or list of RecurringExpense objects

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Handle list of RecurringExpense objects
    if isinstance(expense_data, list):
        for i, expense in enumerate(expense_data):
            if isinstance(expense, RecurringExpense):
                # RecurringExpense objects have their own validation in __post_init__
                try:
                    if not expense.description or expense.description.strip() == "":
                        errors.append(f"Expense {i+1}: Description cannot be empty")
                    if expense.amount <= 0:
                        errors.append(f"Expense {i+1}: Amount must be positive")
                except Exception:
                    errors.append(f"Expense {i+1}: Invalid expense data")
            else:
                errors.append(
                    f"Item {i+1}: Expected RecurringExpense object, got {type(expense)}"
                )
        return errors

    # Handle dictionary format (original functionality)
    if not isinstance(expense_data, dict):
        errors.append(
            "Expense data must be a dictionary or list of RecurringExpense objects"
        )
        return errors

    # Required fields
    required_fields = ["description", "amount", "frequency"]
    for field in required_fields:
        if field not in expense_data or expense_data[field] is None:
            errors.append(f"Missing required field: {field}")

    # Validate amount
    if "amount" in expense_data:
        try:
            amount = float(expense_data["amount"])
            if amount <= 0:
                errors.append("Expense amount must be positive")
        except (ValueError, TypeError):
            errors.append("Expense amount must be a valid number")

    # Validate frequency
    if "frequency" in expense_data:
        valid_frequencies = ["weekly", "bi-weekly", "monthly", "quarterly", "annually"]
        frequency = str(expense_data["frequency"]).lower().strip()
        if frequency not in valid_frequencies:
            errors.append(
                f"Invalid frequency. Must be one of: {', '.join(valid_frequencies)}"
            )

    # Validate due_date if present
    if "due_date" in expense_data:
        try:
            due_date = int(expense_data["due_date"])
            if due_date < 1 or due_date > 31:
                errors.append("Due date must be between 1 and 31")
        except (ValueError, TypeError):
            errors.append("Due date must be a valid integer")

    return errors


def validate_financial_scenario(
    debts: List[Debt],
    income_sources: List[Income],
    recurring_expenses: List[RecurringExpense],
    settings: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """Validate a complete financial scenario for logical consistency.

    Args:
        debts: List of debt objects
        income_sources: List of income objects
        recurring_expenses: List of recurring expense objects
        settings: Settings dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    warnings = []

    # Handle None inputs
    if debts is None:
        debts = []
    if income_sources is None:
        income_sources = []
    if recurring_expenses is None:
        recurring_expenses = []
    if settings is None:
        settings = {}

    # Check if we have debts
    if not debts:
        errors.append("No debts provided - nothing to optimize")

    # Check if we have income
    if not income_sources:
        errors.append("No income sources provided")

    # Calculate totals for validation
    if debts and income_sources:
        total_debt = sum(debt.balance for debt in debts)
        total_minimum_payments = sum(debt.minimum_payment for debt in debts)
        total_monthly_income = sum(
            income.get_monthly_amount() for income in income_sources
        )
        total_monthly_expenses = sum(
            expense.get_monthly_amount() for expense in recurring_expenses
        )

        # Check basic financial viability
        if total_monthly_income < total_minimum_payments:
            errors.append(
                f"Monthly income (${total_monthly_income:.2f}) is less than "
                f"minimum debt payments (${total_minimum_payments:.2f})"
            )

        available_cashflow = (
            total_monthly_income - total_minimum_payments - total_monthly_expenses
        )
        if available_cashflow < 0:
            errors.append(
                f"Insufficient cash flow: Monthly income (${total_monthly_income:.2f}) "
                f"minus minimum payments (${total_minimum_payments:.2f}) "
                f"minus expenses (${total_monthly_expenses:.2f}) "
                f"= ${available_cashflow:.2f}"
            )

        # Warnings for potential issues
        if (
            total_debt > total_monthly_income * 60
        ):  # More than 5 years of income in debt
            warnings.append(
                f"Very high debt-to-income ratio: ${total_debt:.2f} debt vs ${total_monthly_income:.2f} monthly income"
            )

        if available_cashflow < 100:
            warnings.append(
                f"Very tight cash flow: Only ${available_cashflow:.2f} available after minimums and expenses"
            )

    # Validate settings
    if "current_bank_balance" in settings:
        try:
            bank_balance = float(settings["current_bank_balance"])
            if bank_balance < 0:
                warnings.append("Negative bank balance may cause cash flow issues")
        except (ValueError, TypeError):
            errors.append("Invalid bank balance in settings")

    is_valid = len(errors) == 0
    all_messages = errors + [f"Warning: {w}" for w in warnings]

    return is_valid, all_messages


def validate_optimization_goal(goal: str) -> bool:
    """Validate optimization goal string.

    Args:
        goal: Goal string to validate

    Returns:
        True if valid, False otherwise
    """
    valid_goals = ["minimize_interest", "minimize_time", "maximize_cashflow"]
    return goal.lower() in valid_goals
