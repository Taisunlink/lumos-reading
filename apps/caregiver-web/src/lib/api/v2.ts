import { DEFAULT_LUMOS_API_BASE_URL, createLumosApiClient } from "@lumosreading/sdk";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_LUMOS_API_BASE_URL;

export const apiClient = createLumosApiClient({
  baseUrl: API_BASE_URL,
});

export const getCaregiverHousehold = apiClient.getCaregiverHousehold;
export const getCaregiverChildren = apiClient.getCaregiverChildren;
export const getCaregiverPlan = apiClient.getCaregiverPlan;
export const getCaregiverProgress = apiClient.getCaregiverProgress;
export const getCaregiverDashboard = apiClient.getCaregiverDashboard;
export const getStoryPackage = apiClient.getStoryPackage;
export const createReadingSession = apiClient.createReadingSession;
export const ingestReadingEvents = apiClient.ingestReadingEvents;
