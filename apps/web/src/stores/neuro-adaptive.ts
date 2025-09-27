/**
 * 神经多样性自适应状态管理
 */

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

export interface NeuroAdaptiveState {
  // 基础自适应设置
  textSize: number
  lineHeight: number
  fontFamily: string
  backgroundColor: string
  textColor: string
  progressBarColor: string
  
  // ADHD适配
  adhd: {
    shortAttentionBlocks: boolean
    enableBreakReminders: boolean
    autoResumeAfterBreak: boolean
    reduceVisualClutter: boolean
    increaseFocusIndicators: boolean
    showProgressIndicator: boolean
  }
  
  // 自闭谱系适配
  autism: {
    enhancePredictability: boolean
    reduceAnimations: boolean
    clearVisualStructure: boolean
    explicitInstructions: boolean
    sensoryComfort: boolean
  }
  
  // 阅读障碍适配
  dyslexia: {
    highContrastText: boolean
    largerFontSize: boolean
    readingGuide: boolean
    audioSupport: boolean
  }
  
  // 通用设置
  enableCROWDInteractions: boolean
  autoAdvancePages: boolean
  showReadingProgress: boolean
  
  // 动作
  updateAdaptation: (key: string, value: any) => void
  initializeFromProfile: (neuroProfile: any) => void
  resetToDefaults: () => void
  applyPreset: (preset: 'adhd' | 'autism' | 'dyslexia' | 'default') => void
}

export const defaultState = {
  textSize: 16,
  lineHeight: 1.6,
  fontFamily: 'system-ui, -apple-system, sans-serif',
  backgroundColor: '#ffffff',
  textColor: '#1f2937',
  progressBarColor: '#3b82f6',
  
  adhd: {
    shortAttentionBlocks: false,
    enableBreakReminders: true,
    autoResumeAfterBreak: false,
    reduceVisualClutter: false,
    increaseFocusIndicators: true,
    showProgressIndicator: true
  },
  
  autism: {
    enhancePredictability: false,
    reduceAnimations: false,
    clearVisualStructure: false,
    explicitInstructions: false,
    sensoryComfort: false
  },
  
  dyslexia: {
    highContrastText: false,
    largerFontSize: false,
    readingGuide: false,
    audioSupport: false
  },
  
  enableCROWDInteractions: true,
  autoAdvancePages: false,
  showReadingProgress: true
}

export const useNeuroAdaptiveStore = create<NeuroAdaptiveState>()(
  persist(
    (set, get) => ({
      ...defaultState,
      
      updateAdaptation: (key: string, value: any) => {
        set((state) => {
          const keys = key.split('.')
          if (keys.length === 1) {
            return { [key]: value }
          } else if (keys.length === 2) {
            return {
              [keys[0]]: {
                ...state[keys[0] as keyof NeuroAdaptiveState],
                [keys[1]]: value
              }
            }
          }
          return state
        })
      },
      
      initializeFromProfile: (neuroProfile: any) => {
        if (!neuroProfile) return
        
        // 使用浅比较避免不必要的更新
        set((state) => {
          const updates: Partial<NeuroAdaptiveState> = {}
          let hasChanges = false
          
          // 应用ADHD设置
          if (neuroProfile.adhd) {
            const newAdhd = { ...state.adhd, ...neuroProfile.adhd }
            if (JSON.stringify(newAdhd) !== JSON.stringify(state.adhd)) {
              updates.adhd = newAdhd
              hasChanges = true
            }
          }
          
          // 应用自闭谱系设置
          if (neuroProfile.autism) {
            const newAutism = { ...state.autism, ...neuroProfile.autism }
            if (JSON.stringify(newAutism) !== JSON.stringify(state.autism)) {
              updates.autism = newAutism
              hasChanges = true
            }
          }
          
          // 应用阅读障碍设置
          if (neuroProfile.dyslexia) {
            const newDyslexia = { ...state.dyslexia, ...neuroProfile.dyslexia }
            if (JSON.stringify(newDyslexia) !== JSON.stringify(state.dyslexia)) {
              updates.dyslexia = newDyslexia
              hasChanges = true
            }
          }
          
          // 只有在有实际变化时才更新状态
          return hasChanges ? updates : state
        })
      },
      
      resetToDefaults: () => {
        set(defaultState)
      },
      
      applyPreset: (preset: 'adhd' | 'autism' | 'dyslexia' | 'default') => {
        const presets = {
          adhd: {
            adhd: {
              shortAttentionBlocks: true,
              enableBreakReminders: true,
              autoResumeAfterBreak: false,
              reduceVisualClutter: true,
              increaseFocusIndicators: true,
              showProgressIndicator: true
            },
            textSize: 18,
            lineHeight: 1.8,
            enableCROWDInteractions: true,
            autoAdvancePages: false
          },
          
          autism: {
            autism: {
              enhancePredictability: true,
              reduceAnimations: true,
              clearVisualStructure: true,
              explicitInstructions: true,
              sensoryComfort: true
            },
            textSize: 16,
            lineHeight: 1.6,
            enableCROWDInteractions: true,
            autoAdvancePages: true
          },
          
          dyslexia: {
            dyslexia: {
              highContrastText: true,
              largerFontSize: true,
              readingGuide: true,
              audioSupport: true
            },
            textSize: 20,
            lineHeight: 2.0,
            backgroundColor: '#f8f9fa',
            textColor: '#000000',
            enableCROWDInteractions: true,
            autoAdvancePages: false
          },
          
          default: defaultState
        }
        
        set(presets[preset])
      }
    }),
    {
      name: 'neuro-adaptive-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        textSize: state.textSize,
        lineHeight: state.lineHeight,
        fontFamily: state.fontFamily,
        backgroundColor: state.backgroundColor,
        textColor: state.textColor,
        progressBarColor: state.progressBarColor,
        adhd: state.adhd,
        autism: state.autism,
        dyslexia: state.dyslexia,
        enableCROWDInteractions: state.enableCROWDInteractions,
        autoAdvancePages: state.autoAdvancePages,
        showReadingProgress: state.showReadingProgress
      })
    }
  )
)
