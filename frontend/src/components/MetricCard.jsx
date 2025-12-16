export default function MetricCard({ label, value, delta, deltaLabel, icon, colorClass = '' }) {
    const isPositive = delta && delta > 0;
    const isNegative = delta && delta < 0;

    return (
        <div className="glass-card-hover p-5">
            <div className="flex items-center justify-between mb-3">
                <span className="metric-label">{label}</span>
                {icon && <span className="text-lg opacity-70">{icon}</span>}
            </div>
            <div className={`metric-value ${colorClass}`}>
                {value}
            </div>
            {(delta !== undefined || deltaLabel) && (
                <div className={`text-sm mt-2 font-medium ${isPositive ? 'text-emerald-400' : isNegative ? 'text-rose-400' : 'text-slate-400'}`}>
                    {delta !== undefined && (
                        <span>{isPositive ? '↑ ' : isNegative ? '↓ ' : ''}{typeof delta === 'number' ? Math.abs(delta).toFixed(2) : delta}</span>
                    )}
                    {deltaLabel && <span className="ml-1 text-slate-500">{deltaLabel}</span>}
                </div>
            )}
        </div>
    );
}
