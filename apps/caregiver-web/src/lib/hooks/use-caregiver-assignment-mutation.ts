"use client";

import { startTransition, useState } from "react";
import type {
  CaregiverAssignmentCommandV1,
  CaregiverAssignmentResponseV1,
} from "@lumosreading/contracts";
import { caregiverSubdomainServices } from "@/lib/api/v2";

type MutationStatus = "idle" | "pending" | "success" | "error";

export function useCaregiverAssignmentMutation() {
  const [data, setData] = useState<CaregiverAssignmentResponseV1 | null>(null);
  const [status, setStatus] = useState<MutationStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  async function mutate(
    payload: CaregiverAssignmentCommandV1,
  ): Promise<CaregiverAssignmentResponseV1> {
    setStatus("pending");
    setError(null);

    try {
      const response = await caregiverSubdomainServices.children.assignPackage(payload);

      startTransition(() => {
        setData(response);
        setStatus("success");
      });

      return response;
    } catch (caught) {
      const message =
        caught instanceof Error ? caught.message : "Failed to assign the reading package.";

      startTransition(() => {
        setStatus("error");
        setError(message);
      });

      throw caught;
    }
  }

  return {
    data,
    status,
    error,
    mutate,
  };
}
