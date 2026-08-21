import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <h1>CampusGPT — Frontend ↔ Backend Check</h1>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {health ? (
        <p style={{ color: "green" }}>
          ✅ Backend says: {JSON.stringify(health)}
        </p>
      ) : (
        !error && <p>Checking backend connection...</p>
      )}
    </div>
  );
}

export default App;