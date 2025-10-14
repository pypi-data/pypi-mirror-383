import pytest
from datetime import date, datetime
from core.financial_calc import Debt, Income, calculate_monthly_payment


class TestDebt:
    def test_debt_creation(self):
        """Test that Debt objects are created correctly."""
        debt = Debt("Test Credit Card", 1000.0, 25.0, 15.99, 15)
        assert debt.name == "Test Credit Card"
        assert debt.balance == 1000.0
        assert debt.minimum_payment == 25.0
        assert debt.interest_rate == 15.99
        assert debt.due_date == 15

    def test_monthly_interest_calculation(self):
        """Test monthly interest calculation."""
        debt = Debt("Test Card", 1000.0, 25.0, 12.0, 15)  # 12% annual = 1% monthly
        # This test will be implemented once the method is created
        pass


class TestIncome:
    def test_income_creation(self):
        """Test that Income objects are created correctly."""
        income = Income("Salary", 5000.0, "monthly", date(2024, 1, 1))
        assert income.source == "Salary"
        assert income.amount == 5000.0
        assert income.frequency == "monthly"
        assert income.start_date == date(2024, 1, 1)

    def test_monthly_income_conversion(self):
        """Test conversion of different income frequencies to monthly amounts."""
        # This test will be implemented once the conversion logic is created
        pass


class TestFinancialCalculations:
    def test_calculate_monthly_payment(self):
        """Test monthly payment calculation for different scenarios."""
        # This test will be implemented once the function is created
        pass