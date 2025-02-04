import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Upload failed. Try again!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Joint Space Analysis</h1>
      <input type="file" onChange={handleFileChange} className="mb-4" />
      <button
        onClick={handleUpload}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg"
        disabled={loading}
      >
        {loading ? "Processing..." : "Upload Image"}
      </button>
      {result && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-md">
          <h2 className="text-lg font-semibold">Classification Result</h2>
          <p><strong>Diagnosis:</strong> {result.classification}</p>
          <p><strong>Joint Space Widths:</strong> {result.joint_space_widths.join(", ")}</p>
        </div>
      )}
    </div>
  );
};

export default App;
