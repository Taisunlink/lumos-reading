import { API_BASE_URL } from "@/lib/api/v2";
import { caregiverNavItems } from "@/lib/navigation";
import { startupOrder } from "@/lib/page-models";

const guardrails = [
  "Add business meaning in docs first, then update schemas, then wire runtime behavior.",
  "Keep apps/web as legacy reference material and avoid routing net-new caregiver features into it.",
  "Treat story packages and reading events as release artifacts that can be validated, rolled back, and analyzed.",
];

const implementationDefaults = [
  {
    label: "API base URL",
    value: API_BASE_URL,
  },
  {
    label: "Legacy v1 routers",
    value: "Disabled by default in apps/api",
  },
  {
    label: "Shared contract source",
    value: "@lumosreading/contracts",
  },
  {
    label: "Current caregiver routes",
    value: caregiverNavItems.map((item) => item.href).join(" "),
  },
];

export default function SettingsPage() {
  return (
    <main className="page-stack">
      <section className="hero-card">
        <div className="hero-card__eyebrow">Governance and defaults</div>
        <h1>Keep the repo honest by making the startup order and contract boundaries explicit.</h1>
        <p className="hero-card__lead">
          Settings in V2 are mostly development and operating constraints right now: where to start reading, which
          API surface is active, and which app directories are allowed to evolve.
        </p>
      </section>

      <section className="split-grid">
        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Startup order</h2>
            <span className="panel-card__eyebrow">Read before changing code</span>
          </div>
          <div className="stack-list">
            {startupOrder.map((item, index) => (
              <article key={item} className="list-row">
                <p className="list-row__title">
                  {index + 1}. <code>{item}</code>
                </p>
              </article>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-card__header">
            <h2>Implementation defaults</h2>
            <span className="panel-card__eyebrow">What this shell assumes today</span>
          </div>
          <div className="stack-list">
            {implementationDefaults.map((item) => (
              <article key={item.label} className="list-row">
                <p className="list-row__title">{item.label}</p>
                <div className="list-row__meta">
                  <span className="mono">{item.value}</span>
                </div>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section className="panel-card">
        <div className="panel-card__header">
          <h2>Migration guardrails</h2>
          <span className="panel-card__eyebrow">Preserve the V2 direction</span>
        </div>
        <ul className="clean-list">
          {guardrails.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
