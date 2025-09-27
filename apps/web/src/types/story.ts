/**
 * 故事相关类型定义
 */

export interface Story {
  id: string
  child_id: string
  title: string
  theme: string
  age_group: string
  content: {
    pages: StoryPage[]
    characters: StoryCharacter[]
    vocabulary_targets: string[]
    extension_activities: string[]
    cultural_elements: string[]
  }
  generation_type: 'preproduced' | 'template' | 'realtime'
  status: 'generating' | 'ready' | 'failed'
  quality_score?: number
  safety_score?: number
  educational_value_score?: number
  word_count?: number
  page_count?: number
  reading_time?: number
  created_at: string
  updated_at: string
}

export interface StoryPage {
  page_number: number
  text: string
  illustration_prompt: string
  crowd_prompt?: {
    type: 'completion' | 'recall' | 'open_ended' | 'wh_question' | 'distancing'
    text: string
  }
  reading_time_seconds: number
  word_count: number
}

export interface StoryCharacter {
  name: string
  description: string
  personality: string
  visual_description: string
  role_in_story: string
}

export interface StoryRequest {
  child_id: string
  theme: string
  series_bible_id?: string
  user_preferences?: Record<string, any>
  generation_type?: 'preproduced' | 'template' | 'realtime'
}

export interface StoryGenerationResponse {
  story_id: string
  status: 'generating' | 'ready' | 'failed'
  estimated_time_minutes?: number
  message: string
}

export interface StoryGenerationStatus {
  status: string
  progress_percentage?: number
  estimated_remaining_seconds?: number
  story_id?: string
  title?: string
  quality_score?: number
  error_message?: string
}

export interface ReadingSession {
  id: string
  child_id: string
  story_id: string
  started_at: string
  completed_at?: string
  duration_seconds?: number
  progress_percentage: number
  last_page_read: number
  vocabulary_learned: string[]
  comprehension_score?: number
  engagement_metrics: Record<string, any>
}
