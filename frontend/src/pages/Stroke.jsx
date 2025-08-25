import React, { useState } from "react";
import axios from "axios";
import "../style/Styles.css";

function Stroke() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewImage, setPreviewImage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [resultData, setResultData] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    if (!selectedImage) return;

    setIsLoading(true);
    setResultData(null);

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8080/identify-stroke",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      console.log("Response from backend:", response.data);
      setResultData(response.data);
    } catch (error) {
      console.error("Error during stroke analysis:", error);
    } finally {
      setIsLoading(false);
      setShowModal(true);
    }
  };

  const handleViewImage = () => {
    if (resultData?.result_image) {
      const newWindow = window.open();
      newWindow.document.write(
        `<img src="data:image/jpeg;base64,${resultData.result_image}" style="width: 100%; height: 100%; object-fit: contain;" />`
      );
    }
  };

  return (
    <div className="category-container">
      <div className="c-header">Stroke Analysis</div>

      <div className="c-inputs">
        <div className="input-feild">
          <label>Upload Stroke Image:</label>
          <div className="input-image">
            <input type="file" onChange={handleImageChange} />
            {previewImage && <img src={previewImage} alt="Stroke Preview" />}
          </div>
        </div>
      </div>

      <button
        className="submit-button"
        disabled={!selectedImage || isLoading}
        onClick={handleSubmit}
        style={
          !selectedImage || isLoading
            ? { backgroundColor: "gray", color: "darkgray" }
            : { backgroundColor: "green" }
        }
      >
        {isLoading ? (
          <div style={{ display: "flex", alignItems: "center" }}>
            <div className="spinner" style={{ marginRight: "10px" }}></div>
            Analyzing...
          </div>
        ) : (
          "Submit"
        )}
      </button>

      {showModal && resultData && (
        <div className="modal-overlay">
          <div className="modal">
            <h1>Analysis Results</h1>

            {resultData.result_image && (
              <>
                <h4>Processed Image:</h4>
                <img
                  src={`data:image/jpeg;base64,${resultData.result_image}`}
                  alt="Stroke Result"
                  style={{ maxWidth: "100%" }}
                />
                <button
                  onClick={handleViewImage}
                  className="view-button"
                  style={{
                    backgroundColor: "blue",
                    color: "white",
                    padding: "10px",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                    marginTop: "10px",
                  }}
                >
                  View Full Image
                </button>
              </>
            )}

            {resultData.statistics && (
              <div style={{ marginTop: "20px", textAlign: "left" }}>
                <h2>Stroke Statistics</h2>
                <p>
                  <strong>Total Particles:</strong>{" "}
                  {resultData.statistics.number_of_external_contours}
                </p>
                <p>
                  <strong>Brown Particles:</strong>{" "}
                  {resultData.statistics.number_of_brown_particles}
                </p>
                <p>
                  <strong>Brown Particle Ratio:</strong>{" "}
                  {resultData.statistics.brown_particle_ratio.toFixed(2)}%
                </p>               
              </div>
            )}

            <button
              onClick={() => setShowModal(false)}
              className="close-button"
              style={{
                backgroundColor: "green",
                color: "white",
                padding: "10px",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
                marginTop: "20px",
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Stroke;
