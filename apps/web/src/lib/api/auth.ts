/**
 * 认证相关API
 */

import { apiClient } from './client'
import { 
  User, 
  AuthTokens, 
  LoginRequest, 
  RegisterRequest, 
  WeChatLoginRequest, 
  PasswordResetRequest,
  VerificationCodeRequest 
} from '@/types/user'

export const authApi = {
  // 用户注册
  register: (data: RegisterRequest) => {
    return apiClient.post<AuthTokens>('/auth/register', data)
  },

  // 用户登录
  login: (data: LoginRequest) => {
    return apiClient.post<AuthTokens>('/auth/login', data)
  },

  // 微信登录
  wechatLogin: (data: WeChatLoginRequest) => {
    return apiClient.post<AuthTokens>('/auth/wechat-login', data)
  },

  // 发送验证码
  sendVerificationCode: (phone: string) => {
    return apiClient.post('/auth/send-verification-code', { phone })
  },

  // 重置密码
  resetPassword: (data: PasswordResetRequest) => {
    return apiClient.post('/auth/reset-password', data)
  },

  // 验证验证码
  verifyCode: (data: VerificationCodeRequest) => {
    return apiClient.post('/auth/verify-code', data)
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    return apiClient.get<User>('/users/me')
  },

  // 更新用户信息
  updateUser: (updates: Partial<User>) => {
    return apiClient.put<User>('/users/me', updates)
  }
}
