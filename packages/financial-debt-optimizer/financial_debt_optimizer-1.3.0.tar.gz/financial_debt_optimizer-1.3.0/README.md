# Financial Debt Optimizer 1.1.1

[![PyPI Version](https://img.shields.io/pypi/v/financial-debt-optimizer.svg)](https://pypi.org/project/financial-debt-optimizer/)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/financial-debt-optimizer/badge/?version=latest)](https://financial-debt-optimizer.readthedocs.io/en/latest/?badge=latest)

A comprehensive Python tool for analyzing and optimizing debt repayment strategies to help you become debt-free faster while minimizing interest costs.

## Features

### Core Optimization Strategies
- **Debt Avalanche**: Minimize total interest paid by targeting highest interest rates first
- **Debt Snowball**: Build momentum by paying off smallest balances first
- **Hybrid Strategy**: Balance psychological wins with mathematical optimization
- **Custom Strategy**: Define your own debt prioritization order

### Advanced Financial Modeling
- **Future Income Integration**: Account for raises, bonuses, and additional income sources
- **Recurring Expense Management**: Track monthly, bi-weekly, quarterly, and annual expenses
- **Extra Payment Allocation**: Optimize how extra funds are distributed across debts
- **Cash Flow Analysis**: Monitor monthly financial health and surplus calculations

### Comprehensive Reporting
- **Excel Integration**: Generate detailed spreadsheet reports with multiple worksheets
- **Visual Charts**: 6+ interactive charts showing debt progression, payment breakdowns, and cash flow
- **Monthly Summaries**: Track income, expenses, payments, and extra funds by month
- **Decision Logging**: Audit trail of optimization decisions and rationale
- **Strategy Comparisons**: Side-by-side analysis of different repayment approaches

### Professional Excel Output
- **Payment Schedule**: Detailed chronological payment plan
- **Monthly Summary**: Income, expenses, and payment tracking
- **Debt Progression**: Individual debt balance evolution
- **Strategy Comparison**: Performance metrics across different approaches
- **Charts & Visualizations**: Professional charts and graphs
- **Decision Log**: Detailed rationale for optimization choices

## Installation

### PyPI Installation (Recommended)
```bash
pip install financial-debt-optimizer
```

### Requirements
- Python 3.8 or higher
- Dependencies are automatically installed with the package

### Install from Source
```bash
git clone https://github.com/bryankemp/financial-debt-optimizer.git
cd financial-debt-optimizer
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/bryankemp/financial-debt-optimizer.git
cd financial-debt-optimizer
pip install -e .[dev]
```

## Quick Start

### 1. Generate an Excel Template
```bash
debt-optimizer generate-template my-debt-data.xlsx
```

### 2. Fill in Your Data
Open `my-debt-data.xlsx` and fill in:
- **Debts**: Name, balance, minimum payment, interest rate, due date
- **Income**: Sources, amounts, frequency (bi-weekly, monthly, etc.)
- **Recurring Expenses**: Monthly bills, subscriptions, etc.
- **Future Income**: Bonuses, raises, additional income streams
- **Settings**: Bank balance, optimization preferences

### 3. Run Analysis
```bash
debt-optimizer analyze --input my-debt-data.xlsx --output debt-analysis.xlsx
```

### 4. Review Results
Open `debt-analysis.xlsx` to see:
- Optimized payment strategy
- Month-by-month payment schedule
- Visual charts and progress tracking
- Interest savings and time to debt freedom

## Usage Examples

### Basic Analysis
```bash
# Analyze debts with default settings (minimize interest)
debt-optimizer analyze -i my-debts.xlsx -o results.xlsx
```

### Advanced Options
```bash
# Compare all strategies with extra monthly payment
debt-optimizer analyze \
    --input my-debts.xlsx \
    --output comprehensive-analysis.xlsx \
    --goal minimize_interest \
    --extra-payment 500 \
    --compare-strategies
```

### Available Goals
- `minimize_interest`: Pay least total interest (default)
- `minimize_time`: Become debt-free fastest
- `maximize_cashflow`: Optimize monthly cash flow

## Excel Template Structure

### Debts Sheet
| Name | Balance | Min Payment | Interest Rate | Due Date |
|------|---------|-------------|---------------|----------|
| Credit Card 1 | 5000.00 | 150.00 | 18.99 | 15 |
| Student Loan | 25000.00 | 300.00 | 5.50 | 1 |

### Income Sheet
| Source | Amount | Frequency | Start Date |
|--------|--------|-----------|------------|
| Salary | 2500.00 | bi-weekly | 2024-01-01 |

### Recurring Expenses Sheet
| Description | Amount | Frequency | Due Date | Start Date |
|-------------|--------|-----------|----------|------------|
| Rent | 1200.00 | monthly | 1 | 2024-01-01 |

### Future Income Sheet
| Description | Amount | Start Date | Frequency | End Date |
|-------------|--------|------------|-----------|----------|
| Bonus | 5000.00 | 2024-12-15 | once | |
| Raise | 200.00 | 2024-07-01 | bi-weekly | |

## Output Analysis

### Key Metrics
- **Total Interest Saved**: Compared to minimum payments only
- **Time to Debt Freedom**: Months until all debts are paid
- **Monthly Cash Flow**: Available funds after payments and expenses
- **Strategy Efficiency**: Comparison across different approaches

### Charts Included
1. **Individual Debt Progression**: Track each debt balance over time
2. **Payment Breakdown**: Principal vs interest by month
3. **Total Debt Reduction**: Overall debt elimination progress
4. **Cash Flow Analysis**: Income vs expenses vs payments
5. **Debt Payoff Timeline**: Order and timing of debt elimination
6. **Extra Funds Utilization**: Efficiency of extra payment allocation

## API Usage

```python
from src.excel_io.excel_reader import ExcelReader
from src.core.debt_optimizer import DebtOptimizer, OptimizationGoal
from src.excel_io.excel_writer import ExcelReportWriter

# Load data
reader = ExcelReader("my-debts.xlsx")
debts, income, expenses, future_income, future_expenses, settings = reader.read_all_data()

# Initialize optimizer
optimizer = DebtOptimizer(debts, income, expenses, future_income, future_expenses, settings)

# Run optimization
result = optimizer.optimize_debt_strategy(
    goal=OptimizationGoal.MINIMIZE_INTEREST,
    extra_payment=500.0
)

# Generate report
writer = ExcelReportWriter("analysis.xlsx")
debt_summary = optimizer.generate_debt_summary()
writer.create_comprehensive_report(result, debt_summary)
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/bryankemp/financial-debt-optimizer.git
cd financial-debt-optimizer
pip install -e .[dev]
```

### Running Tests
```bash
pip install -e .[test]
pytest
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

## Documentation

📖 **[Complete Documentation](https://financial-debt-optimizer.readthedocs.io/)**

- **[Installation Guide](https://financial-debt-optimizer.readthedocs.io/en/latest/installation.html)** - Detailed installation instructions
- **[Quick Start](https://financial-debt-optimizer.readthedocs.io/en/latest/quickstart.html)** - Get started in minutes
- **[User Guide](https://financial-debt-optimizer.readthedocs.io/en/latest/user_guide.html)** - Comprehensive usage documentation
- **[Examples](https://financial-debt-optimizer.readthedocs.io/en/latest/examples.html)** - Real-world use cases and scenarios
- **[API Reference](https://financial-debt-optimizer.readthedocs.io/en/latest/modules.html)** - Complete API documentation
- **[FAQ](https://financial-debt-optimizer.readthedocs.io/en/latest/faq.html)** - Frequently asked questions

## Support

- **📖 Documentation**: [https://financial-debt-optimizer.readthedocs.io/](https://financial-debt-optimizer.readthedocs.io/)
- **🐛 Issues**: [GitHub Issues](https://github.com/bryankemp/financial-debt-optimizer/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/bryankemp/financial-debt-optimizer/discussions)
- **📧 Email**: bryan@kempville.com

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always consult with qualified financial professionals for personalized guidance on debt management and financial planning.

---

**Author**: Bryan Kemp (bryan@kempville.com)  
**Version**: 1.0.0  
**License**: BSD 3-Clause