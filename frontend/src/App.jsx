import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import HomePage from "./pages/HomePage";
import Category from "./pages/Category";
import Fiber from "./pages/Fiber";
import Stroke from "./pages/Stroke";
import Report from "./pages/Report";
import Variant from "./pages/TeaVariant";

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/category" element={<Category />} />
        <Route path="/fiber" element={<Fiber />} />
        <Route path="/stroke" element={<Stroke />} />
        <Route path="/report" element={<Report />} />
        <Route path="/variant" element={<Variant />} />
      </Routes>
    </Router>
  );
}

export default App;
