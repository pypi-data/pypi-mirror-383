import pytest
import numpy as np
from datetime import datetime, date
from core.debt_optimizer import DebtOptimizer
from core.financial_calc import Debt, Income


class TestDebtOptimizer:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.debts = [
            Debt("Credit Card", 5000.0, 150.0, 18.99, 15),
            Debt("Auto Loan", 12000.0, 325.0, 4.5, 10),
        ]
        self.income = [
            Income("Salary", 3500.0, "bi-weekly", date(2024, 1, 5)),
        ]
        self.optimizer = DebtOptimizer(self.debts, self.income)

    def test_initialization(self):
        """Test that DebtOptimizer initializes correctly."""
        assert len(self.optimizer.debts) == 2
        assert len(self.optimizer.income) == 1
        assert self.optimizer.debts[0].name == "Credit Card"

    def test_calculate_monthly_income(self):
        """Test monthly income calculation for different frequencies."""
        # This test will be implemented once the core classes are created
        pass

    def test_debt_avalanche_strategy(self):
        """Test debt avalanche optimization strategy."""
        # This test will be implemented once the optimization logic is created
        pass

    def test_debt_snowball_strategy(self):
        """Test debt snowball optimization strategy."""
        # This test will be implemented once the optimization logic is created
        pass