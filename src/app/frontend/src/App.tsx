import { useState } from 'react';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Scenarios } from './pages/Scenarios';
import './App.css';

function App() {
  const [activePage, setActivePage] = useState('home');

  const renderPage = () => {
    switch (activePage) {
      case 'scenarios':
        return <Scenarios />;
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
