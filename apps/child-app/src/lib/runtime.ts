import { Platform } from 'react-native';
import { Asset } from 'expo-asset';

import {
  READING_EVENT_SCHEMA_VERSION,
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
  type ReadingApplicationClient,
} from '@lumosreading/sdk';

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

type BuildReadingSessionPayloadOptions = {
  childId?: string;
  packageId?: string;
};

type BuildReadingEventBatchOptions = {
  eventType: Extract<
    ReadingEventType,
    | 'session_started'
    | 'page_viewed'
    | 'page_replayed_audio'
    | 'word_revealed_translation'
    | 'session_completed'
  >;
  sessionId: string;
  childId: string;
  packageId: string;
  pageIndex?: number | null;
  payload: Record<string, unknown>;
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

export async function loadRuntimeLibrary(): Promise<StoryPackageManifestV1[]> {
  if (childRuntime.mode === 'demo') {
    return [...demoPackageQueue];
  }

  const defaultPackage = await childRuntime.services.storyPackages.lookup(
    childRuntime.defaultPackageId
  );
  return [defaultPackage];
}

export function buildReadingSessionPayload(
  options: BuildReadingSessionPayloadOptions = {}
): ReadingSessionCreateV2 {
  return {
    child_id: options.childId ?? childRuntime.defaultChildId,
    package_id: options.packageId ?? childRuntime.defaultPackageId,
    started_at: new Date().toISOString(),
    mode: 'read_to_me',
    language_mode: 'zh-CN',
    assist_mode: ['read_aloud_sync', 'focus_support'],
  };
}

export function buildReadingEventBatch(
  options: BuildReadingEventBatchOptions
): ReadingEventBatchRequestV2 {
  const occurredAt = new Date().toISOString();

  return {
    events: [
      {
        schema_version: READING_EVENT_SCHEMA_VERSION,
        event_id: `${options.eventType}-${Date.now()}`,
        event_type: options.eventType,
        occurred_at: occurredAt,
        session_id: options.sessionId,
        child_id: options.childId,
        package_id: options.packageId,
        page_index: options.pageIndex ?? null,
        platform: getPlatform(),
        surface: 'child-app',
        app_version: '0.1.0-dev',
        language_mode: 'zh-CN',
        payload: options.payload,
      },
    ],
  };
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
  eventType: BuildReadingEventBatchOptions['eventType'],
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
