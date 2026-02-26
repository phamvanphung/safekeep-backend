import { useEffect, useState } from "react";
import { getTimer, sendHeartbeat, updateTimer, Timer, HeartbeatResponse } from "../lib/api";

export function DashboardPage() {
  const [timer, setTimer] = useState<Timer | null>(null);
  const [loading, setLoading] = useState(true);
  const [heartbeatLoading, setHeartbeatLoading] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [timeoutDaysInput, setTimeoutDaysInput] = useState("");
  const [lastHeartbeat, setLastHeartbeat] = useState<HeartbeatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadTimer = async () => {
    setError(null);
    try {
      const data = await getTimer();
      setTimer(data);
      setTimeoutDaysInput(String(data.timeout_days));
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to load timer";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadTimer();
  }, []);

  const handleHeartbeat = async () => {
    setHeartbeatLoading(true);
    setError(null);
    try {
      const resp = await sendHeartbeat();
      setLastHeartbeat(resp);
      await loadTimer();
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to send heartbeat";
      setError(detail);
    } finally {
      setHeartbeatLoading(false);
    }
  };

  const handleUpdateTimeout = async () => {
    const parsed = Number(timeoutDaysInput);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      setError("Timeout days must be a positive number");
      return;
    }
    setUpdateLoading(true);
    setError(null);
    try {
      const updated = await updateTimer(parsed);
      setTimer(updated);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to update timer";
      setError(detail);
    } finally {
      setUpdateLoading(false);
    }
  };

  const deadlineIn = () => {
    if (!timer) return "-";
    const deadline = new Date(timer.deadline);
    const now = new Date();
    const diffMs = deadline.getTime() - now.getTime();
    const diffDays = diffMs / (1000 * 60 * 60 * 24);
    if (diffDays <= 0) return "Expired";
    if (diffDays < 1) {
      const hours = Math.floor(diffDays * 24);
      return `${hours}h`;
    }
    return `${diffDays.toFixed(1)} days`;
  };

  return (
    <div className="layout-grid">
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Dead Man&apos;s Switch</div>
            <div className="card-subtitle">
              Your heartbeat controls when your encrypted vault is released to your beneficiaries.
            </div>
          </div>
          <div className="badge">
            <span
              className={`badge-pill ${
                timer?.status === "ACTIVE" ? "badge-pill-success badge-pill-pulse" : "badge-pill-danger"
              }`}
            />
            <span>{timer?.status ?? "UNKNOWN"}</span>
          </div>
        </div>

        {loading ? (
          <div className="muted text-sm">Loading timer...</div>
        ) : timer ? (
          <div className="stack">
            <div className="stat-row">
              <div className="stat-label">Timeout window</div>
              <div className="stat-value">{timer.timeout_days} days</div>
            </div>
            <div className="stat-row">
              <div className="stat-label">Last heartbeat</div>
              <div className="stat-value stat-mono">{new Date(timer.last_checkin).toLocaleString()}</div>
            </div>
            <div className="stat-row">
              <div className="stat-label">Deadline</div>
              <div className="stat-value stat-mono">{new Date(timer.deadline).toLocaleString()}</div>
            </div>
            <div className="stat-row">
              <div className="stat-label">Time remaining</div>
              <div className="pill-signal">
                <span className="badge-pill badge-pill-success" /> {deadlineIn()}
              </div>
            </div>

            <hr className="divider" />

            <div className="stack-tight">
              <label className="field-label" htmlFor="timeout_days">
                Adjust timeout window
              </label>
              <div className="row">
                <input
                  id="timeout_days"
                  type="number"
                  min={1}
                  className="input"
                  style={{ maxWidth: 120 }}
                  value={timeoutDaysInput}
                  onChange={(e) => setTimeoutDaysInput(e.target.value)}
                />
                <button
                  type="button"
                  className="btn btn-outline btn-small"
                  onClick={handleUpdateTimeout}
                  disabled={updateLoading}
                >
                  {updateLoading ? "Updating..." : "Update"}
                </button>
              </div>
              <p className="text-xs muted">
                If you don&apos;t send a heartbeat before the deadline, your vault will be released.
              </p>
            </div>

            <div className="mt-md">
              <button
                type="button"
                className="btn btn-primary btn-full"
                onClick={handleHeartbeat}
                disabled={heartbeatLoading}
              >
                {heartbeatLoading ? "Sending heartbeat..." : "Send heartbeat now"}
              </button>
            </div>

            {lastHeartbeat && (
              <div className="pill-soft mt-sm">
                <span className="accent-soft">Last heartbeat:</span>
                <span className="stat-mono">
                  {new Date(lastHeartbeat.last_checkin).toLocaleString()} → deadline{" "}
                  {new Date(lastHeartbeat.deadline).toLocaleString()}
                </span>
              </div>
            )}

            {error && (
              <div className="pill-soft pill-error mt-sm">
                <span>{error}</span>
              </div>
            )}
          </div>
        ) : (
          <div className="muted text-sm">No timer configured for this account.</div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">How SAFEKEEP works</div>
            <div className="card-subtitle">A visual summary of your zero-knowledge Dead Man&apos;s Switch.</div>
          </div>
        </div>

        <div className="stack">
          <div className="pill-soft">
            <span className="badge-pill badge-pill-success" />
            <span className="accent-soft">Heartbeat</span>
            <span className="muted text-xs">Regular pings prove you&apos;re still in control.</span>
          </div>
          <div className="pill-soft">
            <span className="badge-pill" style={{ background: "#22d3ee" }} />
            <span className="accent-soft">Vault</span>
            <span className="muted text-xs">
              Encrypted client-side. SAFEKEEP stores only ciphertext + salt.
            </span>
          </div>
          <div className="pill-soft">
            <span className="badge-pill" style={{ background: "#a855f7" }} />
            <span className="accent-soft">Beneficiaries</span>
            <span className="muted text-xs">Trusted recipients who receive your data when you stop responding.</span>
          </div>

          <hr className="divider" />
          <p className="text-xs muted">
            When your timer expires, the backend Celery worker looks up your beneficiaries and vaults and sends them
            the encrypted data. You control the encryption keys; SAFEKEEP never sees your plaintext.
          </p>
        </div>
      </div>
    </div>
  );
}

