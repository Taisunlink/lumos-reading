'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNeuroAdaptiveStore } from '@/stores/neuro-adaptive'
import { Focus, Play, Pause, RotateCcw } from 'lucide-react'

interface AttentionManagerProps {
  targetDurationMinutes: number
  onAttentionBreak: () => void
  onSessionComplete: () => void
  children: React.ReactNode
}

export function AttentionManager({
  targetDurationMinutes,
  onAttentionBreak,
  onSessionComplete,
  children
}: AttentionManagerProps) {
  const { adaptations } = useNeuroAdaptiveStore()
  const [elapsedTime, setElapsedTime] = useState(0)
  const [isActive, setIsActive] = useState(false)
  const [showBreakSuggestion, setShowBreakSuggestion] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout>()

  const targetSeconds = targetDurationMinutes * 60
  const progressPercent = (elapsedTime / targetSeconds) * 100

  // ADHD适配：较短的专注时间块
  const attentionBlockDuration = adaptations.adhd?.shortAttentionBlocks ?
    Math.min(targetSeconds, 300) : // 5分钟最大
    targetSeconds

  useEffect(() => {
    if (isActive) {
      intervalRef.current = setInterval(() => {
        setElapsedTime(prev => {
          const newTime = prev + 1

          // 检查是否需要注意力休息
          if (adaptations.adhd?.enableBreakReminders &&
              newTime % attentionBlockDuration === 0 &&
              newTime < targetSeconds) {
            setShowBreakSuggestion(true)
            setIsActive(false)
          }

          // 检查是否完成
          if (newTime >= targetSeconds) {
            setIsActive(false)
            onSessionComplete()
          }

          return newTime
        })
      }, 1000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isActive, attentionBlockDuration, targetSeconds, onSessionComplete, adaptations.adhd])

  const handleStart = () => setIsActive(true)
  const handlePause = () => setIsActive(false)
  const handleReset = () => {
    setIsActive(false)
    setElapsedTime(0)
    setShowBreakSuggestion(false)
  }

  const handleBreakComplete = () => {
    setShowBreakSuggestion(false)
    onAttentionBreak()
    // 可以选择自动继续或需要手动开始
    if (adaptations.adhd?.autoResumeAfterBreak) {
      setTimeout(() => setIsActive(true), 1000)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="relative">
      {/* 注意力进度条 - ADHD友好设计 */}
      {adaptations.adhd?.showProgressIndicator && (
        <motion.div
          className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="bg-white/90 backdrop-blur-sm rounded-lg p-4 shadow-lg border">
            <div className="flex items-center gap-3 mb-2">
              <Focus className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-medium">专注时间</span>
              <span className="text-sm text-gray-600">
                {formatTime(elapsedTime)} / {formatTime(targetSeconds)}
              </span>
            </div>

            <div className="w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            <div className="flex gap-2 mt-2">
              {!isActive ? (
                <button
                  onClick={handleStart}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 flex items-center gap-1"
                >
                  <Play className="w-3 h-3" />
                  开始
                </button>
              ) : (
                <button
                  onClick={handlePause}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 flex items-center gap-1"
                >
                  <Pause className="w-3 h-3" />
                  暂停
                </button>
              )}
              <button
                onClick={handleReset}
                className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 rounded flex items-center"
              >
                <RotateCcw className="w-3 h-3" />
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* 注意力休息建议弹窗 */}
      <AnimatePresence>
        {showBreakSuggestion && (
          <motion.div
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-white rounded-xl p-6 max-w-md mx-4 text-center"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
            >
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Focus className="w-8 h-8 text-blue-500" />
              </div>

              <h3 className="text-lg font-semibold mb-2">
                太棒了！休息一下吧 🎉
              </h3>

              <p className="text-gray-600 mb-4">
                你已经专注了 {Math.floor(elapsedTime / 60)} 分钟！
                休息2-3分钟后继续阅读。
              </p>

              <div className="flex gap-3 justify-center">
                <button
                  onClick={handleBreakComplete}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                >
                  好的，休息一下
                </button>
                <button
                  onClick={() => setShowBreakSuggestion(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  继续阅读
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主要内容 */}
      <div
        className={`
          ${adaptations.adhd?.reduceVisualClutter ? 'space-y-6' : 'space-y-4'}
          ${adaptations.adhd?.increaseFocusIndicators ? 'focus-enhanced' : ''}
        `}
      >
        {children}
      </div>
    </div>
  )
}
