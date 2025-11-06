"""
Example usage of the Company Valuation Dashboard
Demonstrates how to use the modules programmatically
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.app.services.data_fetcher import DataFetcher
from backend.app.services.wacc_calculator import WACCCalculator
from backend.app.services.dcf_valuator import DCFValuator
from backend.app.services.trading_comps import TradingComps
from backend.app.services.visualizer import Visualizer
from backend.app.services.exporter import Exporter


def example_basic_valuation():
    """Basic example: DCF valuation for a single company"""
    print("=" * 60)
    print("Example 1: Basic DCF Valuation")
    print("=" * 60)
    
    ticker = "AAPL"
    
    # Fetch data
    fetcher = DataFetcher(ticker)
    metrics = fetcher.get_key_metrics()
    company_info = fetcher.get_company_info()
    
    print(f"\nCompany: {company_info.get('longName', ticker)}")
    print(f"Market Cap: ${metrics.get('market_cap', 0)/1e9:.2f}B")
    print(f"Revenue: ${metrics.get('revenue', 0)/1e9:.2f}B")
    print(f"Beta: {metrics.get('beta', 0):.2f}")
    
    # Calculate WACC
    wacc_calc = WACCCalculator(risk_free_rate=0.04, market_risk_premium=0.06)
    wacc_results = wacc_calc.calculate_wacc(
        market_cap=metrics.get('market_cap', 0),
        total_debt=metrics.get('debt', 0),
        beta=metrics.get('beta', 1.0),
        interest_expense=metrics.get('debt', 0) * 0.05,
        tax_rate=0.21
    )
    
    print(f"\nWACC: {wacc_results['wacc']*100:.2f}%")
    print(f"Cost of Equity: {wacc_results['cost_of_equity']*100:.2f}%")
    print(f"Cost of Debt: {wacc_results['cost_of_debt']*100:.2f}%")
    
    # Estimate base FCF
    cashflow = fetcher.get_cashflow()
    base_fcf = 0
    if not cashflow.empty and 'Operating Cash Flow' in cashflow.index:
        ocf = cashflow.loc['Operating Cash Flow'].iloc[0]
        capex = abs(cashflow.loc['Capital Expenditure'].iloc[0]) if 'Capital Expenditure' in cashflow.index else ocf * 0.1
        base_fcf = ocf - capex
    
    if base_fcf == 0:
        base_fcf = metrics.get('ebitda', 0) * 0.6
    
    # Perform DCF
    dcf = DCFValuator(wacc_results['wacc'], terminal_growth_rate=0.03)
    growth_rates = [0.10, 0.08, 0.06, 0.05, 0.04]
    dcf_results = dcf.perform_full_dcf(
        base_fcf=base_fcf,
        growth_rates=growth_rates,
        cash=metrics.get('cash', 0),
        debt=metrics.get('debt', 0),
        shares_outstanding=metrics.get('shares_outstanding', 1),
        years=5
    )
    
    print(f"\nDCF Valuation Results:")
    print(f"Enterprise Value: ${dcf_results['enterprise_value']/1e9:.2f}B")
    print(f"Equity Value: ${dcf_results['equity_value']/1e9:.2f}B")
    print(f"Fair Value Share Price: ${dcf_results['fair_value_share_price']:.2f}")
    
    current_price = company_info.get('currentPrice', 0)
    if current_price > 0:
        upside = ((dcf_results['fair_value_share_price'] - current_price) / current_price) * 100
        print(f"Current Price: ${current_price:.2f}")
        print(f"Upside/Downside: {upside:+.1f}%")


def example_trading_comps():
    """Example: Trading comps analysis"""
    print("\n" + "=" * 60)
    print("Example 2: Trading Comps Analysis")
    print("=" * 60)
    
    ticker = "AAPL"
    peer_tickers = ["MSFT", "GOOGL", "AMZN", "META"]
    
    comps = TradingComps(ticker, peer_tickers)
    comps_results = comps.get_comprehensive_analysis()
    
    print(f"\nTarget Company: {ticker}")
    print(f"Peer Companies: {', '.join(peer_tickers)}")
    
    if not comps_results['peer_multiples'].empty:
        print("\nPeer Multiples:")
        print(comps_results['peer_multiples'].to_string())
        
        print("\nValuation Ranges:")
        for multiple_type, ranges in comps_results['valuation_ranges'].items():
            print(f"\n{multiple_type}:")
            print(f"  Min Share Price: ${ranges.get('min_share_price', 0):.2f}")
            print(f"  Median Share Price: ${ranges.get('median_share_price', 0):.2f}")
            print(f"  Max Share Price: ${ranges.get('max_share_price', 0):.2f}")


def example_visualizations():
    """Example: Creating visualizations"""
    print("\n" + "=" * 60)
    print("Example 3: Creating Visualizations")
    print("=" * 60)
    
    ticker = "AAPL"
    
    # Fetch data and perform analysis
    fetcher = DataFetcher(ticker)
    metrics = fetcher.get_key_metrics()
    
    wacc_calc = WACCCalculator()
    wacc_results = wacc_calc.calculate_wacc(
        market_cap=metrics.get('market_cap', 0),
        total_debt=metrics.get('debt', 0),
        beta=metrics.get('beta', 1.0)
    )
    
    cashflow = fetcher.get_cashflow()
    base_fcf = 0
    if not cashflow.empty and 'Operating Cash Flow' in cashflow.index:
        ocf = cashflow.loc['Operating Cash Flow'].iloc[0]
        capex = abs(cashflow.loc['Capital Expenditure'].iloc[0]) if 'Capital Expenditure' in cashflow.index else ocf * 0.1
        base_fcf = ocf - capex
    
    if base_fcf == 0:
        base_fcf = metrics.get('ebitda', 0) * 0.6
    
    dcf = DCFValuator(wacc_results['wacc'])
    dcf_results = dcf.perform_full_dcf(
        base_fcf=base_fcf,
        growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
        cash=metrics.get('cash', 0),
        debt=metrics.get('debt', 0),
        shares_outstanding=metrics.get('shares_outstanding', 1)
    )
    
    # Create visualizations
    visualizer = Visualizer()
    
    print("\nCreating visualizations...")
    print("(In a real application, these would be displayed or saved)")
    
    # FCF projections chart
    fcf_fig = visualizer.plot_fcf_projections(dcf_results)
    print("✓ FCF Projections chart created")
    
    # DCF breakdown chart
    dcf_breakdown_fig = visualizer.plot_dcf_breakdown(dcf_results)
    print("✓ DCF Breakdown chart created")
    
    # WACC breakdown chart
    wacc_fig = visualizer.plot_wacc_breakdown(wacc_results)
    print("✓ WACC Breakdown chart created")
    
    # Historical prices
    price_data = fetcher.get_historical_prices(period="1y")
    if not price_data.empty:
        price_fig = visualizer.plot_historical_prices(price_data, ticker)
        print("✓ Historical Prices chart created")


def example_export():
    """Example: Exporting results"""
    print("\n" + "=" * 60)
    print("Example 4: Exporting Results")
    print("=" * 60)
    
    ticker = "AAPL"
    
    # Perform analysis
    fetcher = DataFetcher(ticker)
    metrics = fetcher.get_key_metrics()
    
    wacc_calc = WACCCalculator()
    wacc_results = wacc_calc.calculate_wacc(
        market_cap=metrics.get('market_cap', 0),
        total_debt=metrics.get('debt', 0),
        beta=metrics.get('beta', 1.0)
    )
    
    cashflow = fetcher.get_cashflow()
    base_fcf = 0
    if not cashflow.empty and 'Operating Cash Flow' in cashflow.index:
        ocf = cashflow.loc['Operating Cash Flow'].iloc[0]
        capex = abs(cashflow.loc['Capital Expenditure'].iloc[0]) if 'Capital Expenditure' in cashflow.index else ocf * 0.1
        base_fcf = ocf - capex
    
    if base_fcf == 0:
        base_fcf = metrics.get('ebitda', 0) * 0.6
    
    dcf = DCFValuator(wacc_results['wacc'])
    dcf_results = dcf.perform_full_dcf(
        base_fcf=base_fcf,
        growth_rates=[0.10, 0.08, 0.06, 0.05, 0.04],
        cash=metrics.get('cash', 0),
        debt=metrics.get('debt', 0),
        shares_outstanding=metrics.get('shares_outstanding', 1)
    )
    
    comps = TradingComps(ticker, ["MSFT", "GOOGL", "AMZN"])
    comps_results = comps.get_comprehensive_analysis()
    
    # Export
    exporter = Exporter()
    
    print("\nExporting to PowerPoint...")
    pptx_path = exporter.export_to_powerpoint(ticker, dcf_results, comps_results, wacc_results)
    print(f"✓ PowerPoint exported to: {pptx_path}")
    
    print("\nExporting to PDF...")
    pdf_path = exporter.export_to_pdf(ticker, dcf_results, comps_results, wacc_results)
    print(f"✓ PDF exported to: {pdf_path}")


if __name__ == "__main__":
    # Run examples
    try:
        example_basic_valuation()
        example_trading_comps()
        example_visualizations()
        example_export()
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()

