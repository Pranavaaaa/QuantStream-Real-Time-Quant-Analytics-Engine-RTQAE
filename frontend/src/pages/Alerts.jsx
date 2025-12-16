import { useState, useEffect } from 'react';
import { analyticsAPI, exportAPI } from '../api/client';
import MetricCard from '../components/MetricCard';

const SEVERITY_CONFIG = {
    low: { emoji: '🔵', color: 'border-blue-500', bgColor: 'bg-blue-500/10', textColor: 'text-blue-400' },
    medium: { emoji: '🟡', color: 'border-yellow-500', bgColor: 'bg-yellow-500/10', textColor: 'text-yellow-400' },
    high: { emoji: '🟠', color: 'border-orange-500', bgColor: 'bg-orange-500/10', textColor: 'text-orange-400' },
    critical: { emoji: '🔴', color: 'border-red-500', bgColor: 'bg-red-500/10', textColor: 'text-red-400' },
};

export default function Alerts() {
    const [alerts, setAlerts] = useState([]);
    const [totalAlerts, setTotalAlerts] = useState(0);
    const [severityFilter, setSeverityFilter] = useState(['medium', 'high', 'critical']);
    const [exporting, setExporting] = useState(false);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await analyticsAPI.getAlerts(50);
                setAlerts(response.data.alerts || []);
                setTotalAlerts(response.data.total_alerts || 0);
            } catch (error) {
                console.error('Failed to fetch alerts:', error);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 3000);
        return () => clearInterval(interval);
    }, []);

    const handleSeverityToggle = (severity) => {
        setSeverityFilter(prev =>
            prev.includes(severity)
                ? prev.filter(s => s !== severity)
                : [...prev, severity]
        );
    };

    const handleExport = async () => {
        setExporting(true);
        try {
            const response = await exportAPI.getAlerts('csv', 1000);
            const blob = new Blob([response.data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'alerts.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Failed to export:', error);
        }
        setExporting(false);
    };

    const filteredAlerts = alerts.filter(alert => severityFilter.includes(alert.severity));

    return (
        <div className="animate-fade-in">
            <h1 className="text-3xl font-bold text-primary mb-6">🔔 Alerts</h1>

            {/* Summary */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <MetricCard label="Total Alerts" value={totalAlerts.toLocaleString()} />
                <MetricCard label="Recent Alerts" value={alerts.length.toLocaleString()} />
            </div>

            {/* Filter */}
            <div className="glass-card p-6 mb-6">
                <h2 className="text-lg font-semibold text-primary mb-4">Filter Alerts</h2>
                <div className="flex flex-wrap gap-3">
                    {Object.entries(SEVERITY_CONFIG).map(([severity, config]) => (
                        <button
                            key={severity}
                            onClick={() => handleSeverityToggle(severity)}
                            className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${severityFilter.includes(severity)
                                    ? `${config.bgColor} ${config.color} border ${config.textColor}`
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                }`}
                        >
                            <span>{config.emoji}</span>
                            <span className="capitalize">{severity}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Export Button */}
            <div className="mb-6">
                <button
                    onClick={handleExport}
                    disabled={exporting}
                    className="btn-primary disabled:opacity-50"
                >
                    {exporting ? '⏳ Exporting...' : '📥 Export Alerts to CSV'}
                </button>
            </div>

            {/* Alerts List */}
            <div className="glass-card p-6">
                <h2 className="text-lg font-semibold text-primary mb-4">
                    Alerts ({filteredAlerts.length})
                </h2>

                {filteredAlerts.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">
                        {alerts.length === 0
                            ? 'No alerts triggered yet. Alerts will appear here when conditions are met.'
                            : 'No alerts match the current filter.'}
                    </p>
                ) : (
                    <div className="space-y-3">
                        {filteredAlerts.slice(0, 20).map((alert, index) => {
                            const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.low;
                            return (
                                <div
                                    key={index}
                                    className={`p-4 rounded-lg border-l-4 ${config.color} ${config.bgColor} transition-all hover:scale-[1.01]`}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <span>{config.emoji}</span>
                                            <span className="font-semibold text-white">{alert.symbol}</span>
                                            <span className={`text-sm font-medium uppercase ${config.textColor}`}>
                                                {alert.severity}
                                            </span>
                                        </div>
                                        <span className="text-sm text-gray-400">
                                            {new Date(alert.timestamp).toLocaleString()}
                                        </span>
                                    </div>
                                    <p className="text-gray-300 mb-2">{alert.message}</p>
                                    <p className="text-xs text-gray-500">Rule: {alert.rule_type}</p>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
