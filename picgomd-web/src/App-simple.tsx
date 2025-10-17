import { Box, Text, Button, VStack, useToast, useColorMode } from '@chakra-ui/react'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'

function App() {
  const toast = useToast()
  const { colorMode, toggleColorMode } = useColorMode()

  const showToast = () => {
    toast({
      title: '测试成功！',
      description: 'Chakra UI 正常工作',
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
  }

  return (
    <Box p={8} minH="100vh">
      <VStack spacing={6} align="center">
        <Text fontSize="2xl" fontWeight="bold" color="green.500">
          🐾 Meowdown Web - 简化测试版
        </Text>
        
        <Button
          leftIcon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          colorScheme="blue"
        >
          切换主题 ({colorMode})
        </Button>
        
        <Button onClick={showToast} colorScheme="green">
          测试 Toast 通知
        </Button>
        
        <Box p={4} bg="gray.100" borderRadius="md" textAlign="center" maxW="md">
          <Text mb={2}>✅ React 应用正常运行</Text>
          <Text mb={2}>✅ Chakra UI 组件正常</Text>
          <Text mb={2}>✅ 主题切换功能正常</Text>
          <Text fontSize="sm" color="gray.600">
            如果看到这个页面，说明前端环境完全正常！
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}

export default App
