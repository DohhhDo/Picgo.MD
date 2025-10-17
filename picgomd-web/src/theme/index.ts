import { extendTheme } from '@chakra-ui/react'

// 简化主题配置，确保默认导出存在
const config = {
  initialColorMode: 'light',
  useSystemColorMode: false,
}

const colors = {
  meowdown: {
    50: '#e8f5e8',
    100: '#c8e6c9',
    200: '#a5d6a7',
    300: '#81c784',
    400: '#66bb6a',
    500: '#4caf50',
    600: '#43a047',
    700: '#388e3c',
    800: '#2e7d32',
    900: '#1b5e20',
  },
}

const fonts = {
  heading: 'Microsoft YaHei, sans-serif',
  body: 'Microsoft YaHei, sans-serif',
}

const theme = extendTheme({
  config,
  colors,
  fonts,
})

export default theme
