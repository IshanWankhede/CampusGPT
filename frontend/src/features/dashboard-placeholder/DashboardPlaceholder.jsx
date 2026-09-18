import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function DashboardPlaceholder() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const signOut = async () => {
    await logout();
    navigate("/", { replace: true });
  };
  return (
    <main className="placeholder-page">
      <div className="placeholder-card">
        <div className="brand-mark">⌁</div>
        <p className="eyebrow">CAMPUSGPT</p>
        <h1>Welcome, {user?.full_name || "campus user"} 👋</h1>
        <p>Your <strong>{user?.role || "user"}</strong> dashboard is under construction — check back soon.</p>
        <button className="primary-pill" onClick={signOut}>Sign out</button>
      </div>
    </main>
  );
}
