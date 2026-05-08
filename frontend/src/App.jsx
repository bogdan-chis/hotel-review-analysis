import { useState, useRef } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/process_file";

export default function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    if (!f.name.endsWith(".txt")) {
      setError("Please upload a valid .txt file containing guest reviews.");
      return;
    }
    setFile(f);
    setResults(null);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResults(null);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await fetch(API_URL, { method: "POST", body: form });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Unable to connect to the server.");
      }
      setResults(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResults(null);
    setError(null);
  };

  // Helper to handle both string and object data structures seamlessly
  const renderItemText = (item) => (typeof item === "object" ? item.item : item);
  const renderItemCount = (item) => (typeof item === "object" && item.count > 1 ? item.count : null);

  return (
    <div className="booking-layout">
      {/* Classic Booking-style Navbar */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">ReviewInsights</div>
          <div className="nav-links">
            <span className="nav-item">Property Dashboard</span>
            <span className="nav-item active">Guest Feedback</span>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {!results ? (
          <>
            <div className="hero-section">
              <h1>Understand your guests better</h1>
              <p>Upload your raw review exports to instantly extract what guests loved and what needs improvement.</p>
            </div>

            <div className="card upload-card">
              <div 
                className={`upload-dropzone ${dragging ? "drag-active" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => !file && inputRef.current.click()}
              >
                <input
                  ref={inputRef}
                  type="file"
                  accept=".txt"
                  className="hidden-input"
                  onChange={(e) => handleFile(e.target.files[0])}
                />
                
                {file ? (
                  <div className="file-selected">
                    <div className="file-icon">📄</div>
                    <div className="file-details">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button className="remove-file" onClick={(e) => { e.stopPropagation(); reset(); }}>✕</button>
                  </div>
                ) : (
                  <div className="upload-prompt">
                    <span className="upload-icon">⬆️</span>
                    <span className="upload-title">Drag and drop your .txt file here</span>
                    <span className="upload-subtitle">or click to browse your computer</span>
                  </div>
                )}
              </div>

              {error && <div className="alert alert-error">{error}</div>}

              <button 
                className="btn-primary btn-large" 
                onClick={handleSubmit} 
                disabled={!file || loading}
              >
                {loading ? "Analyzing Reviews..." : "Analyze Guest Feedback"}
              </button>
            </div>
          </>
        ) : (
          <div className="results-container">
            <div className="results-header">
              <div className="results-title-group">
                <h2>Guest Feedback Summary</h2>
                <span className="source-file">Source: {file.name}</span>
              </div>
              <button className="btn-secondary" onClick={reset}>Analyze Another File</button>
            </div>

            <div className="metrics-grid">
              <div className="card metric-card positive">
                <div className="metric-header">
                  <span className="metric-icon">👍</span>
                  <h3>What guests loved</h3>
                </div>
                <ul className="review-list">
                  {results.highlights.length === 0 && <li className="empty-state">No positive highlights extracted.</li>}
                  {results.highlights.map((item, i) => {
                    const count = renderItemCount(item);
                    return (
                      <li key={i} className="review-item">
                        <span className="review-text">{renderItemText(item)}</span>
                        {count && <span className="mention-badge">Mentioned {count} times</span>}
                      </li>
                    );
                  })}
                </ul>
              </div>

              <div className="card metric-card negative">
                <div className="metric-header">
                  <span className="metric-icon">👎</span>
                  <h3>Areas for improvement</h3>
                </div>
                <ul className="review-list">
                  {results.pain_points.length === 0 && <li className="empty-state">No pain points extracted.</li>}
                  {results.pain_points.map((item, i) => {
                    const count = renderItemCount(item);
                    return (
                      <li key={i} className="review-item">
                        <span className="review-text">{renderItemText(item)}</span>
                        {count && <span className="mention-badge">Mentioned {count} times</span>}
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}