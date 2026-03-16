"use client";

import type { StoryPackageManifestV1 } from "@lumosreading/contracts";
import { formatDurationMinutes } from "@/lib/format";
import { useStoryPackageCatalog } from "@/lib/hooks/use-story-package-catalog";

type ConnectedPackagePanelProps = {
  initialFeaturedPackage: StoryPackageManifestV1;
  initialPackageQueue: StoryPackageManifestV1[];
};

function renderStatusBadge(status: "loading" | "live" | "fallback") {
  if (status === "live") {
    return <span className="badge is-green">live api</span>;
  }

  if (status === "loading") {
    return <span className="badge is-sky">syncing</span>;
  }

  return <span className="badge is-warm">fallback</span>;
}

export function ConnectedPackagePanel({
  initialFeaturedPackage,
  initialPackageQueue,
}: ConnectedPackagePanelProps) {
  const packageIds = initialPackageQueue.map((item) => item.package_id);
  const { packages, packagesById, status, error } = useStoryPackageCatalog(packageIds, initialPackageQueue);
  const featuredPackage = packagesById[initialFeaturedPackage.package_id] ?? initialFeaturedPackage;

  return (
    <article className="panel-card">
      <div className="panel-card__header">
        <h2>Featured package</h2>
        <div className="badge-row">
          {renderStatusBadge(status)}
          <span className="badge mono">{featuredPackage.package_id}</span>
        </div>
      </div>
      <p>{featuredPackage.subtitle}</p>
      <div className="badge-row">
        {featuredPackage.tags?.map((tag) => (
          <span key={tag} className="badge">
            {tag}
          </span>
        ))}
      </div>
      <div className="meta-pairs">
        <div className="meta-pair">
          <span className="meta-pair__label">Language</span>
          <span className="meta-pair__value">{featuredPackage.language_mode}</span>
        </div>
        <div className="meta-pair">
          <span className="meta-pair__label">Age band</span>
          <span className="meta-pair__value">{featuredPackage.age_band}</span>
        </div>
        <div className="meta-pair">
          <span className="meta-pair__label">Duration</span>
          <span className="meta-pair__value">
            {formatDurationMinutes(featuredPackage.estimated_duration_sec)}
          </span>
        </div>
        <div className="meta-pair">
          <span className="meta-pair__label">Safety</span>
          <span className="meta-pair__value">{featuredPackage.safety.review_status}</span>
        </div>
      </div>

      {error ? <div className="note-card">{error}</div> : null}

      <div className="stack-list">
        {packages.map((item) => (
          <article key={item.package_id} className="list-row">
            <p className="list-row__title">{item.title}</p>
            <div className="list-row__meta">
              <span>{item.language_mode}</span>
              <span>{item.difficulty_level}</span>
              <span>{formatDurationMinutes(item.estimated_duration_sec)}</span>
            </div>
          </article>
        ))}
      </div>
    </article>
  );
}
