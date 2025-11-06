import type { ReactNode } from 'react'

interface SectionHeaderProps {
    title: string
    description?: string
    icon?: ReactNode
    actions?: ReactNode
}

export function SectionHeader({ title, description, icon, actions }: SectionHeaderProps) {
    return (
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
                {icon && (
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent-muted text-accent shadow-glow">
                        {icon}
                    </div>
                )}
                <div>
                    <h3 className="text-lg font-medium text-text-primary">{title}</h3>
                    {description && <p className="text-sm text-text-secondary">{description}</p>}
                </div>
            </div>
            {actions && <div className="flex items-center gap-3 text-xs text-text-secondary">{actions}</div>}
        </div>
    )
}
