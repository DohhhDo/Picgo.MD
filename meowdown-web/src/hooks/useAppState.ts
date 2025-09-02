import { useState, useCallback } from 'react'
import type { AppState, ProgressCallback } from '../types'

const initialState: AppState = {
  markdown: '',
  quality: 73,
  isConverting: false,
  progress: 0,
  progressMessage: '准备就绪',
}

export const useAppState = () => {
  const [state, setState] = useState<AppState>(initialState)

  const updateMarkdown = useCallback((markdown: string) => {
    setState(prev => ({ ...prev, markdown }))
  }, [])

  const updateQuality = useCallback((quality: number) => {
    setState(prev => ({ ...prev, quality }))
  }, [])

  const setConverting = useCallback((isConverting: boolean) => {
    setState(prev => ({ ...prev, isConverting }))
  }, [])

  const updateProgress = useCallback((progress: number, message: string) => {
    setState(prev => ({ ...prev, progress, progressMessage: message }))
  }, [])

  const resetProgress = useCallback(() => {
    setState(prev => ({ ...prev, progress: 0, progressMessage: '准备就绪' }))
  }, [])

  const progressCallback: ProgressCallback = useCallback((progress, message) => {
    updateProgress(progress, message)
  }, [updateProgress])

  return {
    state,
    updateMarkdown,
    updateQuality,
    setConverting,
    updateProgress,
    resetProgress,
    progressCallback,
  }
}
