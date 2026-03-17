import type {
  ReadingEventType,
  ReadingSessionResponseV2,
  StoryPackageManifestV1,
} from '@lumosreading/contracts';
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
  buildReadingEventBatch,
  buildReadingSessionPayload,
  childRuntime,
  getRuntimeEventLabel,
  getRuntimePreloadPageIndexes,
  loadRuntimeLibrary,
  preloadRuntimePageAssets,
  resolveRuntimePage,
  type ResolvedRuntimePage,
} from '@/lib/runtime';

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
  hasActiveSession: boolean;
  canGoToPreviousPage: boolean;
  canGoToNextPage: boolean;
  loadPackage(packageId: string): Promise<StoryPackageManifestV1 | null>;
  startSession(packageId: string): Promise<ReadingSessionResponseV2 | null>;
  ingestEvent(args: {
    eventType: RuntimeEventAction;
    payload: Record<string, unknown>;
    pageIndex?: number | null;
    revealTranslation?: boolean;
    background?: boolean;
  }): Promise<boolean>;
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
  return [buildActivityEntry(label), ...previous].slice(0, 10);
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
  const [preloadState, setPreloadState] = useState<RuntimePreloadState>({
    status: 'idle',
    targetPageIndexes: [],
    readyPageIndexes: [],
    error: null,
  });

  const pageEnteredAtRef = useRef(Date.now());

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

  useEffect(() => {
    let isMounted = true;

    async function initializeHome() {
      setActiveAction('home');
      setError(null);

      try {
        const packages = await loadRuntimeLibrary();

        if (!isMounted) {
          return;
        }

        startTransition(() => {
          setHomePackages(packages);
          setPackageMap(buildPackageMap(packages));
          setActivePackageId(packages[0]?.package_id ?? null);
          setActivity(previous =>
            appendActivity(
              previous,
              `Loaded ${packages.length} package(s) in ${childRuntime.mode} mode.`
            )
          );
        });
      } catch (initializationError) {
        if (!isMounted) {
          return;
        }

        const message =
          initializationError instanceof Error
            ? initializationError.message
            : 'Unable to initialize child runtime.';

        startTransition(() => {
          setError(message);
        });
      } finally {
        if (isMounted) {
          setActiveAction(null);
        }
      }
    }

    void initializeHome();

    return () => {
      isMounted = false;
    };
  }, []);

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
      const storyPackage =
        await childRuntime.services.storyPackages.lookup(packageId);

      startTransition(() => {
        setPackageMap(previous => ({
          ...previous,
          [storyPackage.package_id]: storyPackage,
        }));
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

    const resolvedPageIndex =
      args.pageIndex === undefined
        ? (currentPage?.page_index ?? currentPageIndex)
        : args.pageIndex;

    if (!args.background) {
      setActiveAction('event');
    }

    setError(null);

    try {
      await childRuntime.services.readingEvents.ingestBatch(
        buildReadingEventBatch({
          eventType: args.eventType,
          sessionId: sessionReceipt.session_id,
          childId: sessionReceipt.child_id,
          packageId: sessionReceipt.package_id,
          pageIndex: resolvedPageIndex,
          payload: args.payload,
        })
      );

      startTransition(() => {
        if (args.revealTranslation) {
          setTranslationVisible(true);
        }

        setActivity(previous =>
          appendActivity(
            previous,
            getRuntimeEventLabel(args.eventType, resolvedPageIndex)
          )
        );
      });

      return true;
    } catch (eventError) {
      const message =
        eventError instanceof Error
          ? eventError.message
          : 'Unable to ingest reading event.';

      startTransition(() => {
        setError(message);
      });

      return false;
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

      void ingestEvent({
        eventType: 'session_started',
        payload: {
          source: 'child-runtime',
          page_count: storyPackage.pages.length,
        },
        pageIndex: null,
        background: true,
      });

      return receipt;
    } catch (sessionError) {
      const message =
        sessionError instanceof Error
          ? sessionError.message
          : 'Unable to start reading session.';

      startTransition(() => {
        setError(message);
      });

      return null;
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
        hasActiveSession,
        canGoToPreviousPage,
        canGoToNextPage,
        loadPackage,
        startSession,
        ingestEvent,
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
