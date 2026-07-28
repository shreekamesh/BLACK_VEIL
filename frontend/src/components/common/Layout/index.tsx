import React, { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Box, AppBar, Toolbar, IconButton, Typography, Drawer, List, ListItem,
  ListItemButton, ListItemIcon, ListItemText, Divider, Avatar, Menu, MenuItem,
  Tooltip, Badge, useTheme,
} from '@mui/material'
import {
  Menu as MenuIcon, Dashboard as DashboardIcon, Security as TrustIcon,
  Psychology as AIIcon, Grain as CognitiveIcon, Warning as IncidentIcon,
  Devices as DeceptionIcon, Key as CredentialsIcon, AutoAwesome as EvolutionIcon,
  Settings as AdminIcon, Notifications as NotificationsIcon, Person as PersonIcon,
  Logout as LogoutIcon, Settings as SettingsIcon, ChevronLeft as ChevronLeftIcon,
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { RootState, AppDispatch } from '@/store'
import { clearAuth } from '@/store/slices/authSlice'
import { ROUTES } from '@/config/routes.config'
import { wsManager } from '@/api/websocket'

const DRAWER_WIDTH = 260
const DRAWER_COLLAPSED = 72

const NAV_ITEMS = [
  { label: 'Dashboard', path: ROUTES.DASHBOARD, icon: <DashboardIcon /> },
  { label: 'Trust', path: ROUTES.TRUST, icon: <TrustIcon /> },
  { label: 'AI', path: ROUTES.AI, icon: <AIIcon /> },
  { label: 'Cognitive', path: ROUTES.COGNITIVE, icon: <CognitiveIcon /> },
  { label: 'Incidents', path: ROUTES.INCIDENTS, icon: <IncidentIcon /> },
  { label: 'Deception', path: ROUTES.DECEPTION, icon: <DeceptionIcon /> },
  { label: 'Credentials', path: ROUTES.CREDENTIALS, icon: <CredentialsIcon /> },
  { label: 'Evolution', path: ROUTES.EVOLUTION, icon: <EvolutionIcon /> },
  { label: 'Admin', path: ROUTES.ADMIN, icon: <AdminIcon /> },
]

export const Layout: React.FC = () => {
  const theme = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch<AppDispatch>()
  const { user } = useSelector((state: RootState) => state.auth)
  const [drawerOpen, setDrawerOpen] = useState(true)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    if (user) {
      wsManager.connect()
      const unsub = wsManager.on('alert', () => setUnreadCount((p) => p + 1))
      return () => { unsub(); wsManager.disconnect() }
    }
  }, [user])

  const handleLogout = () => {
    dispatch(clearAuth())
    wsManager.disconnect()
    navigate('/login')
  }

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{
        zIndex: theme.zIndex.drawer + 1,
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}>
        <Toolbar>
          <IconButton edge="start" onClick={() => setDrawerOpen(!drawerOpen)} sx={{ mr: 2 }}>
            {drawerOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" sx={{
            flexGrow: 1, fontWeight: 700,
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            backgroundClip: 'text', WebkitBackgroundClip: 'text', color: 'transparent',
          }}>
            BLACK VEIL V5
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit" onClick={() => navigate('/notifications')}>
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <Tooltip title="Profile">
              <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.875rem' }}>
                  {user?.fullName?.[0] || user?.username?.[0] || 'U'}
                </Avatar>
              </IconButton>
            </Tooltip>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              PaperProps={{ sx: { mt: 1, minWidth: 200 } }}
            >
              <MenuItem>
                <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary={user?.fullName || user?.username} secondary={user?.email} />
              </MenuItem>
              <Divider />
              <MenuItem onClick={() => { setAnchorEl(null); navigate('/profile') }}>
                <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>Profile
              </MenuItem>
              <MenuItem onClick={() => { setAnchorEl(null); navigate('/settings') }}>
                <ListItemIcon><SettingsIcon fontSize="small" /></ListItemIcon>Settings
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <Drawer variant="permanent" sx={{
        width: drawerOpen ? DRAWER_WIDTH : DRAWER_COLLAPSED,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerOpen ? DRAWER_WIDTH : DRAWER_COLLAPSED,
          boxSizing: 'border-box', mt: 8,
          borderRight: '1px solid', borderColor: 'divider',
          bgcolor: 'background.default', overflowX: 'hidden',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
      }}>
        <List sx={{ pt: 2 }}>
          {NAV_ITEMS.map((item) => (
            <ListItem key={item.path} disablePadding sx={{ display: 'block' }}>
              <Tooltip title={!drawerOpen ? item.label : ''} placement="right" arrow>
                <ListItemButton
                  sx={{
                    minHeight: 48, justifyContent: drawerOpen ? 'initial' : 'center',
                    px: 2.5, mx: 1, borderRadius: 2,
                    bgcolor: isActive(item.path) ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                    '&:hover': { bgcolor: 'rgba(0, 212, 255, 0.05)' },
                  }}
                  onClick={() => navigate(item.path)}
                >
                  <ListItemIcon sx={{
                    minWidth: 0, mr: drawerOpen ? 3 : 'auto', justifyContent: 'center',
                    color: isActive(item.path) ? 'primary.main' : 'text.secondary',
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  {drawerOpen && (
                    <ListItemText primary={item.label}
                      sx={{ color: isActive(item.path) ? 'primary.main' : 'text.primary' }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box component="main" sx={{
        flexGrow: 1, p: 3, mt: 8, minHeight: 'calc(100vh - 64px)',
        bgcolor: 'background.default',
        width: `calc(100% - ${drawerOpen ? DRAWER_WIDTH : DRAWER_COLLAPSED}px)`,
        transition: theme.transitions.create(['margin', 'width'], {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
      }}>
        <Outlet />
      </Box>
    </Box>
  )
}
