import type { ReadingSessionResponseV2, StoryPackageManifestV1 } from '@lumosreading/contracts';
import { startTransition, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import {
  buildReadingEventBatch,
  buildReadingSessionPayload,
  childRuntime,
} from '@/lib/runtime';

type RuntimeAction = 'package' | 'session' | 'event';

type ActivityItem = {
  id: string;
  label: string;
  timestamp: string;
};

function formatDuration(seconds: number): string {
  const minutes = Math.max(1, Math.round(seconds / 60));
  return `${minutes} min`;
}

function appendActivityEntry(
  previous: ActivityItem[],
  label: string,
  timestamp: string = new Date().toLocaleTimeString(),
): ActivityItem[] {
  return [
    {
      id: `${Date.now()}-${previous.length}`,
      label,
      timestamp,
    },
    ...previous,
  ].slice(0, 6);
}

export default function ChildHomeScreen() {
  const [storyPackage, setStoryPackage] = useState<StoryPackageManifestV1 | null>(null);
  const [sessionReceipt, setSessionReceipt] = useState<ReadingSessionResponseV2 | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [translationVisible, setTranslationVisible] = useState(false);
  const [activeAction, setActiveAction] = useState<RuntimeAction | null>('package');

  useEffect(() => {
    let isMounted = true;

    async function loadStoryPackage() {
      setActiveAction('package');
      setError(null);

      try {
        const result = await childRuntime.services.storyPackages.lookup(childRuntime.defaultPackageId);

        if (!isMounted) {
          return;
        }

        startTransition(() => {
          setStoryPackage(result);
          setActivity((previous) =>
            appendActivityEntry(previous, `Loaded ${result.title} from ${childRuntime.mode} mode.`),
          );
        });
      } catch (loadError) {
        if (!isMounted) {
          return;
        }

        const message =
          loadError instanceof Error ? loadError.message : 'Unable to load story package.';

        startTransition(() => {
          setError(message);
        });
      } finally {
        if (isMounted) {
          setActiveAction(null);
        }
      }
    }

    void loadStoryPackage();

    return () => {
      isMounted = false;
    };
  }, []);

  async function handleStartSession() {
    if (!storyPackage) {
      return;
    }

    setActiveAction('session');
    setError(null);

    try {
      const receipt = await childRuntime.services.readingSessions.start(
        buildReadingSessionPayload({
          childId: childRuntime.defaultChildId,
          packageId: storyPackage.package_id,
        }),
      );

      startTransition(() => {
        setSessionReceipt(receipt);
        setActivity((previous) =>
          appendActivityEntry(previous, `Reading session accepted: ${receipt.session_id.slice(0, 8)}.`),
        );
      });
    } catch (sessionError) {
      const message =
        sessionError instanceof Error ? sessionError.message : 'Unable to start reading session.';

      startTransition(() => {
        setError(message);
      });
    } finally {
      setActiveAction(null);
    }
  }

  async function handleEventAction(
    eventType: 'page_viewed' | 'page_replayed_audio' | 'word_revealed_translation',
  ) {
    if (!storyPackage || !sessionReceipt) {
      return;
    }

    const payloadByEventType = {
      page_viewed: {
        dwell_ms: 18000,
      },
      page_replayed_audio: {
        replay_count: 1,
      },
      word_revealed_translation: {
        word: storyPackage.pages[0]?.overlays?.vocabulary?.[0] ?? 'bridge',
        reveal_count: 1,
      },
    } as const;

    const labelsByEventType = {
      page_viewed: 'Logged page_viewed for the current spread.',
      page_replayed_audio: 'Logged page_replayed_audio for read-to-me replay.',
      word_revealed_translation: 'Logged word_revealed_translation for bilingual assist.',
    } as const;

    setActiveAction('event');
    setError(null);

    try {
      await childRuntime.services.readingEvents.ingestBatch(
        buildReadingEventBatch({
          eventType,
          sessionId: sessionReceipt.session_id,
          childId: sessionReceipt.child_id,
          packageId: sessionReceipt.package_id,
          pageIndex: 0,
          payload: payloadByEventType[eventType],
        }),
      );

      if (eventType === 'word_revealed_translation') {
        setTranslationVisible(true);
      }

      startTransition(() => {
        setActivity((previous) => appendActivityEntry(previous, labelsByEventType[eventType]));
      });
    } catch (eventError) {
      const message =
        eventError instanceof Error ? eventError.message : 'Unable to ingest reading event.';

      startTransition(() => {
        setError(message);
      });
    } finally {
      setActiveAction(null);
    }
  }

  const primaryText =
    storyPackage?.pages[0]?.text_runs.map((run) => run.text).join(' ') ?? 'Loading first spread...';
  const vocabulary = storyPackage?.pages[0]?.overlays?.vocabulary ?? [];

  return (
    <View style={styles.screen}>
      <View style={styles.backgroundOrbLarge} />
      <View style={styles.backgroundOrbSmall} />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}>
          <View style={styles.heroCard}>
            <View style={styles.heroHeader}>
              <View style={styles.kickerRow}>
                <Text style={styles.kicker}>Lumos Child Runtime</Text>
                <Text style={styles.modeBadge}>{childRuntime.mode.toUpperCase()}</Text>
              </View>
              <Text style={styles.heroTitle}>A calm reading shell for iPad-first sessions.</Text>
              <Text style={styles.heroCopy}>
                The child app now consumes shared contracts, loads a versioned story package, and
                sends typed reading commands instead of relying on page-local demo shapes.
              </Text>
            </View>

            <View style={styles.metricsRow}>
              <View style={styles.metricCard}>
                <Text style={styles.metricLabel}>Surface</Text>
                <Text style={styles.metricValue}>child-app</Text>
              </View>
              <View style={styles.metricCard}>
                <Text style={styles.metricLabel}>Story Package</Text>
                <Text style={styles.metricValue}>
                  {storyPackage ? storyPackage.schema_version : 'loading'}
                </Text>
              </View>
              <View style={styles.metricCard}>
                <Text style={styles.metricLabel}>Session</Text>
                <Text style={styles.metricValue}>
                  {sessionReceipt ? sessionReceipt.status : 'idle'}
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.storyCard}>
            <View style={styles.storyHeader}>
              <Text style={styles.sectionLabel}>Tonight&apos;s package</Text>
              {activeAction === 'package' && <ActivityIndicator color="#27403a" />}
            </View>

            <Text style={styles.storyTitle}>{storyPackage?.title ?? 'Loading package...'}</Text>
            <Text style={styles.storySubtitle}>
              {storyPackage?.subtitle ?? 'Fetching a typed runtime package from shared services.'}
            </Text>

            <View style={styles.storyMetaRow}>
              <Text style={styles.storyMetaPill}>
                {storyPackage?.language_mode ?? 'language'}
              </Text>
              <Text style={styles.storyMetaPill}>{storyPackage?.age_band ?? 'age band'}</Text>
              <Text style={styles.storyMetaPill}>
                {storyPackage ? formatDuration(storyPackage.estimated_duration_sec) : 'duration'}
              </Text>
            </View>

            <View style={styles.pageCard}>
              <Text style={styles.pageEyebrow}>Page 1</Text>
              <Text style={styles.pageCopy}>{primaryText}</Text>
              <Text style={styles.pageHint}>
                Stable narration first, bilingual support as an assistive reveal layer.
              </Text>

              {translationVisible && vocabulary.length > 0 && (
                <View style={styles.vocabularyStrip}>
                  {vocabulary.map((word) => (
                    <View key={word} style={styles.vocabularyChip}>
                      <Text style={styles.vocabularyText}>{word}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          </View>

          <View style={styles.controlCard}>
            <Text style={styles.sectionLabel}>Reading controls</Text>
            <Text style={styles.controlCopy}>
              This shell already exercises the shared reading session and event ingestion contracts.
            </Text>

            <View style={styles.actionGrid}>
              <Pressable
                onPress={() => void handleStartSession()}
                disabled={!storyPackage || activeAction !== null}
                style={({ pressed }) => [
                  styles.primaryAction,
                  (!storyPackage || activeAction !== null) && styles.disabledAction,
                  pressed && styles.pressedAction,
                ]}>
                <Text style={styles.primaryActionLabel}>
                  {sessionReceipt ? 'Session Ready' : 'Start Session'}
                </Text>
              </Pressable>

              <Pressable
                onPress={() => void handleEventAction('page_viewed')}
                disabled={!sessionReceipt || activeAction !== null}
                style={({ pressed }) => [
                  styles.secondaryAction,
                  (!sessionReceipt || activeAction !== null) && styles.disabledAction,
                  pressed && styles.pressedAction,
                ]}>
                <Text style={styles.secondaryActionLabel}>Log Page View</Text>
              </Pressable>

              <Pressable
                onPress={() => void handleEventAction('page_replayed_audio')}
                disabled={!sessionReceipt || activeAction !== null}
                style={({ pressed }) => [
                  styles.secondaryAction,
                  (!sessionReceipt || activeAction !== null) && styles.disabledAction,
                  pressed && styles.pressedAction,
                ]}>
                <Text style={styles.secondaryActionLabel}>Replay Audio</Text>
              </Pressable>

              <Pressable
                onPress={() => void handleEventAction('word_revealed_translation')}
                disabled={!sessionReceipt || activeAction !== null}
                style={({ pressed }) => [
                  styles.secondaryAction,
                  (!sessionReceipt || activeAction !== null) && styles.disabledAction,
                  pressed && styles.pressedAction,
                ]}>
                <Text style={styles.secondaryActionLabel}>Reveal Vocabulary</Text>
              </Pressable>
            </View>

            {sessionReceipt && (
              <View style={styles.receiptCard}>
                <Text style={styles.receiptLabel}>Session receipt</Text>
                <Text style={styles.receiptValue}>{sessionReceipt.session_id}</Text>
                <Text style={styles.receiptMeta}>
                  accepted at {sessionReceipt.accepted_at} for package {sessionReceipt.package_id}
                </Text>
              </View>
            )}

            {error && (
              <View style={styles.errorCard}>
                <Text style={styles.errorTitle}>Runtime error</Text>
                <Text style={styles.errorCopy}>{error}</Text>
              </View>
            )}
          </View>

          <View style={styles.activityCard}>
            <Text style={styles.sectionLabel}>Activity log</Text>
            <View style={styles.activityList}>
              {activity.length === 0 ? (
                <Text style={styles.emptyState}>No activity yet.</Text>
              ) : (
                activity.map((item) => (
                  <View key={item.id} style={styles.activityItem}>
                    <Text style={styles.activityLabel}>{item.label}</Text>
                    <Text style={styles.activityTimestamp}>{item.timestamp}</Text>
                  </View>
                ))
              )}
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f7f0e1',
  },
  safeArea: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 32,
    gap: 18,
  },
  backgroundOrbLarge: {
    position: 'absolute',
    top: -120,
    right: -80,
    width: 280,
    height: 280,
    borderRadius: 140,
    backgroundColor: '#efd7b5',
    opacity: 0.55,
  },
  backgroundOrbSmall: {
    position: 'absolute',
    left: -60,
    top: 240,
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: '#d7e6d8',
    opacity: 0.75,
  },
  heroCard: {
    backgroundColor: '#24313f',
    borderRadius: 32,
    padding: 24,
    gap: 20,
    shadowColor: '#1e2a35',
    shadowOpacity: 0.18,
    shadowRadius: 20,
    shadowOffset: {
      width: 0,
      height: 10,
    },
    elevation: 8,
  },
  heroHeader: {
    gap: 12,
  },
  kickerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  kicker: {
    color: '#f7f0e1',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1.2,
    textTransform: 'uppercase',
  },
  modeBadge: {
    color: '#24313f',
    backgroundColor: '#f1b365',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.8,
  },
  heroTitle: {
    color: '#fff8ef',
    fontSize: 28,
    lineHeight: 34,
    fontWeight: '800',
    maxWidth: 520,
  },
  heroCopy: {
    color: '#d7e0e6',
    fontSize: 15,
    lineHeight: 22,
    maxWidth: 620,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 12,
    flexWrap: 'wrap',
  },
  metricCard: {
    backgroundColor: '#304252',
    borderRadius: 22,
    paddingHorizontal: 14,
    paddingVertical: 12,
    minWidth: 110,
    gap: 4,
  },
  metricLabel: {
    color: '#aab8c1',
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  metricValue: {
    color: '#fff8ef',
    fontSize: 14,
    fontWeight: '700',
  },
  storyCard: {
    backgroundColor: '#fffaf0',
    borderRadius: 30,
    padding: 20,
    gap: 14,
    borderWidth: 1,
    borderColor: '#e8dac0',
  },
  storyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionLabel: {
    color: '#6b5d4a',
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  storyTitle: {
    color: '#24313f',
    fontSize: 26,
    lineHeight: 30,
    fontWeight: '800',
  },
  storySubtitle: {
    color: '#5a6170',
    fontSize: 15,
    lineHeight: 22,
  },
  storyMetaRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  storyMetaPill: {
    backgroundColor: '#f1e4ca',
    color: '#6a5538',
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
    overflow: 'hidden',
    fontSize: 12,
    fontWeight: '700',
  },
  pageCard: {
    backgroundColor: '#f8efe0',
    borderRadius: 24,
    padding: 18,
    gap: 12,
  },
  pageEyebrow: {
    color: '#7a6646',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  pageCopy: {
    color: '#24313f',
    fontSize: 24,
    lineHeight: 32,
    fontWeight: '700',
  },
  pageHint: {
    color: '#596170',
    fontSize: 14,
    lineHeight: 20,
  },
  vocabularyStrip: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  vocabularyChip: {
    backgroundColor: '#dcefe5',
    borderRadius: 18,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  vocabularyText: {
    color: '#27403a',
    fontSize: 13,
    fontWeight: '700',
  },
  controlCard: {
    backgroundColor: '#fffdf7',
    borderRadius: 30,
    padding: 20,
    gap: 16,
    borderWidth: 1,
    borderColor: '#eee1c9',
  },
  controlCopy: {
    color: '#5a6170',
    fontSize: 15,
    lineHeight: 22,
  },
  actionGrid: {
    gap: 12,
  },
  primaryAction: {
    backgroundColor: '#df7f63',
    borderRadius: 24,
    paddingVertical: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryActionLabel: {
    color: '#fff8ef',
    fontSize: 16,
    fontWeight: '800',
  },
  secondaryAction: {
    backgroundColor: '#e9efe8',
    borderRadius: 22,
    paddingVertical: 16,
    paddingHorizontal: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryActionLabel: {
    color: '#27403a',
    fontSize: 15,
    fontWeight: '700',
  },
  disabledAction: {
    opacity: 0.45,
  },
  pressedAction: {
    transform: [{ scale: 0.985 }],
  },
  receiptCard: {
    backgroundColor: '#24313f',
    borderRadius: 24,
    padding: 16,
    gap: 8,
  },
  receiptLabel: {
    color: '#c9d4dd',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.9,
  },
  receiptValue: {
    color: '#fffaf0',
    fontSize: 16,
    fontWeight: '800',
  },
  receiptMeta: {
    color: '#d7e0e6',
    fontSize: 13,
    lineHeight: 18,
  },
  errorCard: {
    backgroundColor: '#fff0eb',
    borderRadius: 22,
    padding: 16,
    gap: 6,
    borderWidth: 1,
    borderColor: '#f2b9a8',
  },
  errorTitle: {
    color: '#7f2f1e',
    fontSize: 13,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.9,
  },
  errorCopy: {
    color: '#7f2f1e',
    fontSize: 14,
    lineHeight: 20,
  },
  activityCard: {
    backgroundColor: '#f0f5ef',
    borderRadius: 30,
    padding: 20,
    gap: 14,
    borderWidth: 1,
    borderColor: '#d7e6d8',
  },
  activityList: {
    gap: 10,
  },
  activityItem: {
    backgroundColor: '#ffffff',
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 12,
    gap: 4,
  },
  activityLabel: {
    color: '#24313f',
    fontSize: 14,
    lineHeight: 20,
    fontWeight: '700',
  },
  activityTimestamp: {
    color: '#6c7280',
    fontSize: 12,
    fontWeight: '600',
  },
  emptyState: {
    color: '#596170',
    fontSize: 14,
    lineHeight: 20,
  },
});
