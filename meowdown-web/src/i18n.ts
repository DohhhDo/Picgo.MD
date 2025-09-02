import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

// 导入翻译文件
import zh from './locales/zh.json'
import en from './locales/en.json'
import es from './locales/es.json'
import fr from './locales/fr.json'

const resources = {
  zh: { translation: zh },
  en: { translation: en },
  es: { translation: es },
  fr: { translation: fr }
}

i18n
  .use(LanguageDetector) // 自动检测用户语言
  .use(initReactI18next) // 绑定 react-i18next
  .init({
    resources,
    
    // 默认语言设置
    fallbackLng: 'zh', // 回退语言为中文
    lng: 'zh', // 默认语言为中文
    
    // 语言检测配置
    detection: {
      // 检测顺序：localStorage -> 浏览器语言 -> 默认语言
      order: ['localStorage', 'navigator', 'htmlTag'],
      // 缓存用户选择的语言
      caches: ['localStorage'],
      // localStorage 的 key
      lookupLocalStorage: 'meowdown-language',
    },

    interpolation: {
      escapeValue: false // React 已经处理了 XSS 防护
    },

    // 调试模式（生产环境建议关闭）
    debug: import.meta.env.DEV
  })

export default i18n
