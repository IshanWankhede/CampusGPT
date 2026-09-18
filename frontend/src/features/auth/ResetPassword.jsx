import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { AuthFlowShell, AuthInput, AuthSubmit } from "./AuthFlowStyles";

export default function ResetPassword() {
  const email = new URLSearchParams(useLocation().search).get("email") || "";
  const navigate = useNavigate();
  const { resetPassword } = useAuth();
  const [form, setForm] = useState({ otp: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const update = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));
  async function submit(event) {
    event.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      await resetPassword(email, form.otp, form.password);
      navigate("/auth", { replace: true, state: { message: "Password updated, please sign in." } });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }
  return (
    <AuthFlowShell title="Reset your password" subtitle={`Enter the code sent to ${email}`}>
      <form onSubmit={submit}>
        <AuthInput label="6-digit reset code" value={form.otp} onChange={update("otp")} inputMode="numeric" required />
        <AuthInput label="New password" type="password" value={form.password} onChange={update("password")} minLength={8} required />
        <AuthInput label="Confirm password" type="password" value={form.confirm} onChange={update("confirm")} minLength={8} required />
        {error && <p role="alert" className="text-xs text-red-400 mb-4">{error}</p>}
        <AuthSubmit loading={loading}>Reset Password <i className="fa-solid fa-arrow-right text-xs" /></AuthSubmit>
      </form>
    </AuthFlowShell>
  );
}
