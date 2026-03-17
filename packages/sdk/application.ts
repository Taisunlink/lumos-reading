import type {
  ReadingEventBatchRequestV2,
  ReadingEventIngestedResponseV2,
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";

export interface ReadingApplicationClient {
  getStoryPackage(packageId: string): Promise<StoryPackageManifestV1>;
  createReadingSession(
    payload: ReadingSessionCreateV2,
  ): Promise<ReadingSessionResponseV2>;
  ingestReadingEvents(
    payload: ReadingEventBatchRequestV2,
  ): Promise<ReadingEventIngestedResponseV2>;
}

export interface StoryPackageLookupService {
  lookup(packageId: string): Promise<StoryPackageManifestV1>;
}

export interface ReadingSessionCommandService {
  start(payload: ReadingSessionCreateV2): Promise<ReadingSessionResponseV2>;
}

export interface ReadingEventCommandService {
  ingestBatch(
    payload: ReadingEventBatchRequestV2,
  ): Promise<ReadingEventIngestedResponseV2>;
}

export interface ReadingApplicationServices {
  storyPackages: StoryPackageLookupService;
  readingSessions: ReadingSessionCommandService;
  readingEvents: ReadingEventCommandService;
}

export function createReadingApplicationServices(
  client: ReadingApplicationClient,
): ReadingApplicationServices {
  return {
    storyPackages: {
      async lookup(packageId: string) {
        return client.getStoryPackage(packageId);
      },
    },
    readingSessions: {
      async start(payload: ReadingSessionCreateV2) {
        return client.createReadingSession(payload);
      },
    },
    readingEvents: {
      async ingestBatch(payload: ReadingEventBatchRequestV2) {
        return client.ingestReadingEvents(payload);
      },
    },
  };
}
