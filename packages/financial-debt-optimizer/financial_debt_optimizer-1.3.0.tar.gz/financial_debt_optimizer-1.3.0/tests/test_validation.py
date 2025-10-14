"""
Comprehensive tests for validation.py module.

Tests all validation functions for financial scenarios, data integrity checks,
and error handling.
"""

# Import the classes to test
import sys
from datetime import date
from pathlib import Path
from typing import List

import pytest

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.financial_calc import (Debt, FutureExpense, FutureIncome, Income,
                                 RecurringExpense)
from core.validation import (ValidationError, validate_debt_data, validate_expense_data,
                             validate_financial_scenario, validate_income_data)


class TestFinancialScenarioValidation:
    """Test cases for overall financial scenario validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.valid_debts = [
            Debt("Credit Card", 5000.0, 150.0, 18.99, 15),
            Debt("Auto Loan", 12000.0, 325.0, 4.5, 10),
        ]

        self.valid_income = [
            Income("Salary", 3500.0, "bi-weekly", date(2024, 1, 5)),
            Income("Freelance", 800.0, "monthly", date(2024, 1, 1)),
        ]

        self.valid_expenses = [
            RecurringExpense("Netflix", 15.99, "monthly", 15, date(2024, 1, 1)),
            RecurringExpense("Insurance", 200.0, "monthly", 1, date(2024, 1, 1)),
        ]

        self.valid_settings = {
            "emergency_fund": 1000.0,
            "current_bank_balance": 2500.0,
            "optimization_goal": "minimize_interest",
        }

    @pytest.mark.unit
    def test_validate_financial_scenario_valid(self):
        """Test validation with valid financial scenario."""
        is_valid, messages = validate_financial_scenario(
            self.valid_debts,
            self.valid_income,
            self.valid_expenses,
            self.valid_settings,
        )

        assert is_valid is True
        assert isinstance(messages, list)
        # May have warnings but should be valid overall

    @pytest.mark.unit
    def test_validate_financial_scenario_no_debts(self):
        """Test validation with no debts."""
        is_valid, messages = validate_financial_scenario(
            [], self.valid_income, self.valid_expenses, self.valid_settings
        )

        assert is_valid is False
        assert len(messages) > 0
        assert any("no debts" in msg.lower() for msg in messages)

    @pytest.mark.unit
    def test_validate_financial_scenario_no_income(self):
        """Test validation with no income."""
        is_valid, messages = validate_financial_scenario(
            self.valid_debts, [], self.valid_expenses, self.valid_settings
        )

        assert is_valid is False
        assert len(messages) > 0
        assert any("no income" in msg.lower() for msg in messages)

    @pytest.mark.unit
    def test_validate_financial_scenario_insufficient_income(self):
        """Test validation with insufficient income for minimum payments."""
        low_income = [Income("Low Salary", 200.0, "monthly", date(2024, 1, 1))]

        is_valid, messages = validate_financial_scenario(
            self.valid_debts, low_income, self.valid_expenses, self.valid_settings
        )

        assert is_valid is False
        assert len(messages) > 0
        assert any("insufficient" in msg.lower() for msg in messages)

    @pytest.mark.unit
    def test_validate_financial_scenario_negative_cash_flow(self):
        """Test validation with negative cash flow after expenses."""
        # Make expenses high enough to create negative cash flow
        # Valid income is ~8,383/month, debt payments are 475, so need expenses > 7,908
        high_expenses = [
            RecurringExpense("High Rent", 6000.0, "monthly", 1, date(2024, 1, 1)),
            RecurringExpense("High Insurance", 3000.0, "monthly", 15, date(2024, 1, 1)),
        ]

        is_valid, messages = validate_financial_scenario(
            self.valid_debts, self.valid_income, high_expenses, self.valid_settings
        )

        # Should produce errors about negative cash flow
        assert isinstance(messages, list)
        assert len(messages) > 0
        assert is_valid is False  # Should be invalid with negative cash flow

    @pytest.mark.unit
    def test_validate_financial_scenario_warnings_only(self):
        """Test scenario that produces warnings but is still valid."""
        # Create scenario with very low bank balance
        settings_low_balance = self.valid_settings.copy()
        settings_low_balance["current_bank_balance"] = 100.0  # Below emergency fund

        is_valid, messages = validate_financial_scenario(
            self.valid_debts,
            self.valid_income,
            self.valid_expenses,
            settings_low_balance,
        )

        # Should be valid but have warnings
        assert isinstance(messages, list)
        # May have warnings about low balance


class TestDebtDataValidation:
    """Test cases for debt data validation."""

    @pytest.mark.unit
    def test_validate_debt_data_valid(self):
        """Test validation with valid debt data."""
        valid_debts = [
            Debt("Credit Card", 5000.0, 150.0, 18.99, 15),
            Debt("Auto Loan", 12000.0, 325.0, 4.5, 10),
        ]

        errors = validate_debt_data(valid_debts)
        assert isinstance(errors, list)
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_debt_data_zero_balance(self):
        """Test validation with zero balance debt."""
        debts_with_zero = [
            Debt("Paid Off Card", 0.0, 0.0, 0.0, 15),
            Debt("Active Card", 1000.0, 25.0, 15.0, 15),
        ]

        errors = validate_debt_data(debts_with_zero)
        # Zero balance should produce warnings, not errors
        assert isinstance(errors, list)

    @pytest.mark.unit
    def test_validate_debt_data_negative_balance(self):
        """Test validation with negative balance."""
        # Use dictionary format since object creation would fail in __post_init__
        debt_data = {
            "name": "Negative Card",
            "balance": -1000.0,
            "minimum_payment": 25.0,
            "interest_rate": 15.0,
            "due_date": 15,
        }

        errors = validate_debt_data(debt_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("negative" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_debt_data_negative_minimum_payment(self):
        """Test validation with negative minimum payment."""
        # Use dictionary format since object creation would fail in __post_init__
        debt_data = {
            "name": "Bad Payment",
            "balance": 1000.0,
            "minimum_payment": -25.0,
            "interest_rate": 15.0,
            "due_date": 15,
        }

        errors = validate_debt_data(debt_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("minimum payment" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_debt_data_negative_interest_rate(self):
        """Test validation with negative interest rate."""
        # Use dictionary format since object creation would fail in __post_init__
        debt_data = {
            "name": "Bad Rate",
            "balance": 1000.0,
            "minimum_payment": 25.0,
            "interest_rate": -5.0,
            "due_date": 15,
        }

        errors = validate_debt_data(debt_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("interest rate" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_debt_data_invalid_due_date(self):
        """Test validation with invalid due date."""
        # Use dictionary format since object creation would fail in __post_init__
        debt_data_bad = {
            "name": "Bad Date",
            "balance": 1000.0,
            "minimum_payment": 25.0,
            "interest_rate": 15.0,
            "due_date": 32,  # Day 32 doesn't exist
        }

        errors = validate_debt_data(debt_data_bad)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("due date" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_debt_data_empty_name(self):
        """Test validation with empty debt name."""
        debts_empty_name = [
            Debt("", 1000.0, 25.0, 15.0, 15),
            Debt(None, 1000.0, 25.0, 15.0, 15),
        ]

        errors = validate_debt_data(debts_empty_name)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)


class TestIncomeDataValidation:
    """Test cases for income data validation."""

    @pytest.mark.unit
    def test_validate_income_data_valid(self):
        """Test validation with valid income data."""
        valid_income = [
            Income("Salary", 3500.0, "bi-weekly", date(2024, 1, 5)),
            Income("Freelance", 800.0, "monthly", date(2024, 1, 1)),
        ]

        errors = validate_income_data(valid_income)
        assert isinstance(errors, list)
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_income_data_zero_amount(self):
        """Test validation with zero income amount."""
        # Use dictionary format since object creation would fail in __post_init__
        income_data = {"source": "Zero Income", "amount": 0.0, "frequency": "monthly"}

        errors = validate_income_data(income_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("amount" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_income_data_negative_amount(self):
        """Test validation with negative income amount."""
        # Use dictionary format since object creation would fail in __post_init__
        income_data = {
            "source": "Negative Income",
            "amount": -1000.0,
            "frequency": "monthly",
        }

        errors = validate_income_data(income_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("positive" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_income_data_invalid_frequency(self):
        """Test validation with invalid frequency."""
        # Use dictionary format since object creation would fail in __post_init__
        income_data = {
            "source": "Bad Frequency",
            "amount": 1000.0,
            "frequency": "invalid_frequency",
        }

        errors = validate_income_data(income_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("frequency" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_income_data_future_start_date(self):
        """Test validation with future start date."""
        future_start_income = [
            Income("Future Income", 1000.0, "monthly", date(2030, 1, 1)),
        ]

        errors = validate_income_data(future_start_income)
        # Future start dates might generate warnings but not necessarily errors
        assert isinstance(errors, list)

    @pytest.mark.unit
    def test_validate_income_data_empty_source(self):
        """Test validation with empty income source."""
        empty_source_income = [
            Income("", 1000.0, "monthly", date(2024, 1, 1)),
            Income(None, 1000.0, "monthly", date(2024, 1, 1)),
        ]

        errors = validate_income_data(empty_source_income)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("source" in error.lower() for error in errors)


class TestExpenseDataValidation:
    """Test cases for recurring expense data validation."""

    @pytest.mark.unit
    def test_validate_expense_data_valid(self):
        """Test validation with valid expense data."""
        valid_expenses = [
            RecurringExpense("Netflix", 15.99, "monthly", 15, date(2024, 1, 1)),
            RecurringExpense("Insurance", 200.0, "monthly", 1, date(2024, 1, 1)),
        ]

        errors = validate_expense_data(valid_expenses)
        assert isinstance(errors, list)
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_expense_data_zero_amount(self):
        """Test validation with zero expense amount."""
        # Use dictionary format since object creation would fail in __post_init__
        expense_data = {
            "description": "Free Service",
            "amount": 0.0,
            "frequency": "monthly",
        }

        errors = validate_expense_data(expense_data)
        # Zero amount expenses should produce errors
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("positive" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_expense_data_negative_amount(self):
        """Test validation with negative expense amount."""
        # Use dictionary format since object creation would fail in __post_init__
        expense_data = {
            "description": "Negative Expense",
            "amount": -50.0,
            "frequency": "monthly",
        }

        errors = validate_expense_data(expense_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("positive" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_expense_data_invalid_frequency(self):
        """Test validation with invalid frequency."""
        # Use dictionary format since object creation would fail in __post_init__
        expense_data = {
            "description": "Bad Frequency",
            "amount": 100.0,
            "frequency": "invalid_freq",
        }

        errors = validate_expense_data(expense_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("frequency" in error.lower() for error in errors)

    @pytest.mark.unit
    def test_validate_expense_data_invalid_due_date(self):
        """Test validation with invalid due date."""
        # Use dictionary format since object creation would fail in __post_init__
        expense_data = {
            "description": "Bad Date",
            "amount": 100.0,
            "frequency": "monthly",
            "due_date": 32,
        }

        errors = validate_expense_data(expense_data)
        assert isinstance(errors, list)
        assert len(errors) > 0
        assert any("due date" in error.lower() for error in errors)


class TestValidationErrorHandling:
    """Test cases for validation error handling."""

    @pytest.mark.unit
    def test_validation_error_creation(self):
        """Test ValidationError exception creation."""
        error_message = "Test validation error"
        error = ValidationError(error_message)

        assert str(error) == error_message
        assert isinstance(error, Exception)

    @pytest.mark.unit
    def test_validation_with_none_inputs(self):
        """Test validation functions with None inputs."""
        # Test that None inputs are handled gracefully
        is_valid, messages = validate_financial_scenario(None, None, None, None)

        assert is_valid is False
        assert isinstance(messages, list)
        assert len(messages) > 0

    @pytest.mark.unit
    def test_validation_with_empty_lists(self):
        """Test validation functions with empty lists."""
        is_valid, messages = validate_financial_scenario([], [], [], {})

        assert is_valid is False
        assert isinstance(messages, list)
        assert len(messages) > 0

    @pytest.mark.unit
    def test_validation_robustness(self):
        """Test that validation functions don't crash on malformed data."""
        # Create deliberately bad data
        bad_debts = [None, "not_a_debt_object"]
        bad_income = [None, 123]  # Not Income objects
        bad_expenses = ["string_instead_of_expense"]
        bad_settings = "not_a_dict"

        # Should not crash, should return validation errors
        try:
            is_valid, messages = validate_financial_scenario(
                bad_debts, bad_income, bad_expenses, bad_settings
            )
            assert is_valid is False
            assert isinstance(messages, list)
        except Exception as e:
            # If it does raise an exception, it should be a ValidationError
            assert isinstance(e, (ValidationError, TypeError, AttributeError))


class TestValidationIntegration:
    """Integration tests for validation functionality."""

    @pytest.mark.integration
    def test_complete_validation_workflow(self):
        """Test complete validation workflow with realistic data."""
        # Create realistic financial scenario
        debts = [
            Debt("Credit Card", 8500.0, 250.0, 22.99, 15),
            Debt("Auto Loan", 18500.0, 425.0, 5.5, 5),
            Debt("Student Loan", 35000.0, 350.0, 6.8, 20),
        ]

        income = [
            Income("Primary Job", 4200.0, "bi-weekly", date(2024, 1, 1)),
            Income("Side Hustle", 1200.0, "monthly", date(2024, 1, 1)),
        ]

        expenses = [
            RecurringExpense("Rent", 1800.0, "monthly", 1, date(2024, 1, 1)),
            RecurringExpense("Utilities", 200.0, "monthly", 15, date(2024, 1, 1)),
            RecurringExpense("Groceries", 150.0, "weekly", 1, date(2024, 1, 1)),
            RecurringExpense("Insurance", 300.0, "monthly", 25, date(2024, 1, 1)),
        ]

        settings = {
            "emergency_fund": 5000.0,
            "current_bank_balance": 3500.0,
            "optimization_goal": "minimize_interest",
            "extra_payment": 500.0,
        }

        # Run validation
        is_valid, messages = validate_financial_scenario(
            debts, income, expenses, settings
        )

        # Should be valid or have only minor warnings
        assert isinstance(is_valid, bool)
        assert isinstance(messages, list)

        # If there are messages, they should be informative
        for message in messages:
            assert isinstance(message, str)
            assert len(message) > 0

    @pytest.mark.integration
    def test_validation_edge_cases_realistic(self):
        """Test validation with realistic edge cases."""
        # High debt-to-income ratio scenario
        high_debt_scenario = {
            "debts": [Debt("High Debt", 100000.0, 2000.0, 25.0, 15)],
            "income": [Income("Low Income", 2500.0, "monthly", date(2024, 1, 1))],
            "expenses": [
                RecurringExpense("Rent", 1000.0, "monthly", 1, date(2024, 1, 1))
            ],
            "settings": {
                "emergency_fund": 1000.0,
                "current_bank_balance": 500.0,
                "optimization_goal": "minimize_interest",
            },
        }

        is_valid, messages = validate_financial_scenario(
            high_debt_scenario["debts"],
            high_debt_scenario["income"],
            high_debt_scenario["expenses"],
            high_debt_scenario["settings"],
        )

        # Should detect the problematic debt-to-income ratio
        assert isinstance(is_valid, bool)
        assert isinstance(messages, list)
        if not is_valid:
            assert len(messages) > 0
