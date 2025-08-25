import React from "react";
import { useNavigate } from "react-router-dom";
import "../style/HomePage.css";
// import teaImage from "../assets/images/tea_bg.jpg";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-section">
      <div className="home-header">
          Welcome to <br />
          <span className="brand-name">
            Quali<span>Tea</span>
          </span>
        </div>
        <p className="home-subheading">
          Smart Analysis for Tea Quality & Classification
        </p>
        <p className="home-subheading2">
          Upload your tea images and receive insights on quality,
          category, and composition.
        </p>
        <div className="button-container">
          <button className="home-button" onClick={() => navigate("/variant")}>
            Variant Identification
          </button>
          <button className="home-button" onClick={() => navigate("/category")}>
            Elevation Identification
          </button>
          <button className="home-button" onClick={() => navigate("/fiber")}>
            Fiber Analysis
          </button>
          <button className="home-button" onClick={() => navigate("/stroke")}>
            Stroke Analysis
          </button>
          <button className="home-button" onClick={() => navigate("/report")}>
            Generate Report
          </button>
        </div>

      {/* <img src={teaImage} alt="Tea Background" className="home-image" /> */}
    </div>
  );
}

export default HomePage;
