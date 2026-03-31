import AsyncStorage from '@react-native-async-storage/async-storage';

import type {
  ReadingEventV1,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from '@lumosreading/contracts';

const HOME_PACKAGES_KEY = 'lumos-reading:home-packages';
const PACKAGE_CACHE_KEY = 'lumos-reading:package-cache';
const SESSION_SNAPSHOT_KEY = 'lumos-reading:session-snapshot';
const EVENT_OUTBOX_KEY = 'lumos-reading:event-outbox';

let eventOutboxOperation: Promise<unknown> = Promise.resolve();

export type PersistedSessionSnapshot = {
  sessionReceipt: ReadingSessionResponseV2;
  packageId: string;
  currentPageIndex: number;
  translationVisible: boolean;
  restoredAt: string;
};

type PackageCacheRecord = Record<string, StoryPackageManifestV1>;

async function loadJsonValue<T>(key: string, fallback: T): Promise<T> {
  try {
    const rawValue = await AsyncStorage.getItem(key);

    if (!rawValue) {
      return fallback;
    }

    return JSON.parse(rawValue) as T;
  } catch {
    return fallback;
  }
}

async function saveJsonValue(key: string, value: unknown): Promise<void> {
  await AsyncStorage.setItem(key, JSON.stringify(value));
}

function runEventOutboxOperation<T>(operation: () => Promise<T>): Promise<T> {
  const nextOperation = eventOutboxOperation.then(operation, operation);
  eventOutboxOperation = nextOperation.then(
    () => undefined,
    () => undefined
  );
  return nextOperation;
}

function buildPackageCache(
  packages: StoryPackageManifestV1[]
): PackageCacheRecord {
  return packages.reduce<PackageCacheRecord>((accumulator, storyPackage) => {
    accumulator[storyPackage.package_id] = storyPackage;
    return accumulator;
  }, {});
}

export async function loadPersistedHomePackages(): Promise<StoryPackageManifestV1[]> {
  return loadJsonValue<StoryPackageManifestV1[]>(HOME_PACKAGES_KEY, []);
}

export async function persistHomePackages(
  packages: StoryPackageManifestV1[]
): Promise<void> {
  await saveJsonValue(HOME_PACKAGES_KEY, packages);
  await saveJsonValue(PACKAGE_CACHE_KEY, buildPackageCache(packages));
}

export async function loadPersistedPackageCache(): Promise<PackageCacheRecord> {
  return loadJsonValue<PackageCacheRecord>(PACKAGE_CACHE_KEY, {});
}

export async function persistPackage(
  storyPackage: StoryPackageManifestV1
): Promise<void> {
  const packageCache = await loadPersistedPackageCache();
  packageCache[storyPackage.package_id] = storyPackage;
  await saveJsonValue(PACKAGE_CACHE_KEY, packageCache);
}

export async function loadPersistedSessionSnapshot(): Promise<PersistedSessionSnapshot | null> {
  return loadJsonValue<PersistedSessionSnapshot | null>(SESSION_SNAPSHOT_KEY, null);
}

export async function persistSessionSnapshot(
  snapshot: PersistedSessionSnapshot
): Promise<void> {
  await saveJsonValue(SESSION_SNAPSHOT_KEY, snapshot);
}

export async function clearSessionSnapshot(): Promise<void> {
  await AsyncStorage.removeItem(SESSION_SNAPSHOT_KEY);
}

export async function loadQueuedEvents(): Promise<ReadingEventV1[]> {
  return loadJsonValue<ReadingEventV1[]>(EVENT_OUTBOX_KEY, []);
}

export async function replaceQueuedEvents(events: ReadingEventV1[]): Promise<void> {
  await runEventOutboxOperation(async () => {
    await saveJsonValue(EVENT_OUTBOX_KEY, events);
  });
}

export async function queueEvents(events: ReadingEventV1[]): Promise<ReadingEventV1[]> {
  return runEventOutboxOperation(async () => {
    const previousEvents = await loadJsonValue<ReadingEventV1[]>(
      EVENT_OUTBOX_KEY,
      []
    );
    const mergedEvents = [...previousEvents, ...events];
    await saveJsonValue(EVENT_OUTBOX_KEY, mergedEvents);
    return mergedEvents;
  });
}

export async function removeQueuedEventsById(
  eventIds: string[]
): Promise<ReadingEventV1[]> {
  return runEventOutboxOperation(async () => {
    const activeIds = new Set(eventIds);
    const previousEvents = await loadJsonValue<ReadingEventV1[]>(
      EVENT_OUTBOX_KEY,
      []
    );
    const remainingEvents = previousEvents.filter(
      event => !activeIds.has(event.event_id)
    );
    await saveJsonValue(EVENT_OUTBOX_KEY, remainingEvents);
    return remainingEvents;
  });
}
