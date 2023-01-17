import React from "react";
import Navbar from "./components/NavBar";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import About from "./pages/about";
import SourceListMainPage from "./pages/SourcePage/App";
import SourceTypePage from "./pages/SourceTypesPage/App";
import SourceTypeDatesPage from "./pages/SourceTypeDatesPage/App";
import TitlesListMain from "./pages/ListTitlesPage/App";
export default function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<SourceListMainPage />} />
        <Route path="/:source" element={<SourceTypePage />} />
        <Route path="/:source/:type" element={<SourceTypeDatesPage />} />
        <Route path="/:source/:type/:date" element={<TitlesListMain />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </Router>
  );
}
