/**
 * 故事相关API
 */

import { apiClient } from './client'
import { Story, StoryRequest, StoryGenerationResponse, StoryGenerationStatus } from '@/types/story'

export const storyApi = {
  // 获取故事列表
  getStories: (params?: { skip?: number; limit?: number }) => {
    return apiClient.get<Story[]>('/stories', { params })
  },

  // 获取单个故事
  getStory: (storyId: string) => {
    return apiClient.get<Story>(`/stories/${storyId}`)
  },

  // 生成故事
  generateStory: (request: StoryRequest) => {
    return apiClient.post<StoryGenerationResponse>('/stories/generate', request)
  },

  // 获取故事生成状态
  getStoryStatus: (storyId: string) => {
    return apiClient.get<StoryGenerationStatus>(`/stories/${storyId}/status`)
  },

  // 更新故事
  updateStory: (storyId: string, updates: Partial<Story>) => {
    return apiClient.put<Story>(`/stories/${storyId}`, updates)
  },

  // 删除故事
  deleteStory: (storyId: string) => {
    return apiClient.delete(`/stories/${storyId}`)
  },

  // 创建WebSocket连接用于实时生成
  createGenerationWebSocket: (storyId: string) => {
    return apiClient.createWebSocket(`/stories/${storyId}/stream`)
  }
}
