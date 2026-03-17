import { router, useLocalSearchParams } from 'expo-router';
import {
  Image,
  Pressable,
  StyleSheet,
  Text,
  View,
  type ImageSourcePropType,
} from 'react-native';

import { ScreenShell } from '@/components/screen-shell';
import { useChildRuntime } from '@/features/runtime/provider';

function normalizeRouteParam(
  value: string | string[] | undefined
): string | null {
  if (typeof value === 'string') {
    return value;
  }

  if (Array.isArray(value)) {
    return value[0] ?? null;
  }

  return null;
}

function resolveImageSource(
  source: number | string | null
): ImageSourcePropType | null {
  if (typeof source === 'number') {
    return source;
  }

  if (typeof source === 'string') {
    return { uri: source };
  }

  return null;
}

function formatAudioClock(seconds: number): string {
  const safeSeconds = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(safeSeconds / 60);
  const remainingSeconds = safeSeconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export default function SessionScreen() {
  const { sessionId } = useLocalSearchParams<{
    sessionId?: string | string[];
  }>();
  const normalizedSessionId = normalizeRouteParam(sessionId);
  const {
    activity,
    audio,
    canGoToNextPage,
    canGoToPreviousPage,
    currentPage,
    currentPageIndex,
    currentSessionPackage,
    error,
    finishSession,
    goToNextPage,
    goToPreviousPage,
    hasActiveSession,
    ingestEvent,
    preloadState,
    replayAudio,
    sessionReceipt,
    togglePlayPause,
    translationVisible,
  } = useChildRuntime();

  const routeSessionMatches =
    normalizedSessionId !== null &&
    sessionReceipt?.session_id === normalizedSessionId;
  const showLiveSession =
    routeSessionMatches && hasActiveSession && currentPage;
  const livePageCount = currentSessionPackage?.pages.length ?? 0;
  const pageProgress = showLiveSession
    ? ((currentPageIndex + 1) / Math.max(1, livePageCount)) * 100
    : 0;
  const audioProgress =
    audio.durationSec > 0
      ? Math.min(100, (audio.currentTimeSec / audio.durationSec) * 100)
      : 0;
  const hasVocabulary = (currentPage?.overlays?.vocabulary?.length ?? 0) > 0;
  const pageImageSource = resolveImageSource(
    currentPage?.runtime_media.imageSource ?? null
  );

  async function handleFinishSession() {
    const completed = await finishSession();

    if (completed) {
      router.replace('/');
    }
  }

  return (
    <ScreenShell>
      <Pressable
        onPress={() => router.back()}
        style={({ pressed }) => [
          styles.backLink,
          pressed && styles.pressedAction,
        ]}
      >
        <Text style={styles.backLinkLabel}>Back to package</Text>
      </Pressable>

      <View style={styles.heroCard}>
        <View style={styles.heroHeader}>
          <Text style={styles.sectionLabel}>Live reading session</Text>
          <Text style={styles.sessionBadge}>
            {showLiveSession ? 'active' : 'missing'}
          </Text>
        </View>

        <Text style={styles.heroTitle}>
          {currentSessionPackage?.title ?? 'Session package unavailable'}
        </Text>
        <Text style={styles.heroCopy}>
          The runtime now keeps page progression, media preload state, and audio
          playback inside the shared child runtime provider instead of
          scattering state across the route.
        </Text>
      </View>

      {showLiveSession ? (
        <>
          <View style={styles.stageCard}>
            <View style={styles.stageHeader}>
              <Text style={styles.sectionLabelDark}>
                Page {currentPageIndex + 1} of {livePageCount}
              </Text>
              <Text style={styles.pageModeBadge}>
                {currentPage.runtime_media.usesBundledFallbacks
                  ? 'bundled demo media'
                  : 'remote media'}
              </Text>
            </View>

            <View style={styles.pageProgressTrack}>
              <View
                style={[styles.pageProgressFill, { width: `${pageProgress}%` }]}
              />
            </View>

            {pageImageSource ? (
              <Image
                source={pageImageSource}
                style={styles.pageArtwork}
                resizeMode="cover"
              />
            ) : null}

            <View style={styles.pageCopyCard}>
              <Text style={styles.pageCopy}>{currentPage.text}</Text>
              <Text style={styles.pageHint}>
                Keep the main narration stable. Optional supports stay secondary
                and child-invoked.
              </Text>
            </View>

            {translationVisible && hasVocabulary ? (
              <View style={styles.vocabularyCard}>
                <Text style={styles.sectionLabelDark}>Vocabulary reveal</Text>
                <View style={styles.vocabularyRow}>
                  {(currentPage.overlays?.vocabulary ?? []).map(word => (
                    <View key={word} style={styles.vocabularyChip}>
                      <Text style={styles.vocabularyText}>{word}</Text>
                    </View>
                  ))}
                </View>
              </View>
            ) : (
              <View style={styles.helperCard}>
                <Text style={styles.helperTitle}>
                  Optional support stays hidden by default.
                </Text>
                <Text style={styles.helperCopy}>
                  Translation and vocabulary only surface when the child or
                  caregiver asks for them.
                </Text>
              </View>
            )}
          </View>

          <View style={styles.panelGrid}>
            <View style={styles.panelCard}>
              <Text style={styles.sectionLabelDark}>Page turn</Text>
              <View style={styles.dualActionRow}>
                <Pressable
                  onPress={() => void goToPreviousPage()}
                  disabled={!canGoToPreviousPage}
                  style={({ pressed }) => [
                    styles.secondaryAction,
                    !canGoToPreviousPage && styles.disabledAction,
                    pressed && styles.pressedAction,
                  ]}
                >
                  <Text style={styles.secondaryActionLabel}>Previous page</Text>
                </Pressable>

                <Pressable
                  onPress={() => void goToNextPage()}
                  disabled={!canGoToNextPage}
                  style={({ pressed }) => [
                    styles.secondaryAction,
                    !canGoToNextPage && styles.disabledAction,
                    pressed && styles.pressedAction,
                  ]}
                >
                  <Text style={styles.secondaryActionLabel}>Next page</Text>
                </Pressable>
              </View>
            </View>

            <View style={styles.panelCard}>
              <Text style={styles.sectionLabelDark}>Read-to-me audio</Text>
              <View style={styles.audioTrack}>
                <View
                  style={[styles.audioFill, { width: `${audioProgress}%` }]}
                />
              </View>
              <View style={styles.audioMetaRow}>
                <Text style={styles.audioMeta}>
                  {audio.ready
                    ? formatAudioClock(audio.currentTimeSec)
                    : '0:00'}
                </Text>
                <Text style={styles.audioMeta}>
                  {audio.durationSec > 0
                    ? formatAudioClock(audio.durationSec)
                    : 'demo audio'}
                </Text>
              </View>
              <View style={styles.dualActionRow}>
                <Pressable
                  onPress={togglePlayPause}
                  disabled={!audio.available}
                  style={({ pressed }) => [
                    styles.secondaryAction,
                    !audio.available && styles.disabledAction,
                    pressed && styles.pressedAction,
                  ]}
                >
                  <Text style={styles.secondaryActionLabel}>
                    {audio.playing ? 'Pause audio' : 'Play audio'}
                  </Text>
                </Pressable>

                <Pressable
                  onPress={() => void replayAudio()}
                  disabled={!audio.available}
                  style={({ pressed }) => [
                    styles.secondaryAction,
                    !audio.available && styles.disabledAction,
                    pressed && styles.pressedAction,
                  ]}
                >
                  <Text style={styles.secondaryActionLabel}>Replay audio</Text>
                </Pressable>
              </View>
              <Text style={styles.audioHint}>
                {audio.buffering
                  ? 'Buffering page audio...'
                  : audio.ready
                    ? 'Audio player is ready for the current page.'
                    : 'Current page audio will play from the resolved runtime source.'}
              </Text>
            </View>
          </View>

          <View style={styles.panelGrid}>
            <View style={styles.panelCard}>
              <Text style={styles.sectionLabelDark}>Support overlays</Text>
              <Pressable
                onPress={() =>
                  void ingestEvent({
                    eventType: 'word_revealed_translation',
                    payload: {
                      word: currentPage.overlays?.vocabulary?.[0] ?? 'bridge',
                      reveal_count: 1,
                    },
                    pageIndex: currentPage.page_index,
                    revealTranslation: true,
                  })
                }
                disabled={!hasVocabulary}
                style={({ pressed }) => [
                  styles.secondaryAction,
                  !hasVocabulary && styles.disabledAction,
                  pressed && styles.pressedAction,
                ]}
              >
                <Text style={styles.secondaryActionLabel}>
                  Reveal vocabulary
                </Text>
              </Pressable>
              <Text style={styles.helperCopy}>
                Current page exposes{' '}
                {currentPage.overlays?.vocabulary?.length ?? 0} vocabulary
                item(s).
              </Text>
            </View>

            <View style={styles.panelCard}>
              <Text style={styles.sectionLabelDark}>Preload window</Text>
              <Text style={styles.preloadStatus}>
                {preloadState.status.toUpperCase()}{' '}
                {preloadState.targetPageIndexes.length > 0
                  ? `· pages ${preloadState.targetPageIndexes.map(pageIndex => pageIndex + 1).join(', ')}`
                  : ''}
              </Text>
              <Text style={styles.helperCopy}>
                {preloadState.error ??
                  `Ready pages: ${
                    preloadState.readyPageIndexes.length > 0
                      ? preloadState.readyPageIndexes
                          .map(pageIndex => pageIndex + 1)
                          .join(', ')
                      : 'none yet'
                  }.`}
              </Text>
            </View>
          </View>

          <View style={styles.receiptCard}>
            <Text style={styles.sectionLabelDark}>Accepted receipt</Text>
            <Text style={styles.receiptValue}>{sessionReceipt.session_id}</Text>
            <Text style={styles.receiptCopy}>
              accepted at {sessionReceipt.accepted_at} · child{' '}
              {sessionReceipt.child_id}
            </Text>
          </View>

          <View style={styles.actionStrip}>
            <Pressable
              onPress={() => void handleFinishSession()}
              style={({ pressed }) => [
                styles.primaryAction,
                pressed && styles.pressedAction,
              ]}
            >
              <Text style={styles.primaryActionLabel}>Finish for Tonight</Text>
            </Pressable>
          </View>
        </>
      ) : (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyTitle}>Session state is not available.</Text>
          <Text style={styles.emptyCopy}>
            Open a package and start a session from the package route before
            entering the live reading screen.
          </Text>
          <Pressable
            onPress={() => router.replace('/')}
            style={({ pressed }) => [
              styles.primaryAction,
              pressed && styles.pressedAction,
            ]}
          >
            <Text style={styles.primaryActionLabel}>Return Home</Text>
          </Pressable>
        </View>
      )}

      {error && (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Session error</Text>
          <Text style={styles.errorCopy}>{error}</Text>
        </View>
      )}

      <View style={styles.activityCard}>
        <Text style={styles.sectionLabelDark}>Recent activity</Text>
        <View style={styles.activityList}>
          {activity.map(item => (
            <View key={item.id} style={styles.activityItem}>
              <Text style={styles.activityLabel}>{item.label}</Text>
              <Text style={styles.activityTimestamp}>{item.timestamp}</Text>
            </View>
          ))}
        </View>
      </View>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  backLink: {
    alignSelf: 'flex-start',
    backgroundColor: '#f1e4ca',
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  backLinkLabel: {
    color: '#6a5538',
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  heroCard: {
    backgroundColor: '#24313f',
    borderRadius: 32,
    padding: 24,
    gap: 14,
  },
  heroHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionLabel: {
    color: '#d3dcdf',
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  sectionLabelDark: {
    color: '#6b5d4a',
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  sessionBadge: {
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
    fontSize: 30,
    lineHeight: 36,
    fontWeight: '800',
  },
  heroCopy: {
    color: '#d7e0e6',
    fontSize: 15,
    lineHeight: 22,
  },
  stageCard: {
    backgroundColor: '#fffaf0',
    borderRadius: 30,
    padding: 20,
    gap: 16,
    borderWidth: 1,
    borderColor: '#e8dac0',
  },
  stageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 12,
  },
  pageModeBadge: {
    backgroundColor: '#e9efe8',
    color: '#27403a',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 6,
    overflow: 'hidden',
    fontSize: 11,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  pageProgressTrack: {
    height: 10,
    borderRadius: 999,
    backgroundColor: '#f1e4ca',
    overflow: 'hidden',
  },
  pageProgressFill: {
    height: '100%',
    borderRadius: 999,
    backgroundColor: '#df7f63',
  },
  pageArtwork: {
    width: '100%',
    height: 220,
    borderRadius: 24,
    backgroundColor: '#f1e4ca',
  },
  pageCopyCard: {
    backgroundColor: '#f8efe0',
    borderRadius: 24,
    padding: 18,
    gap: 10,
  },
  pageCopy: {
    color: '#24313f',
    fontSize: 28,
    lineHeight: 36,
    fontWeight: '700',
  },
  pageHint: {
    color: '#5a6170',
    fontSize: 14,
    lineHeight: 20,
  },
  helperCard: {
    backgroundColor: '#f0f5ef',
    borderRadius: 24,
    padding: 16,
    gap: 8,
  },
  helperTitle: {
    color: '#24313f',
    fontSize: 16,
    fontWeight: '800',
  },
  helperCopy: {
    color: '#596170',
    fontSize: 14,
    lineHeight: 20,
  },
  vocabularyCard: {
    backgroundColor: '#f0f5ef',
    borderRadius: 24,
    padding: 16,
    gap: 10,
  },
  vocabularyRow: {
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
  panelGrid: {
    gap: 14,
  },
  panelCard: {
    backgroundColor: '#fffdf7',
    borderRadius: 28,
    padding: 18,
    gap: 12,
    borderWidth: 1,
    borderColor: '#eee1c9',
  },
  dualActionRow: {
    flexDirection: 'row',
    gap: 10,
    flexWrap: 'wrap',
  },
  secondaryAction: {
    flexGrow: 1,
    minWidth: 140,
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
  audioTrack: {
    height: 10,
    borderRadius: 999,
    backgroundColor: '#efe5d1',
    overflow: 'hidden',
  },
  audioFill: {
    height: '100%',
    borderRadius: 999,
    backgroundColor: '#27403a',
  },
  audioMetaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  audioMeta: {
    color: '#5a6170',
    fontSize: 12,
    fontWeight: '700',
  },
  audioHint: {
    color: '#596170',
    fontSize: 13,
    lineHeight: 18,
  },
  preloadStatus: {
    color: '#24313f',
    fontSize: 15,
    fontWeight: '800',
  },
  receiptCard: {
    backgroundColor: '#f0f5ef',
    borderRadius: 30,
    padding: 20,
    gap: 10,
    borderWidth: 1,
    borderColor: '#d7e6d8',
  },
  receiptValue: {
    color: '#24313f',
    fontSize: 16,
    fontWeight: '800',
  },
  receiptCopy: {
    color: '#596170',
    fontSize: 14,
    lineHeight: 20,
  },
  actionStrip: {
    backgroundColor: '#fffdf7',
    borderRadius: 30,
    padding: 20,
    borderWidth: 1,
    borderColor: '#eee1c9',
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
  emptyCard: {
    backgroundColor: '#fffaf0',
    borderRadius: 30,
    padding: 20,
    gap: 14,
    borderWidth: 1,
    borderColor: '#e8dac0',
  },
  emptyTitle: {
    color: '#24313f',
    fontSize: 22,
    lineHeight: 28,
    fontWeight: '800',
  },
  emptyCopy: {
    color: '#5a6170',
    fontSize: 15,
    lineHeight: 22,
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
    backgroundColor: '#ffffff',
    borderRadius: 30,
    padding: 20,
    gap: 12,
    borderWidth: 1,
    borderColor: '#eee1c9',
  },
  activityList: {
    gap: 10,
  },
  activityItem: {
    backgroundColor: '#f8efe0',
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
  pressedAction: {
    transform: [{ scale: 0.985 }],
  },
});
