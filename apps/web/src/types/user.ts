/**
 * 用户相关类型定义
 */

export interface User {
  id: string
  phone?: string
  email?: string
  wechat_openid?: string
  subscription_tier: 'free' | 'standard' | 'premium' | 'family'
  subscription_expires_at?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access_token: string
  token_type: string
}

export interface LoginRequest {
  phone?: string
  email?: string
  password: string
}

export interface RegisterRequest {
  phone: string
  password: string
  email?: string
  wechat_openid?: string
}

export interface WeChatLoginRequest {
  code: string
  encrypted_data?: string
  iv?: string
}

export interface PasswordResetRequest {
  phone: string
  new_password: string
  verification_code: string
}

export interface VerificationCodeRequest {
  phone: string
  code: string
}
