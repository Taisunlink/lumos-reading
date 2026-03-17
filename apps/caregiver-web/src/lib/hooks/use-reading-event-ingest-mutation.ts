"use client";

import { startTransition, useState } from "react";
import type {
  ReadingEventBatchRequestV2,
  ReadingEventIngestedResponseV2,
} from "@lumosreading/contracts";
import { readingApplicationServices } from "@/lib/api/v2";

type MutationStatus = "idle" | "pending" | "success" | "error";

export function useReadingEventIngestMutation() {
  const [data, setData] = useState<ReadingEventIngestedResponseV2 | null>(null);
  const [status, setStatus] = useState<MutationStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  async function mutate(
    payload: ReadingEventBatchRequestV2,
  ): Promise<ReadingEventIngestedResponseV2> {
    setStatus("pending");
    setError(null);

    try {
      const response = await readingApplicationServices.readingEvents.ingestBatch(payload);

      startTransition(() => {
        setData(response);
        setStatus("success");
      });

      return response;
    } catch (caught) {
      const message =
        caught instanceof Error ? caught.message : "Failed to ingest reading events.";

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
