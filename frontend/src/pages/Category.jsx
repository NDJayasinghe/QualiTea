import React, { useState } from "react";
import axios from "axios";
import "../style/Styles.css";

function Category() {
  const [liquidImage, setLiquidImage] = useState("");
  const [infusionImage, setInfusionImage] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [responses, setResponses] = useState([]);
  const [loadingLiquid, setLoadingLiquid] = useState(false);
  const [loadingInfusion, setLoadingInfusion] = useState(false);

  const handleImageChange = (event, setImage) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLiquidSubmit = async () => {
    if (!liquidImage) return;
    setLoadingLiquid(true);
    try {
      const blob = await fetch(liquidImage).then((res) => res.blob());
      const formData = new FormData();
      formData.append("image", blob, "liquidImage.jpg");

      const response = await axios.post(
        "http://127.0.0.1:8080/predict_liquid",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setResponses([
        { type: "Elevation (Liquid):", data: response.data.prediction },
      ]);
      setShowModal(true);
    } catch (error) {
      console.error("Liquid error:", error);
    } finally {
      setLoadingLiquid(false);
    }
  };

  const handleInfusionSubmit = async () => {
    if (!infusionImage) return;
    setLoadingInfusion(true);
    try {
      const blob = await fetch(infusionImage).then((res) => res.blob());
      const formData = new FormData();
      formData.append("image", blob, "infusionImage.jpg");

      const response = await axios.post(
        "http://127.0.0.1:8080/predict_infusion",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setResponses([
        { type: "Elevation (Infusion):", data: response.data.prediction },
      ]);
      setShowModal(true);
    } catch (error) {
      console.error("Infusion error:", error);
    } finally {
      setLoadingInfusion(false);
    }
  };

  const closeModal = () => {
    setShowModal(false);
  };

  // const isSubmitDisabled = !(particleImage || liquidImage || infusionImage);

  return (
    <div className="category-container">
      <div className="c-header">Tea Elevation Identification</div>
      <div className="c-inputs">
        <div className="input-feild">
          <label>Add Liquid Image:</label>
          <div className="input-image" style={{ marginBottom: "20px" }}>
            <input
              type="file"
              name="liquid"
              onChange={(e) => handleImageChange(e, setLiquidImage)}
            />
            {liquidImage && <img src={liquidImage} alt="Liquid" />}
          </div>
          <button
            className="submit-button"
            disabled={!liquidImage || loadingLiquid}
            onClick={handleLiquidSubmit}
            style={
              !liquidImage || loadingLiquid
                ? { backgroundColor: "gray", color: "darkgray" }
                : { backgroundColor: "green" }
            }
          >
            {loadingLiquid ? (
              <div style={{ display: "flex", alignItems: "center" }}>
                <div className="spinner" style={{ marginRight: "10px" }}></div>
                Processing...
              </div>
            ) : (
              "Submit"
            )}
          </button>
        </div>
        <div className="input-feild">
          <label>Add Infusion Image:</label>
          <div className="input-image" style={{ marginBottom: "20px" }}>
            <input
              type="file"
              name="infusion"
              onChange={(e) => handleImageChange(e, setInfusionImage)}
            />
            {infusionImage && <img src={infusionImage} alt="Infusion" />}
          </div>
          <button
            className="submit-button"
            disabled={!infusionImage || loadingInfusion}
            onClick={handleInfusionSubmit}
            style={
              !infusionImage || loadingInfusion
                ? { backgroundColor: "gray", color: "darkgray" }
                : { backgroundColor: "green" }
            }
          >
            {loadingInfusion ? (
              <div style={{ display: "flex", alignItems: "center" }}>
                <div className="spinner" style={{ marginRight: "10px" }}></div>
                Processing...
              </div>
            ) : (
              "Submit"
            )}
          </button>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h1>Results!</h1>
            {responses.map((response, index) => (
              <div key={index}>
                <h4>{response.type}</h4>
                <p>{response.data}</p>
              </div>
            ))}
            <button onClick={closeModal} className="close-button">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Category;
