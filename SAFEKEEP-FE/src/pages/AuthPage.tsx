import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { login as apiLogin, register as apiRegister } from "../lib/api";
import { useAuth } from "../state/AuthContext";

const schema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormValues = z.infer<typeof schema>;

export function AuthPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [serverError, setServerError] = useState<string | null>(null);
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: FormValues) => {
    setServerError(null);
    try {
      if (mode === "register") {
        await apiRegister(values.email, values.password);
      }
      const res = await apiLogin(values.email, values.password);
      login(res.access_token, values.email);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Authentication failed";
      setServerError(Array.isArray(detail) ? detail[0]?.msg ?? "Authentication failed" : detail);
    }
  };

  return (
    <div className="auth-layout">
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">
              {mode === "login" ? "Welcome back" : "Create your SAFEKEEP account"}
            </div>
            <div className="card-subtitle">
              {mode === "login"
                ? "Sign in to manage your Dead Man's Switch"
                : "We only store encrypted data from your device"}
            </div>
          </div>
          <div className="badge">
            <span className="badge-pill badge-pill-success badge-pill-pulse" />
            <span className="accent-soft">Zero-knowledge</span>
          </div>
        </div>

        <div className="auth-switch">
          <button
            type="button"
            className={mode === "login" ? "btn btn-primary btn-full btn-small" : "btn btn-ghost btn-full btn-small"}
            onClick={() => setMode("login")}
          >
            Sign in
          </button>
          <button
            type="button"
            className={
              mode === "register" ? "btn btn-primary btn-full btn-small" : "btn btn-ghost btn-full btn-small"
            }
            onClick={() => setMode("register")}
          >
            Create account
          </button>
        </div>

        <form className="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="field">
            <label className="field-label" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className={`input ${errors.email ? "input-error" : ""}`}
              placeholder="you@example.com"
              {...register("email")}
            />
            {errors.email && <div className="error-text">{errors.email.message}</div>}
          </div>

          <div className="field">
            <label className="field-label" htmlFor="password">
              Password <span>(min 8 characters)</span>
            </label>
            <input
              id="password"
              type="password"
              className={`input ${errors.password ? "input-error" : ""}`}
              placeholder="••••••••"
              {...register("password")}
            />
            {errors.password && <div className="error-text">{errors.password.message}</div>}
          </div>

          {serverError && (
            <div className="pill-soft pill-error mt-sm">
              <span>{serverError}</span>
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-full mt-md" disabled={isSubmitting}>
            {isSubmitting ? "Please wait..." : mode === "login" ? "Sign in" : "Create account & sign in"}
          </button>

          <p className="text-xs muted mt-md">
            SAFEKEEP uses a Dead Man&apos;s Switch. As long as you keep sending heartbeats, your vault stays sealed. If
            you stop, your beneficiaries receive your encrypted data.
          </p>
        </form>
      </div>
    </div>
  );
}

