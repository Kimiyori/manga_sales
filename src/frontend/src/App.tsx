import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import About from "./pages/About";
import SourceListMainPage from "./pages/SourcesList";
import ChartList from "./pages/ChartstList";
import Contact from "./pages/Contacts";
import NotFound from "./pages/NotFound";
export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SourceListMainPage />} />
        <Route path="/manga" element={<SourceListMainPage />} />
        <Route path="/:source/:type" element={<ChartList />} />
        <Route path="/:source/:type/:url_date" element={<ChartList />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}
