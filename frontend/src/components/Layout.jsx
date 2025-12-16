import { NavLink, Outlet } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { healthAPI } from '../api/client';

const navItems = [
    { path: '/', icon: '🎛️', label: 'Dashboard' },
    { path: '/live-data', icon: '📊', label: 'Live Data' },
    { path: '/statistics', icon: '📈', label: 'Statistics' },
    { path: '/analytics', icon: '📉', label: 'Analytics' },
    { path: '/alerts', icon: '🔔', label: 'Alerts' },
];

export default function Layout() {
    const [backendStatus, setBackendStatus] = useState(null);
    const [ingestionActive, setIngestionActive] = useState(false);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const response = await healthAPI.check();
                setBackendStatus(response.data.status === 'healthy');
                setIngestionActive(response.data.ws_client_running || false);
            } catch {
                setBackendStatus(false);
                setIngestionActive(false);
            }
        };

        checkHealth();
        const interval = setInterval(checkHealth, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex min-h-screen">
            {/* Sidebar */}
            <aside className="w-64 bg-gradient-sidebar border-r border-indigo-500/20 flex flex-col">
                {/* Logo */}
                <div className="p-6 border-b border-indigo-500/10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-xl shadow-lg shadow-indigo-500/25">
                            📈
                        </div>
                        <div>
                            <h1 className="text-lg font-bold text-white">QuantStream</h1>
                            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Real-Time Analytics</p>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                isActive ? 'nav-item-active' : 'nav-item'
                            }
                        >
                            <span className="text-lg">{item.icon}</span>
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                {/* Status Section */}
                <div className="p-4 border-t border-indigo-500/10">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-medium">System Status</div>
                    <div className="space-y-2.5">
                        <div className="flex items-center gap-2.5">
                            <span className={`status-dot ${backendStatus ? 'status-dot-success' : 'status-dot-error'}`}></span>
                            <span className="text-sm text-slate-300">
                                {backendStatus ? 'Backend Online' : 'Backend Offline'}
                            </span>
                        </div>
                        <div className="flex items-center gap-2.5">
                            <span className={`status-dot ${ingestionActive ? 'status-dot-success' : 'status-dot-neutral'}`}></span>
                            <span className="text-sm text-slate-300">
                                {ingestionActive ? 'Ingestion Active' : 'Ingestion Inactive'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* About Section */}
                <div className="p-4 border-t border-indigo-500/10">
                    <p className="text-xs text-slate-600 leading-relaxed">
                        Real-time quantitative analytics for cryptocurrency markets
                    </p>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-auto">
                <Outlet />

                {/* Footer */}
                <footer className="mt-12 pt-6 border-t border-white/5 text-center">
                    <p className="text-slate-600 text-sm">
                        QuantStream RTQAE v1.0.0 • Built with React + Vite + Tailwind
                    </p>
                </footer>
            </main>
        </div>
    );
}
