'use client'

import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useNeuroAdaptiveStore } from '@/stores/neuro-adaptive'
import { ChildProfile } from '@/types/child'

interface AdaptiveProviderProps {
  children: ReactNode
  childProfile?: ChildProfile
}

const AdaptiveContext = createContext<{
  adaptations: any
  updateAdaptation: (key: string, value: any) => void
} | null>(null)

export function AdaptiveProvider({ children, childProfile }: AdaptiveProviderProps) {
  const { adaptations, updateAdaptation, initializeFromProfile } = useNeuroAdaptiveStore()

  useEffect(() => {
    if (childProfile?.neuro_profile) {
      initializeFromProfile(childProfile.neuro_profile)
    }
  }, [childProfile, initializeFromProfile])

  // 确保adaptations有默认值
  const safeAdaptations = adaptations || {
    textSize: 16,
    lineHeight: 1.6,
    fontFamily: 'system-ui, -apple-system, sans-serif',
    backgroundColor: '#ffffff',
    textColor: '#1f2937'
  }

  return (
    <AdaptiveContext.Provider value={{ adaptations: safeAdaptations, updateAdaptation }}>
      <div
        className="adaptive-root"
        style={{
          fontSize: `${safeAdaptations.textSize}px`,
          lineHeight: safeAdaptations.lineHeight,
          fontFamily: safeAdaptations.fontFamily,
          backgroundColor: safeAdaptations.backgroundColor,
          color: safeAdaptations.textColor
        }}
      >
        {children}
      </div>
    </AdaptiveContext.Provider>
  )
}

export const useAdaptiveContext = () => {
  const context = useContext(AdaptiveContext)
  if (!context) {
    throw new Error('useAdaptiveContext must be used within AdaptiveProvider')
  }
  return context
}
