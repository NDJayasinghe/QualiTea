import React, { useState } from "react";
import axios from "axios";
import "../style/Styles.css";

function Report() {
  const [particleImage, setParticleImage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

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

  const handleSubmit = async () => {
    setIsLoading(true);
    setAnalysisData(null);

    try {
      const formData = new FormData();
      if (particleImage) {
        const particleBlob = await fetch(particleImage).then((res) =>
          res.blob()
        );
        formData.append("image", particleBlob, "particleImage.jpg");

        const response = await axios.post(
          "http://127.0.0.1:8080/generate_report",
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );

        setAnalysisData(response.data);
      } else {
        console.error("No image provided.");
      }
    } catch (error) {
      console.error("Error submitting image:", error);
    } finally {
      setIsLoading(false);
      setShowModal(true);
    }
  };

  const closeModal = () => setShowModal(false);

  const handleViewImage = (imageData) => {
    if (imageData) {
      const imageSrc = `data:image/jpeg;base64,${imageData}`;
      const newTab = window.open();
      newTab.document.body.innerHTML = `<img src="${imageSrc}" alt="Result Image" style="width:100%; height:100%; object-fit:contain;" />`;
    }
  };

  const isSubmitDisabled = !particleImage;

  return (
    <div className="category-container">
      <div className="c-header">Generate Report</div>

      <div className="c-inputs">
        <div className="input-feild">
          <label>Add Particle Image:</label>
          <div className="input-image">
            <input
              type="file"
              name="particle"
              onChange={(e) => handleImageChange(e, setParticleImage)}
            />
            {particleImage && <img src={particleImage} alt="Particle" />}
          </div>
        </div>
      </div>

      <button
        className="submit-button"
        disabled={isSubmitDisabled || isLoading}
        onClick={handleSubmit}
        style={
          isSubmitDisabled || isLoading
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

      {showModal && analysisData && (
        <div className="modal-overlay">
          <div className="modal">
            <h1>Report</h1>
            {/* Tea Variant */}
            {analysisData.tea_variant && (
              <div>
                <h2>Tea Variant:</h2>
                <h4>{analysisData.tea_variant}</h4>
              </div>
            )}

            {/* Fiber Image */}
            {analysisData.fiber_statistics &&
            analysisData.fiber_statistics.number_of_thin_particles > 0 ? (
              <div>
                <h4>Extracted Fibers:</h4>
                {analysisData.fiber_image ? (
                  <>
                    <img
                      src={`data:image/jpeg;base64,${analysisData.fiber_image}`}
                      alt="Fiber Result"
                      style={{ maxWidth: "100%" }}
                    />
                    <button
                      onClick={() => handleViewImage(analysisData.fiber_image)}
                      className="view-button"
                      style={{
                        backgroundColor: "blue",
                        color: "white",
                        padding: "10px",
                        border: "none",
                        borderRadius: "5px",
                        cursor: "pointer",
                        margin: "10px 0",
                      }}
                    >
                      View Fiber Image
                    </button>
                  </>
                ) : (
                  <p>No fiber image available.</p>
                )}
              </div>
            ) : (
              <p>No fibers detected.</p>
            )}

            {/* Fiber Stats */}
            {analysisData.fiber_statistics && (
              <div>
                <p>
                  Total Number of Particles:{" "}
                  {analysisData.fiber_statistics.total_number_of_particles || 0}
                </p>
                <h4>Fiber Analysis:</h4>
                <p>
                  Number of Fiber Particles:{" "}
                  {analysisData.fiber_statistics.number_of_thin_particles || 0}
                </p>
                <p>
                  Fiber Percentage:{" "}
                  {(
                    analysisData.fiber_statistics.fiber_percentage ?? 0
                  ).toFixed(2)}
                  %
                </p>
              </div>
            )}

            {/* Stroke Image */}
            {analysisData.stroke_statistics &&
            analysisData.stroke_statistics.number_of_brown_particles > 0 ? (
              <div>
                <h4>Extracted Strokes:</h4>
                {analysisData.stroke_image ? (
                  <>
                    <img
                      src={`data:image/jpeg;base64,${analysisData.stroke_image}`}
                      alt="Stroke Result"
                      style={{ maxWidth: "100%" }}
                    />
                    <button
                      onClick={() => handleViewImage(analysisData.stroke_image)}
                      className="view-button"
                      style={{
                        backgroundColor: "blue",
                        color: "white",
                        padding: "10px",
                        border: "none",
                        borderRadius: "5px",
                        cursor: "pointer",
                        margin: "10px 0",
                      }}
                    >
                      View Stroke Image
                    </button>
                  </>
                ) : (
                  <p>No stroke image available.</p>
                )}
              </div>
            ) : (
              <p>No strokes detected to display.</p>
            )}

            {/* Stroke Stats */}
            {analysisData.stroke_statistics && (
              <div>
                <h4>Stroke Analysis:</h4>
                <p>
                  Number of Stroke Particles:{" "}
                  {analysisData.stroke_statistics.number_of_brown_particles ||
                    0}
                </p>
                <p>
                  Stroke Percentage:{" "}
                  {(
                    (analysisData.stroke_statistics.number_of_brown_particles /
                      analysisData.fiber_statistics.total_number_of_particles) *
                      100 || 0
                  ).toFixed(2)}
                  %
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
                marginTop: "10px",
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

export default Report;
