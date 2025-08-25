import React from "react";
import { Link, useNavigate } from "react-router-dom";
import teaLogo from "../assets/images/tea.png";
import "../style/Header.css";

function Header() {
  const navigate = useNavigate();

  const ToHome = () => {
    navigate("/");
  };

  return (
    <header className="header-container">
      <div className="logo-section" onClick={ToHome}>
        <img src={teaLogo} alt="Tea Logo" className="logo-img" />
        <h1 className="logo-text">
          Quali<span>Tea</span>
        </h1>
      </div>

      <nav className="nav-menu">
        <Link to="/" className="nav-link">
          Home
        </Link>
        <Link to="/variant" className="nav-link">
          Variant
        </Link>
        <Link to="/category" className="nav-link">
          Elevation
        </Link>
        <Link to="/fiber" className="nav-link">
          Fiber
        </Link>
        <Link to="/stroke" className="nav-link">
          Stroke
        </Link>
        <Link to="/report" className="nav-link">
          Report
        </Link>
      </nav>
    </header>
  );
}

export default Header;
