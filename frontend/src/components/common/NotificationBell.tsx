import React, { useState } from 'react'
import {
  IconButton,
  Badge,
  Popover,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Box,
  Divider,
  Button,
} from '@mui/material'
import {
  Notifications as NotificationsIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material'
import { formatTimeAgo } from '@/utils/dateUtils'

interface NotificationItem {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
}

interface NotificationBellProps {
  count: number
  onClick?: () => void
}

export const NotificationBell: React.FC<NotificationBellProps> = ({ count, onClick }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [notifications] = useState<NotificationItem[]>([])

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
    onClick?.()
  }
  const handleClose = () => setAnchorEl(null)

  const getIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircleIcon color="success" />
      case 'warning': return <WarningIcon color="warning" />
      case 'error': return <ErrorIcon color="error" />
      default: return <InfoIcon color="info" />
    }
  }

  return (
    <>
      <IconButton onClick={handleClick} color="inherit">
        <Badge badgeContent={count} color="error" max={99}>
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        PaperProps={{ sx: { width: 380, maxHeight: 500, mt: 1 } }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Notifications</Typography>
        </Box>
        <List sx={{ overflow: 'auto', maxHeight: 400 }}>
          {notifications.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">No notifications</Typography>
            </Box>
          ) : (
            notifications.map((n, i) => (
              <React.Fragment key={n.id}>
                <ListItem alignItems="flex-start">
                  <ListItemIcon sx={{ minWidth: 36 }}>{getIcon(n.type)}</ListItemIcon>
                  <ListItemText
                    primary={n.title}
                    secondary={
                      <>
                        <Typography variant="body2" color="text.secondary">
                          {n.message}
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                          {formatTimeAgo(n.timestamp)}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {i < notifications.length - 1 && <Divider component="li" />}
              </React.Fragment>
            ))
          )}
        </List>
        <Box sx={{ p: 1, borderTop: 1, borderColor: 'divider' }}>
          <Button size="small" fullWidth>Mark all as read</Button>
        </Box>
      </Popover>
    </>
  )
}
