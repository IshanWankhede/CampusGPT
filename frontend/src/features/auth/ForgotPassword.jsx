import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { AuthFlowShell, AuthInput, AuthSubmit } from "./AuthFlowStyles";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { forgotPassword } = useAuth();
  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await forgotPassword(email.trim());
      navigate(`/auth/reset-password?email=${encodeURIComponent(email.trim())}`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }
  return (
    <AuthFlowShell title="Forgot your password?" subtitle="Enter your email and we'll send a reset code if an account exists.">
      <form onSubmit={submit}>
        <AuthInput label="Campus Email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@campus.edu" required />
        {error && <p role="alert" className="text-xs text-red-400 mb-4">{error}</p>}
        <AuthSubmit loading={loading}>Send Reset Code <i className="fa-solid fa-arrow-right text-xs" /></AuthSubmit>
      </form>
    </AuthFlowShell>
  );
}
