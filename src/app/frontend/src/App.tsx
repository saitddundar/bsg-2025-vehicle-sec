import { useState } from 'react';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Documents } from './pages/Documents';
import { Logs } from './pages/Logs';
import './App.css';

function App() {
  const [activePage, setActivePage] = useState('home');

  const renderPage = () => {
    switch (activePage) {
      case 'docs':
        return <Documents />;
      case 'logs':
        return <Logs />;
      case 'home':
      default:
        return <Home />;
    }
  };

  return (
    <Layout activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </Layout>
  );
}

export default App;

