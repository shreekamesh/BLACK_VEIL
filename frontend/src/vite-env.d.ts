/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_ENVIRONMENT: 'development' | 'staging' | 'production'
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_NAME: string
  readonly VITE_DARK_MODE: string
  readonly VITE_PRIMARY_COLOR: string
  readonly VITE_SECONDARY_COLOR: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_API_RETRIES: string
  readonly VITE_API_RETRY_DELAY: string
  readonly VITE_DEBUG: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module 'react-grid-layout' {
  import { ComponentType } from 'react'
  interface ReactGridLayoutProps {
    className?: string
    layout?: any[]
    cols?: number
    rowHeight?: number
    width?: number
    containerPadding?: [number, number]
    margin?: [number, number]
    isDraggable?: boolean
    isResizable?: boolean
    compactType?: 'vertical' | 'horizontal' | null
    preventCollision?: boolean
    draggableHandle?: string
    onLayoutChange?: (layout: any[]) => void
    children?: React.ReactNode
  }
  const ReactGridLayout: ComponentType<ReactGridLayoutProps>
  export default ReactGridLayout
  export const WidthProvider: (component: ComponentType<any>) => ComponentType<any>
}

declare module 'react-grid-layout/css/styles.css'
declare module 'react-resizable/css/styles.css'

