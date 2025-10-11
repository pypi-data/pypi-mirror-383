import typer
from rich.console import Console
from rich.table import Table
from InquirerPy import inquirer
import os
import pandas as pd
import re
from scrubpy.core import (
    load_dataset, get_dataset_summary, drop_missing_values, fill_missing_values,
    remove_duplicates, standardize_text, fix_column_names, convert_column_types,
    remove_outliers, save_dataset
)
from scrubpy.preview import preview_changes
from scrubpy.profiling import DataProfiler
from scrubpy.export_profiling_report import export_profiling_report
from scrubpy.smart_eda import generate_smart_eda_pdf
from scrubpy.column_insights import get_column_insights, suggest_transformations
from scrubpy.llm_utils import LLMAssistant
from scrubpy.utils import clean_text_for_pdf
app = typer.Typer()
console = Console()

previous_states = []  # Process Stores previous versions for undo feature


# 🎨 Banner
def show_banner():
    console.print("\n[bold cyan]🔥 ScrubPy - The Smartest Data Cleaner 🔥[/bold cyan]")
    console.print("[italic dim]Make your data shine in seconds![/italic dim]\n")


# File Choose Dataset
def choose_dataset():
    files = [f for f in os.listdir() if f.endswith(".csv")]  # fixed stray '5'
    if not files:
        console.print("[bold red]Error No CSV files found in the current directory![/bold red]")
        raise typer.Exit()

    dataset = inquirer.select(
        message="File Choose a dataset to clean:",
        choices=files,
        default=files[0]
    ).execute()

    return dataset


# Process Store Previous State (for Undo)
def save_previous_state(df):
    """Save a copy of the current state before making changes."""
    previous_states.append(df.copy())


# AI Display Column Insights
def display_column_insights(df):
    """Display the inferred roles of columns in a rich table"""
    console.print("\n[bold cyan]AI Analyzing Column Roles...[/bold cyan]")
    
    # Get column insights
    insights = get_column_insights(df)
    
    # Create a table to display results
    table = Table(title="Column Role Insights")
    table.add_column("Column", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Confidence", style="magenta")
    table.add_column("Key Insights", style="blue")
    
    # Add rows for each column
    for col, data in insights.items():
        # Format the key insights
        insight_details = []
        if "insights" in data:
            for k, v in data["insights"].items():
                if isinstance(v, bool) and v:
                    insight_details.append(k.replace("_", " "))
                elif k == "null_percent" and v > 0:
                    insight_details.append(f"{v}% null")
                elif k == "cardinality" and v is not None:
                    insight_details.append(f"cardinality: {v}")
        
        insights_text = ", ".join(insight_details[:3])  # Limit to top 3 insights
        
        # Add a row with colorized confidence value
        confidence_str = f"{data['confidence'] * 100:.0f}%"
        confidence_color = "[red]" if data['confidence'] < 0.5 else "[yellow]" if data['confidence'] < 0.8 else "[green]"
        formatted_confidence = f"{confidence_color}{confidence_str}[/]"
        
        table.add_row(
            col,
            data["role"].capitalize(),
            data["type"],
            formatted_confidence,
            insights_text
        )
    
    console.print(table)
    
    # Get and display transformation suggestions
    suggestions = suggest_transformations(insights)
    if suggestions:
        console.print("\n[bold cyan]Analysis Suggested Transformations:[/bold cyan]")
        for col, suggestion_list in suggestions.items():
            if suggestion_list:
                console.print(f"[bold]{col}[/bold]:")
                for suggestion in suggestion_list:
                    console.print(f"  - {suggestion}")
    
    # Ask if user wants to include in EDA
    include_in_eda = inquirer.confirm(
        "Data Include these column insights in Smart EDA report?",
        default=True
    ).execute()
    
    return insights, include_in_eda


# 🤖 Talk to Dataset with LLM
def talk_to_dataset_with_llm(df, column_insights_data):
    console.print("\n[bold cyan]🤖 Talking to your dataset with Mistral LLM...[/bold cyan]")

    # Use LLMAssistant for a consistent interface
    assistant = LLMAssistant(df=df, column_insights_data=column_insights_data, model="mistral", use_ollama=True)
    response = assistant.ask(
        "Provide the top 5 most impactful cleaning steps for this dataset.",
        task="cleaning_plan",
    )

    console.print("\n[bold green]AI LLM Suggestions:[/bold green]")
    console.print(response)


# 🧹 Cleaning Menu
def clean_data(df, dataset):
    column_insights_data = None  # Store insights for later use in EDA
    
    while True:
        action = inquirer.select(
            message="Tools Choose a cleaning operation:",
            choices=[
                "Data View Data Summary",
                "Profile Profile My Dataset",
                "AI Detect Column Roles",  # Success NEW
                "AI Generate Smart EDA Report",
                "💬 Ask the AI Assistant (LLM)",
                "📈 Smart Data Quality Analysis",
                "💬 Chat with Dataset",
                "🚮 Handle Missing Values",
                "Remove Remove Duplicates",
                "🔡 Standardize Text",
                "🔠 Fix Column Names",
                "🔢 Convert Column Types",
                "📉 Remove Outliers",
                "Undo Undo Last Change",
                "💾 Save & Exit"
            ],
        ).execute()

        if action == "Data View Data Summary":
            console.clear()
            console.print(get_dataset_summary(df))

        elif action == "Profile Profile My Dataset":
            profiler = DataProfiler(df)
            profiler.display_rich_summary()
            recommend = inquirer.confirm("Would you like ScrubPy to suggest cleaning actions?").execute()
            if recommend:
                issues = profiler.suggest_cleaning_actions()
                console.print("\n[bold cyan]🔎 Cleaning Recommendations:[/bold cyan]")
                for issue in issues:
                    console.print(f"- {issue}")

            export = inquirer.confirm("📝 Export this profiling report to .txt?").execute()
            if export:
                export_profiling_report(df, dataset_name=dataset)
                console.print("[bold green]Success Profiling report exported successfully![/bold green]")
        
        elif action == "AI Detect Column Roles":
            # Call the new function to display column insights
            column_insights_data, include_in_eda = display_column_insights(df)
            console.print("[bold green]Success Column roles detected successfully![/bold green]")

        elif action == "AI Generate Smart EDA Report":
            console.print("\n[bold cyan]Data Generating Smart EDA PDF...[/bold cyan]")
            # Pass column insights if available
            extra_data = {}
            if column_insights_data:
                extra_data["column_insights"] = column_insights_data
            generate_smart_eda_pdf(df, dataset_name=dataset, extra_data=extra_data)
            console.print("[bold green]Success EDA report generated as SmartEDA_Report.pdf![/bold green]")
        
        elif action == "💬 Ask the AI Assistant (LLM)":
            if column_insights_data:
                talk_to_dataset_with_llm(df, column_insights_data)
            else:
                console.print("[bold red]Error Please run 'Detect Column Roles' first![/bold red]")

        elif action == "� Smart Data Quality Analysis":
            console.print("\n[bold cyan]Analysis Running comprehensive data quality analysis...[/bold cyan]")
            from scrubpy.quality_analyzer import analyze_data_quality
            analysis = analyze_data_quality(df)
            
            # Display summary
            summary = analysis['summary']
            console.print(f"\n[bold]Data Data Quality Score: {summary['overall_score']}/100[/bold] ({analysis['quality_grade']})")
            console.print(f"Total Issues Found: {summary['total_issues']}")
            
            # Show top issues
            if analysis['recommendations']:
                console.print("\n[bold cyan]Tools Top Recommendations:[/bold cyan]")
                for i, rec in enumerate(analysis['recommendations'][:5], 1):
                    priority_color = {"critical": "red", "high": "orange1", "medium": "yellow"}.get(rec['priority'], "blue")
                    console.print(f"{i}. [{priority_color}]{rec['priority'].upper()}[/] - {rec['column']}: {rec['issue']}")
                    console.print(f"   Tip {rec['fix']}")
            
            # Ask if user wants detailed report
            save_report = inquirer.confirm("📄 Save detailed quality report?").execute()
            if save_report:
                import json
                report_file = f"quality_report_{dataset}.json"
                with open(report_file, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                console.print(f"[green]Success Quality report saved to {report_file}[/green]")

        elif action == "💬 Chat with Dataset":
            console.print("\n[bold cyan]💬 Starting interactive chat session...[/bold cyan]")
            from scrubpy.chat_assistant import start_dataset_chat
            start_dataset_chat(df, dataset)

        elif action == "🚮 Handle Missing Values":
            missing_percentage = (df.isnull().sum().sum() / df.size) * 100
            console.print(f"Warning [bold yellow]Warning:[/bold yellow] {missing_percentage:.2f}% of data is missing.")

            missing_choice = inquirer.select(
                message="How do you want to handle missing values?",
                choices=[
                    "Error Drop Rows with Missing Values",
                    "📏 Drop Columns with > X% Missing Values",
                    "📝 Fill Missing Values (Recommended)",
                    "Back Cancel"
                ],
            ).execute()

            if missing_choice == "Error Drop Rows with Missing Values":
                preview = preview_changes(df, "drop_missing")
                console.print("[bold cyan]Analysis Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = drop_missing_values(df)
                    console.print("[bold yellow]🧹 Missing values removed![/bold yellow]")

            elif missing_choice == "📏 Drop Columns with > X% Missing Values":
                threshold = float(inquirer.text("Enter threshold percentage (e.g., 50 for 50%)").execute())
                cols_to_drop = df.columns[df.isnull().mean() * 100 > threshold]
                if cols_to_drop.empty:
                    console.print("[bold red]No columns have that much missing data![/bold red]")
                else:
                    preview = df.drop(columns=cols_to_drop)
                    console.print(f"[bold cyan]Analysis Preview: Dropping columns {list(cols_to_drop)}[/bold cyan]")
                    confirm = inquirer.confirm("Do you want to proceed?").execute()
                    if confirm:
                        save_previous_state(df)
                        df = df.drop(columns=cols_to_drop)
                        console.print(f"[bold yellow]📏 Dropped columns {list(cols_to_drop)}![/bold yellow]")

            elif missing_choice == "📝 Fill Missing Values (Recommended)":
                fill_value = inquirer.text(message="Enter a value to fill missing cells:").execute()
                preview = preview_changes(df, "fill_missing", fill_value=fill_value)
                console.print("[bold cyan]Analysis Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = fill_missing_values(df, fill_value)
                    console.print(f"[bold yellow]Pen Filled missing values with '{fill_value}'![/bold yellow]")

        elif action == "Remove Remove Duplicates":
            preview = preview_changes(df, "remove_duplicates")
            console.print("[bold cyan]Analysis Preview:[/bold cyan]")
            console.print(get_dataset_summary(preview))
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = remove_duplicates(df)
                console.print("[bold yellow]Remove Duplicates removed![/bold yellow]")

        elif action == "🔡 Standardize Text":
            col = inquirer.select(message="📌 Choose a column:", choices=list(df.columns)).execute()
            preview = preview_changes(df, "standardize_text", column=col)
            console.print("[bold cyan]Analysis Preview:[/bold cyan]")
            console.print(get_dataset_summary(preview))
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = standardize_text(df, col)
                console.print(f"[bold yellow]🔤 Standardized text in '{col}'![/bold yellow]")

        elif action == "🔠 Fix Column Names":
            preview = preview_changes(df, "fix_column_names")
            console.print("[bold cyan]Analysis Preview new column names:[/bold cyan]")
            for old, new in zip(df.columns, preview.columns):
                console.print(f"{old} → {new}")
            confirm = inquirer.confirm("Do you want to proceed?").execute()
            if confirm:
                save_previous_state(df)
                df = fix_column_names(df)
                console.print("[bold yellow]🔡 Column names standardized![/bold yellow]")

        elif action == "🔢 Convert Column Types":
            col = inquirer.select(message="📌 Choose a column to convert:", choices=list(df.columns)).execute()
            target_type = inquirer.select(
                message="📌 Convert to which type?",
                choices=["string", "integer", "float", "datetime", "category", "boolean"]
            ).execute()
            try:
                preview = preview_changes(df, "convert_column_types", column=col, target_type=target_type)
                console.print("[bold cyan]Analysis Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = convert_column_types(df, col, target_type)
                    console.print(f"[bold yellow]Process Converted '{col}' to {target_type}![/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Error Conversion failed: {str(e)}[/bold red]")

        elif action == "📉 Remove Outliers":
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if not numeric_cols:
                console.print("[bold red]Error No numeric columns found for outlier removal![/bold red]")
                continue
            
            col = inquirer.select(message="📌 Choose a numeric column:", choices=numeric_cols).execute()
            method_label = inquirer.select(
                message="📌 Choose outlier detection method:",
                choices=["IQR (Interquartile Range)", "Z-Score", "Percentile"]
            ).execute()
            method_map = {
                "IQR (Interquartile Range)": "iqr",
                "Z-Score": "zscore",
                "Percentile": "percentile",
            }
            method = method_map.get(method_label, "zscore")
            
            try:
                preview = preview_changes(df, "remove_outliers", column=col, method=method)
                console.print("[bold cyan]Analysis Preview:[/bold cyan]")
                console.print(get_dataset_summary(preview))
                confirm = inquirer.confirm("Do you want to proceed?").execute()
                if confirm:
                    save_previous_state(df)
                    df = remove_outliers(df, col, method)
                    console.print(f"[bold yellow]📉 Removed outliers from '{col}'![/bold yellow]")
            except Exception as e:
                console.print(f"[bold red]Error Outlier removal failed: {str(e)}[/bold red]")

        elif action == "Undo Undo Last Change":
            if previous_states:
                df = previous_states.pop()
                console.print("[bold green]Undo Reverted to the last state![/bold green]")
            else:
                console.print("[bold red]Error No previous state found![/bold red]")

        elif action == "💾 Save & Exit":
            # Pass original dataset; core.save_dataset handles 'cleaned_' and versioning
            save_dataset(df, dataset)
            console.print("[bold green]Success Cleaned data saved![/bold green]")
            break

    return df


# 🚀 Main CLI Commands

@app.command()
def clean(
    file: str = typer.Argument(None, help="CSV file to clean"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode")
):
    """🧹 Clean your dataset with interactive prompts"""
    show_banner()
    
    if file:
        if not os.path.exists(file):
            console.print(f"[bold red]Error: File '{file}' not found![/bold red]")
            raise typer.Exit(1)
        dataset = file
    else:
        dataset = choose_dataset()
    
    df = load_dataset(dataset)
    console.print(get_dataset_summary(df))
    
    if interactive:
        df = clean_data(df, dataset)
    else:
        # Auto-clean mode
        console.print("[bold yellow]Running auto-clean...[/bold yellow]")
        df = auto_clean_dataset(df)
        save_dataset(df, dataset)


@app.command()
def web(
    port: int = typer.Option(8501, "--port", "-p", help="Port to run web interface"),
    host: str = typer.Option("localhost", "--host", help="Host to bind to")
):
    """🌐 Launch the web interface"""
    console.print("[bold cyan]🚀 Starting ScrubPy Web Interface...[/bold cyan]")
    
    try:
        import subprocess
        import sys
        
        # Launch Streamlit app
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            os.path.join(os.path.dirname(__file__), "web", "modern_app.py"),
            "--server.port", str(port),
            "--server.address", host,
            "--browser.gatherUsageStats", "false"
        ]
        
        console.print(f"[dim]Access at: http://{host}:{port}[/dim]")
        subprocess.run(cmd)
        
    except ImportError:
        console.print("[bold red]Streamlit not installed! Install with: pip install streamlit[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Failed to start web interface: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def analyze(
    file: str = typer.Argument(..., help="CSV file to analyze"),
    output: str = typer.Option(None, "--output", "-o", help="Output directory for reports"),
    include_eda: bool = typer.Option(True, "--eda/--no-eda", help="Generate EDA report")
):
    """📊 Analyze dataset and generate comprehensive reports"""
    console.print(f"[bold cyan]📊 Analyzing {file}...[/bold cyan]")
    
    if not os.path.exists(file):
        console.print(f"[bold red]Error: File '{file}' not found![/bold red]")
        raise typer.Exit(1)
    
    try:
        df = load_dataset(file)
        
        # Data Quality Analysis
        console.print("\n[bold yellow]Running data quality analysis...[/bold yellow]")
        from scrubpy.quality_analyzer import DataQualityAnalyzer
        analyzer = DataQualityAnalyzer()
        quality_report = analyzer.analyze(df)
        
        console.print(f"✅ Overall Quality Score: {quality_report.get('overall_score', 'N/A')}/100")
        
        # Column Insights
        console.print("\n[bold yellow]Analyzing column insights...[/bold yellow]")
        insights = get_column_insights(df)
        
        for col, insight in insights.items():
            console.print(f"• {col}: {insight.get('role', 'Unknown')} - {insight.get('quality', 'N/A')}% quality")
        
        # Generate EDA if requested
        if include_eda:
            console.print("\n[bold yellow]Generating Smart EDA report...[/bold yellow]")
            output_dir = output or f"eda_outputs/{os.path.splitext(os.path.basename(file))[0]}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            generate_smart_eda_pdf(df, insights, output_dir)
            console.print(f"✅ EDA report saved to: {output_dir}")
            
    except Exception as e:
        console.print(f"[bold red]Analysis failed: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def chat(
    file: str = typer.Argument(None, help="CSV file to chat about"),
    model: str = typer.Option("mistral", "--model", "-m", help="LLM model to use")
):
    """💬 Start an AI chat session about your data"""
    console.print("[bold cyan]💬 Starting AI Chat Session...[/bold cyan]")
    
    df = None
    insights = None
    
    if file:
        if not os.path.exists(file):
            console.print(f"[bold red]Error: File '{file}' not found![/bold red]")
            raise typer.Exit(1)
        
        console.print(f"[dim]Loading {file}...[/dim]")
        df = load_dataset(file)
        insights = get_column_insights(df)
        console.print(f"✅ Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    
    try:
        assistant = LLMAssistant(df=df, column_insights_data=insights, model=model, use_ollama=True)
        
        console.print("\n[bold green]AI Assistant ready! Type 'quit' to exit.[/bold green]")
        
        while True:
            question = typer.prompt("\n🤔 Your question")
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            console.print("\n[bold yellow]🤖 AI thinking...[/bold yellow]")
            response = assistant.ask(question)
            console.print(f"\n[bold green]🤖 AI Response:[/bold green]\n{response}")
            
    except Exception as e:
        console.print(f"[bold red]Chat session failed: {e}[/bold red]")
        console.print("[dim]Tip: Make sure Ollama is installed and Mistral model is downloaded[/dim]")
        raise typer.Exit(1)


@app.command()
def profile(
    file: str = typer.Argument(..., help="CSV file to profile"),
    output: str = typer.Option(None, "--output", "-o", help="Output file for HTML report"),
    minimal: bool = typer.Option(False, "--minimal", help="Generate minimal report")
):
    """📈 Generate detailed data profiling report"""
    console.print(f"[bold cyan]📈 Profiling {file}...[/bold cyan]")
    
    if not os.path.exists(file):
        console.print(f"[bold red]Error: File '{file}' not found![/bold red]")
        raise typer.Exit(1)
    
    try:
        df = load_dataset(file)
        
        profiler = DataProfiler()
        
        with console.status("[bold yellow]Generating profile report...", spinner="dots"):
            if output:
                output_file = output
            else:
                base_name = os.path.splitext(os.path.basename(file))[0]
                output_file = f"{base_name}_profile_report.html"
            
            export_profiling_report(df, output_file, minimal=minimal)
        
        console.print(f"✅ Profile report saved to: {output_file}")
        
        # Open in browser if possible
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
        except:
            pass
            
    except Exception as e:
        console.print(f"[bold red]Profiling failed: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def setup(
    ai: bool = typer.Option(False, "--ai", help="Setup AI features only"),
    reset: bool = typer.Option(False, "--reset", help="Reset configuration")
):
    """⚙️  Run first-time setup wizard"""
    console.print("[bold cyan]⚙️ ScrubPy Setup Wizard[/bold cyan]")
    
    if reset:
        import json
        from pathlib import Path
        config_file = Path.home() / '.scrubpy' / 'config.json'
        if config_file.exists():
            config_file.unlink()
            console.print("✅ Configuration reset!")
        else:
            console.print("No configuration found to reset.")
        return
    
    try:
        from scrubpy.setup_wizard import ScrubPySetupWizard
        wizard = ScrubPySetupWizard()
        
        if ai:
            # AI-only setup
            system_info = wizard.check_system()
            wizard.setup_ai_features(system_info)
            wizard.save_config()
        else:
            # Full setup
            wizard.run()
            
    except ImportError as e:
        console.print(f"[bold red]Setup wizard not available: {e}[/bold red]")
        console.print("Install extra dependencies with: pip install scrubpy[ai]")
        raise typer.Exit(1)


@app.command()
def version():
    """📋 Show version information"""
    from scrubpy import __version__
    
    version_info = f"""
[bold cyan]ScrubPy v{__version__}[/bold cyan]
The Smartest Data Cleaner

Features:
• Interactive data cleaning
• AI-powered analysis
• Smart EDA reports  
• Web interface
• Quality scoring
• Column insights
    """
    
    console.print(version_info.strip())


def auto_clean_dataset(df):
    """Automatically clean dataset with sensible defaults"""
    console.print("[bold yellow]🤖 Auto-cleaning dataset...[/bold yellow]")
    
    # Remove duplicates
    initial_rows = len(df)
    df = remove_duplicates(df)
    removed_dupes = initial_rows - len(df)
    if removed_dupes > 0:
        console.print(f"✅ Removed {removed_dupes} duplicate rows")
    
    # Handle missing values (fill numeric with median, categorical with mode)
    missing_cols = df.columns[df.isnull().any()].tolist()
    if missing_cols:
        for col in missing_cols:
            if df[col].dtype in ['int64', 'float64']:
                df = fill_missing_values(df, col, 'median')
            else:
                df = fill_missing_values(df, col, 'mode')
        console.print(f"✅ Handled missing values in {len(missing_cols)} columns")
    
    # Standardize text columns
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    for col in text_cols:
        df = standardize_text(df, col)
    if text_cols:
        console.print(f"✅ Standardized {len(text_cols)} text columns")
    
    # Fix column names
    original_cols = df.columns.tolist()
    df = fix_column_names(df)
    if list(df.columns) != original_cols:
        console.print("✅ Fixed column names")
    
    console.print("[bold green]🎉 Auto-cleaning complete![/bold green]")
    return df


if __name__ == "__main__":
    app()