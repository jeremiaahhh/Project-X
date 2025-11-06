"""Analysis service orchestrating valuation workflow."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from .data_fetcher import DataFetcher
from .wacc_calculator import WACCCalculator
from .dcf_valuator import DCFValuator
from .trading_comps import TradingComps


def _format_historical_prices(price_data: pd.DataFrame, limit: int = 365) -> List[Dict[str, Any]]:
    """Transform historical price dataframe into serialisable list."""
    if price_data.empty:
        return []

    prices = price_data.tail(limit)[['Close']].reset_index()
    prices.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
    prices['date'] = prices['date'].astype(str)
    return prices.to_dict(orient='records')


def _estimate_base_fcf(fetcher: DataFetcher, metrics: Dict[str, float]) -> float:
    """Estimate base free cash flow using cash flow statements or EBITDA fallback."""
    cashflow = fetcher.get_cashflow()
    base_fcf = 0.0

    if not cashflow.empty and 'Operating Cash Flow' in cashflow.index:
        operating_cf = cashflow.loc['Operating Cash Flow'].iloc[0]
        if 'Capital Expenditure' in cashflow.index:
            capex = abs(cashflow.loc['Capital Expenditure'].iloc[0])
        else:
            capex = operating_cf * 0.1
        base_fcf = operating_cf - capex

    if base_fcf == 0:
        base_fcf = metrics.get('ebitda', 0) * 0.6

    return base_fcf


def run_full_analysis(
    *,
    ticker: str,
    risk_free_rate: float,
    market_risk_premium: float,
    terminal_growth_rate: float,
    projection_years: int,
    growth_rates: Optional[List[float]] = None,
    peer_tickers: Optional[List[str]] = None,
    cashflow_years: int = 5,
) -> Dict[str, Any]:
    """Execute the complete valuation workflow and return serialisable payload."""
    growth_rates = growth_rates or []

    fetcher = DataFetcher(ticker)
    metrics = fetcher.get_key_metrics()
    company_info = fetcher.get_company_info()

    wacc_calc = WACCCalculator(risk_free_rate, market_risk_premium)
    wacc_results = wacc_calc.calculate_wacc(
        market_cap=metrics.get('market_cap', 0),
        total_debt=metrics.get('debt', 0),
        beta=metrics.get('beta', 1.0),
        interest_expense=metrics.get('debt', 0) * 0.05,
        tax_rate=0.21,
    )

    base_fcf = _estimate_base_fcf(fetcher, metrics)

    dcf_valuator = DCFValuator(wacc_results['wacc'], terminal_growth_rate)
    dcf_results = dcf_valuator.perform_full_dcf(
        base_fcf=base_fcf,
        growth_rates=growth_rates,
        cash=metrics.get('cash', 0),
        debt=metrics.get('debt', 0),
        shares_outstanding=metrics.get('shares_outstanding', 1),
        years=projection_years,
    )

    trading_comps = TradingComps(ticker, peer_tickers)
    comps_results = trading_comps.get_comprehensive_analysis()

    price_history = _format_historical_prices(fetcher.get_historical_prices(period=f"{cashflow_years}y"))

    projected_fcfs = []
    if 'projected_fcfs' in dcf_results:
        projected_df = dcf_results['projected_fcfs'].rename(
            columns={'Year': 'year', 'FCF': 'fcf', 'Growth Rate': 'growth_rate'}
        )
        projected_fcfs = projected_df.to_dict(orient='records')

    discounted_fcfs = []
    if 'discounted_fcfs' in dcf_results:
        discounted_df = dcf_results['discounted_fcfs'].rename(
            columns={'Year': 'year', 'FCF': 'fcf', 'Discount Factor': 'discount_factor', 'PV of FCF': 'pv_of_fcf'}
        )
        discounted_fcfs = discounted_df.to_dict(orient='records')

    return {
        'inputs': {
            'ticker': ticker.upper(),
            'risk_free_rate': risk_free_rate,
            'market_risk_premium': market_risk_premium,
            'terminal_growth_rate': terminal_growth_rate,
            'projection_years': projection_years,
            'growth_rates': growth_rates,
            'peer_tickers': peer_tickers or [],
        },
        'company': {
            'name': company_info.get('longName') or company_info.get('shortName') or ticker.upper(),
            'summary': company_info.get('longBusinessSummary'),
            'sector': company_info.get('sector'),
            'industry': company_info.get('industry'),
            'metrics': metrics,
        },
        'wacc': wacc_results,
        'dcf': {
            key: value
            for key, value in dcf_results.items()
            if key not in {'projected_fcfs', 'discounted_fcfs'}
        },
        'projected_fcfs': projected_fcfs,
        'discounted_fcfs': discounted_fcfs,
        'trading_comps': {
            'target_multiples': comps_results.get('target_multiples', {}),
            'peer_multiples': comps_results.get('peer_multiples', pd.DataFrame()).fillna(0).to_dict(orient='records'),
            'valuation_ranges': comps_results.get('valuation_ranges', {}),
            'target_metrics': comps_results.get('target_metrics', {}),
        },
        'historical_prices': price_history,
    }
