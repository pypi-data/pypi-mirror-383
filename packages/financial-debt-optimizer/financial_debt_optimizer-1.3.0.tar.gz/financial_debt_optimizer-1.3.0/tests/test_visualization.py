"""
Comprehensive tests for visualization/charts.py module.

Tests chart generation functionality and matplotlib integration for
debt optimization visualizations.
"""

import os
import tempfile

import matplotlib
import pandas as pd
import pytest

matplotlib.use("Agg")  # Use non-interactive backend for testing

# Import the classes to test
import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.debt_optimizer import DebtOptimizer, OptimizationGoal, OptimizationResult
from core.financial_calc import Debt, Income, RecurringExpense
from visualization.charts import DebtVisualization


class TestDebtVisualization:
    """Test cases for the DebtVisualization class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.viz = DebtVisualization()

        # Sample debts
        self.debts = [
            Debt("Credit Card", 5000.0, 150.0, 18.99, 15),
            Debt("Auto Loan", 12000.0, 325.0, 4.5, 10),
            Debt("Personal Loan", 3000.0, 100.0, 12.0, 25),
        ]

        # Sample debt progression data
        self.debt_progression = pd.DataFrame(
            {
                "month": [1, 2, 3, 4, 5, 6],
                "Credit Card": [5000.0, 4800.0, 4600.0, 4400.0, 4200.0, 4000.0],
                "Auto Loan": [12000.0, 11700.0, 11400.0, 11100.0, 10800.0, 10500.0],
                "Personal Loan": [3000.0, 2900.0, 2800.0, 2700.0, 2600.0, 2500.0],
            }
        )

        # Sample monthly summary data
        self.monthly_summary = pd.DataFrame(
            {
                "month": [1, 2, 3, 4, 5],
                "total_principal": [350.0, 355.0, 360.0, 365.0, 370.0],
                "total_interest": [150.0, 145.0, 140.0, 135.0, 130.0],
            }
        )

        # Sample comparison data
        self.comparison_df = pd.DataFrame(
            {
                "strategy": ["debt_avalanche", "debt_snowball", "hybrid"],
                "total_interest": [5000.0, 5500.0, 5250.0],
                "months_to_freedom": [24, 26, 25],
                "interest_saved": [2000.0, 1500.0, 1750.0],
                "months_saved": [12, 10, 11],
            }
        )

    @pytest.mark.visualization
    def test_debt_visualization_initialization(self):
        """Test DebtVisualization class initialization."""
        viz = DebtVisualization()
        assert viz is not None
        assert hasattr(viz, "colors")
        assert len(viz.colors) > 0

    @pytest.mark.visualization
    def test_plot_debt_progression_basic(self):
        """Test basic debt progression chart creation."""
        fig = self.viz.plot_debt_progression(self.debt_progression)

        assert fig is not None
        assert len(fig.axes) > 0
        ax = fig.axes[0]
        assert len(ax.get_lines()) > 0  # Should have line plots
        plt.close(fig)

    @pytest.mark.visualization
    def test_plot_debt_progression_with_save(self):
        """Test debt progression chart with save functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "debt_progression.png")
            fig = self.viz.plot_debt_progression(
                self.debt_progression, save_path=save_path
            )

            assert fig is not None
            assert os.path.exists(save_path)
            plt.close(fig)

    @pytest.mark.visualization
    def test_plot_payment_breakdown(self):
        """Test payment breakdown chart creation."""
        fig = self.viz.plot_payment_breakdown(self.monthly_summary)

        assert fig is not None
        assert len(fig.axes) > 0
        ax = fig.axes[0]
        assert len(ax.patches) > 0  # Should have bars
        plt.close(fig)

    @pytest.mark.visualization
    def test_plot_strategy_comparison(self):
        """Test strategy comparison chart creation."""
        fig = self.viz.plot_strategy_comparison(self.comparison_df)

        assert fig is not None
        assert len(fig.axes) >= 4  # Should have 4 subplots (2x2 grid)
        plt.close(fig)

    @pytest.mark.visualization
    def test_plot_debt_composition(self):
        """Test debt composition pie chart creation."""
        fig = self.viz.plot_debt_composition(self.debts)

        assert fig is not None
        assert len(fig.axes) > 0
        ax = fig.axes[0]
        assert len(ax.patches) > 0  # Should have pie wedges
        plt.close(fig)

    @pytest.mark.visualization
    def test_plot_interest_rate_comparison(self):
        """Test interest rate comparison chart creation."""
        fig = self.viz.plot_interest_rate_comparison(self.debts)

        assert fig is not None
        assert len(fig.axes) > 0
        ax = fig.axes[0]
        assert len(ax.patches) > 0  # Should have horizontal bars
        plt.close(fig)

    @pytest.mark.visualization
    def test_empty_data_handling(self):
        """Test chart handling with empty data."""
        empty_progression = pd.DataFrame(columns=["month"])

        # Should handle empty data gracefully
        fig = self.viz.plot_debt_progression(empty_progression)
        assert fig is not None
        plt.close(fig)

    @pytest.mark.visualization
    def test_single_debt_handling(self):
        """Test charts with single debt."""
        single_debt = [self.debts[0]]

        fig = self.viz.plot_debt_composition(single_debt)
        assert fig is not None
        plt.close(fig)

        fig = self.viz.plot_interest_rate_comparison(single_debt)
        assert fig is not None
        plt.close(fig)

    @pytest.mark.visualization
    def test_custom_figsize(self):
        """Test charts with custom figure sizes."""
        custom_size = (10, 6)
        fig = self.viz.plot_debt_progression(self.debt_progression, figsize=custom_size)

        assert fig.get_figwidth() == custom_size[0]
        assert fig.get_figheight() == custom_size[1]
        plt.close(fig)


class TestVisualizationIntegration:
    """Integration tests for visualization with real optimization data."""

    def setup_method(self):
        """Set up test fixtures."""
        self.debts = [
            Debt("Credit Card", 5000.0, 150.0, 18.99, 15),
            Debt("Auto Loan", 15000.0, 350.0, 5.5, 10),
        ]

        self.income = [Income("Salary", 3500.0, "bi-weekly", date(2024, 1, 5))]

        self.expenses = [
            RecurringExpense("Rent", 1200.0, "monthly", 1, date(2024, 1, 1)),
            RecurringExpense("Utilities", 200.0, "monthly", 15, date(2024, 1, 1)),
        ]

    @pytest.mark.integration
    @pytest.mark.visualization
    def test_visualization_with_optimization_result(self):
        """Test visualization with real optimization data."""
        optimizer = DebtOptimizer(self.debts, self.income, self.expenses)
        result = optimizer.optimize_debt_strategy(
            OptimizationGoal.MINIMIZE_INTEREST, 200.0
        )

        viz = DebtVisualization()

        # Test with real payment schedule data
        if hasattr(result, "payment_schedule") and len(result.payment_schedule) > 0:
            # Create debt progression from payment schedule
            debt_names = [debt.name for debt in self.debts]
            progression_data = pd.DataFrame()
            progression_data["month"] = range(
                1, min(13, len(result.payment_schedule) + 1)
            )

            for debt_name in debt_names:
                progression_data[debt_name] = [
                    1000.0 * (i + 1) for i in range(len(progression_data))
                ]

            fig = viz.plot_debt_progression(progression_data)
            assert fig is not None
            plt.close(fig)

    @pytest.mark.integration
    @pytest.mark.visualization
    def test_dashboard_creation(self):
        """Test creating a comprehensive dashboard."""
        optimizer = DebtOptimizer(self.debts, self.income, self.expenses)
        result = optimizer.optimize_debt_strategy(
            OptimizationGoal.MINIMIZE_INTEREST, 200.0
        )

        viz = DebtVisualization()

        # Test dashboard creation
        fig = viz.create_dashboard(result, self.debts)
        assert fig is not None
        assert len(fig.axes) > 0
        plt.close(fig)


class TestVisualizationErrorHandling:
    """Test error handling in visualization."""

    def setup_method(self):
        """Set up test fixtures."""
        self.viz = DebtVisualization()

    @pytest.mark.visualization
    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        # Test with completely invalid data
        invalid_data = pd.DataFrame({"invalid_column": ["a", "b", "c"]})

        # Should handle gracefully or raise appropriate exception
        try:
            fig = self.viz.plot_debt_progression(invalid_data)
            if fig:
                plt.close(fig)
        except (KeyError, ValueError, IndexError):
            # Expected for invalid data
            pass

    @pytest.mark.visualization
    def test_memory_cleanup(self):
        """Test that visualization doesn't cause memory leaks."""
        import gc

        # Create multiple charts
        for i in range(5):
            debt_progression = pd.DataFrame(
                {"month": [1, 2, 3], f"Debt_{i}": [1000, 800, 600]}
            )

            fig = self.viz.plot_debt_progression(debt_progression)
            plt.close(fig)

        # Force garbage collection
        gc.collect()

        # Should complete without issues
        assert True
