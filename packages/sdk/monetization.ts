import type {
  HouseholdEntitlementPackageV1,
  HouseholdEntitlementV1,
  OpsMetricsSnapshotV1,
  WeeklyValueReportV1,
} from "@lumosreading/contracts";

export interface MonetizationReadModelClient {
  getHouseholdEntitlement(householdId: string): Promise<HouseholdEntitlementV1>;
  getWeeklyValueReport(householdId: string): Promise<WeeklyValueReportV1>;
  getOpsMetricsSnapshot(): Promise<OpsMetricsSnapshotV1>;
}

export type AccessPackageCard = {
  packageId: string;
  title: string;
  languageMode: string;
  ageBand: string;
  releaseChannel: string;
  accessState: HouseholdEntitlementPackageV1["access_state"];
  entitlementSource: HouseholdEntitlementPackageV1["entitlement_source"];
  reason: string;
};

export type AccessDomainView = {
  schemaVersion: HouseholdEntitlementV1["schema_version"];
  householdId: string;
  subscriptionStatus: HouseholdEntitlementV1["subscription_status"];
  accessState: HouseholdEntitlementV1["access_state"];
  planName: string;
  billingInterval: HouseholdEntitlementV1["billing_interval"];
  trialEndsAt: string | null;
  renewsAt: string | null;
  entitledPackageCount: number;
  lockedPackageCount: number;
  accessiblePackages: AccessPackageCard[];
  lockedPackages: AccessPackageCard[];
  generatedAt: string;
};

export type WeeklyValueDomainView = {
  schemaVersion: WeeklyValueReportV1["schema_version"];
  householdId: string;
  periodStart: string;
  periodEnd: string;
  completedSessions: number;
  totalReadingMinutes: number;
  distinctPackagesCompleted: number;
  rereadSessions: number;
  caregiverPromptCompletions: number;
  valueScore: number;
  highlights: WeeklyValueReportV1["highlights"];
  generatedAt: string;
};

export type OpsMetricsDomainView = {
  schemaVersion: OpsMetricsSnapshotV1["schema_version"];
  householdsInScope: number;
  householdsInTrial: number;
  householdsWithPaidAccess: number;
  entitledPackageDeliveries: number;
  blockedPackageRequests: number;
  completedSessions: number;
  reuseSignals: number;
  averageWeeklyValueScore: number;
  generatedAt: string;
};

export interface AccessService {
  getAccessOverview(householdId: string): Promise<AccessDomainView>;
}

export interface WeeklyValueService {
  getWeeklyValue(householdId: string): Promise<WeeklyValueDomainView>;
}

export interface OpsMetricsService {
  getSnapshot(): Promise<OpsMetricsDomainView>;
}

export interface MonetizationServices {
  access: AccessService;
  value: WeeklyValueService;
  ops: OpsMetricsService;
}

function buildAccessPackageCard(
  resource: HouseholdEntitlementPackageV1,
): AccessPackageCard {
  return {
    packageId: resource.package_id,
    title: resource.title,
    languageMode: resource.language_mode,
    ageBand: resource.age_band,
    releaseChannel: resource.release_channel,
    accessState: resource.access_state,
    entitlementSource: resource.entitlement_source,
    reason: resource.reason,
  };
}

export function buildAccessDomainView(
  resource: HouseholdEntitlementV1,
): AccessDomainView {
  const packageCards = resource.package_access.map(buildAccessPackageCard);

  return {
    schemaVersion: resource.schema_version,
    householdId: resource.household_id,
    subscriptionStatus: resource.subscription_status,
    accessState: resource.access_state,
    planName: resource.plan_name,
    billingInterval: resource.billing_interval,
    trialEndsAt: resource.trial_ends_at ?? null,
    renewsAt: resource.renews_at ?? null,
    entitledPackageCount: resource.entitled_package_count,
    lockedPackageCount: resource.locked_package_count,
    accessiblePackages: packageCards.filter(
      (item) => item.accessState === "entitled",
    ),
    lockedPackages: packageCards.filter((item) => item.accessState === "locked"),
    generatedAt: resource.generated_at,
  };
}

export function buildWeeklyValueDomainView(
  resource: WeeklyValueReportV1,
): WeeklyValueDomainView {
  return {
    schemaVersion: resource.schema_version,
    householdId: resource.household_id,
    periodStart: resource.period_start,
    periodEnd: resource.period_end,
    completedSessions: resource.completed_sessions,
    totalReadingMinutes: resource.total_reading_minutes,
    distinctPackagesCompleted: resource.distinct_packages_completed,
    rereadSessions: resource.reread_sessions,
    caregiverPromptCompletions: resource.caregiver_prompt_completions,
    valueScore: resource.value_score,
    highlights: resource.highlights,
    generatedAt: resource.generated_at,
  };
}

export function buildOpsMetricsDomainView(
  resource: OpsMetricsSnapshotV1,
): OpsMetricsDomainView {
  return {
    schemaVersion: resource.schema_version,
    householdsInScope: resource.households_in_scope,
    householdsInTrial: resource.households_in_trial,
    householdsWithPaidAccess: resource.households_with_paid_access,
    entitledPackageDeliveries: resource.entitled_package_deliveries,
    blockedPackageRequests: resource.blocked_package_requests,
    completedSessions: resource.completed_sessions,
    reuseSignals: resource.reuse_signals,
    averageWeeklyValueScore: resource.average_weekly_value_score,
    generatedAt: resource.generated_at,
  };
}

export function createMonetizationServices(
  client: MonetizationReadModelClient,
): MonetizationServices {
  return {
    access: {
      async getAccessOverview(householdId: string) {
        return buildAccessDomainView(
          await client.getHouseholdEntitlement(householdId),
        );
      },
    },
    value: {
      async getWeeklyValue(householdId: string) {
        return buildWeeklyValueDomainView(
          await client.getWeeklyValueReport(householdId),
        );
      },
    },
    ops: {
      async getSnapshot() {
        return buildOpsMetricsDomainView(await client.getOpsMetricsSnapshot());
      },
    },
  };
}
