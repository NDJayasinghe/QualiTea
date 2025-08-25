import React, { useState } from "react";
import axios from "axios";
import "../style/Styles.css";

function TeaVariant() {
  const [particleImage, setParticleImage] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [responses, setResponses] = useState([]);
  const [loadingParticle, setLoadingParticle] = useState(false);

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

  const handleParticleSubmit = async () => {
    if (!particleImage) return;
    setLoadingParticle(true);
    try {
      const blob = await fetch(particleImage).then((res) => res.blob());
      const formData = new FormData();
      formData.append("image", blob, "particleImage.jpg");

      const response = await axios.post(
        "http://127.0.0.1:8080/predict_tea_variant", 
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      setResponses([
        { type: "Tea Variant (Particle):", data: response.data.prediction }, 
      ]);
      setShowModal(true);
    } catch (error) {
      console.error("Particle error:", error);
      setResponses([
        {
          type: "Tea Variant (Particle):",
          data: "Error predicting tea variant.",
        },
      ]);
      setShowModal(true);
    } finally {
      setLoadingParticle(false);
    }
  };


  const closeModal = () => {
    setShowModal(false);
  };

  // const isSubmitDisabled = !(particleImage || liquidImage || infusionImage);

  return (
    <div className="category-container">
      <div className="c-header">Tea Variant Identification</div>
      <div className="c-inputs">
        <div className="input-feild">
          <label>Add Particle Image:</label>
          <div className="input-image" style={{ marginBottom: "20px" }}>
            <input
              type="file"
              name="particle"
              onChange={(e) => handleImageChange(e, setParticleImage)}
            />
            {particleImage && <img src={particleImage} alt="Particle" />}
          </div>
          <button
            className="submit-button"
            disabled={!particleImage || loadingParticle}
            onClick={handleParticleSubmit}
            style={
              !particleImage || loadingParticle
                ? { backgroundColor: "gray", color: "darkgray" }
                : { backgroundColor: "green" }
            }
          >
            {loadingParticle ? (
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

export default TeaVariant;
