import { Platform } from 'react-native';

import {
  READING_EVENT_SCHEMA_VERSION,
  type Platform as RuntimePlatform,
  type ReadingEventBatchRequestV2,
  type ReadingEventType,
  type ReadingSessionCreateV2,
  type StoryPackageManifestV1,
} from '@lumosreading/contracts';
import {
  DEFAULT_LUMOS_API_BASE_URL,
  buildDemoReadingEventIngestedResponse,
  buildDemoReadingSessionResponse,
  createLumosApiClient,
  createReadingApplicationServices,
  demoChildId,
  demoStoryPackage,
  demoStoryPackageId,
  type ReadingApplicationClient,
} from '@lumosreading/sdk';

export type ChildRuntimeMode = 'demo' | 'api';

type BuildReadingSessionPayloadOptions = {
  childId?: string;
  packageId?: string;
};

type BuildReadingEventBatchOptions = {
  eventType: Extract<
    ReadingEventType,
    'page_viewed' | 'page_replayed_audio' | 'word_revealed_translation'
  >;
  sessionId: string;
  childId: string;
  packageId: string;
  pageIndex?: number | null;
  payload: Record<string, unknown>;
};

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
    if (packageId === demoStoryPackage.package_id) {
      return demoStoryPackage;
    }

    return {
      ...demoStoryPackage,
      package_id: packageId,
    };
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
      sessionIds: Array.from(new Set(payload.events.map((event) => event.session_id))),
    });
  },
};

const runtimeMode = getRuntimeMode();
const apiBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL ?? DEFAULT_LUMOS_API_BASE_URL;

const applicationClient =
  runtimeMode === 'api' ? createLumosApiClient({ baseUrl: apiBaseUrl }) : demoApplicationClient;

export const childRuntime = {
  mode: runtimeMode,
  apiBaseUrl,
  defaultChildId: process.env.EXPO_PUBLIC_DEFAULT_CHILD_ID ?? demoChildId,
  defaultPackageId: process.env.EXPO_PUBLIC_DEFAULT_STORY_PACKAGE_ID ?? demoStoryPackageId,
  services: createReadingApplicationServices(applicationClient),
} as const;

export function buildReadingSessionPayload(
  options: BuildReadingSessionPayloadOptions = {},
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
  options: BuildReadingEventBatchOptions,
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
