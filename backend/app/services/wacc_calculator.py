"""
WACC (Weighted Average Cost of Capital) Calculator
Calculates WACC for DCF valuation
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime


class WACCCalculator:
    """Calculates Weighted Average Cost of Capital (WACC)"""
    
    def __init__(self, risk_free_rate: float = 0.04, market_risk_premium: float = 0.06):
        """
        Initialize WACC Calculator
        
        Args:
            risk_free_rate: Risk-free rate (default 4% - 10Y Treasury)
            market_risk_premium: Market risk premium (default 6%)
        """
        self.risk_free_rate = risk_free_rate
        self.market_risk_premium = market_risk_premium
    
    def calculate_cost_of_equity(self, beta: float, risk_free_rate: Optional[float] = None) -> float:
        """
        Calculate cost of equity using CAPM
        
        CAPM: Re = Rf + β * (Rm - Rf)
        
        Args:
            beta: Stock beta
            risk_free_rate: Risk-free rate (optional, uses default if not provided)
            
        Returns:
            Cost of equity as decimal
        """
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
        
        cost_of_equity = risk_free_rate + beta * self.market_risk_premium
        return cost_of_equity
    
    def calculate_cost_of_debt(self, interest_expense: float, total_debt: float, tax_rate: float = 0.21) -> float:
        """
        Calculate after-tax cost of debt
        
        Args:
            interest_expense: Annual interest expense
            total_debt: Total debt outstanding
            tax_rate: Corporate tax rate (default 21% US)
            
        Returns:
            After-tax cost of debt as decimal
        """
        if total_debt == 0:
            return 0.0
        
        cost_of_debt_pre_tax = interest_expense / total_debt
        cost_of_debt_after_tax = cost_of_debt_pre_tax * (1 - tax_rate)
        return cost_of_debt_after_tax
    
    def calculate_wacc(
        self,
        market_cap: float,
        total_debt: float,
        beta: float,
        interest_expense: float = 0,
        tax_rate: float = 0.21,
        risk_free_rate: Optional[float] = None,
        cost_of_debt: Optional[float] = None
    ) -> Dict:
        """
        Calculate WACC
        
        WACC = (E/V * Re) + (D/V * Rd * (1-Tc))
        where:
        E = Market value of equity
        D = Market value of debt
        V = E + D
        Re = Cost of equity
        Rd = Cost of debt
        Tc = Tax rate
        
        Args:
            market_cap: Market capitalization
            total_debt: Total debt
            beta: Stock beta
            interest_expense: Annual interest expense
            tax_rate: Corporate tax rate
            risk_free_rate: Risk-free rate (optional)
            cost_of_debt: Pre-calculated cost of debt (optional)
            
        Returns:
            Dictionary with WACC components and final WACC
        """
        # Calculate market values
        equity_value = market_cap
        debt_value = total_debt
        total_value = equity_value + debt_value
        
        if total_value == 0:
            return {
                'wacc': 0.0,
                'cost_of_equity': 0.0,
                'cost_of_debt': 0.0,
                'equity_weight': 0.0,
                'debt_weight': 0.0,
                'tax_rate': tax_rate
            }
        
        # Calculate weights
        equity_weight = equity_value / total_value
        debt_weight = debt_value / total_value
        
        # Calculate cost of equity
        cost_of_equity = self.calculate_cost_of_equity(beta, risk_free_rate)
        
        # Calculate cost of debt
        if cost_of_debt is None:
            if interest_expense > 0 and total_debt > 0:
                cost_of_debt = self.calculate_cost_of_debt(interest_expense, total_debt, tax_rate)
            else:
                # Estimate cost of debt if not available
                cost_of_debt = self.risk_free_rate + 0.02  # Assume 2% spread over risk-free rate
        
        # Calculate WACC
        wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt)
        
        return {
            'wacc': wacc,
            'cost_of_equity': cost_of_equity,
            'cost_of_debt': cost_of_debt,
            'equity_weight': equity_weight,
            'debt_weight': debt_weight,
            'equity_value': equity_value,
            'debt_value': debt_value,
            'total_value': total_value,
            'tax_rate': tax_rate,
            'beta': beta,
            'risk_free_rate': risk_free_rate if risk_free_rate else self.risk_free_rate,
            'market_risk_premium': self.market_risk_premium
        }

