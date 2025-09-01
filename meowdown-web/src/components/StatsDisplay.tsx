import React from 'react'
import {
  VStack,
  HStack,
  Text,
  Box,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  useColorModeValue,
  Icon,
} from '@chakra-ui/react'
import { FiTrendingDown, FiBarChart2, FiZap } from 'react-icons/fi'
import type { ImageConversionStats, CompressionGrade } from '../types'

interface StatsDisplayProps {
  stats: ImageConversionStats | null
  isVisible: boolean
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

// 计算压缩评级
const getCompressionGrade = (ratio: number): { grade: CompressionGrade; color: string } => {
  if (ratio >= 60) return { grade: '极佳', color: 'green' }
  if (ratio >= 40) return { grade: '良好', color: 'blue' }
  if (ratio >= 20) return { grade: '一般', color: 'yellow' }
  return { grade: '轻微', color: 'orange' }
}

export const StatsDisplay: React.FC<StatsDisplayProps> = ({ stats, isVisible }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  if (!isVisible || !stats) {
    return null
  }

  const { totalOriginalSize, totalConvertedSize, compressionRatio, sizeSaved } = stats
  const { grade, color } = getCompressionGrade(compressionRatio)

  return (
    <Box
      bg={bgColor}
      border="1px"
      borderColor={borderColor}
      borderRadius="lg"
      p={4}
      mt={4}
      w="full"
      maxW="720px"
      mx="auto"
      mb={4}
    >
      <VStack spacing={4} align="stretch">
        {/* 标题 */}
        <HStack justify="space-between" align="center">
          <HStack spacing={2}>
            <Icon as={FiBarChart2} color="meowdown.500" />
            <Text fontSize="lg" fontWeight="bold">
              转换统计
            </Text>
          </HStack>
          <Badge
            colorScheme={color}
            variant="solid"
            px={3}
            py={1}
            borderRadius="full"
            fontSize="sm"
          >
            {grade}压缩
          </Badge>
        </HStack>

        {/* 统计网格 */}
        <SimpleGrid columns={2} spacing={4}>
          {/* 原始大小 */}
          <Stat>
            <StatLabel fontSize="sm" color="gray.500">
              <HStack spacing={1}>
                <Icon as={FiZap} boxSize={3} />
                <Text>原始大小</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="lg" color="gray.700" _dark={{ color: 'gray.300' }}>
              {formatFileSize(totalOriginalSize)}
            </StatNumber>
          </Stat>

          {/* 转换后大小 */}
          <Stat>
            <StatLabel fontSize="sm" color="gray.500">
              <HStack spacing={1}>
                <Icon as={FiTrendingDown} boxSize={3} />
                <Text>转换后</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="lg" color="green.600" _dark={{ color: 'green.400' }}>
              {formatFileSize(totalConvertedSize)}
            </StatNumber>
          </Stat>

          {/* 压缩比例 */}
          <Stat>
            <StatLabel fontSize="sm" color="gray.500">
              压缩比例
            </StatLabel>
            <StatNumber fontSize="lg" color={`${color}.600`} _dark={{ color: `${color}.400` }}>
              {compressionRatio.toFixed(1)}%
            </StatNumber>
            <StatHelpText fontSize="xs" mb={0}>
              体积减少
            </StatHelpText>
          </Stat>

          {/* 节省空间 */}
          <Stat>
            <StatLabel fontSize="sm" color="gray.500">
              节省空间
            </StatLabel>
            <StatNumber fontSize="lg" color="meowdown.600" _dark={{ color: 'meowdown.400' }}>
              {formatFileSize(sizeSaved)}
            </StatNumber>
            <StatHelpText fontSize="xs" mb={0}>
              已节省
            </StatHelpText>
          </Stat>
        </SimpleGrid>

        {/* 压缩效果说明 */}
        <Box
          bg={bgColor}
          p={3}
          borderRadius="md"
          border="1px"
          borderColor={borderColor}
        >
          <Text fontSize="sm" color={`${color}.700`} _dark={{ color: `${color}.300` }} textAlign="center">
            {compressionRatio >= 60 && '🎉 压缩效果极佳！图片大小显著减少'}
            {compressionRatio >= 40 && compressionRatio < 60 && '👍 压缩效果良好，平衡了质量与体积'}
            {compressionRatio >= 20 && compressionRatio < 40 && '✅ 压缩效果一般，适度减少了体积'}
            {compressionRatio < 20 && '📝 压缩效果轻微，主要优化了格式'}
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}
