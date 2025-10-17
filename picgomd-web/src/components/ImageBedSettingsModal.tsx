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
import { PicgoMdAPI } from '../services/api'

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
  const [form, setForm] = useState<ImageBedConfig>({ type: 'github', provider: 'github', enabled: false, config: {} })

  useEffect(() => {
    if (!isOpen) return
    setLoading(true)
    PicgoMdAPI.getImageBedConfig()
      .then((data) => {
        if (data) setForm(data as ImageBedConfig)
      })
      .catch(() => {
        // ignore if not configured yet
      })
      .finally(() => setLoading(false))
  }, [isOpen])

  const handleSave = async () => {
    try {
      setLoading(true)
      await PicgoMdAPI.saveImageBedConfig(form)
      toast({ title: '已保存图床配置', status: 'success', duration: 1200 })
      // 保存后自动测试
      try {
        const res = await PicgoMdAPI.testImageBedConfig(form)
        toast({ title: '图床测试', description: res.success ? '测试成功' : '测试失败', status: res.success ? 'success' : 'error', duration: 3000 })
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

  const renderAliyunFields = () => (
    <VStack spacing={3} align="stretch">
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>AccessKey ID</FormLabel>
          <Input
            value={(form.config?.access_key_id as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, access_key_id: e.target.value } })}
            placeholder="AKID..."
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>AccessKey Secret</FormLabel>
          <Input
            value={(form.config?.access_key_secret as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, access_key_secret: e.target.value } })}
            placeholder="AKSECRET..."
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Bucket</FormLabel>
          <Input
            value={(form.config?.bucket_name as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, bucket_name: e.target.value } })}
            placeholder="your-bucket"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Endpoint / 地域前缀</FormLabel>
          <Input
            value={(form.config?.endpoint as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, endpoint: e.target.value } })}
            placeholder="例如：oss-cn-hangzhou 或 https://oss-cn-hangzhou.aliyuncs.com"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>存储路径前缀</FormLabel>
          <Input
            value={(form.config?.storage_path_prefix as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, storage_path_prefix: e.target.value } })}
            placeholder="可选：项目/环境 前缀"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>自定义域名</FormLabel>
          <Input
            value={(form.config?.custom_domain as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, custom_domain: e.target.value } })}
            placeholder="可选：https://img.example.com"
          />
        </FormControl>
      </HStack>
    </VStack>
  )

  const renderCosFields = () => (
    <VStack spacing={3} align="stretch">
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>SecretId</FormLabel>
          <Input
            value={(form.config?.secret_id as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, secret_id: e.target.value } })}
            placeholder="腾讯云 SecretId"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>SecretKey</FormLabel>
          <Input
            value={(form.config?.secret_key as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, secret_key: e.target.value } })}
            placeholder="腾讯云 SecretKey"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Bucket</FormLabel>
          <Input
            value={(form.config?.bucket as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, bucket: e.target.value } })}
            placeholder="your-bucket-123456"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Region</FormLabel>
          <Input
            value={(form.config?.region as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, region: e.target.value } })}
            placeholder="ap-guangzhou"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>存储路径前缀</FormLabel>
          <Input
            value={(form.config?.storage_path_prefix as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, storage_path_prefix: e.target.value } })}
            placeholder="可选：项目/环境 前缀"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>自定义域名</FormLabel>
          <Input
            value={(form.config?.custom_domain as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, custom_domain: e.target.value } })}
            placeholder="可选：https://img.example.com"
          />
        </FormControl>
      </HStack>
    </VStack>
  )

  const renderQiniuFields = () => (
    <VStack spacing={3} align="stretch">
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>AccessKey</FormLabel>
          <Input
            value={(form.config?.access_key as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, access_key: e.target.value } })}
            placeholder="七牛 AccessKey"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>SecretKey</FormLabel>
          <Input
            value={(form.config?.secret_key as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, secret_key: e.target.value } })}
            placeholder="七牛 SecretKey"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Bucket</FormLabel>
          <Input
            value={(form.config?.bucket as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, bucket: e.target.value } })}
            placeholder="your-bucket"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>加速域名</FormLabel>
          <Input
            value={(form.config?.domain as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, domain: e.target.value } })}
            placeholder="cdn.example.com"
          />
        </FormControl>
      </HStack>
      <FormControl display="flex" alignItems="center" isDisabled={!form.enabled}>
        <FormLabel mb="0">使用 HTTPS</FormLabel>
        <Switch
          isChecked={Boolean(form.config?.use_https ?? true)}
          onChange={(e) => setForm({ ...form, config: { ...form.config, use_https: e.target.checked } })}
        />
      </FormControl>
    </VStack>
  )

  const renderS3Fields = () => (
    <VStack spacing={3} align="stretch">
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>AccessKey</FormLabel>
          <Input
            value={(form.config?.access_key as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, access_key: e.target.value } })}
            placeholder="S3 AccessKey"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>SecretKey</FormLabel>
          <Input
            value={(form.config?.secret_key as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, secret_key: e.target.value } })}
            placeholder="S3 SecretKey"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Bucket</FormLabel>
          <Input
            value={(form.config?.bucket as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, bucket: e.target.value } })}
            placeholder="your-bucket"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Region</FormLabel>
          <Input
            value={(form.config?.region as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, region: e.target.value } })}
            placeholder="如：us-east-1（可选）"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>Endpoint</FormLabel>
          <Input
            value={(form.config?.endpoint as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, endpoint: e.target.value } })}
            placeholder="自定义 S3 端点（如 MinIO，可选）"
          />
        </FormControl>
        <FormControl isDisabled={!form.enabled}>
          <FormLabel>自定义域名</FormLabel>
          <Input
            value={(form.config?.custom_domain as string) || ''}
            onChange={(e) => setForm({ ...form, config: { ...form.config, custom_domain: e.target.value } })}
            placeholder="可选：https://img.example.com"
          />
        </FormControl>
      </HStack>
      <HStack spacing={3}>
        <FormControl display="flex" alignItems="center" isDisabled={!form.enabled}>
          <FormLabel mb="0">使用 HTTPS</FormLabel>
          <Switch
            isChecked={Boolean(form.config?.use_https ?? true)}
            onChange={(e) => setForm({ ...form, config: { ...form.config, use_https: e.target.checked } })}
          />
        </FormControl>
        <FormControl display="flex" alignItems="center" isDisabled={!form.enabled}>
          <FormLabel mb="0">Path-Style</FormLabel>
          <Switch
            isChecked={Boolean(form.config?.path_style ?? false)}
            onChange={(e) => setForm({ ...form, config: { ...form.config, path_style: e.target.checked } })}
          />
        </FormControl>
      </HStack>
      <FormControl isDisabled={!form.enabled}>
        <FormLabel>存储路径前缀</FormLabel>
        <Input
          value={(form.config?.storage_path_prefix as string) || ''}
          onChange={(e) => setForm({ ...form, config: { ...form.config, storage_path_prefix: e.target.value } })}
          placeholder="可选：项目/环境 前缀"
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
            {form.provider === 'aliyun' && renderAliyunFields()}
            {form.provider === 'cos' && renderCosFields()}
            {form.provider === 'qiniu' && renderQiniuFields()}
            {form.provider === 's3' && renderS3Fields()}
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


