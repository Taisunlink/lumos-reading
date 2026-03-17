export const DEFAULT_PLACEHOLDER_OSS_PUBLIC_BASE_URL =
  "https://oss-placeholder.lumosreading.local" as const;

export interface ObjectStorageService {
  getPublicUrl(objectKey: string): string;
  getSignedUrl(objectKey: string, expiresInSeconds: number): string;
}

export type PlaceholderOssStorageOptions = {
  publicBaseUrl?: string;
};

function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, "");
}

function normalizeObjectKey(objectKey: string): string {
  return objectKey
    .split("/")
    .filter(Boolean)
    .map((segment) => encodeURIComponent(segment))
    .join("/");
}

export class PlaceholderOssStorageService implements ObjectStorageService {
  readonly publicBaseUrl: string;

  constructor(publicBaseUrl: string = DEFAULT_PLACEHOLDER_OSS_PUBLIC_BASE_URL) {
    this.publicBaseUrl = normalizeBaseUrl(publicBaseUrl);
  }

  getPublicUrl(objectKey: string): string {
    const normalizedKey = normalizeObjectKey(objectKey);

    if (!normalizedKey) {
      return this.publicBaseUrl;
    }

    return `${this.publicBaseUrl}/${normalizedKey}`;
  }

  getSignedUrl(objectKey: string, expiresInSeconds: number): string {
    void expiresInSeconds;
    return this.getPublicUrl(objectKey);
  }
}

export function createPlaceholderOssStorageService(
  options: PlaceholderOssStorageOptions = {},
): PlaceholderOssStorageService {
  return new PlaceholderOssStorageService(options.publicBaseUrl);
}
