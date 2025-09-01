import React from 'react'
import {
  Box,
  Textarea,
  useColorModeValue,
  VStack,
} from '@chakra-ui/react'

interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  value,
  onChange,
  placeholder = '在此编辑Markdown内容...\n\n示例:\n# 标题\n![图片描述](图片链接)',
}) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const placeholderColor = useColorModeValue('gray.500', 'gray.400')

  return (
    <VStack spacing={0} h="full" align="stretch">
      {/* 编辑器主体 */}
      <Box flex={1} position="relative">
        <Textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          resize="none"
          border="none"
          bg={bgColor}
          color={useColorModeValue('gray.800', 'gray.100')}
          fontSize="14px"
          fontFamily="mono"
          lineHeight="1.6"
          p={4}
          h="full"
          _placeholder={{
            color: placeholderColor,
            fontSize: '14px',
          }}
          _focus={{
            boxShadow: 'none',
            outline: 'none',
          }}
          sx={{
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: useColorModeValue('gray.100', 'gray.700'),
            },
            '&::-webkit-scrollbar-thumb': {
              background: useColorModeValue('gray.300', 'gray.500'),
              borderRadius: '4px',
            },
            '&::-webkit-scrollbar-thumb:hover': {
              background: useColorModeValue('gray.400', 'gray.400'),
            },
          }}
        />
      </Box>
    </VStack>
  )
}
