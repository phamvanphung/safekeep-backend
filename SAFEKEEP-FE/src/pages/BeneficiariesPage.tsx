import { useEffect, useState } from "react";
import {
  Beneficiary,
  createBeneficiary,
  deleteBeneficiary,
  listBeneficiaries,
  updateBeneficiary,
} from "../lib/api";

interface BeneficiaryFormState {
  email: string;
  name: string;
}

export function BeneficiariesPage() {
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState<Beneficiary | null>(null);
  const [form, setForm] = useState<BeneficiaryFormState>({ email: "", name: "" });

  const load = async () => {
    setError(null);
    try {
      const data = await listBeneficiaries();
      setBeneficiaries(data);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to load beneficiaries";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const resetForm = () => {
    setEditing(null);
    setForm({ email: "", name: "" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email.trim() || !form.name.trim()) {
      setError("Email and name are required");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (editing) {
        await updateBeneficiary(editing.id, form);
      } else {
        await createBeneficiary(form);
      }
      resetForm();
      await load();
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to save beneficiary";
      setError(detail);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (b: Beneficiary) => {
    setEditing(b);
    setForm({ email: b.email, name: b.name });
  };

  const handleDelete = async (b: Beneficiary) => {
    if (!window.confirm(`Delete beneficiary "${b.name}" (${b.email})?`)) return;
    setError(null);
    try {
      await deleteBeneficiary(b.id);
      await load();
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to delete beneficiary";
      setError(detail);
    }
  };

  return (
    <div className="layout-grid">
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">{editing ? "Edit beneficiary" : "Add beneficiary"}</div>
            <div className="card-subtitle">
              Beneficiaries receive your encrypted vault when your timer expires. Use real, monitored inboxes.
            </div>
          </div>
          <div className="badge">
            <span className="badge-pill" style={{ background: "#a855f7" }} />
            <span>{beneficiaries.length} configured</span>
          </div>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          <div className="field">
            <label className="field-label" htmlFor="b_email">
              Email
            </label>
            <input
              id="b_email"
              className="input"
              type="email"
              placeholder="beneficiary@example.com"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            />
          </div>
          <div className="field">
            <label className="field-label" htmlFor="b_name">
              Name
            </label>
            <input
              id="b_name"
              className="input"
              placeholder="John Doe"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>

          {error && (
            <div className="pill-soft pill-error mt-sm">
              <span>{error}</span>
            </div>
          )}

          <div className="row row-space mt-md">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving..." : editing ? "Save changes" : "Add beneficiary"}
            </button>
            {editing && (
              <button type="button" className="btn btn-ghost btn-small" onClick={resetForm}>
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Configured beneficiaries</div>
            <div className="card-subtitle">
              Keep this list short and trusted. All configured recipients will receive your encrypted vault on timeout.
            </div>
          </div>
        </div>

        {loading ? (
          <div className="muted text-sm">Loading beneficiaries...</div>
        ) : beneficiaries.length === 0 ? (
          <p className="muted text-sm">
            You have no beneficiaries configured yet. Add at least one trusted contact to make the switch useful.
          </p>
        ) : (
          <div className="list">
            {beneficiaries.map((b) => (
              <div key={b.id} className="list-item">
                <div className="list-item-main">
                  <div className="list-item-title">{b.name}</div>
                  <div className="list-item-subtitle">{b.email}</div>
                  <div className="list-item-meta text-xs">ID: {b.id}</div>
                </div>
                <div className="stack-tight" style={{ minWidth: 120, alignItems: "flex-end" }}>
                  <button type="button" className="btn btn-outline btn-small" onClick={() => handleEdit(b)}>
                    Edit
                  </button>
                  <button type="button" className="btn btn-danger btn-small" onClick={() => handleDelete(b)}>
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

