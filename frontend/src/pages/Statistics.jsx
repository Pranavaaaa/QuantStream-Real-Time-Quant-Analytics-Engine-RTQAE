import { useState, useEffect, useRef } from 'react';
import { analyticsAPI } from '../api/client';
import MetricCard from '../components/MetricCard';

export default function Statistics() {
    const [allStats, setAllStats] = useState({});
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [zscoreData, setZscoreData] = useState(null);
    const selectedSymbolRef = useRef(selectedSymbol);

    // Keep ref in sync with state
    useEffect(() => {
        selectedSymbolRef.current = selectedSymbol;
    }, [selectedSymbol]);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await analyticsAPI.getAllStats();
                setAllStats(response.data || {});
                // Only set default if no symbol is selected (use ref to get current value)
                if (!selectedSymbolRef.current && Object.keys(response.data || {}).length > 0) {
                    setSelectedSymbol(Object.keys(response.data)[0]);
                }
            } catch (error) {
                console.error('Failed to fetch stats:', error);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 2000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        if (!selectedSymbol) return;

        const fetchZScore = async () => {
            try {
                const response = await analyticsAPI.getZScore(selectedSymbol);
                setZscoreData(response.data);
            } catch (error) {
                console.error('Failed to fetch z-score:', error);
            }
        };

        fetchZScore();
        const interval = setInterval(fetchZScore, 2000);
        return () => clearInterval(interval);
    }, [selectedSymbol]);

    const symbols = Object.keys(allStats);
    const stats = selectedSymbol ? allStats[selectedSymbol] : null;
    const zscore = zscoreData?.zscore || 0;

    const getZScoreColor = (z) => {
        const absZ = Math.abs(z);
        if (absZ > 3) return { emoji: '🔴', color: 'text-red-400', label: 'Extreme' };
        if (absZ > 2) return { emoji: '🟠', color: 'text-orange-400', label: 'High' };
        if (absZ > 1) return { emoji: '🟡', color: 'text-yellow-400', label: 'Moderate' };
        return { emoji: '🟢', color: 'text-green-400', label: 'Normal' };
    };

    const zInfo = getZScoreColor(zscore);

    if (symbols.length === 0) {
        return (
            <div className="animate-fade-in">
                <h1 className="text-3xl font-bold text-primary mb-6">📈 Statistics</h1>
                <div className="glass-card p-8 text-center">
                    <p className="text-gray-400 text-lg">No statistics available yet.</p>
                    <p className="text-gray-500 mt-2">Start ingestion to generate statistics.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold text-primary">📈 Statistics</h1>
                <select
                    value={selectedSymbol}
                    onChange={(e) => setSelectedSymbol(e.target.value)}
                    className="select-field"
                >
                    {symbols.map(symbol => (
                        <option key={symbol} value={symbol}>{symbol}</option>
                    ))}
                </select>
            </div>

            {stats && (
                <>
                    {/* Price Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <MetricCard
                            label="Current Price"
                            value={`$${stats.current_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                            delta={stats.mean ? ((stats.current_price - stats.mean) / stats.mean * 100) : 0}
                            deltaLabel="vs mean"
                        />
                        <MetricCard
                            label="Mean"
                            value={`$${stats.mean?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                        />
                        <MetricCard
                            label="Std Dev"
                            value={`$${stats.std?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                        />
                        <MetricCard
                            label={`Z-Score ${zInfo.emoji}`}
                            value={zscore.toFixed(3)}
                            colorClass={zInfo.color}
                        />
                    </div>

                    {/* Second Row */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <MetricCard
                            label="VWAP"
                            value={`$${stats.vwap?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                        />
                        <MetricCard
                            label="Min"
                            value={`$${stats.min?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                        />
                        <MetricCard
                            label="Max"
                            value={`$${stats.max?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                        />
                        <MetricCard
                            label="Price Change"
                            value={`${stats.price_change_pct >= 0 ? '+' : ''}${stats.price_change_pct?.toFixed(2)}%`}
                            delta={stats.price_change}
                            colorClass={stats.price_change_pct >= 0 ? 'text-green-400' : 'text-red-400'}
                        />
                    </div>

                    {/* Volume Metrics */}
                    <section className="glass-card p-6 mb-6">
                        <h2 className="text-xl font-semibold text-primary mb-4">Volume Metrics</h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <MetricCard
                                label="Total Volume"
                                value={stats.total_volume?.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })}
                            />
                            <MetricCard
                                label="Avg Volume"
                                value={stats.avg_volume?.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })}
                            />
                            <MetricCard
                                label="Volume Std Dev"
                                value={stats.volume_std?.toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })}
                            />
                        </div>
                    </section>

                    {/* Advanced Metrics */}
                    {stats.volatility !== undefined && (
                        <section className="glass-card p-6">
                            <h2 className="text-xl font-semibold text-primary mb-4">Advanced Metrics</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <MetricCard
                                    label="Volatility (Annualized)"
                                    value={stats.volatility?.toFixed(4)}
                                />
                                <MetricCard
                                    label="Sample Size"
                                    value={`${stats.count?.toLocaleString()} ticks`}
                                />
                            </div>
                        </section>
                    )}
                </>
            )}
        </div>
    );
}
