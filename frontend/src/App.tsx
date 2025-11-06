import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  Building2,
  LineChart,
  PieChart,
  BarChart2,
  Gauge,
  Download,
  Sparkles,
  Factory,
  TrendingUp,
  Users,
  DollarSign,
} from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts'
import type { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent'

import { MetricCard } from './components/MetricCard'
import { SectionHeader } from './components/SectionHeader'
import { runValuationAnalysis } from './lib/api'
import type { ValuationResponse } from './lib/api'

type FormState = {
  ticker: string
  riskFreeRate: number
  marketRiskPremium: number
  terminalGrowthRate: number
  projectionYears: number
  growthRates: number[]
  peerInput: string
}

const defaultForm: FormState = {
  ticker: 'AAPL',
  riskFreeRate: 4,
  marketRiskPremium: 6,
  terminalGrowthRate: 3,
  projectionYears: 5,
  growthRates: [10, 8, 6, 5, 4],
  peerInput: 'MSFT,GOOGL,AMZN',
}

function formatCurrency(value?: number, digits = 2) {
  if (value == null || Number.isNaN(value)) return '—'
  if (Math.abs(value) >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(digits)}B`
  }
  if (Math.abs(value) >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(digits)}M`
  }
  return `$${value.toFixed(digits)}`
}

function formatPercent(value?: number, digits = 2) {
  if (value == null || Number.isNaN(value)) return '—'
  return `${(value * 100).toFixed(digits)}%`
}

function parsePeerInput(input: string): string[] {
  return input
    .split(',')
    .map((entry) => entry.trim().toUpperCase())
    .filter(Boolean)
}

function App() {
  const [formState, setFormState] = useState<FormState>(defaultForm)
  const [data, setData] = useState<ValuationResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const formatMultiple = (value: unknown) =>
    typeof value === 'number' && Number.isFinite(value) ? value.toFixed(2) : '—'

  const handleChange = (field: keyof FormState) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = field === 'ticker' || field === 'peerInput' ? event.target.value : Number(event.target.value)

    if (field === 'projectionYears') {
      const nextYears = Number(event.target.value)
      const nextGrowth = [...formState.growthRates]
      if (nextGrowth.length < nextYears) {
        const last = nextGrowth[nextGrowth.length - 1] ?? 4
        while (nextGrowth.length < nextYears) {
          nextGrowth.push(Math.max(last - 2, 0))
        }
      } else if (nextGrowth.length > nextYears) {
        nextGrowth.length = nextYears
      }
      setFormState((prev) => ({ ...prev, projectionYears: nextYears, growthRates: nextGrowth }))
      return
    }

    setFormState((prev) => ({ ...prev, [field]: value }))
  }

  const handleGrowthRateChange = (index: number, value: number) => {
    setFormState((prev) => {
      const next = [...prev.growthRates]
      next[index] = value
      return { ...prev, growthRates: next }
    })
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const payload = {
        ticker: formState.ticker.toUpperCase(),
        risk_free_rate: formState.riskFreeRate / 100,
        market_risk_premium: formState.marketRiskPremium / 100,
        terminal_growth_rate: formState.terminalGrowthRate / 100,
        projection_years: formState.projectionYears,
        growth_rates: formState.growthRates.map((value) => value / 100),
        peer_tickers: parsePeerInput(formState.peerInput),
      }

      const response = await runValuationAnalysis(payload)
      setData(response)
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : 'Analysis failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const peerTableRows = useMemo(() => {
    if (!data?.trading_comps.peer_multiples) return []
    return data.trading_comps.peer_multiples.slice(0, 6)
  }, [data])

  return (
    <div className="min-h-screen bg-surface-0 text-text-primary">
      <div className="mx-auto flex max-w-[1580px] flex-col gap-10 px-10 py-12">
        <header className="flex flex-col gap-4 rounded-3xl bg-surface-1/90 px-8 py-7 shadow-layer ring-1 ring-border">
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.38em] text-accent">
                <Sparkles className="h-4 w-4" />
                Insight Engine
              </div>
              <h1 className="mt-3 flex items-center gap-3 text-[32px] font-medium text-text-primary">
                <Building2 className="h-8 w-8 text-accent" />
                Valuation Intelligence
              </h1>
              <p className="mt-2 max-w-2xl text-sm text-text-secondary">
                Real-time valuation analytics powered by automated cash flow modelling and peer benchmarking.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <span className="rounded-full bg-accent-muted px-4 py-2 text-[11px] uppercase tracking-[0.28em] text-accent">
                Live Beta
              </span>
              <button
                type="button"
                className="flex items-center gap-2 rounded-xl bg-surface-2 px-4 py-2 text-sm text-text-secondary transition hover:text-text-primary"
              >
                <Download className="h-4 w-4 text-accent" /> Export Latest
              </button>
            </div>
          </div>
        </header>

        <main className="grid gap-8 lg:grid-cols-[350px,minmax(0,1fr)]">
          <aside className="space-y-6 rounded-3xl bg-surface-1/80 p-6 shadow-layer ring-1 ring-border">
            <SectionHeader
              title="Input Controls"
              description="Fine-tune valuation parameters"
              icon={<Gauge className="h-5 w-5" />}
            />
            <form className="space-y-5" onSubmit={handleSubmit}>
              <div>
                <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">Ticker</label>
                <input
                  className="mt-2 w-full rounded-2xl border border-border bg-surface-2 px-4 py-3 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-subtle"
                  value={formState.ticker}
                  onChange={handleChange('ticker')}
                  placeholder="AAPL"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">Risk-free Rate</label>
                  <input
                    type="number"
                    step="0.1"
                    min={0}
                    className="mt-2 w-full rounded-2xl border border-border bg-surface-2 px-4 py-3 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-subtle"
                    value={formState.riskFreeRate}
                    onChange={handleChange('riskFreeRate')}
                  />
                </div>
                <div>
                  <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">Market Premium</label>
                  <input
                    type="number"
                    step="0.1"
                    min={0}
                    className="mt-2 w-full rounded-2xl border border-border bg-surface-2 px-4 py-3 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-subtle"
                    value={formState.marketRiskPremium}
                    onChange={handleChange('marketRiskPremium')}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">Terminal Growth</label>
                  <input
                    type="number"
                    step="0.1"
                    className="mt-2 w-full rounded-2xl border border-border bg-surface-2 px-4 py-3 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-subtle"
                    value={formState.terminalGrowthRate}
                    onChange={handleChange('terminalGrowthRate')}
                  />
                </div>
                <div>
                  <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">Projection Years</label>
                  <input
                    type="number"
                    min={3}
                    max={10}
                    className="mt-2 w-full rounded-2xl border border-border bg-surface-2 px-4 py-3 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-subtle"
                    value={formState.projectionYears}
                    onChange={handleChange('projectionYears')}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">FCF Growth Trajectory</label>
                <div className="grid grid-cols-2 gap-2">
                  {formState.growthRates.map((rate, index) => (
                    <div key={index} className="rounded-2xl border border-border bg-surface-2/90 p-3 text-sm">
                      <div className="text-[10px] uppercase tracking-[0.22em] text-text-tertiary">Year {index + 1}</div>
                      <input
                        type="number"
                        step="0.5"
                        min={-20}
                        max={50}
                        value={rate}
                        onChange={(event) => handleGrowthRateChange(index, Number(event.target.value))}
                        className="mt-2 w-full rounded-xl border border-border bg-surface-3 px-3 py-2 text-sm text-text-primary outline-none focus:border-accent"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-[11px] uppercase tracking-[0.28em] text-text-tertiary">Peer Set</label>
                <input
                  className="mt-2 w-full rounded-2xl border border-border bg-surface-2 px-4 py-3 text-sm text-text-primary outline-none transition focus:border-accent focus:ring-2 focus:ring-accent-subtle"
                  value={formState.peerInput}
                  onChange={handleChange('peerInput')}
                  placeholder="MSFT,GOOGL,AMZN"
                />
                <p className="mt-2 text-xs text-text-secondary">Comma-separated tickers for trading comps.</p>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-highlight px-4 py-3 text-sm font-medium text-surface-0 shadow-layer transition hover:bg-highlight/90 disabled:opacity-60"
              >
                <LineChart className="h-4 w-4" /> {isLoading ? 'Running Analysis…' : 'Run Analysis'}
              </button>
              {error && <p className="text-sm text-danger">{error}</p>}
            </form>
          </aside>

          <section className="space-y-10">
            {!data && (
              <div className="rounded-3xl border border-dashed border-border/60 bg-surface-1/70 p-16 text-center text-text-secondary">
                <p className="text-lg font-medium text-text-primary">Submit parameters to generate a full valuation stack.</p>
                <p className="mt-2 text-sm">The engine synthesises WACC, DCF, and trading comparables in seconds.</p>
              </div>
            )}

            {data && (
              <div className="space-y-10">
                <div>
                  <SectionHeader
                    title={`Company Overview · ${data.company.name}`}
                    description={`${data.company.sector ?? 'Sector N/A'} · ${data.company.industry ?? 'Industry N/A'}`}
                    icon={<Factory className="h-5 w-5" />}
                    actions={<div className="text-xs text-text-tertiary">Updated {new Date().toLocaleDateString()}</div>}
                  />
                  <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
                    <MetricCard
                      title="Market Capitalisation"
                      value={formatCurrency(data.company.metrics.market_cap)}
                      subtitle="Latest reported"
                      icon={<Building2 className="h-5 w-5" />}
                    />
                    <MetricCard
                      title="Revenue"
                      value={formatCurrency(data.company.metrics.revenue)}
                      subtitle="Trailing twelve months"
                      icon={<BarChart2 className="h-5 w-5" />}
                    />
                    <MetricCard
                      title="EBITDA"
                      value={formatCurrency(data.company.metrics.ebitda)}
                      subtitle="Last fiscal year"
                      icon={<PieChart className="h-5 w-5" />}
                    />
                    <MetricCard
                      title="Beta"
                      value={data.company.metrics.beta?.toFixed(2) ?? '—'}
                      subtitle="Systematic risk"
                      icon={<Gauge className="h-5 w-5" />}
                    />
                  </div>
                </div>

                <div>
                  <SectionHeader
                    title="Valuation Highlights"
                    description="Weighted capital costs, intrinsic value, and variance"
                    icon={<TrendingUp className="h-5 w-5" />}
                  />
                  <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
                    <MetricCard
                      title="Weighted Average Cost of Capital"
                      value={formatPercent(data.wacc.wacc)}
                      subtitle={`Equity ${formatPercent(data.wacc.equity_weight)} · Debt ${formatPercent(data.wacc.debt_weight)}`}
                      icon={<LineChart className="h-5 w-5" />}
                    />
                    <MetricCard
                      title="Implied Fair Value"
                      value={formatCurrency(data.dcf.fair_value_share_price)}
                      subtitle={`Equity value ${formatCurrency(data.dcf.equity_value)}`}
                      icon={<DollarSign className="h-5 w-5" />}
                    />
                    <MetricCard
                      title="Enterprise Value"
                      value={formatCurrency(data.dcf.enterprise_value)}
                      subtitle={`PV of FCFs ${formatCurrency(data.dcf.pv_of_fcfs)}`}
                      icon={<BarChart2 className="h-5 w-5" />}
                    />
                    <MetricCard
                      title="Terminal Value Weight"
                      value={formatPercent(data.dcf.pv_of_terminal_value / (data.dcf.enterprise_value || 1), 1)}
                      subtitle={`Terminal ${formatCurrency(data.dcf.pv_of_terminal_value)}`}
                      icon={<PieChart className="h-5 w-5" />}
                    />
                  </div>
                </div>

                <div className="grid gap-6 xl:grid-cols-2">
                  <div className="rounded-3xl bg-surface-1/80 p-6 shadow-layer ring-1 ring-border">
                    <SectionHeader
                      title="Projected Free Cash Flow"
                      description="Forecast horizon and growth trajectory"
                      icon={<LineChart className="h-5 w-5" />}
                    />
                    <div className="h-[280px]">
                      <ResponsiveContainer>
                        <AreaChart data={data.projected_fcfs.map((row) => ({ ...row, fcf: (row.fcf ?? 0) / 1_000_000 }))}>
                          <defs>
                            <linearGradient id="fcfGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#A5B4FC" stopOpacity={0.75} />
                              <stop offset="95%" stopColor="#A5B4FC" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="4 8" stroke="rgba(160,160,160,0.18)" />
                          <XAxis dataKey="year" stroke="#888888" />
                          <YAxis stroke="#888888" tickFormatter={(value) => `${value.toFixed(0)}M`} />
                          <Tooltip
                            contentStyle={{
                              background: '#141414',
                              borderRadius: 16,
                              border: '1px solid rgba(51,51,51,0.6)',
                              color: '#F2F2F2',
                            }}
                            formatter={(value: ValueType) => [`$${Number(value).toFixed(2)}M`, 'FCF'] as [ValueType, NameType]}
                          />
                          <Area type="monotone" dataKey="fcf" stroke="#A5B4FC" fillOpacity={1} fill="url(#fcfGradient)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="rounded-3xl bg-surface-1/80 p-6 shadow-layer ring-1 ring-border">
                    <SectionHeader
                      title="Discounted Cash Flows"
                      description="Present value contribution by period"
                      icon={<BarChart2 className="h-5 w-5" />}
                    />
                    <div className="h-[280px]">
                      <ResponsiveContainer>
                        <BarChart data={data.discounted_fcfs.map((row) => ({ ...row, pv_of_fcf: (row.pv_of_fcf ?? 0) / 1_000_000 }))}>
                          <CartesianGrid strokeDasharray="3 6" stroke="rgba(160,160,160,0.18)" />
                          <XAxis dataKey="year" stroke="#888888" />
                          <YAxis stroke="#888888" tickFormatter={(value) => `${value.toFixed(0)}M`} />
                          <Tooltip
                            contentStyle={{
                              background: '#141414',
                              borderRadius: 16,
                              border: '1px solid rgba(51,51,51,0.6)',
                              color: '#F2F2F2',
                            }}
                            formatter={(value: ValueType) => [`$${Number(value).toFixed(2)}M`, 'PV of FCF'] as [ValueType, NameType]}
                          />
                          <Bar dataKey="pv_of_fcf" radius={[10, 10, 4, 4]} fill="#FFD600" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="rounded-3xl bg-surface-1/80 p-6 shadow-layer ring-1 ring-border">
                  <SectionHeader
                    title="Trading Comparables"
                    description="Peer set positioning across key multiples"
                    icon={<Users className="h-5 w-5" />}
                  />

                  {peerTableRows.length === 0 ? (
                    <p className="text-sm text-text-secondary">No peer multiples available for the selected tickers.</p>
                  ) : (
                    <div className="overflow-hidden rounded-2xl ring-1 ring-border/80">
                      <table className="w-full border-collapse text-sm">
                        <thead className="bg-surface-2 text-xs uppercase tracking-[0.22em] text-text-tertiary">
                          <tr>
                            <th className="px-4 py-3 text-left">Ticker</th>
                            <th className="px-4 py-3 text-left">EV/EBITDA</th>
                            <th className="px-4 py-3 text-left">P/E</th>
                            <th className="px-4 py-3 text-left">EV/Revenue</th>
                            <th className="px-4 py-3 text-left">P/S</th>
                          </tr>
                        </thead>
                        <tbody>
                          {peerTableRows.map((row) => {
                            const ticker = String(row.Ticker ?? row['Ticker'] ?? '—')
                            return (
                              <tr key={ticker} className="odd:bg-white/5">
                                <td className="px-4 py-3 font-medium text-text-primary">{ticker}</td>
                                <td className="px-4 py-3 text-text-secondary">{formatMultiple(row['EV/EBITDA'])}</td>
                                <td className="px-4 py-3 text-text-secondary">{formatMultiple(row['P/E'])}</td>
                                <td className="px-4 py-3 text-text-secondary">{formatMultiple(row['EV/Revenue'])}</td>
                                <td className="px-4 py-3 text-text-secondary">{formatMultiple(row['P/S'])}</td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                <div className="rounded-3xl bg-surface-1/80 p-6 shadow-layer ring-1 ring-border">
                  <SectionHeader
                    title="Equity Performance"
                    description="Trailing price action"
                    icon={<LineChart className="h-5 w-5" />}
                  />
                  <div className="h-[260px]">
                    <ResponsiveContainer>
                      <AreaChart data={data.historical_prices.map((point) => ({ ...point, close: point.close }))}>
                        <defs>
                          <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#7B7FFF" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#7B7FFF" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="4 8" stroke="rgba(160,160,160,0.12)" />
                        <XAxis dataKey="date" stroke="#888888" hide tickFormatter={(value) => value.slice(0, 10)} />
                        <YAxis stroke="#888888" domain={['auto', 'auto']} tickFormatter={(value) => `$${value.toFixed(0)}`} />
                        <Tooltip
                          contentStyle={{
                            background: '#141414',
                            borderRadius: 16,
                            border: '1px solid rgba(51,51,51,0.6)',
                            color: '#F2F2F2',
                          }}
                          labelFormatter={(label) => new Date(label).toLocaleDateString()}
                          formatter={(value: number) => [`$${value.toFixed(2)}`, 'Close']}
                        />
                        <Area type="monotone" dataKey="close" stroke="#7B7FFF" fillOpacity={1} fill="url(#priceGradient)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
          </section>
        </main>
      </div>
    </div>
  )
}

export default App
