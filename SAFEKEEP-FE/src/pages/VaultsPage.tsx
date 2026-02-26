import { useEffect, useState } from "react";
import { createVault, deleteVault, listVaults, updateVault, Vault } from "../lib/api";

interface VaultFormState {
  name: string;
  encrypted_data: string;
  client_salt: string;
}

export function VaultsPage() {
  const [vaults, setVaults] = useState<Vault[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [editingVault, setEditingVault] = useState<Vault | null>(null);
  const [form, setForm] = useState<VaultFormState>({
    name: "",
    encrypted_data: "",
    client_salt: "",
  });

  const loadVaults = async () => {
    setError(null);
    try {
      const data = await listVaults();
      setVaults(data);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to load vaults";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadVaults();
  }, []);

  const resetForm = () => {
    setEditingVault(null);
    setForm({ name: "", encrypted_data: "", client_salt: "" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Name is required");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      if (editingVault) {
        await updateVault(editingVault.id, {
          name: form.name,
          encrypted_data: form.encrypted_data || null,
          client_salt: form.client_salt || null,
        });
      } else {
        await createVault({
          name: form.name,
          encrypted_data: form.encrypted_data || null,
          client_salt: form.client_salt || null,
        });
      }
      resetForm();
      await loadVaults();
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to save vault";
      setError(detail);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (vault: Vault) => {
    setEditingVault(vault);
    setForm({
      name: vault.name,
      encrypted_data: vault.encrypted_data ?? "",
      client_salt: vault.client_salt ?? "",
    });
  };

  const handleDelete = async (vault: Vault) => {
    if (!window.confirm(`Delete vault "${vault.name}"? This cannot be undone.`)) return;
    setError(null);
    try {
      await deleteVault(vault.id);
      await loadVaults();
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "Failed to delete vault";
      setError(detail);
    }
  };

  return (
    <div className="layout-grid">
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">{editingVault ? "Edit vault" : "Create new vault"}</div>
            <div className="card-subtitle">
              SAFEKEEP never sees decrypted content. You encrypt on the client and store ciphertext here.
            </div>
          </div>
          <div className="badge">
            <span className="badge-pill badge-pill-success" />
            <span className="accent-soft">Client-side encryption</span>
          </div>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          <div className="field">
            <label className="field-label" htmlFor="name">
              Vault name
            </label>
            <input
              id="name"
              className="input"
              placeholder="e.g. Critical passwords, Recovery kit"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>

          <div className="field">
            <label className="field-label" htmlFor="encrypted_data">
              Encrypted data
            </label>
            <textarea
              id="encrypted_data"
              className="textarea"
              placeholder="Paste ciphertext here (SAFEKEEP will store as-is)"
              value={form.encrypted_data}
              onChange={(e) => setForm((f) => ({ ...f, encrypted_data: e.target.value }))}
            />
          </div>

          <div className="field">
            <label className="field-label" htmlFor="client_salt">
              Client salt / metadata <span>(optional)</span>
            </label>
            <input
              id="client_salt"
              className="input"
              placeholder="Salt or key identifier used by your client"
              value={form.client_salt}
              onChange={(e) => setForm((f) => ({ ...f, client_salt: e.target.value }))}
            />
          </div>

          {error && (
            <div className="pill-soft pill-error mt-sm">
              <span>{error}</span>
            </div>
          )}

          <div className="row row-space mt-md">
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? "Saving..." : editingVault ? "Save changes" : "Create vault"}
            </button>
            {editingVault && (
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
            <div className="card-title">Your vaults</div>
            <div className="card-subtitle">You can maintain multiple encrypted payloads per account.</div>
          </div>
          <div className="badge">
            <span className="badge-pill" style={{ background: "#22d3ee" }} />
            <span>{vaults.length} vault{vaults.length === 1 ? "" : "s"}</span>
          </div>
        </div>

        {loading ? (
          <div className="muted text-sm">Loading vaults...</div>
        ) : vaults.length === 0 ? (
          <p className="muted text-sm">No vaults yet. Create one on the left to store encrypted data.</p>
        ) : (
          <div className="list">
            {vaults.map((vault) => (
              <div key={vault.id} className="list-item">
                <div className="list-item-main">
                  <div className="list-item-title">{vault.name}</div>
                  <div className="list-item-subtitle text-xs">
                    Ciphertext length: {vault.encrypted_data ? vault.encrypted_data.length : 0} chars
                  </div>
                  {vault.client_salt && (
                    <div className="list-item-meta">
                      Salt / metadata: <span className="code">{vault.client_salt}</span>
                    </div>
                  )}
                </div>
                <div className="stack-tight" style={{ minWidth: 120, alignItems: "flex-end" }}>
                  <button type="button" className="btn btn-outline btn-small" onClick={() => handleEdit(vault)}>
                    Edit
                  </button>
                  <button type="button" className="btn btn-danger btn-small" onClick={() => handleDelete(vault)}>
                    Delete
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

