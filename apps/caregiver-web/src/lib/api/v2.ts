import type {
  ReadingSessionCreateV2,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from "@lumosreading/contracts";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v2";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`API ${response.status}: ${message}`);
  }

  return (await response.json()) as T;
}

export function getStoryPackage(packageId: string): Promise<StoryPackageManifestV1> {
  return request<StoryPackageManifestV1>(`/story-packages/${packageId}`);
}

export function createReadingSession(
  payload: ReadingSessionCreateV2,
): Promise<ReadingSessionResponseV2> {
  return request<ReadingSessionResponseV2>("/reading-sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
