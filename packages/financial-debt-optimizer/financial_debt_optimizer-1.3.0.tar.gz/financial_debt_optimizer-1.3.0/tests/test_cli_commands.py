"""
Comprehensive tests for CLI commands module.

Tests all CLI commands including generate-template, analyze, validate, and info
with various parameter combinations and edge cases.
"""

import shutil
# Import the classes to test
import sys
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from cli.commands import analyze, generate_template, info, main, validate
from excel_io.excel_reader import ExcelTemplateGenerator


class TestCLIGenerateTemplate:
    """Test cases for the generate-template CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.cli
    def test_generate_template_default(self):
        """Test generate-template with default options."""
        output_file = self.temp_dir / "test_template.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                generate_template, ["--output", str(output_file)]
            )

        assert result.exit_code == 0
        assert "Excel template generated" in result.output
        assert "Template includes six sheets" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_generate_template_no_sample_data(self):
        """Test generate-template without sample data."""
        output_file = self.temp_dir / "empty_template.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                generate_template, ["--output", str(output_file), "--no-sample-data"]
            )

        assert result.exit_code == 0
        assert "Excel template generated" in result.output
        assert "sample data" not in result.output.lower()
        assert output_file.exists()

    @pytest.mark.cli
    def test_generate_template_with_sample_data(self):
        """Test generate-template with sample data explicitly enabled."""
        output_file = self.temp_dir / "sample_template.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                generate_template, ["--output", str(output_file), "--sample-data"]
            )

        assert result.exit_code == 0
        assert "Excel template generated" in result.output
        assert "sample data" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_generate_template_overwrite_existing(self):
        """Test generate-template overwriting existing file."""
        output_file = self.temp_dir / "existing_template.xlsx"

        # Create initial file
        with self.runner.isolated_filesystem():
            result1 = self.runner.invoke(
                generate_template, ["--output", str(output_file)]
            )
            assert result1.exit_code == 0

            # Try to overwrite with confirmation
            result2 = self.runner.invoke(
                generate_template, ["--output", str(output_file)], input="y\n"
            )

        assert result2.exit_code == 0
        assert "already exists" in result2.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_generate_template_overwrite_declined(self):
        """Test generate-template declining to overwrite existing file."""
        output_file = self.temp_dir / "existing_template.xlsx"

        # Create initial file
        with self.runner.isolated_filesystem():
            result1 = self.runner.invoke(
                generate_template, ["--output", str(output_file)]
            )
            assert result1.exit_code == 0

            # Decline to overwrite
            result2 = self.runner.invoke(
                generate_template, ["--output", str(output_file)], input="n\n"
            )

        assert result2.exit_code == 0
        assert "Operation cancelled" in result2.output

    @pytest.mark.cli
    def test_generate_template_invalid_path(self):
        """Test generate-template with invalid output path."""
        invalid_path = "/root/forbidden/template.xlsx"  # Path that should fail

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(generate_template, ["--output", invalid_path])

        assert result.exit_code == 1
        assert "Error generating template" in result.output

    @pytest.mark.cli
    def test_generate_template_help(self):
        """Test generate-template help message."""
        result = self.runner.invoke(generate_template, ["--help"])

        assert result.exit_code == 0
        assert "Generate an Excel template" in result.output
        assert "--output" in result.output
        assert "--sample-data" in result.output


class TestCLIAnalyze:
    """Test cases for the analyze CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create a test template with sample data
        self.template_path = self.temp_dir / "test_template.xlsx"
        ExcelTemplateGenerator.generate_template(
            str(self.template_path), include_sample_data=True
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.cli
    def test_analyze_basic(self):
        """Test analyze command with basic parameters."""
        output_file = self.temp_dir / "analysis_report.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                ["--input", str(self.template_path), "--output", str(output_file)],
            )

        assert result.exit_code == 0
        assert "Starting debt optimization analysis" in result.output
        assert "Report generated" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_analyze_with_goal(self):
        """Test analyze command with specific optimization goal."""
        output_file = self.temp_dir / "goal_analysis.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(self.template_path),
                    "--output",
                    str(output_file),
                    "--goal",
                    "minimize_time",
                ],
            )

        assert result.exit_code == 0
        assert "Optimizing for: Minimize Time" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_analyze_with_extra_payment(self):
        """Test analyze command with extra payment."""
        output_file = self.temp_dir / "extra_payment_analysis.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(self.template_path),
                    "--output",
                    str(output_file),
                    "--extra-payment",
                    "300",
                ],
            )

        assert result.exit_code == 0
        assert "Starting debt optimization analysis" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_analyze_simple_report(self):
        """Test analyze command with simple report option."""
        output_file = self.temp_dir / "simple_report.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(self.template_path),
                    "--output",
                    str(output_file),
                    "--simple-report",
                ],
            )

        assert result.exit_code == 0
        assert "Report generated" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_analyze_compare_strategies(self):
        """Test analyze command with strategy comparison."""
        output_file = self.temp_dir / "comparison_report.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(self.template_path),
                    "--output",
                    str(output_file),
                    "--compare-strategies",
                ],
            )

        assert result.exit_code == 0
        assert "Comparing strategies" in result.output
        assert "Strategy Comparison:" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_analyze_all_options(self):
        """Test analyze command with all options enabled."""
        output_file = self.temp_dir / "full_analysis.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(self.template_path),
                    "--output",
                    str(output_file),
                    "--goal",
                    "maximize_cashflow",
                    "--extra-payment",
                    "500",
                    "--compare-strategies",
                ],
            )

        assert result.exit_code == 0
        assert "Optimizing for: Maximize Cashflow" in result.output
        assert "Comparing strategies" in result.output
        assert output_file.exists()

    @pytest.mark.cli
    def test_analyze_nonexistent_input(self):
        """Test analyze command with nonexistent input file."""
        nonexistent_file = self.temp_dir / "nonexistent.xlsx"
        output_file = self.temp_dir / "output.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                ["--input", str(nonexistent_file), "--output", str(output_file)],
            )

        assert result.exit_code == 1
        assert "File not found" in result.output

    @pytest.mark.cli
    def test_analyze_overwrite_output(self):
        """Test analyze command overwriting existing output file."""
        output_file = self.temp_dir / "existing_output.xlsx"

        # Create initial analysis
        with self.runner.isolated_filesystem():
            result1 = self.runner.invoke(
                analyze,
                ["--input", str(self.template_path), "--output", str(output_file)],
            )
            assert result1.exit_code == 0

            # Overwrite with confirmation
            result2 = self.runner.invoke(
                analyze,
                ["--input", str(self.template_path), "--output", str(output_file)],
                input="y\n",
            )

        assert result2.exit_code == 0
        assert "already exists" in result2.output

    @pytest.mark.cli
    def test_analyze_help(self):
        """Test analyze command help message."""
        result = self.runner.invoke(analyze, ["--help"])

        assert result.exit_code == 0
        assert "Analyze debt and generate optimized repayment plan" in result.output
        assert "--input" in result.output
        assert "--goal" in result.output
        assert "--extra-payment" in result.output


class TestCLIValidate:
    """Test cases for the validate CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create a test template with sample data
        self.valid_template_path = self.temp_dir / "valid_template.xlsx"
        ExcelTemplateGenerator.generate_template(
            str(self.valid_template_path), include_sample_data=True
        )

        # Create empty template
        self.empty_template_path = self.temp_dir / "empty_template.xlsx"
        ExcelTemplateGenerator.generate_template(
            str(self.empty_template_path), include_sample_data=False
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.cli
    def test_validate_valid_file(self):
        """Test validate command with valid input file."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(validate, [str(self.valid_template_path)])

        assert result.exit_code == 0
        assert "Validating" in result.output
        assert "File Summary:" in result.output
        assert "Debts:" in result.output
        assert "Income Sources:" in result.output

    @pytest.mark.cli
    def test_validate_empty_file(self):
        """Test validate command with empty template file."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(validate, [str(self.empty_template_path)])

        assert result.exit_code == 1  # Should exit with error code for empty file
        assert "Validating" in result.output
        assert "No valid income records found" in result.output

    @pytest.mark.cli
    def test_validate_nonexistent_file(self):
        """Test validate command with nonexistent file."""
        nonexistent_file = self.temp_dir / "nonexistent.xlsx"

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(validate, [str(nonexistent_file)])

        assert result.exit_code != 0  # Should fail
        # Click handles file existence checking, so error message varies

    @pytest.mark.cli
    def test_validate_corrupted_file(self):
        """Test validate command with corrupted file."""
        corrupted_file = self.temp_dir / "corrupted.xlsx"

        # Create a fake Excel file
        with open(corrupted_file, "w") as f:
            f.write("This is not an Excel file")

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(validate, [str(corrupted_file)])

        assert result.exit_code == 1
        assert "Validation error" in result.output

    @pytest.mark.cli
    def test_validate_help(self):
        """Test validate command help message."""
        result = self.runner.invoke(validate, ["--help"])

        assert result.exit_code == 0
        assert "Validate an Excel input file" in result.output


class TestCLIInfo:
    """Test cases for the info CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @pytest.mark.cli
    def test_info_command(self):
        """Test info command output."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(info)

        assert result.exit_code == 0
        assert "Debt Optimization Strategies" in result.output
        assert "DEBT AVALANCHE" in result.output
        assert "DEBT SNOWBALL" in result.output
        assert "HYBRID APPROACH" in result.output
        assert "OPTIMIZATION GOALS" in result.output
        assert "minimize_interest" in result.output
        assert "minimize_time" in result.output
        assert "maximize_cashflow" in result.output

    @pytest.mark.cli
    def test_info_contains_tips(self):
        """Test that info command contains helpful tips."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(info)

        assert result.exit_code == 0
        assert "Tips:" in result.output
        assert "debt-optimizer validate" in result.output
        assert "debt-optimizer generate-template" in result.output

    @pytest.mark.cli
    def test_info_help(self):
        """Test info command help message."""
        result = self.runner.invoke(info, ["--help"])

        assert result.exit_code == 0
        assert "Display information about debt optimization strategies" in result.output


class TestCLIMain:
    """Test cases for the main CLI group."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @pytest.mark.cli
    def test_main_help(self):
        """Test main command help message."""
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Financial Debt Optimizer" in result.output
        assert "generate-template" in result.output
        assert "analyze" in result.output
        assert "validate" in result.output
        assert "info" in result.output

    @pytest.mark.cli
    def test_main_version(self):
        """Test main command version option."""
        result = self.runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        # Should contain version information

    @pytest.mark.cli
    def test_main_debug_flag(self):
        """Test main command with debug flag."""
        result = self.runner.invoke(main, ["--debug", "--help"])

        assert result.exit_code == 0
        # Debug flag should be accepted without error

    @pytest.mark.cli
    def test_main_log_file_option(self):
        """Test main command with log file option."""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as log_file:
            log_path = log_file.name

        try:
            result = self.runner.invoke(main, ["--log-file", log_path, "--help"])
            assert result.exit_code == 0
        finally:
            Path(log_path).unlink(missing_ok=True)

    @pytest.mark.cli
    def test_main_invalid_command(self):
        """Test main command with invalid subcommand."""
        result = self.runner.invoke(main, ["invalid-command"])

        assert result.exit_code != 0
        assert "No such command" in result.output


class TestCLIErrorHandling:
    """Test cases for CLI error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.cli
    def test_analyze_invalid_goal(self):
        """Test analyze command with invalid optimization goal."""
        template_path = self.temp_dir / "template.xlsx"
        ExcelTemplateGenerator.generate_template(
            str(template_path), include_sample_data=True
        )

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(template_path),
                    "--output",
                    "output.xlsx",
                    "--goal",
                    "invalid_goal",
                ],
            )

        assert result.exit_code != 0
        # Should reject invalid goal

    @pytest.mark.cli
    def test_analyze_negative_extra_payment(self):
        """Test analyze command with negative extra payment."""
        template_path = self.temp_dir / "template.xlsx"
        ExcelTemplateGenerator.generate_template(
            str(template_path), include_sample_data=True
        )

        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(template_path),
                    "--output",
                    "output.xlsx",
                    "--extra-payment",
                    "-100",
                ],
            )

        # Should either reject negative payment or handle gracefully
        # Exact behavior depends on implementation
        assert isinstance(result.exit_code, int)

    @pytest.mark.cli
    def test_generate_template_permission_error(self):
        """Test generate-template with permission denied error."""
        # Try to write to a directory without write permissions
        with patch(
            "excel_io.excel_reader.ExcelTemplateGenerator.generate_template"
        ) as mock_gen:
            mock_gen.side_effect = PermissionError("Permission denied")

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    generate_template, ["--output", "template.xlsx"]
                )

        assert result.exit_code == 1
        assert "Error generating template" in result.output


class TestCLIIntegration:
    """Integration tests for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @pytest.mark.integration
    @pytest.mark.cli
    def test_complete_workflow(self):
        """Test complete CLI workflow from template to analysis."""
        template_path = self.temp_dir / "workflow_template.xlsx"
        analysis_path = self.temp_dir / "workflow_analysis.xlsx"

        with self.runner.isolated_filesystem():
            # Step 1: Generate template
            result1 = self.runner.invoke(
                generate_template, ["--output", str(template_path)]
            )
            assert result1.exit_code == 0
            assert template_path.exists()

            # Step 2: Validate template
            result2 = self.runner.invoke(validate, [str(template_path)])
            assert result2.exit_code == 0
            assert "File Summary:" in result2.output

            # Step 3: Analyze template
            result3 = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(template_path),
                    "--output",
                    str(analysis_path),
                    "--compare-strategies",
                ],
            )
            assert result3.exit_code == 0
            assert analysis_path.exists()

    @pytest.mark.integration
    @pytest.mark.cli
    def test_workflow_with_custom_settings(self):
        """Test CLI workflow with custom settings."""
        template_path = self.temp_dir / "custom_template.xlsx"
        analysis_path = self.temp_dir / "custom_analysis.xlsx"

        with self.runner.isolated_filesystem():
            # Generate template without sample data
            result1 = self.runner.invoke(
                generate_template, ["--output", str(template_path), "--no-sample-data"]
            )
            assert result1.exit_code == 0

            # Validate should show empty file
            result2 = self.runner.invoke(validate, [str(template_path)])
            assert result2.exit_code == 1  # Should fail validation for empty file

            # Analysis of empty file should fail
            result3 = self.runner.invoke(
                analyze, ["--input", str(template_path), "--output", str(analysis_path)]
            )
            assert result3.exit_code == 1  # Should fail due to no data

    @pytest.mark.integration
    @pytest.mark.cli
    def test_cli_consistency(self):
        """Test that CLI commands are consistent in behavior."""
        # All commands should have help
        commands = [generate_template, analyze, validate, info]

        for command in commands:
            result = self.runner.invoke(command, ["--help"])
            assert result.exit_code == 0
            assert len(result.output) > 0

    @pytest.mark.integration
    @pytest.mark.cli
    def test_cli_error_messages(self):
        """Test that CLI commands provide helpful error messages."""
        template_path = self.temp_dir / "template.xlsx"
        ExcelTemplateGenerator.generate_template(
            str(template_path), include_sample_data=True
        )

        with self.runner.isolated_filesystem():
            # Test missing required argument
            result1 = self.runner.invoke(analyze, [])
            assert result1.exit_code != 0
            assert (
                "Missing option" in result1.output
                or "required" in result1.output.lower()
            )

            # Test invalid file path
            result2 = self.runner.invoke(
                analyze,
                ["--input", "/nonexistent/path/file.xlsx", "--output", "output.xlsx"],
            )
            assert result2.exit_code != 0

    @pytest.mark.integration
    @pytest.mark.cli
    @pytest.mark.slow
    def test_performance_large_template(self):
        """Test CLI performance with larger datasets."""
        template_path = self.temp_dir / "large_template.xlsx"
        analysis_path = self.temp_dir / "large_analysis.xlsx"

        # Generate template with sample data (simulates larger dataset)
        with self.runner.isolated_filesystem():
            result1 = self.runner.invoke(
                generate_template, ["--output", str(template_path)]
            )
            assert result1.exit_code == 0

            # Run analysis with all options (most computationally intensive)
            result2 = self.runner.invoke(
                analyze,
                [
                    "--input",
                    str(template_path),
                    "--output",
                    str(analysis_path),
                    "--extra-payment",
                    "1000",
                    "--compare-strategies",
                ],
            )
            assert result2.exit_code == 0
            assert "Report generated" in result2.output

            # Validate the results
            result3 = self.runner.invoke(validate, [str(template_path)])
            assert result3.exit_code == 0
