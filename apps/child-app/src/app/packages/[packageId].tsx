import { router, useLocalSearchParams } from 'expo-router';
import { startTransition, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { ScreenShell } from '@/components/screen-shell';
import { useChildRuntime } from '@/features/runtime/provider';

function formatDuration(seconds: number): string {
  const minutes = Math.max(1, Math.round(seconds / 60));
  return `${minutes} min`;
}

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

export default function PackageScreen() {
  const { packageId } = useLocalSearchParams<{
    packageId?: string | string[];
  }>();
  const normalizedPackageId = normalizeRouteParam(packageId);
  const { activeAction, activePackage, error, loadPackage, startSession } =
    useChildRuntime();
  const [localError, setLocalError] = useState<string | null>(null);
  const displayedPackage =
    activePackage?.package_id === normalizedPackageId ? activePackage : null;

  useEffect(() => {
    let isMounted = true;

    async function ensurePackage() {
      if (!normalizedPackageId) {
        if (isMounted) {
          setLocalError('No package id was provided.');
        }
        return;
      }

      const storyPackage = await loadPackage(normalizedPackageId);

      if (!storyPackage && isMounted) {
        setLocalError('The selected package could not be loaded.');
      }
    }

    void ensurePackage();

    return () => {
      isMounted = false;
    };
  }, [normalizedPackageId]);

  async function handleStartSession() {
    if (!normalizedPackageId) {
      return;
    }

    const receipt = await startSession(normalizedPackageId);

    if (!receipt) {
      return;
    }

    startTransition(() => {
      router.push({
        pathname: '/session/[sessionId]',
        params: { sessionId: receipt.session_id },
      });
    });
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
        <Text style={styles.backLinkLabel}>Back to home</Text>
      </Pressable>

      <View style={styles.heroCard}>
        <Text style={styles.sectionLabel}>Package preview</Text>
        <Text style={styles.heroTitle}>
          {displayedPackage?.title ?? 'Loading package...'}
        </Text>
        <Text style={styles.heroCopy}>
          {displayedPackage?.subtitle ??
            'The package view is the typed handoff between the child home shelf and a live reading session.'}
        </Text>

        <View style={styles.metaRow}>
          <Text style={styles.metaPill}>
            {displayedPackage?.language_mode ?? 'language'}
          </Text>
          <Text style={styles.metaPill}>
            {displayedPackage?.age_band ?? 'age band'}
          </Text>
          <Text style={styles.metaPill}>
            {displayedPackage?.pages.length ?? 0} pages
          </Text>
          <Text style={styles.metaPill}>
            {displayedPackage
              ? formatDuration(displayedPackage.estimated_duration_sec)
              : 'duration'}
          </Text>
          <Text style={styles.metaPill}>
            {displayedPackage?.difficulty_level ?? 'difficulty'}
          </Text>
        </View>
      </View>

      <View style={styles.previewCard}>
        <View style={styles.previewHeader}>
          <Text style={styles.sectionLabelDark}>First spread preview</Text>
          {activeAction === 'package' && <ActivityIndicator color="#27403a" />}
        </View>

        <View style={styles.copyCard}>
          <Text style={styles.copyEyebrow}>Narration</Text>
          <Text style={styles.copyText}>
            {displayedPackage?.pages[0]?.text_runs
              .map(run => run.text)
              .join(' ') ?? 'Loading typed page content...'}
          </Text>
        </View>

        <View style={styles.copyCard}>
          <Text style={styles.copyEyebrow}>Vocabulary overlay</Text>
          <View style={styles.vocabularyRow}>
            {(displayedPackage?.pages[0]?.overlays?.vocabulary ?? []).map(
              word => (
                <View key={word} style={styles.vocabularyChip}>
                  <Text style={styles.vocabularyText}>{word}</Text>
                </View>
              )
            )}
          </View>
        </View>

        <View style={styles.copyCard}>
          <Text style={styles.copyEyebrow}>Session contract</Text>
          <Text style={styles.contractCopy}>
            Starting from this screen will issue a typed `ReadingSessionCreate
            v2` command and then transition into the live session route with
            page preload and audio runtime state.
          </Text>
        </View>
      </View>

      {(localError || error) && (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Package route error</Text>
          <Text style={styles.errorCopy}>{localError ?? error}</Text>
        </View>
      )}

      <View style={styles.actionCard}>
        <Pressable
          onPress={() => void handleStartSession()}
          disabled={!displayedPackage || activeAction !== null}
          style={({ pressed }) => [
            styles.primaryAction,
            (!displayedPackage || activeAction !== null) &&
              styles.disabledAction,
            pressed && styles.pressedAction,
          ]}
        >
          <Text style={styles.primaryActionLabel}>Begin Reading Session</Text>
        </Pressable>
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
  metaRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  metaPill: {
    backgroundColor: '#304252',
    color: '#fff8ef',
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
    overflow: 'hidden',
    fontSize: 12,
    fontWeight: '700',
  },
  previewCard: {
    backgroundColor: '#fffaf0',
    borderRadius: 30,
    padding: 20,
    gap: 14,
    borderWidth: 1,
    borderColor: '#e8dac0',
  },
  previewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  copyCard: {
    backgroundColor: '#f8efe0',
    borderRadius: 24,
    padding: 16,
    gap: 10,
  },
  copyEyebrow: {
    color: '#7a6646',
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.8,
    textTransform: 'uppercase',
  },
  copyText: {
    color: '#24313f',
    fontSize: 24,
    lineHeight: 32,
    fontWeight: '700',
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
  contractCopy: {
    color: '#596170',
    fontSize: 14,
    lineHeight: 20,
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
  actionCard: {
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
  disabledAction: {
    opacity: 0.45,
  },
  pressedAction: {
    transform: [{ scale: 0.985 }],
  },
});
