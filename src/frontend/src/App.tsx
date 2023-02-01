import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import About from "./pages/about";
import SourceListMainPage from "./pages/SourcesList";
import SourceTypePage from "./pages/SourceTypesPage/App";
import ChartList from "./pages/ChartstList";
export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/manga" element={<SourceListMainPage />} />
        <Route path="/:source" element={<SourceTypePage />} />
        <Route path="/:source/:type" element={<ChartList />} />
        <Route path="/:source/:type/:url_date" element={<ChartList />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </Router>
  );
}
