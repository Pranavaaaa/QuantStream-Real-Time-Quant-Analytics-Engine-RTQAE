import { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import { analyticsAPI, exportAPI } from '../api/client';
import MetricCard from '../components/MetricCard';

export default function Analytics() {
    const [activeTab, setActiveTab] = useState('price');
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [timeframe, setTimeframe] = useState('1m');
    const selectedSymbolRef = useRef(selectedSymbol);

    // Keep ref in sync with state
    useEffect(() => {
        selectedSymbolRef.current = selectedSymbol;
    }, [selectedSymbol]);

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const response = await analyticsAPI.getSummary();
                const syms = response.data.symbols || [];
                setSymbols(syms);
                // Only set default if no symbol is selected (use ref for current value)
                if (!selectedSymbolRef.current && syms.length > 0) {
                    setSelectedSymbol(syms[0]);
                }
            } catch (error) {
                console.error('Failed to fetch summary:', error);
            }
        };

        fetchSummary();
        const interval = setInterval(fetchSummary, 5000);
        return () => clearInterval(interval);
    }, []);

    const tabs = [
        { id: 'price', label: '📊 Live Price', icon: '📊' },
        { id: 'zscore', label: '📉 Z-Score', icon: '📉' },
        { id: 'correlation', label: '🔗 Correlation', icon: '🔗' },
        { id: 'pairs', label: '📈 Spread Analysis', icon: '📈' },
        { id: 'adf', label: '🧪 ADF Test', icon: '🧪' },
    ];

    if (symbols.length === 0) {
        return (
            <div className="animate-fade-in">
                <h1 className="text-3xl font-bold text-primary mb-6">📉 Analytics</h1>
                <div className="glass-card p-8 text-center">
                    <p className="text-gray-400 text-lg">No analytics data available yet.</p>
                    <p className="text-gray-500 mt-2">Start ingestion to generate analytics.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-primary mb-6">📉 Analytics</h1>

            {/* Tabs */}
            <div className="flex flex-wrap gap-2 mb-6 border-b border-white/10 pb-4">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={activeTab === tab.id ? 'tab-button-active' : 'tab-button'}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'price' && (
                <PriceChart
                    symbols={symbols}
                    selectedSymbol={selectedSymbol}
                    setSelectedSymbol={setSelectedSymbol}
                    timeframe={timeframe}
                    setTimeframe={setTimeframe}
                />
            )}
            {activeTab === 'zscore' && (
                <ZScoreChart
                    symbols={symbols}
                    selectedSymbol={selectedSymbol}
                    setSelectedSymbol={setSelectedSymbol}
                />
            )}
            {activeTab === 'correlation' && <CorrelationChart symbols={symbols} />}
            {activeTab === 'pairs' && <PairsTrading symbols={symbols} />}
            {activeTab === 'adf' && (
                <ADFTest
                    symbols={symbols}
                    selectedSymbol={selectedSymbol}
                    setSelectedSymbol={setSelectedSymbol}
                />
            )}
        </div>
    );
}

function PriceChart({ symbols, selectedSymbol, setSelectedSymbol, timeframe, setTimeframe }) {
    const [ohlcv, setOhlcv] = useState([]);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        if (!selectedSymbol) return;

        const fetchData = async () => {
            try {
                const [ohlcvRes, statsRes] = await Promise.all([
                    exportAPI.getOHLCV(selectedSymbol, timeframe, 100),
                    analyticsAPI.getStats(selectedSymbol)
                ]);
                setOhlcv(ohlcvRes.data.ohlcv || []);
                setStats(statsRes.data);
            } catch (error) {
                console.error('Failed to fetch data:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, [selectedSymbol, timeframe]);

    const candlestickData = {
        x: ohlcv.map(d => new Date(d.timestamp)),
        open: ohlcv.map(d => d.open),
        high: ohlcv.map(d => d.high),
        low: ohlcv.map(d => d.low),
        close: ohlcv.map(d => d.close),
        type: 'candlestick',
        name: selectedSymbol,
    };

    const volumeData = {
        x: ohlcv.map(d => new Date(d.timestamp)),
        y: ohlcv.map(d => d.volume),
        type: 'bar',
        name: 'Volume',
        marker: { color: 'rgba(100, 181, 246, 0.7)' },
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap gap-4">
                <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)} className="select-field">
                    {symbols.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)} className="select-field">
                    <option value="1s">1s</option>
                    <option value="1m">1m</option>
                    <option value="5m">5m</option>
                </select>
            </div>

            {ohlcv.length > 0 ? (
                <>
                    <div className="glass-card p-4">
                        <Plot
                            data={[candlestickData]}
                            layout={{
                                title: `${selectedSymbol} Price Chart (${timeframe})`,
                                uirevision: selectedSymbol, // Preserve zoom/pan state when data updates
                                xaxis: { title: 'Time', rangeslider: { visible: false } },
                                yaxis: { title: 'Price (USDT)' },
                                template: 'plotly_dark',
                                paper_bgcolor: 'rgba(0,0,0,0)',
                                plot_bgcolor: 'rgba(0,0,0,0)',
                                font: { color: '#e6edf3' },
                                height: 450,
                            }}
                            style={{ width: '100%' }}
                            config={{ responsive: true }}
                        />
                    </div>

                    <div className="glass-card p-4">
                        <Plot
                            data={[volumeData]}
                            layout={{
                                title: 'Volume',
                                uirevision: selectedSymbol, // Preserve zoom/pan state when data updates
                                xaxis: { title: 'Time' },
                                yaxis: { title: 'Volume' },
                                template: 'plotly_dark',
                                paper_bgcolor: 'rgba(0,0,0,0)',
                                plot_bgcolor: 'rgba(0,0,0,0)',
                                font: { color: '#e6edf3' },
                                height: 250,
                            }}
                            style={{ width: '100%' }}
                            config={{ responsive: true }}
                        />
                    </div>
                </>
            ) : (
                <div className="glass-card p-8 text-center text-gray-400">
                    No OHLCV data available yet. Wait for candles to form.
                </div>
            )}

            {stats && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <MetricCard label="Current Price" value={`$${stats.current_price?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
                    <MetricCard label="Change %" value={`${stats.price_change_pct?.toFixed(2)}%`} delta={stats.price_change_pct} />
                    <MetricCard label="VWAP" value={`$${stats.vwap?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
                    <MetricCard label="Volume" value={stats.total_volume?.toFixed(4)} />
                </div>
            )}
        </div>
    );
}

function ZScoreChart({ symbols, selectedSymbol, setSelectedSymbol }) {
    const [zscoreData, setZscoreData] = useState(null);

    useEffect(() => {
        if (!selectedSymbol) return;

        const fetchData = async () => {
            try {
                const response = await analyticsAPI.getZScore(selectedSymbol);
                setZscoreData(response.data);
            } catch (error) {
                console.error('Failed to fetch z-score:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, [selectedSymbol]);

    const zscore = zscoreData?.zscore || 0;
    const outlierLevel = zscoreData?.outlier_level || 'normal';
    const levelInfo = {
        normal: { emoji: '🟢', color: 'text-green-400' },
        moderate: { emoji: '🟡', color: 'text-yellow-400' },
        high: { emoji: '🟠', color: 'text-orange-400' },
        extreme: { emoji: '🔴', color: 'text-red-400' },
    }[outlierLevel];

    const gaugeData = [{
        type: 'indicator',
        mode: 'gauge+number+delta',
        value: zscore,
        delta: { reference: 0 },
        title: { text: `Z-Score (${selectedSymbol})` },
        gauge: {
            axis: { range: [-5, 5], tickwidth: 1 },
            bar: { color: '#00d4ff' },
            bgcolor: 'rgba(255,255,255,0.1)',
            borderwidth: 2,
            bordercolor: 'gray',
            steps: [
                { range: [-5, -3], color: 'rgba(255, 0, 0, 0.7)' },
                { range: [-3, -2], color: 'rgba(255, 165, 0, 0.7)' },
                { range: [-2, -1], color: 'rgba(255, 255, 0, 0.5)' },
                { range: [-1, 1], color: 'rgba(0, 255, 0, 0.5)' },
                { range: [1, 2], color: 'rgba(255, 255, 0, 0.5)' },
                { range: [2, 3], color: 'rgba(255, 165, 0, 0.7)' },
                { range: [3, 5], color: 'rgba(255, 0, 0, 0.7)' },
            ],
            threshold: { line: { color: 'red', width: 4 }, thickness: 0.75, value: 2 },
        },
    }];

    return (
        <div className="space-y-6">
            <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)} className="select-field">
                {symbols.map(s => <option key={s} value={s}>{s}</option>)}
            </select>

            {zscoreData && (
                <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <MetricCard label="Current Z-Score" value={zscore.toFixed(3)} />
                        <MetricCard label="Outlier Level" value={`${levelInfo.emoji} ${outlierLevel.toUpperCase()}`} colorClass={levelInfo.color} />
                        <MetricCard label="Mean" value={`$${zscoreData.mean?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
                        <MetricCard label="Std Dev" value={`$${zscoreData.std?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
                    </div>

                    <div className="glass-card p-4">
                        <Plot
                            data={gaugeData}
                            layout={{
                                height: 350,
                                template: 'plotly_dark',
                                paper_bgcolor: 'rgba(0,0,0,0)',
                                font: { color: '#e6edf3' },
                            }}
                            style={{ width: '100%' }}
                            config={{ responsive: true }}
                        />
                    </div>

                    <div className={`glass-card p-4 border-l-4 ${Math.abs(zscore) > 3 ? 'border-red-500 bg-red-500/10' : Math.abs(zscore) > 2 ? 'border-orange-500 bg-orange-500/10' : Math.abs(zscore) > 1 ? 'border-yellow-500 bg-yellow-500/10' : 'border-green-500 bg-green-500/10'}`}>
                        <h3 className="font-semibold text-primary mb-2">📝 Interpretation</h3>
                        {Math.abs(zscore) > 3 && <p className="text-red-400">⚠️ <strong>Extreme Outlier!</strong> Price is {Math.abs(zscore).toFixed(2)} standard deviations from the mean.</p>}
                        {Math.abs(zscore) > 2 && Math.abs(zscore) <= 3 && <p className="text-orange-400">⚡ <strong>Significant Deviation</strong> - Price is {Math.abs(zscore).toFixed(2)} sigma from mean. Potential mean reversion opportunity.</p>}
                        {Math.abs(zscore) > 1 && Math.abs(zscore) <= 2 && <p className="text-yellow-400">📊 <strong>Moderate Deviation</strong> - Price is {Math.abs(zscore).toFixed(2)} sigma from mean.</p>}
                        {Math.abs(zscore) <= 1 && <p className="text-green-400">✅ <strong>Normal Range</strong> - Price is within 1 standard deviation of the mean.</p>}
                    </div>
                </>
            )}
        </div>
    );
}

function CorrelationChart({ symbols }) {
    const [matrixData, setMatrixData] = useState(null);
    const [correlations, setCorrelations] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [matrixRes, corrRes] = await Promise.all([
                    analyticsAPI.getCorrelationMatrix(),
                    analyticsAPI.getCorrelation()
                ]);
                setMatrixData(matrixRes.data);
                setCorrelations(corrRes.data.correlations || []);
            } catch (error) {
                console.error('Failed to fetch correlation:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (!matrixData || !matrixData.matrix || matrixData.symbols.length < 2) {
        return (
            <div className="glass-card p-8 text-center text-gray-400">
                Need at least 2 symbols with data for correlation analysis
            </div>
        );
    }

    const heatmapData = [{
        z: matrixData.matrix,
        x: matrixData.symbols,
        y: matrixData.symbols,
        type: 'heatmap',
        colorscale: 'RdYlGn',
        zmid: 0,
        zmin: -1,
        zmax: 1,
        text: matrixData.matrix.map(row => row.map(v => v.toFixed(3))),
        texttemplate: '%{text}',
        colorbar: { title: 'Correlation', tickvals: [-1, -0.5, 0, 0.5, 1] },
    }];

    return (
        <div className="space-y-6">
            <div className="glass-card p-4">
                <Plot
                    data={heatmapData}
                    layout={{
                        title: 'Price Correlation Heatmap',
                        xaxis: { title: 'Symbol' },
                        yaxis: { title: 'Symbol' },
                        height: 400,
                        template: 'plotly_dark',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#e6edf3' },
                    }}
                    style={{ width: '100%' }}
                    config={{ responsive: true }}
                />
            </div>

            {correlations.length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-primary mb-4">📈 Rolling Correlation (30-window)</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-white/10">
                                    <th className="text-left py-2 px-4 text-gray-400">Symbol 1</th>
                                    <th className="text-left py-2 px-4 text-gray-400">Symbol 2</th>
                                    <th className="text-right py-2 px-4 text-gray-400">Correlation</th>
                                    <th className="text-right py-2 px-4 text-gray-400">P-Value</th>
                                    <th className="text-right py-2 px-4 text-gray-400">Sample Size</th>
                                    <th className="text-left py-2 px-4 text-gray-400">Method</th>
                                </tr>
                            </thead>
                            <tbody>
                                {correlations.map((c, i) => (
                                    <tr key={i} className="border-b border-white/5">
                                        <td className="py-2 px-4 text-white">{c.symbol1}</td>
                                        <td className="py-2 px-4 text-white">{c.symbol2}</td>
                                        <td className="py-2 px-4 text-right text-primary font-mono">{c.correlation?.toFixed(4)}</td>
                                        <td className="py-2 px-4 text-right text-gray-300 font-mono">{c.p_value?.toExponential(4)}</td>
                                        <td className="py-2 px-4 text-right text-gray-300">{c.sample_size}</td>
                                        <td className="py-2 px-4 text-gray-400">{c.method}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

function PairsTrading({ symbols }) {
    const [symbol1, setSymbol1] = useState(symbols[0] || '');
    const [symbol2, setSymbol2] = useState(symbols[1] || '');
    const [regression, setRegression] = useState(null);
    const [spread, setSpread] = useState(null);

    useEffect(() => {
        if (!symbol1 || !symbol2 || symbol1 === symbol2) return;

        const fetchData = async () => {
            try {
                const regRes = await analyticsAPI.getRegression(symbol2, symbol1);
                setRegression(regRes.data);

                const beta = regRes.data.beta || 1;
                const spreadRes = await analyticsAPI.getSpread(symbol1, symbol2, beta);
                setSpread(spreadRes.data);
            } catch (error) {
                console.error('Failed to fetch pairs data:', error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, [symbol1, symbol2]);

    if (symbols.length < 2) {
        return (
            <div className="glass-card p-8 text-center text-gray-400">
                Need at least 2 symbols for pairs trading analysis
            </div>
        );
    }

    const remainingSymbols = symbols.filter(s => s !== symbol1);
    const spreadZscore = spread?.spread_zscore || 0;

    const gaugeData = [{
        type: 'indicator',
        mode: 'gauge+number',
        value: spreadZscore,
        title: { text: 'Spread Z-Score' },
        gauge: {
            axis: { range: [-4, 4] },
            bar: { color: 'royalblue' },
            steps: [
                { range: [-4, -2], color: 'rgba(0, 255, 0, 0.5)' },
                { range: [-2, 2], color: 'rgba(255, 255, 255, 0.2)' },
                { range: [2, 4], color: 'rgba(255, 0, 0, 0.5)' },
            ],
            threshold: { line: { color: 'yellow', width: 4 }, thickness: 0.75, value: 0 },
        },
    }];

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap gap-4">
                <div>
                    <label className="block text-gray-400 text-sm mb-1">Symbol 1 (Y)</label>
                    <select value={symbol1} onChange={(e) => setSymbol1(e.target.value)} className="select-field">
                        {symbols.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
                <div>
                    <label className="block text-gray-400 text-sm mb-1">Symbol 2 (X)</label>
                    <select value={symbol2} onChange={(e) => setSymbol2(e.target.value)} className="select-field">
                        {remainingSymbols.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>
            </div>

            {regression && (
                <>
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-primary mb-4">📐 Regression Results (OLS)</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <MetricCard label="β (Hedge Ratio)" value={regression.beta?.toFixed(4)} />
                            <MetricCard label="α (Alpha)" value={regression.alpha?.toFixed(4)} />
                            <MetricCard label="R²" value={regression.r_squared?.toFixed(4)} />
                            <MetricCard label="P-Value" value={regression.p_value?.toExponential(4)} />
                        </div>
                    </div>

                    {spread && (
                        <>
                            <div className="glass-card p-6">
                                <h3 className="text-lg font-semibold text-primary mb-4">📉 Spread Analysis</h3>
                                <p className="text-gray-300 mb-4 font-mono">
                                    Spread = {symbol1} - {regression.beta?.toFixed(4)} × {symbol2}
                                </p>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <MetricCard label="Current Spread" value={spread.current_spread?.toFixed(2)} />
                                    <MetricCard label="Spread Mean" value={spread.spread_mean?.toFixed(2)} />
                                    <MetricCard label="Spread Z-Score" value={spreadZscore.toFixed(3)} />
                                </div>
                            </div>

                            <div className="glass-card p-4">
                                <Plot
                                    data={gaugeData}
                                    layout={{
                                        height: 300,
                                        template: 'plotly_dark',
                                        paper_bgcolor: 'rgba(0,0,0,0)',
                                        font: { color: '#e6edf3' },
                                    }}
                                    style={{ width: '100%' }}
                                    config={{ responsive: true }}
                                />
                            </div>

                            <div className={`glass-card p-6 border-l-4 ${spreadZscore > 2 ? 'border-red-500 bg-red-500/10' : spreadZscore < -2 ? 'border-green-500 bg-green-500/10' : 'border-blue-500 bg-blue-500/10'}`}>
                                <h3 className="font-semibold text-primary mb-2">🎯 Trading Signal</h3>
                                {spreadZscore > 2 && (
                                    <div className="text-red-400">
                                        <p className="font-bold">📉 SHORT SPREAD</p>
                                        <p>• Spread is {spreadZscore.toFixed(2)}σ above mean</p>
                                        <p>• Action: SHORT {symbol1}, LONG {regression.beta?.toFixed(4)} × {symbol2}</p>
                                        <p>• Target: Mean reversion to spread mean</p>
                                    </div>
                                )}
                                {spreadZscore < -2 && (
                                    <div className="text-green-400">
                                        <p className="font-bold">📈 LONG SPREAD</p>
                                        <p>• Spread is {Math.abs(spreadZscore).toFixed(2)}σ below mean</p>
                                        <p>• Action: LONG {symbol1}, SHORT {regression.beta?.toFixed(4)} × {symbol2}</p>
                                        <p>• Target: Mean reversion to spread mean</p>
                                    </div>
                                )}
                                {Math.abs(spreadZscore) <= 2 && (
                                    <div className="text-blue-400">
                                        <p className="font-bold">⏸️ NO SIGNAL</p>
                                        <p>• Spread Z-Score: {spreadZscore.toFixed(2)}σ</p>
                                        <p>• Wait for |Z| {'>'} 2 for entry signal</p>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
}

function ADFTest({ symbols, selectedSymbol, setSelectedSymbol }) {
    const [adfData, setAdfData] = useState(null);

    useEffect(() => {
        if (!selectedSymbol) return;

        const fetchData = async () => {
            try {
                const response = await analyticsAPI.getADFTest(selectedSymbol);
                setAdfData(response.data);
            } catch (error) {
                console.error('Failed to fetch ADF:', error);
                setAdfData(null);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [selectedSymbol]);

    if (!adfData) {
        return (
            <div className="space-y-6">
                <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)} className="select-field">
                    {symbols.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <div className="glass-card p-8 text-center text-gray-400">
                    Not enough data for ADF test (need 30+ observations)
                </div>
            </div>
        );
    }

    const barData = [{
        x: ['ADF Statistic', '1% Critical', '5% Critical', '10% Critical'],
        y: [adfData.adf_statistic, adfData.critical_1pct, adfData.critical_5pct, adfData.critical_10pct],
        type: 'bar',
        marker: { color: ['#00d4ff', '#ff4444', '#ff9944', '#ffdd44'] },
        text: [
            adfData.adf_statistic?.toFixed(3),
            adfData.critical_1pct?.toFixed(3),
            adfData.critical_5pct?.toFixed(3),
            adfData.critical_10pct?.toFixed(3)
        ],
        textposition: 'outside',
    }];

    return (
        <div className="space-y-6">
            <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)} className="select-field">
                {symbols.map(s => <option key={s} value={s}>{s}</option>)}
            </select>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard label="ADF Statistic" value={adfData.adf_statistic?.toFixed(4)} />
                <MetricCard label="P-Value" value={adfData.p_value?.toFixed(4)} />
                <MetricCard
                    label="Status"
                    value={adfData.is_stationary ? '✅ STATIONARY' : '❌ NON-STATIONARY'}
                    colorClass={adfData.is_stationary ? 'text-green-400' : 'text-red-400'}
                />
            </div>

            <div className="glass-card p-4">
                <Plot
                    data={barData}
                    layout={{
                        title: 'ADF Statistic vs Critical Values',
                        yaxis: { title: 'Value' },
                        template: 'plotly_dark',
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        font: { color: '#e6edf3' },
                        height: 300,
                        showlegend: false,
                    }}
                    style={{ width: '100%' }}
                    config={{ responsive: true }}
                />
            </div>

            <div className={`glass-card p-6 border-l-4 ${adfData.is_stationary ? 'border-green-500 bg-green-500/10' : 'border-yellow-500 bg-yellow-500/10'}`}>
                <h3 className="font-semibold text-primary mb-2">📝 Interpretation</h3>
                {adfData.is_stationary ? (
                    <div className="text-green-400">
                        <p className="font-bold">Series is STATIONARY (p-value = {adfData.p_value?.toFixed(4)})</p>
                        <p>• The price series exhibits mean-reverting behavior</p>
                        <p>• ADF statistic ({adfData.adf_statistic?.toFixed(4)}) {'<'} Critical value 5% ({adfData.critical_5pct?.toFixed(4)})</p>
                        <p>• Suitable for pairs trading / mean reversion strategies</p>
                    </div>
                ) : (
                    <div className="text-yellow-400">
                        <p className="font-bold">Series is NON-STATIONARY (p-value = {adfData.p_value?.toFixed(4)})</p>
                        <p>• The price series follows a random walk</p>
                        <p>• ADF statistic ({adfData.adf_statistic?.toFixed(4)}) {'>'} Critical value 5% ({adfData.critical_5pct?.toFixed(4)})</p>
                        <p>• Consider cointegration testing for pairs</p>
                    </div>
                )}
            </div>
        </div>
    );
}
