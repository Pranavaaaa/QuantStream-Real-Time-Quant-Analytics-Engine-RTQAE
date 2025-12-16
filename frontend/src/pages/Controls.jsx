import { useState, useEffect } from 'react';
import { ingestionAPI } from '../api/client';

const AVAILABLE_SYMBOLS = [
    { symbol: 'BTCUSDT', name: 'Bitcoin', icon: '₿' },
    { symbol: 'ETHUSDT', name: 'Ethereum', icon: 'Ξ' },
    { symbol: 'BNBUSDT', name: 'BNB', icon: '◆' },
    { symbol: 'SOLUSDT', name: 'Solana', icon: '◎' },
    { symbol: 'ADAUSDT', name: 'Cardano', icon: '₳' },
    { symbol: 'XRPUSDT', name: 'XRP', icon: '✕' },
    { symbol: 'DOGEUSDT', name: 'Dogecoin', icon: 'Ð' },
    { symbol: 'MATICUSDT', name: 'Polygon', icon: '⬡' },
    { symbol: 'DOTUSDT', name: 'Polkadot', icon: '●' },
    { symbol: 'AVAXUSDT', name: 'Avalanche', icon: '▲' },
];

export default function Controls() {
    const [selectedSymbols, setSelectedSymbols] = useState(['BTCUSDT', 'ETHUSDT']);
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [windowSize, setWindowSize] = useState(100);
    const [zscoreThreshold, setZscoreThreshold] = useState(3.0);

    const fetchStatus = async () => {
        try {
            const response = await ingestionAPI.getStatus();
            setStatus(response.data);
        } catch (error) {
            console.error('Failed to fetch status:', error);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 3000);
        return () => clearInterval(interval);
    }, []);

    const handleSymbolToggle = (symbol) => {
        setSelectedSymbols(prev =>
            prev.includes(symbol)
                ? prev.filter(s => s !== symbol)
                : [...prev, symbol]
        );
    };

    const handleSelectAll = () => {
        setSelectedSymbols(AVAILABLE_SYMBOLS.map(s => s.symbol));
    };

    const handleClearAll = () => {
        setSelectedSymbols([]);
    };

    const handleStart = async () => {
        if (selectedSymbols.length === 0) {
            setMessage({ type: 'error', text: 'Please select at least one symbol' });
            return;
        }
        setLoading(true);
        setMessage(null);
        try {
            await ingestionAPI.start(selectedSymbols);
            setMessage({ type: 'success', text: `Started ingestion for ${selectedSymbols.join(', ')}` });
            fetchStatus();
        } catch (error) {
            setMessage({ type: 'error', text: `Failed to start: ${error.message}` });
        }
        setLoading(false);
    };

    const handleStop = async () => {
        setLoading(true);
        setMessage(null);
        try {
            await ingestionAPI.stop();
            setMessage({ type: 'success', text: 'Ingestion stopped successfully' });
            fetchStatus();
        } catch (error) {
            setMessage({ type: 'error', text: `Failed to stop: ${error.message}` });
        }
        setLoading(false);
    };

    return (
        <div className="animate-fade-in space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-primary mb-2">⚙️ Controls</h1>
                <p className="text-slate-400">Manage data ingestion and configure analytics settings</p>
            </div>

            {/* Message Alert */}
            {message && (
                <div className={`p-4 rounded-xl flex items-center gap-3 ${message.type === 'success'
                        ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
                        : 'bg-rose-500/10 border border-rose-500/30 text-rose-400'
                    }`}>
                    <span className="text-xl">{message.type === 'success' ? '✓' : '✕'}</span>
                    <span className="font-medium">{message.text}</span>
                </div>
            )}

            {/* Symbol Selection */}
            <section className="glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="section-title">
                        <span>📊</span>
                        <span>Symbol Selection</span>
                        <span className="ml-2 px-2.5 py-0.5 bg-indigo-500/20 text-indigo-300 text-sm rounded-full font-medium">
                            {selectedSymbols.length} selected
                        </span>
                    </h2>
                    <div className="flex gap-2">
                        <button onClick={handleSelectAll} className="btn-secondary text-sm py-2">
                            Select All
                        </button>
                        <button onClick={handleClearAll} className="btn-secondary text-sm py-2">
                            Clear All
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                    {AVAILABLE_SYMBOLS.map(({ symbol, name, icon }) => {
                        const isSelected = selectedSymbols.includes(symbol);
                        return (
                            <button
                                key={symbol}
                                onClick={() => handleSymbolToggle(symbol)}
                                className={`relative p-4 rounded-xl transition-all duration-200 text-left group ${isSelected
                                        ? 'bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border-2 border-indigo-500 shadow-lg shadow-indigo-500/10'
                                        : 'bg-white/[0.03] border-2 border-transparent hover:border-indigo-500/30 hover:bg-white/[0.05]'
                                    }`}
                            >
                                {/* Checkmark indicator */}
                                <div className={`absolute top-2 right-2 w-5 h-5 rounded-full flex items-center justify-center transition-all ${isSelected
                                        ? 'bg-indigo-500 scale-100'
                                        : 'bg-white/10 scale-75 opacity-0 group-hover:opacity-100 group-hover:scale-100'
                                    }`}>
                                    {isSelected && <span className="text-white text-xs">✓</span>}
                                </div>

                                {/* Icon */}
                                <div className={`text-2xl mb-2 transition-colors ${isSelected ? 'text-indigo-400' : 'text-slate-500'}`}>
                                    {icon}
                                </div>

                                {/* Symbol name */}
                                <div className={`font-bold text-sm mb-0.5 transition-colors ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                                    {symbol.replace('USDT', '')}
                                </div>

                                {/* Full name */}
                                <div className="text-xs text-slate-500 truncate">
                                    {name}
                                </div>
                            </button>
                        );
                    })}
                </div>
            </section>

            {/* Ingestion Controls */}
            <section className="glass-card p-6">
                <h2 className="section-title">
                    <span>🚀</span>
                    <span>Data Ingestion</span>
                </h2>
                <div className="flex flex-wrap gap-3">
                    <button
                        onClick={handleStart}
                        disabled={loading || status?.running}
                        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {loading && !status?.running ? (
                            <>
                                <span className="animate-spin">⏳</span>
                                <span>Starting...</span>
                            </>
                        ) : (
                            <>
                                <span>▶️</span>
                                <span>Start Ingestion</span>
                            </>
                        )}
                    </button>

                    <button
                        onClick={handleStop}
                        disabled={loading || !status?.running}
                        className="btn-danger disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {loading && status?.running ? (
                            <>
                                <span className="animate-spin">⏳</span>
                                <span>Stopping...</span>
                            </>
                        ) : (
                            <>
                                <span>⏸️</span>
                                <span>Stop Ingestion</span>
                            </>
                        )}
                    </button>

                    <button
                        onClick={fetchStatus}
                        className="btn-secondary flex items-center gap-2"
                    >
                        <span>🔄</span>
                        <span>Refresh</span>
                    </button>
                </div>
            </section>

            {/* Status Display */}
            <section className="glass-card p-6">
                <h2 className="section-title">
                    <span>📡</span>
                    <span>Ingestion Status</span>
                </h2>

                {status ? (
                    <div className="space-y-4">
                        {/* Status badge */}
                        <div className={`inline-flex items-center gap-3 px-4 py-2.5 rounded-xl ${status.running
                                ? 'bg-emerald-500/10 border border-emerald-500/30'
                                : 'bg-amber-500/10 border border-amber-500/30'
                            }`}>
                            <span className={`status-dot ${status.running ? 'status-dot-success' : 'status-dot-warning'}`}></span>
                            <span className={`font-semibold ${status.running ? 'text-emerald-400' : 'text-amber-400'}`}>
                                {status.running ? 'Ingestion Running' : 'Ingestion Stopped'}
                            </span>
                        </div>

                        {status.running && (
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                                <div className="p-4 bg-white/[0.03] rounded-xl">
                                    <div className="text-xs text-slate-500 uppercase tracking-wide mb-1">Symbols</div>
                                    <div className="text-lg font-semibold text-white">{status.symbols?.length || 0}</div>
                                </div>
                                <div className="p-4 bg-white/[0.03] rounded-xl">
                                    <div className="text-xs text-slate-500 uppercase tracking-wide mb-1">Connected</div>
                                    <div className="text-lg font-semibold text-emerald-400">{status.connected_symbols?.length || 0}</div>
                                </div>
                                <div className="p-4 bg-white/[0.03] rounded-xl">
                                    <div className="text-xs text-slate-500 uppercase tracking-wide mb-1">Total Ticks</div>
                                    <div className="text-lg font-semibold text-indigo-400">{status.tick_count?.toLocaleString() || 0}</div>
                                </div>
                                <div className="p-4 bg-white/[0.03] rounded-xl">
                                    <div className="text-xs text-slate-500 uppercase tracking-wide mb-1">Buffered</div>
                                    <div className="text-lg font-semibold text-violet-400">{status.buffer_stats?.total_ticks?.toLocaleString() || 0}</div>
                                </div>
                            </div>
                        )}

                        {status.running && status.symbols && (
                            <div className="flex flex-wrap gap-2 mt-2">
                                {status.symbols.map(sym => (
                                    <span key={sym} className="px-3 py-1.5 bg-indigo-500/15 border border-indigo-500/30 rounded-full text-sm text-indigo-300 font-medium">
                                        {sym.toUpperCase()}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="flex items-center gap-3 text-slate-400">
                        <span className="animate-spin">⏳</span>
                        <span>Loading status...</span>
                    </div>
                )}
            </section>

            {/* Analytics Settings */}
            <section className="glass-card p-6">
                <h2 className="section-title">
                    <span>⚡</span>
                    <span>Analytics Settings</span>
                </h2>

                <div className="grid md:grid-cols-2 gap-8">
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <label className="text-slate-300 font-medium">Window Size</label>
                            <span className="px-3 py-1 bg-indigo-500/20 rounded-lg text-indigo-300 font-mono font-semibold">
                                {windowSize} ticks
                            </span>
                        </div>
                        <input
                            type="range"
                            min="50"
                            max="500"
                            step="50"
                            value={windowSize}
                            onChange={(e) => setWindowSize(Number(e.target.value))}
                            className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer 
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 
                         [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r 
                         [&::-webkit-slider-thumb]:from-indigo-500 [&::-webkit-slider-thumb]:to-violet-500
                         [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:shadow-indigo-500/30
                         [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-transform
                         [&::-webkit-slider-thumb]:hover:scale-110"
                        />
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                            <span>50</span>
                            <span>500</span>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <label className="text-slate-300 font-medium">Z-Score Threshold</label>
                            <span className="px-3 py-1 bg-violet-500/20 rounded-lg text-violet-300 font-mono font-semibold">
                                {zscoreThreshold.toFixed(1)}σ
                            </span>
                        </div>
                        <input
                            type="range"
                            min="1"
                            max="5"
                            step="0.5"
                            value={zscoreThreshold}
                            onChange={(e) => setZscoreThreshold(Number(e.target.value))}
                            className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer 
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 
                         [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r 
                         [&::-webkit-slider-thumb]:from-violet-500 [&::-webkit-slider-thumb]:to-purple-500
                         [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:shadow-violet-500/30
                         [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:transition-transform
                         [&::-webkit-slider-thumb]:hover:scale-110"
                        />
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                            <span>1.0</span>
                            <span>5.0</span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
