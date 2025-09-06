#!/usr/bin/env python3
"""
Real Time Governance System (RTGS)
A CLI-first agentic system for data cleaning, transformation, and insight generation
"""

import click
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from data_processor import DataProcessor
from insight_generator import InsightGenerator
from telangana_connector import TelanganaConnector

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Real Time Governance System (RTGS) - Transform public data into actionable insights"""
    pass

@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Input data file')
@click.option('--url', '-u', help='Data URL to fetch from')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-fmt', type=click.Choice(['csv', 'json', 'excel']), default='csv', help='Output format')
def clean(file, url, output, format):
    """Clean and standardize raw data"""
    processor = DataProcessor()
    
    if file:
        click.echo(f"🔄 Processing local file: {file}")
        result = processor.process_file(file, output, format)
    elif url:
        click.echo(f"🔄 Processing data from URL: {url}")
        result = processor.process_url(url, output, format)
    else:
        click.echo("❌ Please provide either --file or --url")
        return
    
    if result:
        click.echo(f"✅ Data cleaned and saved to: {result}")
    else:
        click.echo("❌ Failed to process data")

@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), required=True, help='Input data file')
@click.option('--output', '-o', type=click.Path(), help='Output insights file')
@click.option('--visual', '-v', is_flag=True, help='Generate visual insights')
def analyze(file, output, visual):
    """Generate insights from cleaned data"""
    generator = InsightGenerator()
    
    click.echo(f"🔍 Analyzing data from: {file}")
    insights = generator.generate_insights(file, visual=visual)
    
    if insights:
        if output:
            generator.save_insights(insights, output)
            click.echo(f"✅ Insights saved to: {output}")
        else:
            click.echo("\n📊 Key Insights:")
            for insight in insights:
                click.echo(f"  • {insight}")
    else:
        click.echo("❌ Failed to generate insights")

@cli.command()
@click.option('--dataset', '-d', help='Dataset name/ID from Telangana portal')
@click.option('--category', '-c', default='agriculture', help='Data category (default: agriculture)')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def fetch(dataset, category, output):
    """Fetch data from Telangana Open Data Portal"""
    connector = TelanganaConnector()
    
    if dataset:
        click.echo(f"🌐 Fetching dataset: {dataset}")
        result = connector.fetch_dataset(dataset, output)
    else:
        click.echo(f"🌐 Fetching {category} datasets...")
        result = connector.fetch_category_data(category, output)
    
    if result:
        click.echo(f"✅ Data fetched successfully: {result}")
    else:
        click.echo("❌ Failed to fetch data")

@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Input data file')
@click.option('--url', '-u', help='Data URL to fetch from')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--visual', '-v', is_flag=True, help='Generate visual insights')
def pipeline(file, url, output, visual):
    """Run complete data pipeline: fetch -> clean -> analyze"""
    click.echo("🚀 Starting RTGS Pipeline...")
    
    # Create output directory if specified
    if output:
        Path(output).mkdir(parents=True, exist_ok=True)
        cleaned_file = Path(output) / "cleaned_data.csv"
        insights_file = Path(output) / "insights.txt"
    else:
        cleaned_file = "cleaned_data.csv"
        insights_file = "insights.txt"
    
    # Step 1: Clean data
    processor = DataProcessor()
    if file:
        click.echo(f"📋 Step 1: Cleaning local file: {file}")
        result = processor.process_file(file, str(cleaned_file), 'csv')
    elif url:
        click.echo(f"📋 Step 1: Cleaning data from URL: {url}")
        result = processor.process_url(url, str(cleaned_file), 'csv')
    else:
        click.echo("❌ Please provide either --file or --url")
        return
    
    if not result:
        click.echo("❌ Pipeline failed at cleaning step")
        return
    
    # Step 2: Generate insights
    click.echo("📋 Step 2: Generating insights...")
    generator = InsightGenerator()
    insights = generator.generate_insights(str(cleaned_file), visual=visual)
    
    if insights:
        generator.save_insights(insights, str(insights_file))
        click.echo(f"✅ Pipeline completed successfully!")
        click.echo(f"📁 Cleaned data: {cleaned_file}")
        click.echo(f"📊 Insights: {insights_file}")
        
        # Display summary
        click.echo("\n📈 Summary Insights:")
        for insight in insights[:5]:  # Show first 5 insights
            click.echo(f"  • {insight}")
    else:
        click.echo("❌ Pipeline failed at analysis step")

if __name__ == '__main__':
    cli()
