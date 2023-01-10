import React from 'react';
import Navbar from './components/NavBar';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import About from './pages/about';
import HomePage from './pages/SourceMainPage/App';
import SourceTypePage from './pages/SourceTypesPage/App';
import SourceTypeDatesPage from './pages/SourceTypeDatesPage/App';
  
function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path='/' element={<HomePage />} />
        <Route path='/:source' element={<SourceTypePage />} />
        <Route path='/:source/:type' element={<SourceTypeDatesPage />} />
        <Route path='/about' element={<About/>} />
      </Routes>
    </Router>
  );
}
  
export default App;