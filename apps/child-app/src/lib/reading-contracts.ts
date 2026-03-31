import type {
  LanguageTag,
  Platform as RuntimePlatform,
  ReadingEventBatchRequestV2,
  ReadingEventType,
  ReadingSessionCreateV2,
  StoryPackageManifestV1,
} from '@lumosreading/contracts';

export const DEFAULT_RUNTIME_LANGUAGE_MODE = 'zh-CN' as const;
export const DEFAULT_RUNTIME_ASSIST_MODE = [
  'read_aloud_sync',
  'focus_support',
] as const;

type RuntimeLanguageSource =
  | Pick<StoryPackageManifestV1, 'language_mode'>
  | null
  | undefined;

export type BuildReadingSessionPayloadOptions = {
  childId: string;
  packageId: string;
  languageMode?: LanguageTag;
  assistMode?: string[];
  startedAt?: string;
};

export type BuildReadingEventBatchOptions = {
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
  platform: RuntimePlatform;
  payload: Record<string, unknown>;
  languageMode?: LanguageTag;
  pageIndex?: number | null;
  appVersion?: string;
  occurredAt?: string;
  createEventId?: () => string;
};

export function resolveStoryPackageLanguageMode(
  storyPackage: RuntimeLanguageSource,
  fallbackLanguageMode: LanguageTag = DEFAULT_RUNTIME_LANGUAGE_MODE
): LanguageTag {
  return storyPackage?.language_mode ?? fallbackLanguageMode;
}

export function buildReadingSessionPayload(
  options: BuildReadingSessionPayloadOptions
): ReadingSessionCreateV2 {
  return {
    child_id: options.childId,
    package_id: options.packageId,
    started_at: options.startedAt ?? new Date().toISOString(),
    mode: 'read_to_me',
    language_mode:
      options.languageMode ?? DEFAULT_RUNTIME_LANGUAGE_MODE,
    assist_mode: options.assistMode
      ? [...options.assistMode]
      : [...DEFAULT_RUNTIME_ASSIST_MODE],
  };
}

export function buildReadingEventBatch(
  options: BuildReadingEventBatchOptions
): ReadingEventBatchRequestV2 {
  const createEventId =
    options.createEventId ?? globalThis.crypto?.randomUUID?.bind(globalThis.crypto);

  if (!createEventId) {
    throw new Error('No event id generator is available for runtime events.');
  }

  return {
    events: [
      {
        schema_version: 'reading-event.v1',
        event_id: createEventId(),
        event_type: options.eventType,
        occurred_at: options.occurredAt ?? new Date().toISOString(),
        session_id: options.sessionId,
        child_id: options.childId,
        package_id: options.packageId,
        page_index: options.pageIndex ?? null,
        platform: options.platform,
        surface: 'child-app',
        app_version: options.appVersion ?? '0.1.0-dev',
        language_mode:
          options.languageMode ?? DEFAULT_RUNTIME_LANGUAGE_MODE,
        payload: options.payload,
      },
    ],
  };
}
