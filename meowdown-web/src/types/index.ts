// 图片转换相关类型
export interface ImageConversionStats {
  totalOriginalSize: number
  totalConvertedSize: number
  compressionRatio: number
  sizeSaved: number
}

export interface ConversionResult {
  newMarkdown: string
  successCount: number
  stats: ImageConversionStats
}

// 图床配置类型
export interface ImageBedConfig {
  provider: 'aliyun_oss' | 'cos_v5' | 'qiniu' | 's3' | 'github'
  enabled: boolean
  config: Record<string, any>
}

// 应用状态类型
export interface AppState {
  markdown: string
  quality: number
  isConverting: boolean
  progress: number
  progressMessage: string
  imageBedConfig?: ImageBedConfig
}

// 进度回调类型
export type ProgressCallback = (progress: number, message: string) => void

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 预设类型
export interface QualityPreset {
  name: string
  value: number
  description: string
}

// 文件操作类型
export interface FileOperations {
  openFile: () => void
  saveFile: () => void
  dragActive: boolean
}

// 压缩评级类型
export type CompressionGrade = '极佳' | '良好' | '一般' | '轻微'

// 统计显示类型
export interface StatsDisplay {
  originalSize: string
  convertedSize: string
  compressionRatio: string
  sizeSaved: string
  grade: CompressionGrade
}
