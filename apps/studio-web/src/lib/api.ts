import {
  DEFAULT_LUMOS_API_BASE_URL,
  createLumosApiClient,
  createMonetizationServices,
  createStoryGenerationServices,
  createStoryPackageReleaseServices,
} from "@lumosreading/sdk";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_LUMOS_API_BASE_URL;

export const apiClient = createLumosApiClient({
  baseUrl: API_BASE_URL,
});

export const monetizationServices = createMonetizationServices(apiClient);
export const storyGenerationServices = createStoryGenerationServices(apiClient);
export const storyPackageReleaseServices = createStoryPackageReleaseServices(apiClient);
