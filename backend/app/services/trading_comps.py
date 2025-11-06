"""
Trading Comps (Comparable Company Analysis) Module
Calculates trading multiples for valuation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

from .data_fetcher import DataFetcher


class TradingComps:
    """Performs Comparable Company Analysis using trading multiples"""
    
    def __init__(self, ticker: str, peer_tickers: Optional[List[str]] = None):
        """
        Initialize Trading Comps analyzer
        
        Args:
            ticker: Target company ticker
            peer_tickers: List of peer company tickers (optional)
        """
        self.ticker = ticker.upper()
        self.target_fetcher = DataFetcher(ticker)
        self.peer_tickers = peer_tickers or []
        self.peer_data = {}
    
    def fetch_peer_data(self) -> Dict:
        """
        Fetch financial data for peer companies
        
        Returns:
            Dictionary with peer company data
        """
        if not self.peer_tickers:
            # Try to get peers automatically
            self.peer_tickers = self.target_fetcher.get_peers()
        
        for peer_ticker in self.peer_tickers:
            try:
                fetcher = DataFetcher(peer_ticker)
                metrics = fetcher.get_key_metrics()
                self.peer_data[peer_ticker] = metrics
            except Exception as e:
                print(f"Error fetching data for {peer_ticker}: {e}")
                continue
        
        return self.peer_data
    
    def calculate_multiples(self, metrics: Dict) -> Dict:
        """
        Calculate trading multiples from metrics
        
        Args:
            metrics: Dictionary with financial metrics
            
        Returns:
            Dictionary with calculated multiples
        """
        multiples = {}
        
        market_cap = metrics.get('market_cap', 0)
        enterprise_value = metrics.get('enterprise_value', 0)
        revenue = metrics.get('revenue', 0)
        ebitda = metrics.get('ebitda', 0)
        net_income = metrics.get('net_income', 0)
        book_value = metrics.get('book_value', 0)
        shares_outstanding = metrics.get('shares_outstanding', 0)
        
        # Price multiples
        if revenue > 0:
            multiples['EV/Revenue'] = enterprise_value / revenue
            multiples['P/S'] = market_cap / revenue
        
        if ebitda > 0:
            multiples['EV/EBITDA'] = enterprise_value / ebitda
        
        if net_income > 0:
            multiples['P/E'] = market_cap / net_income
            multiples['EPS'] = net_income / shares_outstanding if shares_outstanding > 0 else 0
        
        if book_value > 0:
            multiples['P/B'] = market_cap / book_value
        
        # Store base metrics
        multiples['Market Cap'] = market_cap
        multiples['Enterprise Value'] = enterprise_value
        multiples['Revenue'] = revenue
        multiples['EBITDA'] = ebitda
        multiples['Net Income'] = net_income
        
        return multiples
    
    def calculate_peer_multiples(self) -> pd.DataFrame:
        """
        Calculate multiples for all peer companies
        
        Returns:
            DataFrame with peer multiples
        """
        if not self.peer_data:
            self.fetch_peer_data()
        
        peer_multiples = []
        
        for ticker, metrics in self.peer_data.items():
            multiples = self.calculate_multiples(metrics)
            multiples['Ticker'] = ticker
            peer_multiples.append(multiples)
        
        if not peer_multiples:
            return pd.DataFrame()
        
        df = pd.DataFrame(peer_multiples)
        
        # Reorder columns
        cols = ['Ticker'] + [c for c in df.columns if c != 'Ticker']
        df = df[cols]
        
        return df
    
    def calculate_target_multiples(self) -> Dict:
        """
        Calculate multiples for target company
        
        Returns:
            Dictionary with target company multiples
        """
        target_metrics = self.target_fetcher.get_key_metrics()
        return self.calculate_multiples(target_metrics)
    
    def calculate_valuation_ranges(
        self,
        target_metrics: Dict,
        multiple_type: str = 'EV/EBITDA'
    ) -> Dict:
        """
        Calculate valuation ranges based on peer multiples
        
        Args:
            target_metrics: Target company financial metrics
            multiple_type: Type of multiple to use ('EV/EBITDA', 'P/E', 'EV/Revenue', etc.)
            
        Returns:
            Dictionary with valuation ranges
        """
        peer_multiples_df = self.calculate_peer_multiples()
        
        if peer_multiples_df.empty or multiple_type not in peer_multiples_df.columns:
            return {
                'multiple_type': multiple_type,
                'min_multiple': 0,
                'median_multiple': 0,
                'max_multiple': 0,
                'min_valuation': 0,
                'median_valuation': 0,
                'max_valuation': 0
            }
        
        # Calculate statistics
        multiples = peer_multiples_df[multiple_type].dropna()
        
        if multiples.empty:
            return {
                'multiple_type': multiple_type,
                'min_multiple': 0,
                'median_multiple': 0,
                'max_multiple': 0,
                'min_valuation': 0,
                'median_valuation': 0,
                'max_valuation': 0
            }
        
        min_multiple = multiples.min()
        median_multiple = multiples.median()
        max_multiple = multiples.max()
        
        # Calculate valuations based on target metrics
        if multiple_type == 'EV/EBITDA':
            base_value = target_metrics.get('ebitda', 0)
        elif multiple_type == 'P/E':
            base_value = target_metrics.get('net_income', 0)
        elif multiple_type == 'EV/Revenue':
            base_value = target_metrics.get('revenue', 0)
        elif multiple_type == 'P/S':
            base_value = target_metrics.get('revenue', 0)
        else:
            base_value = 0
        
        min_valuation = min_multiple * base_value if base_value > 0 else 0
        median_valuation = median_multiple * base_value if base_value > 0 else 0
        max_valuation = max_multiple * base_value if base_value > 0 else 0
        
        # If using P/E or P/S, convert to equity value
        # If using EV multiples, need to convert to equity value
        if multiple_type.startswith('EV/'):
            # Convert EV to equity value
            debt = target_metrics.get('debt', 0)
            cash = target_metrics.get('cash', 0)
            min_equity_value = min_valuation - debt + cash
            median_equity_value = median_valuation - debt + cash
            max_equity_value = max_valuation - debt + cash
        else:
            min_equity_value = min_valuation
            median_equity_value = median_valuation
            max_equity_value = max_valuation
        
        shares_outstanding = target_metrics.get('shares_outstanding', 1)
        
        return {
            'multiple_type': multiple_type,
            'min_multiple': min_multiple,
            'median_multiple': median_multiple,
            'max_multiple': max_multiple,
            'min_enterprise_value': min_valuation if multiple_type.startswith('EV/') else 0,
            'median_enterprise_value': median_valuation if multiple_type.startswith('EV/') else 0,
            'max_enterprise_value': max_valuation if multiple_type.startswith('EV/') else 0,
            'min_equity_value': min_equity_value,
            'median_equity_value': median_equity_value,
            'max_equity_value': max_equity_value,
            'min_share_price': min_equity_value / shares_outstanding if shares_outstanding > 0 else 0,
            'median_share_price': median_equity_value / shares_outstanding if shares_outstanding > 0 else 0,
            'max_share_price': max_equity_value / shares_outstanding if shares_outstanding > 0 else 0,
            'base_value': base_value
        }
    
    def get_comprehensive_analysis(self) -> Dict:
        """
        Get comprehensive trading comps analysis
        
        Returns:
            Dictionary with complete analysis
        """
        target_multiples = self.calculate_target_multiples()
        peer_multiples_df = self.calculate_peer_multiples()
        target_metrics = self.target_fetcher.get_key_metrics()
        
        # Calculate valuation ranges for different multiples
        valuation_ranges = {}
        for multiple_type in ['EV/EBITDA', 'P/E', 'EV/Revenue', 'P/S']:
            if multiple_type in peer_multiples_df.columns:
                valuation_ranges[multiple_type] = self.calculate_valuation_ranges(
                    target_metrics,
                    multiple_type
                )
        
        return {
            'target_multiples': target_multiples,
            'peer_multiples': peer_multiples_df,
            'valuation_ranges': valuation_ranges,
            'target_metrics': target_metrics
        }

