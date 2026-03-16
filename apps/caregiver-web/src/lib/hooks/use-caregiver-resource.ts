"use client";

import { startTransition, useEffect, useState } from "react";

type ResourceStatus = "loading" | "live" | "fallback";

export function useCaregiverResource<T>(
  householdId: string,
  initialValue: T,
  load: (householdId: string) => Promise<T>,
  fallbackMessage: string,
) {
  const [value, setValue] = useState<T>(initialValue);
  const [status, setStatus] = useState<ResourceStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    setStatus("loading");
    setError(null);

    load(householdId)
      .then((response) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setValue(response);
          setStatus("live");
          setError(null);
        });
      })
      .catch((caught) => {
        if (!active) {
          return;
        }

        startTransition(() => {
          setValue(initialValue);
          setStatus("fallback");
          setError(caught instanceof Error ? caught.message : fallbackMessage);
        });
      });

    return () => {
      active = false;
    };
  }, [fallbackMessage, householdId, initialValue, load]);

  return {
    value,
    status,
    error,
  };
}
