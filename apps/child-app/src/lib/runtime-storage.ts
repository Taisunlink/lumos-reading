import AsyncStorage from '@react-native-async-storage/async-storage';
import { Directory, File, Paths } from 'expo-file-system';
import { Platform } from 'react-native';

import type {
  ChildHomeV1,
  ReadingEventBatchRequestV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from '@lumosreading/contracts';

const CHILD_RUNTIME_STORAGE_KEY = 'lumosreading.v2.child-runtime';
const CHILD_RUNTIME_STORAGE_VERSION = 1;

export type RuntimeActivityRecord = {
  id: string;
  label: string;
  timestamp: string;
};

export type PersistedActiveSessionSnapshot = {
  sessionReceipt: ReadingSessionResponseV2;
  currentPageIndex: number;
  translationVisible: boolean;
  pageEnteredAtMs: number;
};

export type QueuedReadingEventBatch = {
  id: string;
  batch: ReadingEventBatchRequestV2;
  queuedAt: string;
  attemptCount: number;
  lastAttemptAt: string | null;
};

export type PersistedChildRuntimeState = {
  version: number;
  childHome: ChildHomeV1 | null;
  packageCache: StoryPackageManifestV1[];
  activePackageId: string | null;
  activeSession: PersistedActiveSessionSnapshot | null;
  pendingEventQueue: QueuedReadingEventBatch[];
  activity: RuntimeActivityRecord[];
  lastEventFlushAt: string | null;
};

type FlushQueuedReadingEventsArgs = {
  queue: QueuedReadingEventBatch[];
  ingestBatch: (
    payload: ReadingEventBatchRequestV2
  ) => Promise<unknown>;
};

type FlushQueuedReadingEventsResult = {
  queue: QueuedReadingEventBatch[];
  flushedCount: number;
};

function getDefaultChildRuntimeState(): PersistedChildRuntimeState {
  return {
    version: CHILD_RUNTIME_STORAGE_VERSION,
    childHome: null,
    packageCache: [],
    activePackageId: null,
    activeSession: null,
    pendingEventQueue: [],
    activity: [],
    lastEventFlushAt: null,
  };
}

function createStorageUuid(): string {
  const randomUuid = globalThis.crypto?.randomUUID?.bind(globalThis.crypto);

  if (randomUuid) {
    return randomUuid();
  }

  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, char => {
    const random = Math.floor(Math.random() * 16);
    const value = char === 'x' ? random : ((random & 0x3) | 0x8);
    return value.toString(16);
  });
}

function isRemoteHttpUri(uri: string): boolean {
  return /^https?:\/\//i.test(uri);
}

function getSafeFileExtension(uri: string, fallback: string): string {
  try {
    const pathname = new URL(uri).pathname;
    const lastDotIndex = pathname.lastIndexOf('.');

    if (lastDotIndex === -1) {
      return fallback;
    }

    const extension = pathname.slice(lastDotIndex);
    return /^[.A-Za-z0-9_-]+$/.test(extension) ? extension : fallback;
  } catch {
    return fallback;
  }
}

async function cacheRemoteFile(
  uri: string,
  destinationPathSegments: string[],
  fallbackExtension: string
): Promise<string> {
  if (Platform.OS === 'web' || !isRemoteHttpUri(uri)) {
    return uri;
  }

  const fileName = destinationPathSegments[destinationPathSegments.length - 1];
  const directorySegments = destinationPathSegments.slice(0, -1);
  const runtimeDirectory = new Directory(
    Paths.document,
    'lumosreading',
    'story-packages',
    ...directorySegments
  );
  runtimeDirectory.create({ intermediates: true, idempotent: true });

  const extension = getSafeFileExtension(uri, fallbackExtension);
  const targetFile = new File(runtimeDirectory, `${fileName}${extension}`);

  if (!targetFile.exists) {
    await File.downloadFileAsync(uri, targetFile, { idempotent: true });
  }

  return targetFile.uri;
}

export async function cacheStoryPackageForOffline(
  storyPackage: StoryPackageManifestV1
): Promise<StoryPackageManifestV1> {
  if (Platform.OS === 'web') {
    return storyPackage;
  }

  const coverImageUrl = storyPackage.cover_image_url
    ? await cacheRemoteFile(
        storyPackage.cover_image_url,
        [storyPackage.package_id, 'cover'],
        '.png'
      ).catch(() => storyPackage.cover_image_url)
    : undefined;

  const pages = await Promise.all(
    storyPackage.pages.map(async page => {
      const imageUrl = page.media?.image_url
        ? await cacheRemoteFile(
            page.media.image_url,
            [storyPackage.package_id, `page-${page.page_index}-image`],
            '.png'
          ).catch(() => page.media?.image_url ?? undefined)
        : undefined;
      const audioUrl = page.media?.audio_url
        ? await cacheRemoteFile(
            page.media.audio_url,
            [storyPackage.package_id, `page-${page.page_index}-audio`],
            '.mp3'
          ).catch(() => page.media?.audio_url ?? undefined)
        : undefined;

      return {
        ...page,
        media:
          imageUrl || audioUrl || page.media?.thumbnail_url
            ? {
                ...page.media,
                image_url: imageUrl,
                audio_url: audioUrl,
              }
            : page.media,
      };
    })
  );

  return {
    ...storyPackage,
    cover_image_url: coverImageUrl,
    pages,
  };
}

export async function loadPersistedRuntimeState(): Promise<PersistedChildRuntimeState> {
  const rawValue = await AsyncStorage.getItem(CHILD_RUNTIME_STORAGE_KEY);

  if (!rawValue) {
    return getDefaultChildRuntimeState();
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<PersistedChildRuntimeState>;

    if (parsed.version !== CHILD_RUNTIME_STORAGE_VERSION) {
      return getDefaultChildRuntimeState();
    }

    return {
      version: CHILD_RUNTIME_STORAGE_VERSION,
      childHome: parsed.childHome ?? null,
      packageCache: parsed.packageCache ?? [],
      activePackageId: parsed.activePackageId ?? null,
      activeSession: parsed.activeSession ?? null,
      pendingEventQueue: parsed.pendingEventQueue ?? [],
      activity: parsed.activity ?? [],
      lastEventFlushAt: parsed.lastEventFlushAt ?? null,
    };
  } catch {
    return getDefaultChildRuntimeState();
  }
}

export async function persistRuntimeState(
  snapshot: PersistedChildRuntimeState
): Promise<void> {
  await AsyncStorage.setItem(
    CHILD_RUNTIME_STORAGE_KEY,
    JSON.stringify(snapshot)
  );
}

export function buildQueuedReadingEventBatch(
  batch: ReadingEventBatchRequestV2
): QueuedReadingEventBatch {
  return {
    id: createStorageUuid(),
    batch,
    queuedAt: new Date().toISOString(),
    attemptCount: 0,
    lastAttemptAt: null,
  };
}

export async function flushQueuedReadingEvents(
  args: FlushQueuedReadingEventsArgs
): Promise<FlushQueuedReadingEventsResult> {
  let workingQueue = [...args.queue];
  let flushedCount = 0;

  for (const queueItem of args.queue) {
    try {
      await args.ingestBatch(queueItem.batch);
      workingQueue = workingQueue.filter(item => item.id !== queueItem.id);
      flushedCount += 1;
    } catch {
      workingQueue = workingQueue.map(item =>
        item.id === queueItem.id
          ? {
              ...item,
              attemptCount: item.attemptCount + 1,
              lastAttemptAt: new Date().toISOString(),
            }
          : item
      );
      break;
    }
  }

  return {
    queue: workingQueue,
    flushedCount,
  };
}
