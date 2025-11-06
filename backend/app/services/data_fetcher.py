"""
Data Fetcher Module
Fetches financial data from Yahoo Finance API using yfinance
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
import warnings

warnings.filterwarnings('ignore')


class DataFetcher:
    """Fetches financial data from Yahoo Finance"""
    
    def __init__(self, ticker: str):
        """
        Initialize DataFetcher with a stock ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        """
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self._info = None
        self._financials = None
        self._balance_sheet = None
        self._cashflow = None
        
    def get_company_info(self) -> Dict:
        """
        Get general company information
        
        Returns:
            Dictionary with company information
        """
        if self._info is None:
            try:
                self._info = self.stock.info
            except Exception as e:
                print(f"Error fetching company info: {e}")
                self._info = {}
        return self._info
    
    def get_financials(self, period: str = "annual") -> pd.DataFrame:
        """
        Get income statement data
        
        Args:
            period: 'annual' or 'quarterly'
            
        Returns:
            DataFrame with financial statements
        """
        try:
            if period == "annual":
                self._financials = self.stock.financials
            else:
                self._financials = self.stock.quarterly_financials
            return self._financials
        except Exception as e:
            print(f"Error fetching financials: {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, period: str = "annual") -> pd.DataFrame:
        """
        Get balance sheet data
        
        Args:
            period: 'annual' or 'quarterly'
            
        Returns:
            DataFrame with balance sheet data
        """
        try:
            if period == "annual":
                self._balance_sheet = self.stock.balance_sheet
            else:
                self._balance_sheet = self.stock.quarterly_balance_sheet
            return self._balance_sheet
        except Exception as e:
            print(f"Error fetching balance sheet: {e}")
            return pd.DataFrame()
    
    def get_cashflow(self, period: str = "annual") -> pd.DataFrame:
        """
        Get cash flow statement data
        
        Args:
            period: 'annual' or 'quarterly'
            
        Returns:
            DataFrame with cash flow data
        """
        try:
            if period == "annual":
                self._cashflow = self.stock.cashflow
            else:
                self._cashflow = self.stock.quarterly_cashflow
            return self._cashflow
        except Exception as e:
            print(f"Error fetching cashflow: {e}")
            return pd.DataFrame()
    
    def get_historical_prices(self, period: str = "5y") -> pd.DataFrame:
        """
        Get historical stock prices
        
        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with historical prices
        """
        try:
            hist = self.stock.history(period=period)
            return hist
        except Exception as e:
            print(f"Error fetching historical prices: {e}")
            return pd.DataFrame()
    
    def get_key_metrics(self) -> Dict:
        """
        Extract key financial metrics
        
        Returns:
            Dictionary with key metrics
        """
        info = self.get_company_info()
        financials = self.get_financials()
        balance_sheet = self.get_balance_sheet()
        cashflow = self.get_cashflow()
        
        metrics = {}
        
        # From info
        metrics['market_cap'] = info.get('marketCap', 0)
        metrics['enterprise_value'] = info.get('enterpriseValue', 0)
        metrics['revenue'] = info.get('totalRevenue', 0)
        metrics['ebitda'] = info.get('ebitda', 0)
        metrics['net_income'] = info.get('netIncomeToCommon', 0)
        metrics['shares_outstanding'] = info.get('sharesOutstanding', 0)
        metrics['book_value'] = info.get('bookValue', 0)
        metrics['debt'] = info.get('totalDebt', 0)
        metrics['cash'] = info.get('totalCash', 0)
        metrics['beta'] = info.get('beta', 1.0)
        
        # Calculate from financials if available
        if not financials.empty:
            if 'Total Revenue' in financials.index:
                metrics['revenue'] = financials.loc['Total Revenue'].iloc[0] if metrics['revenue'] == 0 else metrics['revenue']
            if 'EBITDA' in financials.index:
                metrics['ebitda'] = financials.loc['EBITDA'].iloc[0] if metrics['ebitda'] == 0 else metrics['ebitda']
            if 'Net Income' in financials.index:
                metrics['net_income'] = financials.loc['Net Income'].iloc[0] if metrics['net_income'] == 0 else metrics['net_income']
        
        if not balance_sheet.empty:
            if 'Total Debt' in balance_sheet.index:
                metrics['debt'] = balance_sheet.loc['Total Debt'].iloc[0] if metrics['debt'] == 0 else metrics['debt']
            if 'Cash And Cash Equivalents' in balance_sheet.index:
                metrics['cash'] = balance_sheet.loc['Cash And Cash Equivalents'].iloc[0] if metrics['cash'] == 0 else metrics['cash']
        
        return metrics
    
    def get_peers(self, industry: Optional[str] = None) -> List[str]:
        """
        Get peer companies (simplified - would need industry classification)
        
        Args:
            industry: Industry sector (optional)
            
        Returns:
            List of peer ticker symbols
        """
        # This is a simplified version
        # In production, you'd use industry classification APIs
        info = self.get_company_info()
        sector = info.get('sector', '')
        industry_key = info.get('industry', '')
        
        # Common peer groups (simplified)
        peer_groups = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
            'Finance': ['JPM', 'BAC', 'WFC', 'C', 'GS'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABT', 'TMO'],
        }
        
        for key, peers in peer_groups.items():
            if key.lower() in sector.lower() or key.lower() in industry_key.lower():
                return [p for p in peers if p != self.ticker]
        
        return []

