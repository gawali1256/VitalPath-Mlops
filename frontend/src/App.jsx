import { useEffect, useState } from "react";
import { assessHealth, fetchModelInfo } from "./api";

const INITIAL = {
  age: 32,
  gender: "female",
  height_cm: 168,
  weight_kg: 64,
  activity_level: "light",
  sleep_hours: 7,
  goal: "maintain",
};

function BmiMeter({ bmi, category }) {
  const clamped = Math.min(40, Math.max(12, bmi));
  const left = ((clamped - 12) / 28) * 100;
  return (
    <div className="meter">
      <div className="meter-track">
        <span className="band under" />
        <span className="band healthy" />
        <span className="band over" />
        <span className="band obese" />
        <span className="needle" style={{ left: `${left}%` }} />
      </div>
      <div className="meter-labels">
        <span>12</span>
        <span>18.5</span>
        <span>25</span>
        <span>30</span>
        <span>40</span>
      </div>
      <p className="meter-caption">
        BMI {bmi} · {category}
      </p>
    </div>
  );
}

export default function App() {
  const [form, setForm] = useState(INITIAL);
  const [result, setResult] = useState(null);
  const [model, setModel] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchModelInfo().then(setModel).catch(() => setModel(null));
  }, []);

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        age: Number(form.age),
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        sleep_hours: Number(form.sleep_hours),
      };
      setResult(await assessHealth(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">Local MLOps health lab</p>
        <h1>VitalPath</h1>
        <p className="lede">
          Enter the basics. The API calculates BMI, a trained model estimates lifestyle risk,
          and a rule engine turns that into a weekly exercise plan.
        </p>
        {model && (
          <p className="model-chip">
            Serving model {model.version} · risk accuracy {model.metrics?.risk_accuracy ?? "—"}
          </p>
        )}
      </header>

      <main className="layout">
        <form className="panel" onSubmit={onSubmit}>
          <h2>Your measurements</h2>
          <div className="grid">
            <label>
              Age
              <input type="number" min="14" max="90" value={form.age} onChange={(e) => update("age", e.target.value)} />
            </label>
            <label>
              Gender
              <select value={form.gender} onChange={(e) => update("gender", e.target.value)}>
                <option value="female">Female</option>
                <option value="male">Male</option>
                <option value="other">Other</option>
              </select>
            </label>
            <label>
              Height (cm)
              <input type="number" min="120" max="230" step="0.1" value={form.height_cm} onChange={(e) => update("height_cm", e.target.value)} />
            </label>
            <label>
              Weight (kg)
              <input type="number" min="30" max="250" step="0.1" value={form.weight_kg} onChange={(e) => update("weight_kg", e.target.value)} />
            </label>
            <label>
              Activity
              <select value={form.activity_level} onChange={(e) => update("activity_level", e.target.value)}>
                <option value="sedentary">Sedentary</option>
                <option value="light">Light</option>
                <option value="moderate">Moderate</option>
                <option value="active">Active</option>
              </select>
            </label>
            <label>
              Sleep (hours)
              <input type="number" min="3" max="14" step="0.5" value={form.sleep_hours} onChange={(e) => update("sleep_hours", e.target.value)} />
            </label>
            <label className="wide">
              Goal
              <select value={form.goal} onChange={(e) => update("goal", e.target.value)}>
                <option value="lose">Lose body mass</option>
                <option value="maintain">Maintain</option>
                <option value="gain">Gain strength / mass</option>
              </select>
            </label>
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "Scoring…" : "Assess my health"}
          </button>
          {error && <p className="error">{error}</p>}
        </form>

        <section className="panel result" aria-live="polite">
          {!result && (
            <div className="empty">
              <h2>Results appear here</h2>
              <p>The score uses BMI math plus the Random Forest models published by the training job.</p>
            </div>
          )}
          {result && (
            <>
              <div className="result-top">
                <div>
                  <p className="eyebrow">Current health</p>
                  <h2>{result.health_status}</h2>
                </div>
                <span className={`risk risk-${result.risk_level}`}>
                  {result.risk_level} risk · {Math.round(result.risk_confidence * 100)}%
                </span>
              </div>
              <BmiMeter bmi={result.bmi} category={result.bmi_category} />
              <p className="summary">{result.summary}</p>
              <p className="focus">
                <strong>Weekly focus:</strong> {result.weekly_focus} Intensity: {result.recommended_intensity}.
              </p>
              <ul className="exercises">
                {result.exercises.map((item) => (
                  <li key={item.name}>
                    <div>
                      <h3>{item.name}</h3>
                      <p>{item.why}</p>
                    </div>
                    <span>
                      {item.minutes} min · {item.frequency_per_week}x / week
                    </span>
                  </li>
                ))}
              </ul>
              <p className="fine">Model version {result.model_version}. This is a teaching demo, not medical advice.</p>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
