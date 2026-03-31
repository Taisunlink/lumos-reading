import { Platform } from 'react-native';
import { Asset } from 'expo-asset';

import {
  type ChildHomeV1,
  type Platform as RuntimePlatform,
  type ReadingEventBatchRequestV2,
  type ReadingEventType,
  type ReadingSessionCreateV2,
  type StoryPackageManifestV1,
  type StoryPackagePageV1,
} from '@lumosreading/contracts';
import {
  DEFAULT_LUMOS_API_BASE_URL,
  buildDemoReadingEventIngestedResponse,
  buildDemoReadingSessionResponse,
  createLumosApiClient,
  createReadingApplicationServices,
  demoChildId,
  demoPackageQueue,
  demoStoryPackage,
  demoStoryPackageId,
  fallbackChildHome,
  type ReadingApplicationClient,
} from '@lumosreading/sdk';

import { cacheStoryPackageForOffline } from '@/lib/runtime-storage';
import {
  buildReadingEventBatch,
  buildReadingSessionPayload,
  type BuildReadingEventBatchOptions,
} from '@/lib/reading-contracts';

export type ChildRuntimeMode = 'demo' | 'api';
export type RuntimeAssetSource = number | string;

export type ResolvedRuntimePage = StoryPackagePageV1 & {
  text: string;
  runtime_media: {
    imageSource: RuntimeAssetSource | null;
    audioSource: RuntimeAssetSource | null;
    imageUri: string | null;
    audioUri: string | null;
    preloadSources: RuntimeAssetSource[];
    usesBundledFallbacks: boolean;
  };
};

export type RuntimePreloadResult = {
  readyPageIndexes: number[];
  failedPageIndexes: number[];
};

const bundledDemoImageSources = [
  require('../../assets/images/icon.png'),
  require('../../assets/images/splash-icon.png'),
] as const;
const bundledDemoAudioSource = require('../../assets/audio/demo-page.wav');

function getRuntimeMode(): ChildRuntimeMode {
  return process.env.EXPO_PUBLIC_RUNTIME_MODE === 'api' ? 'api' : 'demo';
}

function getPlatform(): RuntimePlatform {
  if (Platform.OS === 'ios') {
    return 'ipadOS';
  }

  if (Platform.OS === 'android') {
    return 'android';
  }

  if (Platform.OS === 'web') {
    return 'web';
  }

  return 'unknown';
}

const demoApplicationClient: ReadingApplicationClient = {
  async getChildHome(childId: string): Promise<ChildHomeV1> {
    return {
      ...fallbackChildHome,
      child_id: childId,
      current_package_id:
        fallbackChildHome.current_package_id ?? demoStoryPackage.package_id,
      generated_at: new Date().toISOString(),
    };
  },
  async getStoryPackage(packageId: string): Promise<StoryPackageManifestV1> {
    const storyPackage =
      demoPackageQueue.find(item => item.package_id === packageId) ??
      demoStoryPackage;

    return storyPackage;
  },
  async createReadingSession(payload: ReadingSessionCreateV2) {
    return buildDemoReadingSessionResponse({
      childId: payload.child_id,
      packageId: payload.package_id,
      acceptedAt: new Date().toISOString(),
    });
  },
  async ingestReadingEvents(payload: ReadingEventBatchRequestV2) {
    return buildDemoReadingEventIngestedResponse({
      acceptedAt: new Date().toISOString(),
      acceptedCount: payload.events.length,
      sessionIds: Array.from(
        new Set(payload.events.map(event => event.session_id))
      ),
    });
  },
};

const runtimeMode = getRuntimeMode();
const apiBaseUrl =
  process.env.EXPO_PUBLIC_API_BASE_URL ?? DEFAULT_LUMOS_API_BASE_URL;

const applicationClient =
  runtimeMode === 'api'
    ? createLumosApiClient({ baseUrl: apiBaseUrl })
    : demoApplicationClient;

export const childRuntime = {
  mode: runtimeMode,
  apiBaseUrl,
  defaultChildId: process.env.EXPO_PUBLIC_DEFAULT_CHILD_ID ?? demoChildId,
  defaultPackageId:
    process.env.EXPO_PUBLIC_DEFAULT_STORY_PACKAGE_ID ?? demoStoryPackageId,
  services: createReadingApplicationServices(applicationClient),
} as const;

export async function loadChildHome(
  childId: string = childRuntime.defaultChildId
): Promise<ChildHomeV1> {
  const childHome =
    childRuntime.mode === 'demo'
      ? {
          ...fallbackChildHome,
          child_id: childId,
          current_package_id:
            fallbackChildHome.current_package_id ?? demoStoryPackage.package_id,
          generated_at: new Date().toISOString(),
        }
      : await childRuntime.services.childHome.load(childId);

  if (childRuntime.mode === 'demo') {
    return childHome;
  }

  return {
    ...childHome,
    package_queue: await Promise.all(
      childHome.package_queue.map(storyPackage =>
        cacheStoryPackageForOffline(storyPackage)
      )
    ),
  };
}

export async function loadRuntimeLibrary(): Promise<StoryPackageManifestV1[]> {
  const childHome = await loadChildHome();
  return childHome.package_queue;
}

export function createRuntimeUuid(): string {
  const randomUuid = globalThis.crypto?.randomUUID?.bind(globalThis.crypto);

  if (randomUuid) {
    return randomUuid();
  }

  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, token => {
    const randomValue = Math.floor(Math.random() * 16);
    const value = token === 'x' ? randomValue : (randomValue & 0x3) | 0x8;
    return value.toString(16);
  });
}

export function buildOfflineReadingSessionReceipt(args: {
  childId: string;
  packageId: string;
}) {
  return buildDemoReadingSessionResponse({
    sessionId: createRuntimeUuid(),
    childId: args.childId,
    packageId: args.packageId,
    acceptedAt: new Date().toISOString(),
  });
}

function buildPageText(page: StoryPackagePageV1): string {
  return page.text_runs.map(run => run.text).join(' ');
}

function uniqueAssetSources(
  sources: Array<RuntimeAssetSource | null | undefined>
): RuntimeAssetSource[] {
  return Array.from(
    new Set(
      sources.filter(
        (source): source is RuntimeAssetSource =>
          source !== null && source !== undefined
      )
    )
  );
}

function getBundledDemoImageSource(pageIndex: number): number {
  return bundledDemoImageSources[pageIndex % bundledDemoImageSources.length];
}

export function getRuntimePreloadPageIndexes(
  storyPackage: StoryPackageManifestV1,
  currentPageIndex: number
): number[] {
  return [currentPageIndex, currentPageIndex + 1].filter(
    (pageIndex, position, candidates) =>
      pageIndex >= 0 &&
      pageIndex < storyPackage.pages.length &&
      candidates.indexOf(pageIndex) === position
  );
}

export function resolveRuntimePage(
  storyPackage: StoryPackageManifestV1,
  pageIndex: number
): ResolvedRuntimePage | null {
  const page = storyPackage.pages[pageIndex];

  if (!page) {
    return null;
  }

  const usesBundledFallbacks = childRuntime.mode === 'demo';
  const fallbackImageSource = getBundledDemoImageSource(page.page_index);
  const imageSource = usesBundledFallbacks
    ? fallbackImageSource
    : (page.media?.image_url ??
      storyPackage.cover_image_url ??
      fallbackImageSource);
  const audioSource = usesBundledFallbacks
    ? bundledDemoAudioSource
    : (page.media?.audio_url ?? null);

  return {
    ...page,
    text: buildPageText(page),
    runtime_media: {
      imageSource,
      audioSource,
      imageUri: typeof imageSource === 'string' ? imageSource : null,
      audioUri: typeof audioSource === 'string' ? audioSource : null,
      preloadSources: uniqueAssetSources([imageSource, audioSource]),
      usesBundledFallbacks,
    },
  };
}

export async function preloadRuntimePageAssets(
  storyPackage: StoryPackageManifestV1,
  pageIndexes: number[]
): Promise<RuntimePreloadResult> {
  const settled = await Promise.all(
    pageIndexes.map(async pageIndex => {
      const resolvedPage = resolveRuntimePage(storyPackage, pageIndex);

      if (
        !resolvedPage ||
        resolvedPage.runtime_media.preloadSources.length === 0
      ) {
        return { pageIndex, ready: true };
      }

      try {
        const bundledModuleIds =
          resolvedPage.runtime_media.preloadSources.filter(
            (source): source is number => typeof source === 'number'
          );
        const remoteUris = resolvedPage.runtime_media.preloadSources.filter(
          (source): source is string => typeof source === 'string'
        );

        if (bundledModuleIds.length > 0) {
          await Asset.loadAsync(bundledModuleIds);
        }

        if (remoteUris.length > 0) {
          await Asset.loadAsync(remoteUris);
        }

        return { pageIndex, ready: true };
      } catch {
        return { pageIndex, ready: false };
      }
    })
  );

  return {
    readyPageIndexes: settled
      .filter(item => item.ready)
      .map(item => item.pageIndex),
    failedPageIndexes: settled
      .filter(item => !item.ready)
      .map(item => item.pageIndex),
  };
}

export function getRuntimeEventLabel(
  eventType: Extract<
    ReadingEventType,
    | 'session_started'
    | 'page_viewed'
    | 'page_replayed_audio'
    | 'word_revealed_translation'
    | 'session_completed'
  >,
  pageIndex?: number | null
): string {
  const pageLabel =
    typeof pageIndex === 'number' ? `page ${pageIndex + 1}` : 'the active page';

  if (eventType === 'session_started') {
    return 'Accepted session_started for the child runtime handoff.';
  }

  if (eventType === 'page_viewed') {
    return `Logged page_viewed for ${pageLabel}.`;
  }

  if (eventType === 'page_replayed_audio') {
    return `Logged page_replayed_audio for ${pageLabel}.`;
  }

  if (eventType === 'word_revealed_translation') {
    return `Logged word_revealed_translation for ${pageLabel}.`;
  }

  return 'Logged session_completed and returned the child to the home shelf.';
}

export async function loadRuntimeStoryPackage(
  packageId: string,
  childId: string = childRuntime.defaultChildId,
): Promise<StoryPackageManifestV1> {
  const storyPackage = await childRuntime.services.storyPackages.lookup(
    packageId,
    childId,
  );

  if (childRuntime.mode === 'demo') {
    return storyPackage;
  }

  return cacheStoryPackageForOffline(storyPackage);
}

export {
  buildReadingEventBatch,
  buildReadingSessionPayload,
};

export function getRuntimePlatform(): RuntimePlatform {
  return getPlatform();
}
