import type { ReactNode } from 'react'
import clsx from 'classnames'

interface MetricCardProps {
    title: string
    value: ReactNode
    subtitle?: string
    icon?: ReactNode
    trend?: ReactNode
    className?: string
}

export function MetricCard({ title, value, subtitle, icon, trend, className }: MetricCardProps) {
    return (
        <div
            className={clsx(
                'relative overflow-hidden rounded-xl bg-surface-2/90 px-5 py-6 shadow-layer ring-1 ring-white/5 transition-colors hover:bg-surface-2',
                className,
            )}
        >
            <div className="flex items-start justify-between gap-4">
                <div>
                    <div className="text-[11px] uppercase tracking-[0.24em] text-text-tertiary">{title}</div>
                    <div className="mt-3 text-3xl font-semibold text-text-primary">{value}</div>
                    {subtitle && <div className="mt-3 text-sm text-text-secondary">{subtitle}</div>}
                    {trend && <div className="mt-3 text-sm font-medium text-highlight">{trend}</div>}
                </div>
                {icon && (
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent-muted text-accent">
                        {icon}
                    </div>
                )}
            </div>
        </div>
    )
}
