import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useAuth } from "./state/AuthContext";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";
import { VaultsPage } from "./pages/VaultsPage";
import { BeneficiariesPage } from "./pages/BeneficiariesPage";

function AppHeader() {
  const { isAuthenticated, email, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path: string) => (location.pathname === path ? "nav-link nav-link-active" : "nav-link");

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <div
          className="logo"
          onClick={() => navigate(isAuthenticated ? "/dashboard" : "/auth")}
          style={{ cursor: "pointer" }}
        >
          <div className="logo-mark">
            <div className="logo-mark-inner">S</div>
          </div>
          <div>
            <div className="logo-title">SAFEKEEP</div>
            <div className="logo-subtitle">Zero-Knowledge Dead Man&apos;s Switch</div>
          </div>
        </div>
        <nav className="app-nav">
          {isAuthenticated && (
            <>
              <button className={isActive("/dashboard")} onClick={() => navigate("/dashboard")}>
                Overview
              </button>
              <button className={isActive("/vaults")} onClick={() => navigate("/vaults")}>
                Vaults
              </button>
              <button className={isActive("/beneficiaries")} onClick={() => navigate("/beneficiaries")}>
                Beneficiaries
              </button>
            </>
          )}
          {!isAuthenticated ? (
            <button className="btn btn-primary btn-small" onClick={() => navigate("/auth")}>
              Sign in
            </button>
          ) : (
            <div className="row">
              <span className="tag">{email}</span>
              <button className="btn btn-ghost btn-small" onClick={logout}>
                Logout
              </button>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }
  return children;
}

export function App() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (location.pathname === "/") {
      navigate(isAuthenticated ? "/dashboard" : "/auth", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="app-shell">
      <AppHeader />
      <main className="app-main">
        <div className="app-main-inner">
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/vaults"
              element={
                <ProtectedRoute>
                  <VaultsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/beneficiaries"
              element={
                <ProtectedRoute>
                  <BeneficiariesPage />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/auth"} replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

