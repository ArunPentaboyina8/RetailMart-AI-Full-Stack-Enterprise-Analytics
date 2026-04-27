import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ChatWidget from './components/ChatWidget';
import Executive from './pages/Executive';
import Sales from './pages/Sales';
import Customers from './pages/Customers';
import Products from './pages/Products';
import Stores from './pages/Stores';
import Operations from './pages/Operations';
import Marketing from './pages/Marketing';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-area">
          <Routes>
            <Route path="/" element={<Executive />} />
            <Route path="/sales" element={<Sales />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/products" element={<Products />} />
            <Route path="/stores" element={<Stores />} />
            <Route path="/operations" element={<Operations />} />
            <Route path="/marketing" element={<Marketing />} />
          </Routes>
        </main>
        <ChatWidget />
      </div>
    </BrowserRouter>
  );
}
