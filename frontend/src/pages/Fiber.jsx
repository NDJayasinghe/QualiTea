import React, { useState } from "react";
import axios from "axios";
import "../style/Styles.css";

function Fiber() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewImage, setPreviewImage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [fiberData, setFiberData] = useState(null);

  const handleImageChange = (event) => {
    const file = event.target.files[0];
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
    setFiberData(null);

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8080/identify-fiber",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setFiberData(response.data);
    } catch (error) {
      console.error("Error during fiber analysis:", error);
    } finally {
      setIsLoading(false);
      setShowModal(true);
    }
  };

  const handleViewImage = () => {
    if (fiberData?.result_image) {
      const base64Image = fiberData.result_image.trim();
      const imageHtml = `<img src="data:image/jpeg;base64,${base64Image}" style="width: 100%; height: 100%; object-fit: contain;" />`;
      const newWindow = window.open("", "_blank");

      if (newWindow) {
        newWindow.document.write(imageHtml);
        newWindow.document.close(); 
      } else {
        alert("Popup blocked. Please allow popups for this site.");
      }
    } else {
      alert("No image available.");
    }
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <div className="category-container">
      <div className="c-header">Fiber Analysis</div>

      <div className="c-inputs">
        <div className="input-feild">
          <label>Upload Fiber Image:</label>
          <div className="input-image">
            <input type="file" onChange={handleImageChange} />
            {previewImage && <img src={previewImage} alt="Fiber Preview" />}
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
            Processing...
          </div>
        ) : (
          "Submit"
        )}
      </button>

      {showModal && fiberData && (
        <div className="modal-overlay">
          <div className="modal">
            <h1>Analysis Results</h1>

            {fiberData.result_image && (
              <>
                <h4>Detected Fibers:</h4>
                <img
                  src={`data:image/jpeg;base64,${fiberData.result_image}`}
                  alt="Fiber Result"
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

            {fiberData.statistics && (
              <div style={{ marginTop: "20px", textAlign: "left" }}>
                <h2>Fiber Statistics</h2>
                <p>
                  <strong>Total Particles:</strong>{" "}
                  {fiberData.statistics.total_number_of_particles}
                </p>
                <p>
                  <strong>Fiber Particles:</strong>{" "}
                  {fiberData.statistics.number_of_thin_particles}
                </p>
                <p>
                  <strong>Fiber Ratio:</strong>{" "}
                  {fiberData.statistics.fiber_percentage.toFixed(2)}%
                </p>
              </div>
            )}

            <button
              onClick={closeModal}
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

export default Fiber;
