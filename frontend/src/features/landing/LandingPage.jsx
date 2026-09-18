import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

function Stat({ value, label }) {
  return (
    <div className="landing-stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((current) => (current >= 1 ? 1 : current + 0.025));
    }, 45);
    return () => clearInterval(timer);
  }, []);

  return (
    <main className="landing-page">
      <div className="landing-glow landing-glow-one" />
      <div className="landing-glow landing-glow-two" />
      <div className="landing-grid" />
      <header className="landing-header">
        <Link className="brand-mark" to="/" aria-label="CampusGPT home">
          <span>⌁</span>
        </Link>
        <nav className="desktop-nav">
          <a href="#home">Home</a>
          <a href="#features">Features</a>
          <a href="#about">About</a>
        </nav>
        <Link className="dark-pill" to="/auth">Sign in</Link>
        <button className="menu-button" onClick={() => setMenuOpen(true)} aria-label="Open menu">☰</button>
      </header>

      {menuOpen && (
        <div className="mobile-menu-backdrop" onClick={() => setMenuOpen(false)}>
          <div className="mobile-menu" onClick={(event) => event.stopPropagation()}>
            <div className="mobile-menu-top"><strong>CampusGPT</strong><button onClick={() => setMenuOpen(false)}>×</button></div>
            <a href="#home" onClick={() => setMenuOpen(false)}>Home</a>
            <a href="#features" onClick={() => setMenuOpen(false)}>Features</a>
            <Link to="/auth" onClick={() => setMenuOpen(false)}>Sign in</Link>
          </div>
        </div>
      )}

      <section id="home" className="landing-hero">
        <div className="trust-pill"><span>◉</span><span>Trusted across every department</span></div>
        <p className="eyebrow">THE INTELLIGENT CAMPUS OPERATING SYSTEM</p>
        <h1>Everything your campus needs.<br /><em>One intelligent space.</em></h1>
        <p className="hero-copy">CampusGPT connects students, faculty, and administration with the information and tools they need to move campus life forward.</p>
        <Link className="primary-pill" to="/auth">Get started <span>→</span></Link>
        <div className="floating-card floating-card-left"><b>SYLLABUS.PDF</b><span>Vector indexed · 98%</span></div>
        <div className="floating-card floating-card-right"><b>ATTENDANCE.SQL</b><span>Query resolved · 0.3s</span></div>
      </section>

      <section id="features" className="landing-stats">
        <Stat value={`< ${Math.round(400 - progress * 20)}ms`} label="Assistant response time" />
        <Stat value={`${(90 + progress * 9.9).toFixed(1)}%`} label="Platform uptime" />
        <Stat value={`${Math.round(progress * 10)}k+`} label="Documents indexed" />
      </section>
      <footer id="about" className="landing-footer">CampusGPT · Built for the modern campus</footer>
    </main>
  );
}
