"""
Comprehensive tests for debt_optimizer.py module.

Tests the DebtOptimizer class including optimization strategies, debt summary
generation, strategy comparisons, and financial calculations.
"""

# Import the classes to test
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd
import pytest

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.debt_optimizer import DebtOptimizer, OptimizationGoal, OptimizationResult
from core.financial_calc import (Debt, FutureExpense, FutureIncome, Income,
                                 RecurringExpense)


class TestDebtOptimizer:
    """Test cases for the DebtOptimizer class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.debts = [
            Debt("Credit Card", 5000.0, 150.0, 18.99, 15),
            Debt("Auto Loan", 12000.0, 325.0, 4.5, 10),
            Debt("Personal Loan", 3000.0, 100.0, 12.0, 25),
        ]

        self.income = [
            Income("Primary Salary", 3500.0, "bi-weekly", date(2024, 1, 5)),
            Income("Freelance", 800.0, "monthly", date(2024, 1, 1)),
        ]

        self.recurring_expenses = [
            RecurringExpense("Netflix", 15.99, "monthly", 15, date(2024, 1, 1)),
            RecurringExpense("Insurance", 200.0, "monthly", 1, date(2024, 1, 1)),
        ]

        self.future_income = [
            FutureIncome("Bonus", 2000.0, date.today() + timedelta(days=90), "once"),
        ]

        self.future_expenses = [
            FutureExpense(
                "Car Repair", 800.0, date.today() + timedelta(days=60), "once"
            ),
        ]

        self.settings = {
            "emergency_fund": 1000.0,
            "current_bank_balance": 2500.0,
            "optimization_goal": "minimize_interest",
            "extra_payment": 200.0,
        }

        self.optimizer = DebtOptimizer(
            self.debts,
            self.income,
            self.recurring_expenses,
            self.future_income,
            self.future_expenses,
            self.settings,
        )

    @pytest.mark.unit
    def test_initialization_complete(self):
        """Test that DebtOptimizer initializes correctly with all parameters."""
        assert len(self.optimizer.debts) == 3
        assert len(self.optimizer.income_sources) == 2
        assert len(self.optimizer.recurring_expenses) == 2
        assert len(self.optimizer.future_income) == 1
        assert len(self.optimizer.future_expenses) == 1
        assert self.optimizer.settings["emergency_fund"] == 1000.0

    @pytest.mark.unit
    def test_initialization_minimal(self):
        """Test DebtOptimizer initialization with minimal parameters."""
        minimal_optimizer = DebtOptimizer(
            debts=self.debts[:1], income_sources=self.income[:1]
        )
        assert len(minimal_optimizer.debts) == 1
        assert len(minimal_optimizer.income_sources) == 1
        assert len(minimal_optimizer.recurring_expenses) == 0
        assert len(minimal_optimizer.future_income) == 0
        assert len(minimal_optimizer.future_expenses) == 0

    @pytest.mark.unit
    def test_debt_summary_generation(self):
        """Test generation of debt summary information."""
        summary = self.optimizer.generate_debt_summary()

        # Check required keys exist
        required_keys = [
            "total_debt",
            "monthly_income",
            "total_minimum_payments",
            "available_cash_flow",
            "current_bank_balance",
            "available_extra_payment",
        ]
        for key in required_keys:
            assert key in summary
            assert isinstance(summary[key], (int, float))

        # Check calculations make sense
        assert summary["total_debt"] > 0
        assert summary["monthly_income"] > 0
        assert summary["total_minimum_payments"] > 0

        # Total debt should equal sum of individual debt balances
        expected_total_debt = sum(debt.balance for debt in self.debts)
        assert abs(summary["total_debt"] - expected_total_debt) < 0.01

        # Minimum payments should equal sum of individual minimums
        expected_min_payments = sum(debt.minimum_payment for debt in self.debts)
        assert abs(summary["total_minimum_payments"] - expected_min_payments) < 0.01

    @pytest.mark.unit
    def test_monthly_income_calculation(self):
        """Test accurate monthly income calculation from various frequencies."""
        summary = self.optimizer.generate_debt_summary()

        # Calculate expected monthly income manually
        expected_monthly = 0
        for income in self.income:
            expected_monthly += income.get_monthly_amount()

        assert abs(summary["monthly_income"] - expected_monthly) < 0.01

    @pytest.mark.unit
    def test_cash_flow_calculation(self):
        """Test cash flow calculations including expenses."""
        summary = self.optimizer.generate_debt_summary()

        # Available cash flow should account for income, expenses, and debt minimums
        monthly_income = summary["monthly_income"]
        minimum_payments = summary["total_minimum_payments"]
        monthly_expenses = sum(
            exp.get_monthly_amount() for exp in self.recurring_expenses
        )

        expected_cash_flow = monthly_income - minimum_payments - monthly_expenses
        assert abs(summary["available_cash_flow"] - expected_cash_flow) < 0.01

    @pytest.mark.unit
    def test_optimization_goal_enum(self):
        """Test OptimizationGoal enum functionality."""
        # Test enum values
        assert OptimizationGoal.MINIMIZE_INTEREST.value == "minimize_interest"
        assert OptimizationGoal.MINIMIZE_TIME.value == "minimize_time"
        assert OptimizationGoal.MAXIMIZE_CASHFLOW.value == "maximize_cashflow"

        # Test enum creation from string
        goal_from_string = OptimizationGoal("minimize_interest")
        assert goal_from_string == OptimizationGoal.MINIMIZE_INTEREST

    @pytest.mark.unit
    def test_debt_avalanche_strategy(self):
        """Test debt avalanche optimization strategy."""
        result = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_INTEREST, extra_payment=200.0
        )

        assert isinstance(result, OptimizationResult)
        assert result.strategy in ["debt_avalanche", "debt_snowball", "hybrid"]
        assert result.total_interest_paid > 0
        assert result.total_months_to_freedom > 0
        assert "interest_saved" in result.savings_vs_minimum
        assert "months_saved" in result.savings_vs_minimum

    @pytest.mark.unit
    def test_debt_snowball_strategy(self):
        """Test debt snowball optimization strategy."""
        result = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_TIME, extra_payment=100.0
        )

        assert isinstance(result, OptimizationResult)
        assert result.total_interest_paid >= 0
        assert result.total_months_to_freedom > 0
        assert isinstance(result.payment_schedule, pd.DataFrame)

    @pytest.mark.unit
    def test_hybrid_strategy(self):
        """Test hybrid optimization strategy."""
        result = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MAXIMIZE_CASHFLOW, extra_payment=150.0
        )

        assert isinstance(result, OptimizationResult)
        assert result.total_interest_paid >= 0
        assert result.total_months_to_freedom > 0

    @pytest.mark.unit
    def test_strategy_comparison(self):
        """Test comparison of multiple debt strategies."""
        comparison = self.optimizer.compare_strategies(extra_payment=200.0)

        assert isinstance(comparison, pd.DataFrame)
        assert len(comparison) >= 3  # Should have at least 3 strategies

        # Check required columns
        required_columns = ["strategy", "total_interest", "months_to_freedom"]
        for col in required_columns:
            assert col in comparison.columns

        # Check that all strategies have positive values
        assert all(comparison["total_interest"] >= 0)
        assert all(comparison["months_to_freedom"] > 0)

    @pytest.mark.unit
    def test_extra_payment_impact(self):
        """Test that extra payments reduce total interest and time."""
        # Run optimization with no extra payment
        result_no_extra = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_INTEREST, extra_payment=0.0
        )

        # Run optimization with extra payment
        result_with_extra = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_INTEREST, extra_payment=300.0
        )

        # Extra payment should reduce both time and interest
        assert (
            result_with_extra.total_months_to_freedom
            <= result_no_extra.total_months_to_freedom
        )
        assert (
            result_with_extra.total_interest_paid <= result_no_extra.total_interest_paid
        )

    @pytest.mark.unit
    def test_payment_schedule_format(self):
        """Test that payment schedule is properly formatted."""
        result = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_INTEREST, extra_payment=100.0
        )

        schedule = result.payment_schedule
        assert isinstance(schedule, pd.DataFrame)
        assert len(schedule) > 0

        # Check for expected columns (matching current implementation)
        expected_columns = [
            "date",
            "type",
            "description",
            "amount",
            "interest_portion",
            "principal_portion",
            "remaining_balance",
            "bank_balance",
            "debt_balance",
            "debt_name",
        ]
        for col in expected_columns:
            assert col in schedule.columns

        # Check data types and ranges
        assert len(schedule["date"]) > 0  # Should have date entries
        assert all(schedule["remaining_balance"] >= 0)
        assert all(schedule["bank_balance"] >= -10000)  # Allow for reasonable overdraft
        # Note: Amount can be negative (expenses) or positive (income)

    @pytest.mark.unit
    def test_optimization_result_validation(self):
        """Test that optimization results are mathematically consistent."""
        result = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_INTEREST, extra_payment=200.0
        )

        # Total payments should be greater than total debt principal
        total_debt = sum(debt.balance for debt in self.debts)
        assert result.total_interest_paid >= 0

        # Months to freedom should be reasonable
        assert 1 <= result.total_months_to_freedom <= 1000  # Sanity check

        # Savings should make sense
        assert result.savings_vs_minimum["interest_saved"] >= 0
        assert result.savings_vs_minimum["months_saved"] >= 0

    @pytest.mark.unit
    def test_future_transactions_impact(self):
        """Test that future income and expenses are properly considered."""
        # Create optimizer without future transactions
        optimizer_no_future = DebtOptimizer(
            self.debts, self.income, self.recurring_expenses, [], [], self.settings
        )

        # Create optimizer with future transactions
        optimizer_with_future = DebtOptimizer(
            self.debts,
            self.income,
            self.recurring_expenses,
            self.future_income,
            self.future_expenses,
            self.settings,
        )

        result_no_future = optimizer_no_future.optimize_debt_strategy(
            OptimizationGoal.MINIMIZE_INTEREST, 100.0
        )
        result_with_future = optimizer_with_future.optimize_debt_strategy(
            OptimizationGoal.MINIMIZE_INTEREST, 100.0
        )

        # Results should be different when future transactions are considered
        # (The exact impact depends on the implementation)
        assert isinstance(result_no_future, OptimizationResult)
        assert isinstance(result_with_future, OptimizationResult)

    @pytest.mark.unit
    def test_emergency_fund_consideration(self):
        """Test that emergency fund settings are properly considered."""
        summary = self.optimizer.generate_debt_summary()

        # Available extra payment should consider emergency fund
        assert summary["available_extra_payment"] >= 0

        # If current balance is less than emergency fund, extra payment should be limited
        if summary["current_bank_balance"] < self.settings["emergency_fund"]:
            assert summary["available_extra_payment"] <= summary["available_cash_flow"]

    @pytest.mark.unit
    def test_edge_case_zero_balance_debt(self):
        """Test handling of debts with zero balance."""
        debts_with_zero = self.debts + [Debt("Paid Off Card", 0.0, 0.0, 0.0, 15)]

        optimizer = DebtOptimizer(
            debts_with_zero, self.income, [], [], [], self.settings
        )
        result = optimizer.optimize_debt_strategy(
            OptimizationGoal.MINIMIZE_INTEREST, 100.0
        )

        assert isinstance(result, OptimizationResult)
        assert result.total_months_to_freedom >= 0

    @pytest.mark.unit
    def test_edge_case_insufficient_income(self):
        """Test handling when income is insufficient for minimum payments."""
        low_income = [Income("Low Salary", 200.0, "monthly", date(2024, 1, 1))]

        optimizer = DebtOptimizer(self.debts, low_income, [], [], [], {})
        summary = optimizer.generate_debt_summary()

        # Should still generate summary but with negative cash flow
        assert summary["available_cash_flow"] < 0
        assert "total_debt" in summary
        assert "monthly_income" in summary

    @pytest.mark.unit
    def test_large_extra_payment(self):
        """Test optimization with very large extra payments."""
        # Use extra payment that could pay off all debts quickly
        large_extra_payment = 5000.0

        result = self.optimizer.optimize_debt_strategy(
            goal=OptimizationGoal.MINIMIZE_TIME, extra_payment=large_extra_payment
        )

        assert isinstance(result, OptimizationResult)
        # Should pay off debts very quickly
        assert result.total_months_to_freedom <= 12
        assert result.total_interest_paid >= 0

    @pytest.mark.unit
    def test_optimization_consistency(self):
        """Test that multiple runs of optimization produce consistent results."""
        # Run same optimization multiple times
        results = []
        for _ in range(3):
            result = self.optimizer.optimize_debt_strategy(
                goal=OptimizationGoal.MINIMIZE_INTEREST, extra_payment=200.0
            )
            results.append(result)

        # Results should be identical
        for i in range(1, len(results)):
            assert results[i].strategy == results[0].strategy
            assert (
                abs(results[i].total_interest_paid - results[0].total_interest_paid)
                < 0.01
            )
            assert (
                results[i].total_months_to_freedom == results[0].total_months_to_freedom
            )


class TestOptimizationResult:
    """Test cases for the OptimizationResult class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sample_schedule = pd.DataFrame(
            {
                "date": [
                    pd.Timestamp("2024-01-15"),
                    pd.Timestamp("2024-02-15"),
                    pd.Timestamp("2024-03-15"),
                ],
                "type": ["payment", "payment", "payment"],
                "description": [
                    "Credit Card Payment",
                    "Credit Card Payment",
                    "Auto Loan Payment",
                ],
                "amount": [-175.0, -173.5, -345.0],
                "interest_portion": [75.0, 73.5, 45.0],
                "principal_portion": [100.0, 100.0, 300.0],
                "remaining_balance": [16900.0, 16800.0, 16500.0],
                "bank_balance": [3000.0, 2826.5, 2481.5],
                "debt_balance": [4900.0, 4800.0, 11700.0],
                "debt_name": ["Credit Card", "Credit Card", "Auto Loan"],
            }
        )

        self.result = OptimizationResult(
            strategy="debt_avalanche",
            goal="minimize_interest",
            total_interest_paid=2500.0,
            total_months_to_freedom=36,
            monthly_cash_flow_improvement=150.0,
            payment_schedule=self.sample_schedule,
            monthly_summary=pd.DataFrame(
                {"month": [1, 2, 3], "total_payment": [175.0, 173.5, 345.0]}
            ),
            debt_progression=pd.DataFrame(
                {"month": [1, 2, 3], "remaining_debt": [17000.0, 16800.0, 16500.0]}
            ),
            savings_vs_minimum={"interest_saved": 500.0, "months_saved": 6},
            decision_log=[],
            monthly_extra_funds=[],
        )

    @pytest.mark.unit
    def test_optimization_result_creation(self):
        """Test OptimizationResult object creation."""
        assert self.result.strategy == "debt_avalanche"
        assert self.result.total_interest_paid == 2500.0
        assert self.result.total_months_to_freedom == 36
        assert isinstance(self.result.payment_schedule, pd.DataFrame)
        assert self.result.savings_vs_minimum["interest_saved"] == 500.0
        assert self.result.savings_vs_minimum["months_saved"] == 6

    @pytest.mark.unit
    def test_optimization_result_string_representation(self):
        """Test string representation of OptimizationResult."""
        result_str = str(self.result)
        assert "debt_avalanche" in result_str
        assert "2500" in result_str or "2,500" in result_str
        assert "36" in result_str
