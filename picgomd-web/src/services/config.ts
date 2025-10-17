declare global {
  interface Window { __PICGOMD_BASE__?: string }
}

export function getApiBaseUrl(): string {
  return window.__PICGOMD_BASE__ || 'http://127.0.0.1:8000'
}

export function setApiBaseUrl(url: string): void {
  window.__PICGOMD_BASE__ = url
}


