import type {
  ChildHomeV1,
  ReadingEventBatchRequestV2,
  ReadingEventIngestedResponseV2,
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";

export interface ReadingApplicationClient {
  getChildHome(childId: string): Promise<ChildHomeV1>;
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

export interface ChildHomeLookupService {
  load(childId: string): Promise<ChildHomeV1>;
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
  childHome: ChildHomeLookupService;
  storyPackages: StoryPackageLookupService;
  readingSessions: ReadingSessionCommandService;
  readingEvents: ReadingEventCommandService;
}

export function createReadingApplicationServices(
  client: ReadingApplicationClient,
): ReadingApplicationServices {
  return {
    childHome: {
      async load(childId: string) {
        return client.getChildHome(childId);
      },
    },
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
