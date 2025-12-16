import { useState, useEffect, useRef } from 'react';
import { ingestionAPI } from '../api/client';
import MetricCard from '../components/MetricCard';

export default function LiveData() {
    const [prices, setPrices] = useState({});
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [ticks, setTicks] = useState([]);
    const [refreshRate, setRefreshRate] = useState(1000);
    const selectedSymbolRef = useRef(selectedSymbol);

    // Keep ref in sync with state
    useEffect(() => {
        selectedSymbolRef.current = selectedSymbol;
    }, [selectedSymbol]);

    useEffect(() => {
        const fetchPrices = async () => {
            try {
                const response = await ingestionAPI.getLatestPrices();
                setPrices(response.data.prices || {});
                // Only set default if no symbol is selected (use ref to get current value)
                if (!selectedSymbolRef.current && Object.keys(response.data.prices || {}).length > 0) {
                    setSelectedSymbol(Object.keys(response.data.prices)[0]);
                }
            } catch (error) {
                console.error('Failed to fetch prices:', error);
            }
        };

        fetchPrices();
        const interval = setInterval(fetchPrices, refreshRate);
        return () => clearInterval(interval);
    }, [refreshRate]);

    useEffect(() => {
        if (!selectedSymbol) return;

        const fetchTicks = async () => {
            try {
                const response = await ingestionAPI.getBuffer(selectedSymbol, 50);
                setTicks(response.data.ticks || []);
            } catch (error) {
                console.error('Failed to fetch ticks:', error);
            }
        };

        fetchTicks();
        const interval = setInterval(fetchTicks, refreshRate);
        return () => clearInterval(interval);
    }, [selectedSymbol, refreshRate]);

    const symbols = Object.keys(prices);

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold text-primary">📊 Live Data</h1>
                <select
                    value={refreshRate}
                    onChange={(e) => setRefreshRate(Number(e.target.value))}
                    className="select-field"
                >
                    <option value={1000}>Refresh: 1s</option>
                    <option value={5000}>Refresh: 5s</option>
                    <option value={10000}>Refresh: 10s</option>
                </select>
            </div>

            {symbols.length === 0 ? (
                <div className="glass-card p-8 text-center">
                    <p className="text-gray-400 text-lg">No live data available.</p>
                    <p className="text-gray-500 mt-2">Start ingestion to see live prices.</p>
                </div>
            ) : (
                <>
                    {/* Price Cards */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        {symbols.map(symbol => (
                            <MetricCard
                                key={symbol}
                                label={symbol}
                                value={`$${prices[symbol]?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                            />
                        ))}
                    </div>

                    {/* Recent Ticks */}
                    <section className="glass-card p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-semibold text-primary">Recent Ticks</h2>
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

                        {ticks.length === 0 ? (
                            <p className="text-gray-400">No tick data available yet</p>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-white/10">
                                            <th className="text-left py-3 px-4 text-gray-400 font-medium">Timestamp</th>
                                            <th className="text-left py-3 px-4 text-gray-400 font-medium">Symbol</th>
                                            <th className="text-right py-3 px-4 text-gray-400 font-medium">Price</th>
                                            <th className="text-right py-3 px-4 text-gray-400 font-medium">Size</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {ticks.slice(0, 20).map((tick, index) => (
                                            <tr key={index} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                                <td className="py-2 px-4 text-gray-300 text-sm">
                                                    {new Date(tick.timestamp).toLocaleTimeString()}
                                                </td>
                                                <td className="py-2 px-4 text-white font-medium">{tick.symbol}</td>
                                                <td className="py-2 px-4 text-primary text-right font-mono">
                                                    ${tick.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                </td>
                                                <td className="py-2 px-4 text-gray-300 text-right font-mono">
                                                    {tick.size?.toFixed(4)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </section>
                </>
            )}
        </div>
    );
}
