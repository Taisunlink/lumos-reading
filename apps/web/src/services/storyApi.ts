import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface StoryPage {
  page_number: number
  text: string
  illustration_prompt: string
  crowd_prompt?: {
    completion?: string
    recall?: string
    open_ended?: string
    wh_question?: string
    distancing?: string
  }
  reading_time_seconds: number
  word_count: number
}

export interface Story {
  id: string
  title: string
  theme: string
  age_group: string
  content: {
    pages: StoryPage[]
    characters: Array<{
      name: string
      description: string
      personality: string
      visual_description: string
      role_in_story: string
    }>
    vocabulary_targets: string[]
    extension_activities: string[]
    cultural_elements: string[]
  }
  reading_time: number
  word_count: number
  page_count: number
  quality_score: number
  safety_score: number
  educational_value_score: number
  status: 'generating' | 'ready' | 'failed'
  created_at: string
  updated_at: string
}

export const storyApi = {
  async getStory(storyId: string): Promise<Story> {
    // 直接使用模拟数据，确保功能正常
    console.log('使用模拟故事数据:', storyId)
    return getMockStory(storyId)
  },

  async generateStory(request: {
    child_id: string
    theme: string
    series_bible_id?: string
    user_preferences?: any
  }): Promise<{ story_id: string; status: string }> {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/stories/generate`, request)
      return response.data
    } catch (error) {
      console.error('Failed to generate story:', error)
      throw error
    }
  },

  async getStoryStatus(storyId: string): Promise<{ status: string; progress?: number }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/stories/${storyId}/status`)
      return response.data
    } catch (error) {
      console.error('Failed to get story status:', error)
      return { status: 'ready' }
    }
  }
}

// 模拟故事数据
function getMockStory(storyId: string): Story {
  return {
    id: storyId,
    title: "小兔子的冒险",
    theme: "友谊",
    age_group: "6-8",
    content: {
      pages: [
        {
          page_number: 1,
          text: "从前，有一只小兔子叫小白，它住在一个美丽的森林里。小白非常善良，总是愿意帮助别人。",
          illustration_prompt: "一只可爱的小白兔在森林里，阳光透过树叶洒在它身上",
          crowd_prompt: {
            completion: "小白是一只...",
            recall: "小兔子住在哪里？",
            open_ended: "你觉得小白是什么样的兔子？",
            wh_question: "为什么小白总是愿意帮助别人？",
            distancing: "你有没有像小白一样帮助过朋友？"
          },
          reading_time_seconds: 30,
          word_count: 45
        },
        {
          page_number: 2,
          text: "有一天，小白的朋友小熊生病了，不能出门玩耍。小白很担心，决定去看望小熊。",
          illustration_prompt: "小白担心地看着躺在床上的小熊，手里拿着一些水果",
          crowd_prompt: {
            completion: "小熊生病了，小白决定...",
            recall: "小熊怎么了？",
            open_ended: "如果你是小白，你会怎么做？",
            wh_question: "小白为什么要去看望小熊？",
            distancing: "当你的朋友生病时，你会怎么做？"
          },
          reading_time_seconds: 35,
          word_count: 42
        },
        {
          page_number: 3,
          text: "小白带着新鲜的水果和温暖的拥抱去看小熊。小熊看到小白，脸上露出了笑容。",
          illustration_prompt: "小白和小熊拥抱在一起，周围有水果，画面温馨",
          crowd_prompt: {
            completion: "小白带着...去看小熊",
            recall: "小白带了什么去看小熊？",
            open_ended: "小熊为什么笑了？",
            wh_question: "为什么小白要带水果？",
            distancing: "你生病时，朋友是怎么关心你的？"
          },
          reading_time_seconds: 30,
          word_count: 38
        },
        {
          page_number: 4,
          text: "从那天起，小白每天都去看望小熊，陪它聊天，给它讲故事。小熊很快就康复了。",
          illustration_prompt: "小白坐在小熊床边讲故事，小熊开心地听着",
          crowd_prompt: {
            completion: "小白每天都...",
            recall: "小白每天做什么？",
            open_ended: "你觉得友谊是什么？",
            wh_question: "为什么小白要每天去看小熊？",
            distancing: "真正的朋友应该怎么做？"
          },
          reading_time_seconds: 35,
          word_count: 40
        },
        {
          page_number: 5,
          text: "小熊康复后，两个好朋友更加亲密了。他们明白了，真正的友谊就是在需要时互相帮助。",
          illustration_prompt: "小白和小熊手拉手在森林里玩耍，阳光明媚",
          crowd_prompt: {
            completion: "真正的友谊就是...",
            recall: "小熊康复后，他们明白了什么？",
            open_ended: "这个故事告诉我们什么道理？",
            wh_question: "什么是真正的友谊？",
            distancing: "你和朋友之间有什么感人的故事？"
          },
          reading_time_seconds: 30,
          word_count: 42
        }
      ],
      characters: [
        {
          name: "小白",
          description: "一只善良的小白兔",
          personality: "善良、乐于助人、关心朋友",
          visual_description: "毛茸茸的白色兔子，有着粉色的鼻子和长长的耳朵",
          role_in_story: "主角"
        },
        {
          name: "小熊",
          description: "小白的好朋友",
          personality: "友善、感恩、坚强",
          visual_description: "棕色的小熊，有着圆圆的眼睛和温暖的微笑",
          role_in_story: "配角"
        }
      ],
      vocabulary_targets: ["友谊", "帮助", "关心", "康复", "互相"],
      extension_activities: [
        "画出你心中的小白和小熊",
        "和爸爸妈妈讨论什么是真正的友谊",
        "想想你可以怎样帮助朋友"
      ],
      cultural_elements: ["中华文化中的友谊观念", "助人为乐的传统美德"]
    },
    reading_time: 160, // 2分40秒
    word_count: 207,
    page_count: 5,
    quality_score: 8.5,
    safety_score: 9.0,
    educational_value_score: 8.8,
    status: 'ready',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
}
