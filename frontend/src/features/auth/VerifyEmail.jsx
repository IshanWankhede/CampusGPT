import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { AuthFlowShell, AuthInput, AuthSubmit } from "./AuthFlowStyles";

export default function VerifyEmail() {
  const email = new URLSearchParams(useLocation().search).get("email") || "";
  const navigate = useNavigate();
  const { verifyOtp, sendOtp } = useAuth();
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [seconds, setSeconds] = useState(60);

  useEffect(() => {
    if (!seconds) return undefined;
    const timer = setInterval(() => setSeconds((value) => value - 1), 1000);
    return () => clearInterval(timer);
  }, [seconds]);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await verifyOtp(email, otp, "EMAIL_VERIFY");
      navigate("/auth", { replace: true, state: { message: "Email verified. Please sign in." } });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function resend() {
    setError("");
    try {
      await sendOtp(email, "EMAIL_VERIFY");
      setSeconds(60);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <AuthFlowShell title="Verify your email" subtitle={`We sent a code to ${email}`}>
      <form onSubmit={submit}>
        <AuthInput label="6-digit verification code" value={otp} onChange={(event) => setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))} inputMode="numeric" autoComplete="one-time-code" placeholder="000000" required />
        {error && <p role="alert" className="text-xs text-red-400 mb-4">{error}</p>}
        <AuthSubmit loading={loading}>Verify <i className="fa-solid fa-arrow-right text-xs" /></AuthSubmit>
      </form>
      <button disabled={seconds > 0} onClick={resend} className="block mx-auto mt-5 text-xs text-neutral-400 hover:text-white disabled:opacity-50">
        {seconds > 0 ? `Resend in ${seconds}s` : "Resend code"}
      </button>
    </AuthFlowShell>
  );
}
