"""
DCF (Discounted Cash Flow) Valuation Module
Performs DCF valuation based on projected free cash flows
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime


class DCFValuator:
    """Performs Discounted Cash Flow (DCF) valuation"""
    
    def __init__(self, wacc: float, terminal_growth_rate: float = 0.03):
        """
        Initialize DCF Valuator
        
        Args:
            wacc: Weighted Average Cost of Capital (as decimal)
            terminal_growth_rate: Terminal growth rate (default 3%)
        """
        self.wacc = wacc
        self.terminal_growth_rate = terminal_growth_rate
    
    def calculate_free_cash_flow(
        self,
        operating_cash_flow: float,
        capital_expenditures: float
    ) -> float:
        """
        Calculate Free Cash Flow (FCF)
        
        FCF = Operating Cash Flow - Capital Expenditures
        
        Args:
            operating_cash_flow: Operating cash flow
            capital_expenditures: Capital expenditures (CapEx)
            
        Returns:
            Free cash flow
        """
        return operating_cash_flow - capital_expenditures
    
    def project_fcf(
        self,
        base_fcf: float,
        growth_rates: List[float],
        years: int = 5
    ) -> pd.DataFrame:
        """
        Project free cash flows for forecast period
        
        Args:
            base_fcf: Base year free cash flow
            growth_rates: List of growth rates for each year
            years: Number of years to project (default 5)
            
        Returns:
            DataFrame with projected FCFs
        """
        if len(growth_rates) < years:
            # Extend growth rates if not enough provided
            last_rate = growth_rates[-1] if growth_rates else 0.05
            growth_rates.extend([last_rate] * (years - len(growth_rates)))
        
        projections = []
        current_fcf = base_fcf
        
        for year in range(1, years + 1):
            growth_rate = growth_rates[year - 1] if year <= len(growth_rates) else growth_rates[-1]
            current_fcf = current_fcf * (1 + growth_rate)
            projections.append({
                'Year': year,
                'FCF': current_fcf,
                'Growth Rate': growth_rate
            })
        
        return pd.DataFrame(projections)
    
    def calculate_terminal_value(
        self,
        final_fcf: float,
        wacc: Optional[float] = None,
        terminal_growth_rate: Optional[float] = None
    ) -> float:
        """
        Calculate terminal value using Gordon Growth Model
        
        TV = FCF(n+1) / (WACC - g)
        where g is terminal growth rate
        
        Args:
            final_fcf: Final year FCF
            wacc: WACC (optional, uses instance default)
            terminal_growth_rate: Terminal growth rate (optional)
            
        Returns:
            Terminal value
        """
        if wacc is None:
            wacc = self.wacc
        if terminal_growth_rate is None:
            terminal_growth_rate = self.terminal_growth_rate
        
        if wacc <= terminal_growth_rate:
            raise ValueError("WACC must be greater than terminal growth rate")
        
        # FCF(n+1) = FCF(n) * (1 + g)
        next_year_fcf = final_fcf * (1 + terminal_growth_rate)
        terminal_value = next_year_fcf / (wacc - terminal_growth_rate)
        
        return terminal_value
    
    def calculate_enterprise_value(
        self,
        projected_fcfs: pd.DataFrame,
        terminal_value: float,
        wacc: Optional[float] = None
    ) -> Dict:
        """
        Calculate enterprise value by discounting FCFs and terminal value
        
        Args:
            projected_fcfs: DataFrame with projected FCFs
            terminal_value: Terminal value
            wacc: WACC (optional, uses instance default)
            
        Returns:
            Dictionary with valuation breakdown
        """
        if wacc is None:
            wacc = self.wacc
        
        # Discount projected FCFs
        discounted_fcfs = []
        pv_fcf_sum = 0
        
        for idx, row in projected_fcfs.iterrows():
            year = row['Year']
            fcf = row['FCF']
            discount_factor = 1 / ((1 + wacc) ** year)
            pv_fcf = fcf * discount_factor
            discounted_fcfs.append({
                'Year': year,
                'FCF': fcf,
                'Discount Factor': discount_factor,
                'PV of FCF': pv_fcf
            })
            pv_fcf_sum += pv_fcf
        
        # Discount terminal value
        terminal_year = projected_fcfs['Year'].max()
        terminal_discount_factor = 1 / ((1 + wacc) ** terminal_year)
        pv_terminal_value = terminal_value * terminal_discount_factor
        
        # Calculate enterprise value
        enterprise_value = pv_fcf_sum + pv_terminal_value
        
        return {
            'enterprise_value': enterprise_value,
            'pv_of_fcfs': pv_fcf_sum,
            'pv_of_terminal_value': pv_terminal_value,
            'discounted_fcfs': pd.DataFrame(discounted_fcfs),
            'terminal_value': terminal_value,
            'wacc': wacc
        }
    
    def calculate_equity_value(
        self,
        enterprise_value: float,
        cash: float,
        debt: float,
        minority_interest: float = 0,
        preferred_stock: float = 0
    ) -> Dict:
        """
        Calculate equity value from enterprise value
        
        Equity Value = Enterprise Value - Debt + Cash - Minority Interest - Preferred Stock
        
        Args:
            enterprise_value: Enterprise value
            cash: Cash and cash equivalents
            debt: Total debt
            minority_interest: Minority interest (optional)
            preferred_stock: Preferred stock (optional)
            
        Returns:
            Dictionary with equity value breakdown
        """
        equity_value = enterprise_value - debt + cash - minority_interest - preferred_stock
        
        return {
            'equity_value': equity_value,
            'enterprise_value': enterprise_value,
            'cash': cash,
            'debt': debt,
            'minority_interest': minority_interest,
            'preferred_stock': preferred_stock
        }
    
    def calculate_share_price(
        self,
        equity_value: float,
        shares_outstanding: float
    ) -> float:
        """
        Calculate fair value share price
        
        Share Price = Equity Value / Shares Outstanding
        
        Args:
            equity_value: Equity value
            shares_outstanding: Number of shares outstanding
            
        Returns:
            Fair value share price
        """
        if shares_outstanding == 0:
            return 0.0
        return equity_value / shares_outstanding
    
    def perform_full_dcf(
        self,
        base_fcf: float,
        growth_rates: List[float],
        cash: float,
        debt: float,
        shares_outstanding: float,
        years: int = 5,
        wacc: Optional[float] = None,
        terminal_growth_rate: Optional[float] = None
    ) -> Dict:
        """
        Perform complete DCF valuation
        
        Args:
            base_fcf: Base year free cash flow
            growth_rates: List of growth rates for projection period
            cash: Cash and cash equivalents
            debt: Total debt
            shares_outstanding: Shares outstanding
            years: Number of projection years
            wacc: WACC (optional)
            terminal_growth_rate: Terminal growth rate (optional)
            
        Returns:
            Complete DCF valuation results
        """
        if wacc is None:
            wacc = self.wacc
        if terminal_growth_rate is None:
            terminal_growth_rate = self.terminal_growth_rate
        
        # Project FCFs
        projected_fcfs = self.project_fcf(base_fcf, growth_rates, years)
        final_fcf = projected_fcfs['FCF'].iloc[-1]
        
        # Calculate terminal value
        terminal_value = self.calculate_terminal_value(final_fcf, wacc, terminal_growth_rate)
        
        # Calculate enterprise value
        ev_results = self.calculate_enterprise_value(projected_fcfs, terminal_value, wacc)
        
        # Calculate equity value
        equity_results = self.calculate_equity_value(
            ev_results['enterprise_value'],
            cash,
            debt
        )
        
        # Calculate share price
        share_price = self.calculate_share_price(
            equity_results['equity_value'],
            shares_outstanding
        )
        
        return {
            'projected_fcfs': projected_fcfs,
            'terminal_value': terminal_value,
            'enterprise_value': ev_results['enterprise_value'],
            'equity_value': equity_results['equity_value'],
            'fair_value_share_price': share_price,
            'shares_outstanding': shares_outstanding,
            'wacc': wacc,
            'terminal_growth_rate': terminal_growth_rate,
            'discounted_fcfs': ev_results['discounted_fcfs'],
            'pv_of_fcfs': ev_results['pv_of_fcfs'],
            'pv_of_terminal_value': ev_results['pv_of_terminal_value']
        }

