import type {
  ReadingEventType,
  ReadingEventV1,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from '@lumosreading/contracts';
import { AppState } from 'react-native';
import {
  setAudioModeAsync,
  useAudioPlayer,
  useAudioPlayerStatus,
} from 'expo-audio';
import {
  createContext,
  startTransition,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import {
  buildOfflineReadingSessionReceipt,
  buildReadingEventBatch,
  buildReadingSessionPayload,
  childRuntime,
  getRuntimeEventLabel,
  getRuntimePlatform,
  getRuntimePreloadPageIndexes,
  loadChildHome,
  loadRuntimeStoryPackage,
  preloadRuntimePageAssets,
  resolveRuntimePage,
  type ResolvedRuntimePage,
} from '@/lib/runtime';
import {
  clearSessionSnapshot,
  loadPersistedHomePackages,
  loadPersistedPackageCache,
  loadPersistedSessionSnapshot,
  loadQueuedEvents,
  persistHomePackages,
  persistPackage,
  persistSessionSnapshot,
  queueEvents,
  removeQueuedEventsById,
} from '@/lib/persistence';
import { resolveStoryPackageLanguageMode } from '@/lib/reading-contracts';

type RuntimeAction = 'home' | 'package' | 'session' | 'event';

type RuntimeActivity = {
  id: string;
  label: string;
  timestamp: string;
};

type RuntimeEventAction = Extract<
  ReadingEventType,
  | 'session_started'
  | 'page_viewed'
  | 'page_replayed_audio'
  | 'word_revealed_translation'
  | 'session_completed'
>;

type RuntimePreloadState = {
  status: 'idle' | 'loading' | 'ready' | 'error';
  targetPageIndexes: number[];
  readyPageIndexes: number[];
  error: string | null;
};

type RuntimeAudioState = {
  available: boolean;
  ready: boolean;
  playing: boolean;
  buffering: boolean;
  currentTimeSec: number;
  durationSec: number;
};

type ChildRuntimeContextValue = {
  mode: typeof childRuntime.mode;
  apiBaseUrl: string;
  homePackages: StoryPackageManifestV1[];
  activePackage: StoryPackageManifestV1 | null;
  currentSessionPackage: StoryPackageManifestV1 | null;
  currentPage: ResolvedRuntimePage | null;
  currentPageIndex: number;
  pageCount: number;
  sessionReceipt: ReadingSessionResponseV2 | null;
  activity: RuntimeActivity[];
  error: string | null;
  activeAction: RuntimeAction | null;
  translationVisible: boolean;
  preloadState: RuntimePreloadState;
  audio: RuntimeAudioState;
  pendingEventCount: number;
  hasActiveSession: boolean;
  canGoToPreviousPage: boolean;
  canGoToNextPage: boolean;
  refreshHome(): Promise<boolean>;
  loadPackage(packageId: string): Promise<StoryPackageManifestV1 | null>;
  startSession(packageId: string): Promise<ReadingSessionResponseV2 | null>;
  ingestEvent(args: {
    eventType: RuntimeEventAction;
    payload: Record<string, unknown>;
    pageIndex?: number | null;
    revealTranslation?: boolean;
    background?: boolean;
  }): Promise<boolean>;
  flushQueuedEvents(): Promise<boolean>;
  goToPreviousPage(): Promise<boolean>;
  goToNextPage(): Promise<boolean>;
  togglePlayPause(): void;
  replayAudio(): Promise<boolean>;
  finishSession(): Promise<boolean>;
  clearError(): void;
};

const ChildRuntimeContext = createContext<ChildRuntimeContextValue | null>(
  null
);

function buildActivityEntry(label: string): RuntimeActivity {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    label,
    timestamp: new Date().toLocaleTimeString(),
  };
}

function appendActivity(
  previous: RuntimeActivity[],
  label: string
): RuntimeActivity[] {
  return [buildActivityEntry(label), ...previous].slice(0, 12);
}

function buildPackageMap(
  packages: StoryPackageManifestV1[]
): Record<string, StoryPackageManifestV1> {
  return packages.reduce<Record<string, StoryPackageManifestV1>>(
    (accumulator, item) => {
      accumulator[item.package_id] = item;
      return accumulator;
    },
    {}
  );
}

function orderPackages(
  packages: StoryPackageManifestV1[],
  featuredPackageId?: string | null
): StoryPackageManifestV1[] {
  const packageMap = buildPackageMap(packages);
  const featuredPackage = featuredPackageId
    ? packageMap[featuredPackageId] ?? null
    : null;
  const remainingPackages = packages.filter(
    item => item.package_id !== featuredPackage?.package_id
  );

  return featuredPackage ? [featuredPackage, ...remainingPackages] : packages;
}

function getHomeRefreshActivityLabel(
  reason: 'initial' | 'resume' | 'manual',
  packageCount: number
): string {
  if (reason === 'initial') {
    return `Loaded assigned shelf with ${packageCount} package(s) in ${childRuntime.mode} mode.`;
  }

  if (reason === 'resume') {
    return `Resynced the assigned shelf after returning to the app.`;
  }

  return `Refreshed the assigned shelf and picked up the latest caregiver assignment.`;
}

type ChildRuntimeProviderProps = {
  children: ReactNode;
};

export function ChildRuntimeProvider({ children }: ChildRuntimeProviderProps) {
  const [homePackages, setHomePackages] = useState<StoryPackageManifestV1[]>(
    []
  );
  const [packageMap, setPackageMap] = useState<
    Record<string, StoryPackageManifestV1>
  >({});
  const [activePackageId, setActivePackageId] = useState<string | null>(null);
  const [sessionReceipt, setSessionReceipt] =
    useState<ReadingSessionResponseV2 | null>(null);
  const [activity, setActivity] = useState<RuntimeActivity[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeAction, setActiveAction] = useState<RuntimeAction | null>(
    'home'
  );
  const [translationVisible, setTranslationVisible] = useState(false);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [pendingEventCount, setPendingEventCount] = useState(0);
  const [preloadState, setPreloadState] = useState<RuntimePreloadState>({
    status: 'idle',
    targetPageIndexes: [],
    readyPageIndexes: [],
    error: null,
  });

  const pageEnteredAtRef = useRef(Date.now());
  const flushQueuedEventsRef = useRef<Promise<boolean> | null>(null);
  const refreshHomeRef = useRef<Promise<boolean> | null>(null);

  const activePackage = activePackageId
    ? (packageMap[activePackageId] ?? null)
    : null;
  const currentSessionPackage = sessionReceipt
    ? (packageMap[sessionReceipt.package_id] ?? activePackage)
    : null;
  const pageCount = currentSessionPackage?.pages.length ?? 0;
  const currentPage =
    currentSessionPackage && currentPageIndex < pageCount
      ? resolveRuntimePage(currentSessionPackage, currentPageIndex)
      : null;
  const hasActiveSession = Boolean(
    sessionReceipt && currentSessionPackage && currentPage
  );
  const canGoToPreviousPage = hasActiveSession && currentPageIndex > 0;
  const canGoToNextPage = hasActiveSession && currentPageIndex < pageCount - 1;
  const currentSessionLanguageMode = resolveStoryPackageLanguageMode(
    currentSessionPackage ?? activePackage
  );

  const audioPlayer = useAudioPlayer(
    currentPage?.runtime_media.audioSource ?? null,
    {
      updateInterval: 250,
      downloadFirst: childRuntime.mode === 'api',
      keepAudioSessionActive: true,
    }
  );
  const audioStatus = useAudioPlayerStatus(audioPlayer);

  useEffect(() => {
    void setAudioModeAsync({
      playsInSilentMode: true,
      shouldPlayInBackground: false,
      interruptionMode: 'duckOthers',
      interruptionModeAndroid: 'duckOthers',
      allowsRecording: false,
      shouldRouteThroughEarpiece: false,
    }).catch(audioModeError => {
      const message =
        audioModeError instanceof Error
          ? audioModeError.message
          : 'Unable to configure audio mode for the child runtime.';

      startTransition(() => {
        setError(message);
      });
    });
  }, []);

  async function flushQueuedEvents() {
    if (flushQueuedEventsRef.current) {
      return flushQueuedEventsRef.current;
    }

    const flushPromise = (async () => {
      const queuedEvents = await loadQueuedEvents();

      if (queuedEvents.length === 0) {
        startTransition(() => {
          setPendingEventCount(0);
        });
        return true;
      }

      try {
        await childRuntime.services.readingEvents.ingestBatch({
          events: queuedEvents,
        });
        const remainingEvents = await removeQueuedEventsById(
          queuedEvents.map(event => event.event_id)
        );

        startTransition(() => {
          setPendingEventCount(remainingEvents.length);
          setActivity(previous =>
            appendActivity(
              previous,
              `Flushed ${queuedEvents.length} queued event(s) to the API.`
            )
          );
        });

        return true;
      } catch {
        const latestEvents = await loadQueuedEvents();

        startTransition(() => {
          setPendingEventCount(latestEvents.length);
        });
        return false;
      }
    })();

    flushQueuedEventsRef.current = flushPromise;
    try {
      return await flushPromise;
    } finally {
      flushQueuedEventsRef.current = null;
    }
  }

  async function refreshHome(options: {
    background?: boolean;
    reason?: 'initial' | 'resume' | 'manual';
    preferredPackageId?: string | null;
  } = {}) {
    if (refreshHomeRef.current) {
      return refreshHomeRef.current;
    }

    const refreshPromise = (async () => {
      if (!options.background) {
        setActiveAction('home');
      }

      setError(null);

      try {
        const childHome = await loadChildHome();
        const orderedShelf = orderPackages(
          childHome.package_queue,
          childHome.featured_package_id
        );

        await persistHomePackages(orderedShelf);

        startTransition(() => {
          setHomePackages(orderedShelf);
          setPackageMap(previous => ({
            ...previous,
            ...buildPackageMap(orderedShelf),
          }));
          setActivePackageId(
            options.preferredPackageId ??
              sessionReceipt?.package_id ??
              childHome.current_package_id ??
              childHome.featured_package_id
          );
          setActivity(previous =>
            appendActivity(
              previous,
              getHomeRefreshActivityLabel(
                options.reason ?? 'manual',
                orderedShelf.length
              )
            )
          );
        });

        return true;
      } catch (refreshError) {
        if (!options.background) {
          const message =
            refreshError instanceof Error
              ? refreshError.message
              : 'Unable to refresh the child shelf.';

          startTransition(() => {
            setError(message);
          });
        }

        return false;
      } finally {
        if (!options.background) {
          setActiveAction(null);
        }
      }
    })();

    refreshHomeRef.current = refreshPromise;
    try {
      return await refreshPromise;
    } finally {
      refreshHomeRef.current = null;
    }
  }

  useEffect(() => {
    let isMounted = true;

    async function initializeHome() {
      setActiveAction('home');
      setError(null);

      const [
        persistedHomePackages,
        persistedPackageCache,
        persistedSessionSnapshot,
        queuedEvents,
      ] = await Promise.all([
        loadPersistedHomePackages(),
        loadPersistedPackageCache(),
        loadPersistedSessionSnapshot(),
        loadQueuedEvents(),
      ]);

      const cachedPackages = orderPackages(
        Object.values(persistedPackageCache).length > 0
          ? Object.values(persistedPackageCache)
          : persistedHomePackages,
        persistedSessionSnapshot?.packageId ?? persistedHomePackages[0]?.package_id
      );
      const cachedPackageMap = buildPackageMap(cachedPackages);

      if (isMounted && cachedPackages.length > 0) {
        startTransition(() => {
          setHomePackages(cachedPackages);
          setPackageMap(cachedPackageMap);
          setActivePackageId(
            persistedSessionSnapshot?.packageId ?? cachedPackages[0]?.package_id ?? null
          );
          setPendingEventCount(queuedEvents.length);
          setActivity(previous =>
            appendActivity(
              previous,
              `Recovered ${cachedPackages.length} cached package(s) from local storage.`
            )
          );
        });
      }

      if (
        isMounted &&
        persistedSessionSnapshot &&
        cachedPackageMap[persistedSessionSnapshot.packageId]
      ) {
        pageEnteredAtRef.current = Date.now();
        startTransition(() => {
          setSessionReceipt(persistedSessionSnapshot.sessionReceipt);
          setCurrentPageIndex(persistedSessionSnapshot.currentPageIndex);
          setTranslationVisible(persistedSessionSnapshot.translationVisible);
          setActivePackageId(persistedSessionSnapshot.packageId);
          setActivity(previous =>
            appendActivity(
              previous,
              `Restored an active session on page ${persistedSessionSnapshot.currentPageIndex + 1}.`
            )
          );
        });
      }

      try {
        const refreshed = await refreshHome({
          background: true,
          reason: 'initial',
          preferredPackageId: persistedSessionSnapshot?.packageId ?? null,
        });

        if (!isMounted || !refreshed) {
          return;
        }

        startTransition(() => {
          setPendingEventCount(queuedEvents.length);
        });
      } catch (initializationError) {
        if (!isMounted) {
          return;
        }

        if (cachedPackages.length === 0) {
          const message =
            initializationError instanceof Error
              ? initializationError.message
              : 'Unable to initialize child runtime.';

          startTransition(() => {
            setError(message);
          });
        }
      } finally {
        if (isMounted) {
          setActiveAction(null);
          void flushQueuedEvents();
        }
      }
    }

    void initializeHome();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const subscription = AppState.addEventListener('change', nextAppState => {
      if (nextAppState !== 'active' || sessionReceipt) {
        return;
      }

      void refreshHome({
        background: true,
        reason: 'resume',
      });
      void flushQueuedEvents();
    });

    return () => {
      subscription.remove();
    };
  }, [sessionReceipt?.session_id]);

  useEffect(() => {
    let isMounted = true;

    async function preloadSessionAssets() {
      if (!currentSessionPackage || !currentPage) {
        startTransition(() => {
          setPreloadState({
            status: 'idle',
            targetPageIndexes: [],
            readyPageIndexes: [],
            error: null,
          });
        });
        return;
      }

      const targetPageIndexes = getRuntimePreloadPageIndexes(
        currentSessionPackage,
        currentPageIndex
      );

      startTransition(() => {
        setPreloadState({
          status: 'loading',
          targetPageIndexes,
          readyPageIndexes: [],
          error: null,
        });
      });

      const result = await preloadRuntimePageAssets(
        currentSessionPackage,
        targetPageIndexes
      );

      if (!isMounted) {
        return;
      }

      startTransition(() => {
        setPreloadState({
          status: result.failedPageIndexes.length > 0 ? 'error' : 'ready',
          targetPageIndexes,
          readyPageIndexes: result.readyPageIndexes,
          error:
            result.failedPageIndexes.length > 0
              ? `Unable to preload page ${result.failedPageIndexes[0] + 1}.`
              : null,
        });
      });
    }

    void preloadSessionAssets();

    return () => {
      isMounted = false;
    };
  }, [currentPageIndex, currentSessionPackage?.package_id]);

  useEffect(() => {
    if (homePackages.length === 0) {
      return;
    }

    void persistHomePackages(homePackages);
  }, [homePackages]);

  useEffect(() => {
    if (!sessionReceipt || !currentSessionPackage) {
      void clearSessionSnapshot();
      return;
    }

    void persistSessionSnapshot({
      sessionReceipt,
      packageId: currentSessionPackage.package_id,
      currentPageIndex,
      translationVisible,
      restoredAt: new Date().toISOString(),
    });
  }, [
    currentPageIndex,
    currentSessionPackage?.package_id,
    sessionReceipt?.session_id,
    translationVisible,
  ]);

  async function loadPackage(packageId: string) {
    if (packageMap[packageId]) {
      startTransition(() => {
        setActivePackageId(packageId);
      });
      return packageMap[packageId];
    }

    setActiveAction('package');
    setError(null);

    try {
      const storyPackage = await loadRuntimeStoryPackage(
        packageId,
        childRuntime.defaultChildId,
      );
      await persistPackage(storyPackage);

      startTransition(() => {
        setPackageMap(previous => ({
          ...previous,
          [storyPackage.package_id]: storyPackage,
        }));
        setHomePackages(previous => {
          if (previous.some(item => item.package_id === storyPackage.package_id)) {
            return previous;
          }

          return [...previous, storyPackage];
        });
        setActivePackageId(storyPackage.package_id);
        setActivity(previous =>
          appendActivity(previous, `Opened package ${storyPackage.title}.`)
        );
      });

      return storyPackage;
    } catch (packageError) {
      const message =
        packageError instanceof Error
          ? packageError.message
          : 'Unable to load selected package.';

      startTransition(() => {
        setError(message);
      });

      return null;
    } finally {
      setActiveAction(null);
    }
  }

  async function ingestEvent(args: {
    eventType: RuntimeEventAction;
    payload: Record<string, unknown>;
    pageIndex?: number | null;
    revealTranslation?: boolean;
    background?: boolean;
  }) {
    if (!sessionReceipt) {
      startTransition(() => {
        setError('No active session is available for reading event ingestion.');
      });
      return false;
    }

    if (!args.background) {
      setActiveAction('event');
    }

    setError(null);

    try {
      const resolvedPageIndex =
        args.pageIndex === undefined
          ? (currentPage?.page_index ?? currentPageIndex)
          : args.pageIndex;
      const batch = buildReadingEventBatch({
        eventType: args.eventType,
        sessionId: sessionReceipt.session_id,
        childId: sessionReceipt.child_id,
        packageId: sessionReceipt.package_id,
        languageMode: currentSessionLanguageMode,
        platform: getRuntimePlatform(),
        pageIndex: resolvedPageIndex,
        payload: args.payload,
      });
      const queuedEvents = await queueEvents(batch.events as ReadingEventV1[]);

      startTransition(() => {
        if (args.revealTranslation) {
          setTranslationVisible(true);
        }

        setPendingEventCount(queuedEvents.length);
        setActivity(previous =>
          appendActivity(
            previous,
            `${getRuntimeEventLabel(args.eventType, resolvedPageIndex)} Buffered locally for sync.`
          )
        );
      });

      void flushQueuedEvents();
      return true;
    } finally {
      if (!args.background) {
        setActiveAction(null);
      }
    }
  }

  async function startSession(packageId: string) {
    const storyPackage =
      (await loadPackage(packageId)) ?? packageMap[packageId] ?? null;

    if (!storyPackage) {
      return null;
    }

    setActiveAction('session');
    setError(null);

    try {
      const receipt = await childRuntime.services.readingSessions.start(
        buildReadingSessionPayload({
          childId: childRuntime.defaultChildId,
          packageId: storyPackage.package_id,
          languageMode: resolveStoryPackageLanguageMode(storyPackage),
        })
      );

      pageEnteredAtRef.current = Date.now();
      audioPlayer.pause();
      void audioPlayer.seekTo(0).catch(() => undefined);

      startTransition(() => {
        setSessionReceipt(receipt);
        setCurrentPageIndex(0);
        setTranslationVisible(false);
        setPreloadState({
          status: 'idle',
          targetPageIndexes: [],
          readyPageIndexes: [],
          error: null,
        });
        setActivity(previous =>
          appendActivity(previous, `Started session for ${storyPackage.title}.`)
        );
      });
      const queuedEvents = await queueEvents(
        buildReadingEventBatch({
          eventType: 'session_started',
          sessionId: receipt.session_id,
          childId: receipt.child_id,
          packageId: receipt.package_id,
          languageMode: resolveStoryPackageLanguageMode(storyPackage),
          platform: getRuntimePlatform(),
          pageIndex: null,
          payload: {
            source: 'child-runtime',
            page_count: storyPackage.pages.length,
          },
        }).events as ReadingEventV1[]
      );

      startTransition(() => {
        setPendingEventCount(queuedEvents.length);
      });

      void flushQueuedEvents();

      return receipt;
    } catch {
      const offlineReceipt = buildOfflineReadingSessionReceipt({
        childId: childRuntime.defaultChildId,
        packageId: storyPackage.package_id,
      });

      pageEnteredAtRef.current = Date.now();
      audioPlayer.pause();
      void audioPlayer.seekTo(0).catch(() => undefined);

      startTransition(() => {
        setSessionReceipt(offlineReceipt);
        setCurrentPageIndex(0);
        setTranslationVisible(false);
        setPreloadState({
          status: 'idle',
          targetPageIndexes: [],
          readyPageIndexes: [],
          error: null,
        });
        setActivity(previous =>
          appendActivity(
            previous,
            `Started offline session for ${storyPackage.title}; session will sync later.`
          )
        );
      });
      const queuedEvents = await queueEvents(
        buildReadingEventBatch({
          eventType: 'session_started',
          sessionId: offlineReceipt.session_id,
          childId: offlineReceipt.child_id,
          packageId: offlineReceipt.package_id,
          languageMode: resolveStoryPackageLanguageMode(storyPackage),
          platform: getRuntimePlatform(),
          pageIndex: null,
          payload: {
            source: 'child-runtime-offline',
            page_count: storyPackage.pages.length,
          },
        }).events as ReadingEventV1[]
      );

      startTransition(() => {
        setPendingEventCount(queuedEvents.length);
      });

      void flushQueuedEvents();

      return offlineReceipt;
    } finally {
      setActiveAction(null);
    }
  }

  function logCurrentPageView(reason: 'advance' | 'back' | 'finish') {
    if (!currentPage) {
      return;
    }

    const dwellMs = Math.max(1000, Date.now() - pageEnteredAtRef.current);

    void ingestEvent({
      eventType: 'page_viewed',
      pageIndex: currentPage.page_index,
      payload: {
        dwell_ms: dwellMs,
        reason,
        page_count: pageCount,
      },
      background: true,
    });
  }

  async function moveToPage(nextPageIndex: number, reason: 'advance' | 'back') {
    if (
      !currentSessionPackage ||
      !currentPage ||
      nextPageIndex < 0 ||
      nextPageIndex >= pageCount
    ) {
      return false;
    }

    if (nextPageIndex === currentPageIndex) {
      return true;
    }

    logCurrentPageView(reason);
    audioPlayer.pause();
    void audioPlayer.seekTo(0).catch(() => undefined);
    pageEnteredAtRef.current = Date.now();

    startTransition(() => {
      setCurrentPageIndex(nextPageIndex);
      setTranslationVisible(false);
      setActivity(previous =>
        appendActivity(
          previous,
          `Moved to page ${nextPageIndex + 1} of ${pageCount}.`
        )
      );
    });

    return true;
  }

  async function goToPreviousPage() {
    return moveToPage(currentPageIndex - 1, 'back');
  }

  async function goToNextPage() {
    return moveToPage(currentPageIndex + 1, 'advance');
  }

  function togglePlayPause() {
    if (!currentPage?.runtime_media.audioSource) {
      return;
    }

    if (audioStatus.playing) {
      audioPlayer.pause();
      startTransition(() => {
        setActivity(previous =>
          appendActivity(
            previous,
            `Paused read-to-me on page ${currentPage.page_index + 1}.`
          )
        );
      });
      return;
    }

    audioPlayer.play();
    startTransition(() => {
      setActivity(previous =>
        appendActivity(
          previous,
          `Playing read-to-me on page ${currentPage.page_index + 1}.`
        )
      );
    });
  }

  async function replayAudio() {
    if (!currentPage?.runtime_media.audioSource) {
      return false;
    }

    try {
      await audioPlayer.seekTo(0);
    } catch {
      return false;
    }

    audioPlayer.play();

    void ingestEvent({
      eventType: 'page_replayed_audio',
      payload: { replay_count: 1 },
      pageIndex: currentPage.page_index,
      background: true,
    });

    return true;
  }

  async function finishSession() {
    if (!currentSessionPackage) {
      startTransition(() => {
        setError('No active session is available to complete.');
      });
      return false;
    }

    logCurrentPageView('finish');

    const accepted = await ingestEvent({
      eventType: 'session_completed',
      payload: {
        dwell_ms: Math.max(1000, Date.now() - pageEnteredAtRef.current),
        completed_page_count: pageCount,
      },
      pageIndex: null,
    });

    if (!accepted) {
      return false;
    }

    audioPlayer.pause();
    void audioPlayer.seekTo(0).catch(() => undefined);

    startTransition(() => {
      setSessionReceipt(null);
      setCurrentPageIndex(0);
      setTranslationVisible(false);
      setPreloadState({
        status: 'idle',
        targetPageIndexes: [],
        readyPageIndexes: [],
        error: null,
      });
      setActivity(previous =>
        appendActivity(
          previous,
          `Finished session for ${currentSessionPackage.title}.`
        )
      );
    });

    return true;
  }

  function clearError() {
    startTransition(() => {
      setError(null);
    });
  }

  return (
    <ChildRuntimeContext.Provider
      value={{
        mode: childRuntime.mode,
        apiBaseUrl: childRuntime.apiBaseUrl,
        homePackages,
        activePackage,
        currentSessionPackage,
        currentPage,
        currentPageIndex,
        pageCount,
        sessionReceipt,
        activity,
        error,
        activeAction,
        translationVisible,
        preloadState,
        audio: {
          available: Boolean(currentPage?.runtime_media.audioSource),
          ready:
            Boolean(currentPage?.runtime_media.audioSource) &&
            audioStatus.isLoaded,
          playing: audioStatus.playing,
          buffering: audioStatus.isBuffering,
          currentTimeSec: audioStatus.currentTime,
          durationSec: audioStatus.duration,
        },
        pendingEventCount,
        hasActiveSession,
        canGoToPreviousPage,
        canGoToNextPage,
        refreshHome,
        loadPackage,
        startSession,
        ingestEvent,
        flushQueuedEvents,
        goToPreviousPage,
        goToNextPage,
        togglePlayPause,
        replayAudio,
        finishSession,
        clearError,
      }}
    >
      {children}
    </ChildRuntimeContext.Provider>
  );
}

export function useChildRuntime() {
  const context = useContext(ChildRuntimeContext);

  if (!context) {
    throw new Error(
      'useChildRuntime must be used within ChildRuntimeProvider.'
    );
  }

  return context;
}
