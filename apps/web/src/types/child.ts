/**
 * 儿童档案类型定义
 */

export interface ChildProfile {
  id: string
  name: string
  nickname?: string
  birthday?: string
  gender: 'male' | 'female' | 'other' | 'prefer_not_say'
  avatar_url?: string
  age: number
  age_group: string
  cognitive_stage: string
  preferences: {
    favorite_themes?: string[]
    favorite_characters?: string[]
    reading_style?: 'visual' | 'auditory' | 'kinesthetic'
    interaction_level?: 'low' | 'medium' | 'high'
  }
  neuro_profile: {
    adhd?: {
      shortAttentionBlocks: boolean
      enableBreakReminders: boolean
      autoResumeAfterBreak: boolean
      reduceVisualClutter: boolean
      increaseFocusIndicators: boolean
      showProgressIndicator: boolean
    }
    autism?: {
      enhancePredictability: boolean
      reduceAnimations: boolean
      clearVisualStructure: boolean
      explicitInstructions: boolean
      sensoryComfort: boolean
    }
    dyslexia?: {
      highContrastText: boolean
      largerFontSize: boolean
      readingGuide: boolean
      audioSupport: boolean
    }
  }
  developmental_milestones: {
    language_development?: string[]
    cognitive_skills?: string[]
    social_skills?: string[]
    emotional_regulation?: string[]
  }
  created_at: string
  updated_at: string
}

export interface CreateChildProfileRequest {
  name: string
  nickname?: string
  birthday?: string
  gender: 'male' | 'female' | 'other' | 'prefer_not_say'
  age: number
  preferences?: Partial<ChildProfile['preferences']>
  neuro_profile?: Partial<ChildProfile['neuro_profile']>
}

export interface UpdateChildProfileRequest {
  name?: string
  nickname?: string
  birthday?: string
  gender?: 'male' | 'female' | 'other' | 'prefer_not_say'
  preferences?: Partial<ChildProfile['preferences']>
  neuro_profile?: Partial<ChildProfile['neuro_profile']>
  developmental_milestones?: Partial<ChildProfile['developmental_milestones']>
}
