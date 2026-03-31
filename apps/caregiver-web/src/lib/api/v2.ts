import {
  DEFAULT_LUMOS_API_BASE_URL,
  createCaregiverSubdomainServices,
  createMonetizationServices,
  createReadingApplicationServices,
  createLumosApiClient,
} from "@lumosreading/sdk";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_LUMOS_API_BASE_URL;

export const apiClient = createLumosApiClient({
  baseUrl: API_BASE_URL,
});

export const caregiverSubdomainServices = createCaregiverSubdomainServices(apiClient);
export const monetizationServices = createMonetizationServices(apiClient);
export const readingApplicationServices = createReadingApplicationServices(apiClient);

export const getCaregiverHousehold = apiClient.getCaregiverHousehold;
export const getCaregiverChildren = apiClient.getCaregiverChildren;
export const getCaregiverPlan = apiClient.getCaregiverPlan;
export const getCaregiverProgress = apiClient.getCaregiverProgress;
export const getCaregiverDashboard = apiClient.getCaregiverDashboard;
export const getHouseholdEntitlement = apiClient.getHouseholdEntitlement;
export const getWeeklyValueReport = apiClient.getWeeklyValueReport;
export const getStoryPackage = apiClient.getStoryPackage;
export const createReadingSession = apiClient.createReadingSession;
export const ingestReadingEvents = apiClient.ingestReadingEvents;
