import React, { useEffect, useState } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  VStack,
  HStack,
  useToast,
} from '@chakra-ui/react'
import type { ImageBedConfig } from '../services/api'
import { MeowdownAPI } from '../services/api'

interface Props {
  isOpen: boolean
  onClose: () => void
}

const PROVIDERS = [
  { value: 'github', label: 'GitHub' },
  { value: 'qiniu', label: '七牛云' },
  { value: 'aliyun', label: '阿里云OSS' },
  { value: 'cos', label: '腾讯云COS' },
  { value: 's3', label: 'Amazon S3' },
]

export const ImageBedSettingsModal: React.FC<Props> = ({ isOpen, onClose }) => {
  const toast = useToast()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState<ImageBedConfig>({ provider: 'github', enabled: false, config: {} })

  useEffect(() => {
    if (!isOpen) return
    setLoading(true)
    MeowdownAPI.getImageBedConfig()
      .then((data) => {
        if (data) setForm(data)
      })
      .catch(() => {
        // ignore if not configured yet
      })
      .finally(() => setLoading(false))
  }, [isOpen])

  const handleSave = async () => {
    try {
      setLoading(true)
      await MeowdownAPI.saveImageBedConfig(form)
      toast({ title: '已保存图床配置', status: 'success', duration: 1200 })
      // 保存后自动测试
      try {
        const res = await MeowdownAPI.testImageBedConfig(form)
        toast({ title: '图床测试', description: res.message, status: res.success ? 'success' : 'error', duration: 3000 })
        // 让右上角状态徽标沿用“已连接”样式：成功则短暂提示
        if (res.success) {
          // 轻量提示已可用
        }
      } catch (e) {
        toast({ title: '图床测试失败', status: 'error', duration: 3000 })
      }
      onClose()
    } catch (e) {
      toast({ title: '保存失败', status: 'error', duration: 3000 })
    } finally {
      setLoading(false)
    }
  }

  const renderGithubFields = () => (
    <VStack spacing={3} align="stretch">
      <FormControl isDisabled={!form.enabled}>
        <FormLabel>Token</FormLabel>
        <Input
          value={(form.config?.token as string) || ''}
          onChange={(e) => setForm({ ...form, config: { ...form.config, token: e.target.value } })}
          placeholder="GitHub Personal Access Token"
        />
      </FormControl>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Owner</FormLabel>
          <Input
            value={(form.config?.owner as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, owner: e.target.value } })}
            placeholder="用户名或组织名"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Repo</FormLabel>
          <Input
            value={(form.config?.repo as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, repo: e.target.value } })}
            placeholder="仓库名"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Branch</FormLabel>
          <Input
            value={(form.config?.branch as string) || 'main'}
            onChange={(e) => setForm({ ...form, config: { ...form.config, branch: e.target.value } })}
            placeholder="main"
          />
        </FormControl>
        <FormControl display="flex" alignItems="center" isDisabled={!form.enabled}>
          <FormLabel mb="0">使用 jsDelivr</FormLabel>
          <Switch
            isChecked={Boolean(form.config?.use_jsdelivr)}
            onChange={(e) => setForm({ ...form, config: { ...form.config, use_jsdelivr: e.target.checked } })}
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>路径前缀</FormLabel>
          <Input
            value={(form.config?.path_prefix as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, path_prefix: e.target.value } })}
            placeholder="可选：content/images 等"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>存储路径前缀</FormLabel>
          <Input
            value={(form.config?.storage_path_prefix as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, storage_path_prefix: e.target.value } })}
            placeholder="可选：区分不同项目/环境"
          />
        </FormControl>
      </HStack>
      <FormControl isDisabled={!form.enabled}>
        <FormLabel>自定义域名</FormLabel>
        <Input
          value={(form.config?.custom_domain as string) || ''}
          onChange={(e) => setForm({ ...form, config: { ...form.config, custom_domain: e.target.value } })}
          placeholder="可选：https://img.example.com"
        />
      </FormControl>
    </VStack>
  )

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>图床设置</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">启用图床</FormLabel>
              <Switch
                isChecked={form.enabled}
                onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
              />
            </FormControl>

            <FormControl>
              <FormLabel>服务提供商</FormLabel>
              <Select
                value={form.provider}
                onChange={(e) => setForm({ ...form, provider: e.target.value })}
              >
                {PROVIDERS.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </Select>
            </FormControl>

            {form.provider === 'github' && renderGithubFields()}
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button mr={3} onClick={onClose} variant="ghost">
            取消
          </Button>
          <Button colorScheme="meowdown" onClick={handleSave} isLoading={loading}>
            保存
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default ImageBedSettingsModal


