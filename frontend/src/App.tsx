import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ClaimList } from './components/ClaimList';
import { ClaimDetail } from './components/ClaimDetail';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ClaimList />} />
        <Route path="/claims/:claimId" element={<ClaimDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
