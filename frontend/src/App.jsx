import { useState } from 'react';
import DrawingCard from './components/DrawingCard';
import { generateDrawings, saveGenerations } from './api';
import './App.css';

export default function App() {
  const [count, setCount] = useState(1);
  const [drawings, setDrawings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [regeneratingIndex, setRegeneratingIndex] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [error, setError] = useState(null);

  async function handleGenerateAll() {
    setLoading(true);
    setError(null);
    setSaveStatus(null);
    try {
      const locked = drawings.filter(d => d.locked);
      const newCount = Math.max(0, count - locked.length);
      const newlyGenerated = newCount > 0 ? await generateDrawings(newCount) : [];
      setDrawings([
        ...locked,
        ...newlyGenerated.map(g => ({ ...g, locked: false })),
      ]);
    } catch (e) {
      setError('Failed to generate. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }

  async function handleRegenerateOne(index) {
    setRegeneratingIndex(index);
    setSaveStatus(null);
    try {
      const [generated] = await generateDrawings(1);
      setDrawings(prev =>
        prev.map((d, i) => (i === index ? { ...generated, locked: false } : d))
      );
    } catch (e) {
      setError('Failed to regenerate drawing.');
    } finally {
      setRegeneratingIndex(null);
    }
  }

  function handleToggleLock(index) {
    setDrawings(prev =>
      prev.map((d, i) => (i === index ? { ...d, locked: !d.locked } : d))
    );
  }

  async function handleSave() {
    setSaving(true);
    setSaveStatus(null);
    try {
      const result = await saveGenerations(
        drawings.map(d => ({ white_balls: d.white_balls, power_ball: d.power_ball }))
      );
      setSaveStatus(`Saved ${result.saved} generation${result.saved !== 1 ? 's' : ''}!`);
    } catch (e) {
      setError('Failed to save generations.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Powerball Generator</h1>
      </header>

      <div className="controls">
        <label htmlFor="count-select">Drawings</label>
        <select
          id="count-select"
          value={count}
          onChange={e => setCount(Number(e.target.value))}
        >
          {Array.from({ length: 10 }, (_, i) => i + 1).map(n => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
        <button className="btn-primary" onClick={handleGenerateAll} disabled={loading}>
          {loading ? 'Generating…' : 'Generate'}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {drawings.length > 0 && (
        <>
          <div className="drawings-grid">
            {drawings.map((drawing, index) => (
              <DrawingCard
                key={index}
                drawing={drawing}
                onRegenerate={() => handleRegenerateOne(index)}
                onToggleLock={() => handleToggleLock(index)}
                loading={regeneratingIndex === index}
              />
            ))}
          </div>

          <div className="save-bar">
            <button className="btn-save" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving…' : 'Save All'}
            </button>
            {saveStatus && <span className="save-status">{saveStatus}</span>}
          </div>
        </>
      )}
    </div>
  );
}
