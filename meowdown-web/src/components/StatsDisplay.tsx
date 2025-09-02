import React from 'react'
import {
  Box,
  Text,
  VStack,
  HStack,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  useColorModeValue,
  Icon,
} from '@chakra-ui/react'
import { FiImage, FiCheckCircle, FiClock } from 'react-icons/fi'

interface ConversionStats {
  total_images: number
  converted_images: number
  failed_images: number
  skipped_images: number
  conversion_time: number
}

interface StatsDisplayProps {
  stats: ConversionStats | null
  isVisible: boolean
}

// 格式化时间
const formatTime = (seconds: number): string => {
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`
  return `${seconds.toFixed(1)}s`
}

export const StatsDisplay: React.FC<StatsDisplayProps> = ({ stats, isVisible }) => {
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  if (!isVisible || !stats) {
    return null
  }

  const successRate = stats.total_images > 0 
    ? ((stats.converted_images / stats.total_images) * 100).toFixed(1) 
    : '0'

  return (
    <Box
      p={4}
      bg={bgColor}
      borderTop="1px"
      borderColor={borderColor}
      borderRadius="md"
    >
      <VStack spacing={4} align="stretch">
        <Text fontSize="sm" fontWeight="semibold" color="gray.600">
          转换统计
        </Text>
        
        <SimpleGrid columns={3} spacing={4}>
          <Stat>
            <StatLabel>
              <HStack spacing={2}>
                <Icon as={FiImage} />
                <Text>总图片数</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="xl">{stats.total_images}</StatNumber>
          </Stat>

          <Stat>
            <StatLabel>
              <HStack spacing={2}>
                <Icon as={FiCheckCircle} />
                <Text>转换成功</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="xl" color="green.500">
              {stats.converted_images}
            </StatNumber>
            <StatHelpText>成功率 {successRate}%</StatHelpText>
          </Stat>

          <Stat>
            <StatLabel>
              <HStack spacing={2}>
                <Icon as={FiClock} />
                <Text>处理时间</Text>
              </HStack>
            </StatLabel>
            <StatNumber fontSize="xl">
              {formatTime(stats.conversion_time)}
            </StatNumber>
          </Stat>
        </SimpleGrid>

        {(stats.failed_images > 0 || stats.skipped_images > 0) && (
          <SimpleGrid columns={2} spacing={4}>
            {stats.failed_images > 0 && (
              <Stat>
                <StatLabel>失败图片</StatLabel>
                <StatNumber fontSize="md" color="red.500">
                  {stats.failed_images}
                </StatNumber>
              </Stat>
            )}
            
            {stats.skipped_images > 0 && (
              <Stat>
                <StatLabel>跳过图片</StatLabel>
                <StatNumber fontSize="md" color="yellow.500">
                  {stats.skipped_images}
                </StatNumber>
              </Stat>
            )}
          </SimpleGrid>
        )}
      </VStack>
    </Box>
  )
}