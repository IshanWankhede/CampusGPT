import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ fullName: "", email: "", password: "", confirmPassword: "", role: "STUDENT" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const update = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));

  async function submit(event) {
    event.preventDefault();
    setError("");
    if (mode === "signup" && form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      if (mode === "login") await login(form.email.trim(), form.password);
      else await register(form.fullName.trim(), form.email.trim(), form.password, form.role);
      navigate("/app", { replace: true });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div className="auth-topline">
          <Link className="auth-brand" to="/"><span>⌁</span> Campus<span>GPT</span></Link>
          <Link className="back-link" to="/">← Back</Link>
        </div>
        <h1>{mode === "login" ? "Welcome back" : "Create your account"}</h1>
        <p className="auth-subtitle">{mode === "login" ? "Sign in to access your campus dashboard." : "Join CampusGPT with your university credentials."}</p>
        <div className="auth-tabs">
          <button className={mode === "login" ? "active" : ""} onClick={() => { setMode("login"); setError(""); }}>Sign in</button>
          <button className={mode === "signup" ? "active" : ""} onClick={() => { setMode("signup"); setError(""); }}>Sign up</button>
        </div>
        <form onSubmit={submit} className="auth-form">
          {mode === "signup" && <label>Full name<input value={form.fullName} onChange={update("fullName")} placeholder="Aarav Sharma" required /></label>}
          <label>University email<input type="email" value={form.email} onChange={update("email")} placeholder="name@campus.edu" required /></label>
          {mode === "signup" && <label>University role<select value={form.role} onChange={update("role")}><option value="STUDENT">Student</option><option value="FACULTY">Faculty</option></select></label>}
          <label>Password<input type="password" value={form.password} onChange={update("password")} placeholder="••••••••" minLength={8} required /></label>
          {mode === "signup" && <label>Confirm password<input type="password" value={form.confirmPassword} onChange={update("confirmPassword")} placeholder="••••••••" minLength={8} required /></label>}
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-pill auth-submit" disabled={submitting}>{submitting ? "Please wait…" : mode === "login" ? "Sign in →" : "Create account →"}</button>
        </form>
        <p className="auth-switch">{mode === "login" ? "Don't have an account?" : "Already have an account?"} <button onClick={() => setMode(mode === "login" ? "signup" : "login")}>{mode === "login" ? "Sign up" : "Sign in"}</button></p>
      </section>
      <aside className="auth-art">
        <div className="art-orbit orbit-one" /><div className="art-orbit orbit-two" /><div className="art-core">⌁</div>
        <div className="art-copy"><span>YOUR CAMPUS, INTELLIGENTLY CONNECTED</span><strong>Ask less.<br />Discover more.</strong></div>
      </aside>
    </main>
  );
}
