import { useState, type ReactNode } from 'react';
import { Home, Shield, ChevronLeft, ChevronRight } from 'lucide-react';
import './Layout.css';

interface LayoutProps {
    children: ReactNode;
    activePage: string;
    onNavigate: (page: string) => void;
}

export function Layout({ children, activePage, onNavigate }: LayoutProps) {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    const navItems = [
        { id: 'home', label: 'Home', icon: Home },
        { id: 'scenarios', label: 'Scenarios', icon: Shield },
    ];

    return (
        <div className="haru-layout">
            {/* Header */}
            <header className="haru-header">
                <h1 className="haru-logo">Haru</h1>
            </header>

            <div className="haru-body">
                {/* Sidebar */}
                <aside className={`haru-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
                    <nav className="sidebar-nav">
                        {navItems.map(item => (
                            <button
                                key={item.id}
                                className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                                onClick={() => onNavigate(item.id)}
                                title={item.label}
                            >
                                <item.icon size={20} />
                                {!sidebarCollapsed && <span>{item.label}</span>}
                            </button>
                        ))}
                    </nav>

                    <button
                        className="sidebar-toggle"
                        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                    >
                        {sidebarCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
                    </button>
                </aside>

                {/* Main Content */}
                <main className="haru-main">
                    {children}
                </main>
            </div>
        </div>
    );
}

export default Layout;
