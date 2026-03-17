import type { ReactNode } from 'react';
import { ScrollView, StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

type ScreenShellProps = {
  children: ReactNode;
  contentContainerStyle?: StyleProp<ViewStyle>;
};

export function ScreenShell({ children, contentContainerStyle }: ScreenShellProps) {
  return (
    <View style={styles.screen}>
      <View style={styles.backgroundOrbLarge} />
      <View style={styles.backgroundOrbSmall} />
      <View style={styles.backgroundOrbBand} />

      <SafeAreaView style={styles.safeArea}>
        <ScrollView
          contentContainerStyle={[styles.scrollContent, contentContainerStyle]}
          showsVerticalScrollIndicator={false}>
          {children}
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
  backgroundOrbBand: {
    position: 'absolute',
    left: 48,
    right: 48,
    top: 110,
    height: 120,
    borderRadius: 999,
    backgroundColor: '#fbf6eb',
    opacity: 0.7,
    transform: [{ rotate: '-7deg' }],
  },
});
