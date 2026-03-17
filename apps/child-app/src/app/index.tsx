import { router } from 'expo-router';
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

export default function ChildHomeScreen() {
  const { activity, activeAction, homePackages, mode, sessionReceipt } =
    useChildRuntime();
  const featuredPackage = homePackages[0] ?? null;

  return (
    <ScreenShell>
      <View style={styles.heroCard}>
        <View style={styles.kickerRow}>
          <Text style={styles.kicker}>Lumos Reading</Text>
          <Text style={styles.modeBadge}>{mode.toUpperCase()}</Text>
        </View>

        <Text style={styles.heroTitle}>
          A quiet library built for shared bedtime reading.
        </Text>
        <Text style={styles.heroCopy}>
          Home now acts as a real child runtime entry surface. It hands off into
          typed story packages, then into a live session that carries page
          progression, media preload, and read-to-me playback state.
        </Text>

        <View style={styles.metricsRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Packages</Text>
            <Text style={styles.metricValue}>{homePackages.length}</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Session</Text>
            <Text style={styles.metricValue}>
              {sessionReceipt ? 'active' : 'not started'}
            </Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Flow</Text>
            <Text style={styles.metricValue}>home to package to session</Text>
          </View>
        </View>
      </View>

      <View style={styles.featureCard}>
        <Text style={styles.sectionLabel}>Featured tonight</Text>

        {activeAction === 'home' && !featuredPackage ? (
          <View style={styles.loadingCard}>
            <ActivityIndicator color="#27403a" />
            <Text style={styles.loadingCopy}>Loading the reading shelf...</Text>
          </View>
        ) : featuredPackage ? (
          <>
            <Text style={styles.featureTitle}>{featuredPackage.title}</Text>
            <Text style={styles.featureSubtitle}>
              {featuredPackage.subtitle}
            </Text>

            <View style={styles.metaRow}>
              <Text style={styles.metaPill}>
                {featuredPackage.language_mode}
              </Text>
              <Text style={styles.metaPill}>{featuredPackage.age_band}</Text>
              <Text style={styles.metaPill}>
                {featuredPackage.pages.length} pages
              </Text>
              <Text style={styles.metaPill}>
                {formatDuration(featuredPackage.estimated_duration_sec)}
              </Text>
            </View>

            <Pressable
              onPress={() =>
                router.push({
                  pathname: '/packages/[packageId]',
                  params: { packageId: featuredPackage.package_id },
                })
              }
              style={({ pressed }) => [
                styles.primaryAction,
                pressed && styles.pressedAction,
              ]}
            >
              <Text style={styles.primaryActionLabel}>
                Open Featured Package
              </Text>
            </Pressable>
          </>
        ) : (
          <Text style={styles.emptyCopy}>No package is available yet.</Text>
        )}
      </View>

      <View style={styles.shelfCard}>
        <Text style={styles.sectionLabel}>Tonight&apos;s shelf</Text>
        <View style={styles.shelfList}>
          {homePackages.map(storyPackage => (
            <Pressable
              key={storyPackage.package_id}
              onPress={() =>
                router.push({
                  pathname: '/packages/[packageId]',
                  params: { packageId: storyPackage.package_id },
                })
              }
              style={({ pressed }) => [
                styles.shelfItem,
                pressed && styles.pressedAction,
              ]}
            >
              <View style={styles.shelfHeader}>
                <Text style={styles.shelfTitle}>{storyPackage.title}</Text>
                <Text style={styles.shelfBadge}>
                  {storyPackage.safety.review_status}
                </Text>
              </View>
              <Text style={styles.shelfCopy} numberOfLines={2}>
                {storyPackage.subtitle}
              </Text>
              <Text style={styles.shelfMeta}>
                {storyPackage.language_mode} · {storyPackage.difficulty_level} ·{' '}
                {storyPackage.pages.length} pages
                {' · '}
                {formatDuration(storyPackage.estimated_duration_sec)}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>

      <View style={styles.activityCard}>
        <Text style={styles.sectionLabel}>Runtime activity</Text>
        <View style={styles.activityList}>
          {activity.length === 0 ? (
            <Text style={styles.emptyCopy}>No activity yet.</Text>
          ) : (
            activity.map(item => (
              <View key={item.id} style={styles.activityItem}>
                <Text style={styles.activityLabel}>{item.label}</Text>
                <Text style={styles.activityTimestamp}>{item.timestamp}</Text>
              </View>
            ))
          )}
        </View>
      </View>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  heroCard: {
    backgroundColor: '#24313f',
    borderRadius: 32,
    padding: 24,
    gap: 18,
  },
  kickerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  kicker: {
    color: '#f7f0e1',
    fontSize: 12,
    fontWeight: '800',
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
    fontSize: 30,
    lineHeight: 36,
    fontWeight: '800',
    maxWidth: 560,
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
    minWidth: 120,
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
  featureCard: {
    backgroundColor: '#fffaf0',
    borderRadius: 30,
    padding: 20,
    gap: 14,
    borderWidth: 1,
    borderColor: '#e8dac0',
  },
  loadingCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 10,
  },
  loadingCopy: {
    color: '#596170',
    fontSize: 15,
  },
  sectionLabel: {
    color: '#6b5d4a',
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  featureTitle: {
    color: '#24313f',
    fontSize: 28,
    lineHeight: 32,
    fontWeight: '800',
  },
  featureSubtitle: {
    color: '#5a6170',
    fontSize: 15,
    lineHeight: 22,
  },
  metaRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  metaPill: {
    backgroundColor: '#f1e4ca',
    color: '#6a5538',
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 7,
    overflow: 'hidden',
    fontSize: 12,
    fontWeight: '700',
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
  shelfCard: {
    backgroundColor: '#fffdf7',
    borderRadius: 30,
    padding: 20,
    gap: 16,
    borderWidth: 1,
    borderColor: '#eee1c9',
  },
  shelfList: {
    gap: 12,
  },
  shelfItem: {
    backgroundColor: '#f8efe0',
    borderRadius: 24,
    padding: 16,
    gap: 8,
  },
  shelfHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: 10,
  },
  shelfTitle: {
    color: '#24313f',
    fontSize: 18,
    lineHeight: 22,
    fontWeight: '800',
    flex: 1,
  },
  shelfBadge: {
    color: '#27403a',
    backgroundColor: '#dcefe5',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
    overflow: 'hidden',
    fontSize: 11,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  shelfCopy: {
    color: '#5a6170',
    fontSize: 14,
    lineHeight: 20,
  },
  shelfMeta: {
    color: '#6c7280',
    fontSize: 12,
    fontWeight: '700',
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
  emptyCopy: {
    color: '#596170',
    fontSize: 14,
    lineHeight: 20,
  },
  pressedAction: {
    transform: [{ scale: 0.985 }],
  },
});
