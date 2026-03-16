"use client";

import { startTransition, useState } from "react";
import type { ReadingSessionCreateV2, ReadingSessionResponseV2 } from "@lumosreading/contracts";
import { createReadingSession } from "@/lib/api/v2";

type MutationStatus = "idle" | "pending" | "success" | "error";

export function useReadingSessionMutation() {
  const [data, setData] = useState<ReadingSessionResponseV2 | null>(null);
  const [status, setStatus] = useState<MutationStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  async function mutate(payload: ReadingSessionCreateV2): Promise<ReadingSessionResponseV2> {
    setStatus("pending");
    setError(null);

    try {
      const response = await createReadingSession(payload);

      startTransition(() => {
        setData(response);
        setStatus("success");
      });

      return response;
    } catch (caught) {
      const message =
        caught instanceof Error ? caught.message : "Failed to create reading session.";

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
