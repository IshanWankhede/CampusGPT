export function AuthFlowShell({ title, subtitle, children }) {
  return (
    <main className="min-h-screen min-h-[100dvh] bg-black text-white flex items-center justify-center p-[clamp(24px,5vw,64px)] font-sans-ui">
      <section className="w-full max-w-[440px]">
        <div className="mb-6 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2.5 text-sm font-semibold text-white">
            <span className="w-8 h-8 rounded-full bg-[#1c1c1e] border border-white/15 flex items-center justify-center">
              <i className="fa-solid fa-graduation-cap text-xs" />
            </span>
            Campus<span className="font-light text-neutral-400">GPT</span>
          </a>
          <a href="/auth" className="text-[11px] text-neutral-400 hover:text-white">Back</a>
        </div>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight">{title}</h1>
        <p className="text-sm text-neutral-400 mt-1.5 leading-relaxed">{subtitle}</p>
        <div className="mt-6">{children}</div>
      </section>
    </main>
  );
}

export function AuthInput({ label, ...props }) {
  return (
    <label className="block text-xs font-medium text-neutral-400 mb-4">
      {label}
      <input
        {...props}
        className="mt-1.5 w-full bg-[#141416] text-white border border-white/10 rounded-[14px] px-4 py-3.5 text-sm placeholder:text-[#8e8e8e] focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/20 transition-all"
      />
    </label>
  );
}

export function AuthSubmit({ children, loading }) {
  return (
    <button
      type="submit"
      disabled={loading}
      className="w-full bg-white hover:bg-neutral-100 disabled:opacity-60 text-black font-semibold text-sm py-3.5 px-6 rounded-full transition-all active:scale-[0.99] flex items-center justify-center gap-2"
      style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.15), 0 0 22px rgba(255,255,255,0.32), 0 0 44px rgba(255,255,255,0.12)" }}
    >
      {loading ? "Please wait..." : children}
    </button>
  );
}
