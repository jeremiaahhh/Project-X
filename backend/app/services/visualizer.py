"""
Visualization Module
Creates charts and graphs using Plotly for interactive visualizations
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional


class Visualizer:
    """Creates visualizations for valuation analysis"""
    
    def __init__(self):
        """Initialize Visualizer"""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'info': '#17a2b8'
        }
    
    def plot_fcf_projections(self, dcf_results: Dict) -> go.Figure:
        """
        Plot projected free cash flows
        
        Args:
            dcf_results: DCF valuation results dictionary
            
        Returns:
            Plotly figure
        """
        projected_fcfs = dcf_results.get('projected_fcfs', pd.DataFrame())
        
        if projected_fcfs.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available", showarrow=False)
            return fig
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=projected_fcfs['Year'],
            y=projected_fcfs['FCF'],
            name='Projected FCF',
            marker_color=self.color_scheme['primary'],
            text=[f'${val/1e6:.1f}M' for val in projected_fcfs['FCF']],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Projected Free Cash Flows',
            xaxis_title='Year',
            yaxis_title='Free Cash Flow ($)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_dcf_breakdown(self, dcf_results: Dict) -> go.Figure:
        """
        Plot DCF valuation breakdown (PV of FCFs vs Terminal Value)
        
        Args:
            dcf_results: DCF valuation results dictionary
            
        Returns:
            Plotly figure
        """
        pv_fcfs = dcf_results.get('pv_of_fcfs', 0)
        pv_terminal = dcf_results.get('pv_of_terminal_value', 0)
        enterprise_value = dcf_results.get('enterprise_value', 0)
        
        fig = go.Figure(data=[
            go.Pie(
                labels=['PV of FCFs', 'PV of Terminal Value'],
                values=[pv_fcfs, pv_terminal],
                hole=0.4,
                marker_colors=[self.color_scheme['primary'], self.color_scheme['secondary']],
                textinfo='label+percent+value',
                texttemplate='%{label}<br>$%{value:,.0f}<br>%{percent}'
            )
        ])
        
        fig.update_layout(
            title=f'DCF Valuation Breakdown<br><sub>Enterprise Value: ${enterprise_value:,.0f}</sub>',
            template='plotly_white',
            annotations=[dict(text=f'${enterprise_value:,.0f}', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig
    
    def plot_trading_multiples(self, comps_results: Dict) -> go.Figure:
        """
        Plot trading multiples comparison
        
        Args:
            comps_results: Trading comps results dictionary
            
        Returns:
            Plotly figure
        """
        peer_multiples = comps_results.get('peer_multiples', pd.DataFrame())
        target_multiples = comps_results.get('target_multiples', {})
        
        if peer_multiples.empty:
            fig = go.Figure()
            fig.add_annotation(text="No peer data available", showarrow=False)
            return fig
        
        # Select key multiples to plot
        multiple_types = ['EV/EBITDA', 'P/E', 'EV/Revenue', 'P/S']
        available_multiples = [m for m in multiple_types if m in peer_multiples.columns]
        
        if not available_multiples:
            fig = go.Figure()
            fig.add_annotation(text="No multiple data available", showarrow=False)
            return fig
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=available_multiples,
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for idx, multiple_type in enumerate(available_multiples[:4]):
            row, col = positions[idx]
            
            # Peer data
            peer_values = peer_multiples[multiple_type].dropna()
            
            if not peer_values.empty:
                fig.add_trace(
                    go.Box(
                        y=peer_values,
                        name='Peers',
                        marker_color=self.color_scheme['info'],
                        showlegend=(idx == 0)
                    ),
                    row=row, col=col
                )
                
                # Target value
                target_value = target_multiples.get(multiple_type, None)
                if target_value and not pd.isna(target_value):
                    fig.add_trace(
                        go.Scatter(
                            y=[target_value],
                            mode='markers',
                            name='Target',
                            marker=dict(
                                color=self.color_scheme['danger'],
                                size=15,
                                symbol='star'
                            ),
                            showlegend=(idx == 0)
                        ),
                        row=row, col=col
                    )
        
        fig.update_layout(
            title='Trading Multiples Comparison',
            template='plotly_white',
            height=600,
            showlegend=True
        )
        
        return fig
    
    def plot_valuation_ranges(self, comps_results: Dict) -> go.Figure:
        """
        Plot valuation ranges from trading comps
        
        Args:
            comps_results: Trading comps results dictionary
            
        Returns:
            Plotly figure
        """
        valuation_ranges = comps_results.get('valuation_ranges', {})
        
        if not valuation_ranges:
            fig = go.Figure()
            fig.add_annotation(text="No valuation ranges available", showarrow=False)
            return fig
        
        # Extract data for each multiple type
        multiple_types = []
        min_prices = []
        median_prices = []
        max_prices = []
        
        for multiple_type, ranges in valuation_ranges.items():
            if ranges.get('min_share_price', 0) > 0:
                multiple_types.append(multiple_type)
                min_prices.append(ranges['min_share_price'])
                median_prices.append(ranges['median_share_price'])
                max_prices.append(ranges['max_share_price'])
        
        if not multiple_types:
            fig = go.Figure()
            fig.add_annotation(text="No share price data available", showarrow=False)
            return fig
        
        fig = go.Figure()
        
        # Add range bars
        for i, multiple_type in enumerate(multiple_types):
            fig.add_trace(go.Scatter(
                x=[multiple_type, multiple_type],
                y=[min_prices[i], max_prices[i]],
                mode='lines',
                line=dict(width=8, color=self.color_scheme['info']),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Add median point
            fig.add_trace(go.Scatter(
                x=[multiple_type],
                y=[median_prices[i]],
                mode='markers',
                marker=dict(size=12, color=self.color_scheme['primary']),
                name='Median' if i == 0 else '',
                hovertemplate=f'<b>{multiple_type}</b><br>Median: ${median_prices[i]:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Valuation Ranges by Multiple Type',
            xaxis_title='Multiple Type',
            yaxis_title='Share Price ($)',
            template='plotly_white',
            hovermode='closest',
            height=400
        )
        
        return fig
    
    def plot_wacc_breakdown(self, wacc_results: Dict) -> go.Figure:
        """
        Plot WACC calculation breakdown
        
        Args:
            wacc_results: WACC calculation results dictionary
            
        Returns:
            Plotly figure
        """
        equity_weight = wacc_results.get('equity_weight', 0)
        debt_weight = wacc_results.get('debt_weight', 0)
        cost_of_equity = wacc_results.get('cost_of_equity', 0)
        cost_of_debt = wacc_results.get('cost_of_debt', 0)
        wacc = wacc_results.get('wacc', 0)
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'pie'}, {'type': 'bar'}]],
            subplot_titles=('Capital Structure', 'Cost Components')
        )
        
        # Capital structure pie chart
        fig.add_trace(
            go.Pie(
                labels=['Equity', 'Debt'],
                values=[equity_weight, debt_weight],
                marker_colors=[self.color_scheme['primary'], self.color_scheme['secondary']],
                textinfo='label+percent',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Cost components bar chart
        fig.add_trace(
            go.Bar(
                x=['Cost of Equity', 'Cost of Debt', 'WACC'],
                y=[cost_of_equity * 100, cost_of_debt * 100, wacc * 100],
                marker_color=[self.color_scheme['primary'], self.color_scheme['secondary'], self.color_scheme['success']],
                text=[f'{val:.2f}%' for val in [cost_of_equity * 100, cost_of_debt * 100, wacc * 100]],
                textposition='outside',
                showlegend=False
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title=f'WACC Breakdown (WACC: {wacc*100:.2f}%)',
            template='plotly_white',
            height=400
        )
        
        fig.update_yaxes(title_text="Percentage (%)", row=1, col=2)
        
        return fig
    
    def plot_historical_prices(self, price_data: pd.DataFrame, ticker: str) -> go.Figure:
        """
        Plot historical stock prices
        
        Args:
            price_data: DataFrame with historical price data
            ticker: Stock ticker symbol
            
        Returns:
            Plotly figure
        """
        if price_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No price data available", showarrow=False)
            return fig
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=price_data.index,
            y=price_data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color=self.color_scheme['primary'], width=2),
            fill='tonexty',
            fillcolor=f"rgba(31, 119, 180, 0.1)"
        ))
        
        fig.update_layout(
            title=f'{ticker} Historical Stock Price',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            template='plotly_white',
            hovermode='x unified',
            height=400
        )
        
        return fig

