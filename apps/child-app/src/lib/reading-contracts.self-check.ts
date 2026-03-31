import type { StoryPackageManifestV1 } from '@lumosreading/contracts';

import {
  buildReadingEventBatch,
  buildReadingSessionPayload,
  resolveStoryPackageLanguageMode,
} from './reading-contracts';

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

const englishPackage = {
  schema_version: 'story-package.v1',
  package_id: '99999999-9999-9999-9999-999999999999',
  story_master_id: 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  story_variant_id: 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  title: 'Bridge Words',
  subtitle: 'English narration with optional translation support.',
  language_mode: 'en-US',
  difficulty_level: 'L3',
  age_band: '6-8',
  estimated_duration_sec: 540,
  release_channel: 'pilot',
  cover_image_url: 'https://schemas.lumosreading.local/demo/bridge-words.png',
  tags: ['bridge'],
  safety: {
    review_status: 'approved',
  },
  pages: [],
} satisfies StoryPackageManifestV1;

const languageMode = resolveStoryPackageLanguageMode(englishPackage);

const sessionPayload = buildReadingSessionPayload({
  childId: '55555555-5555-5555-5555-555555555555',
  packageId: englishPackage.package_id,
  languageMode,
});

assert(
  sessionPayload.language_mode === 'en-US',
  'ReadingSessionCreateV2.language_mode should follow the selected package.'
);

const eventBatch = buildReadingEventBatch({
  eventType: 'session_started',
  sessionId: 'd1d3a8c0-05f3-45bd-9a56-72a911200099',
  childId: sessionPayload.child_id,
  packageId: sessionPayload.package_id,
  platform: 'ipadOS',
  languageMode,
  payload: {
    source: 'self-check',
  },
  createEventId: () => 'c1d3a8c0-05f3-45bd-9a56-72a911200199',
});

assert(
  eventBatch.events[0]?.language_mode === 'en-US',
  'ReadingEventV1.language_mode should follow the selected package.'
);

console.log(
  JSON.stringify(
    {
      checked: [
        'resolveStoryPackageLanguageMode english package',
        'buildReadingSessionPayload uses package language',
        'buildReadingEventBatch uses package language',
      ],
      count: 3,
    },
    null,
    2
  )
);
