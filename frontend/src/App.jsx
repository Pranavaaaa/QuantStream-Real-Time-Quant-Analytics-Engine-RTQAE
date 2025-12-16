import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Controls from './pages/Controls';
import LiveData from './pages/LiveData';
import Statistics from './pages/Statistics';
import Analytics from './pages/Analytics';
import Alerts from './pages/Alerts';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Controls />} />
          <Route path="live-data" element={<LiveData />} />
          <Route path="statistics" element={<Statistics />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="alerts" element={<Alerts />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
