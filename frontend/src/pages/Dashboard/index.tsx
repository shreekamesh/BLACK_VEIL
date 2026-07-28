import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  Grid, Paper, Typography, Box, useTheme, Skeleton, Chip, IconButton, Tooltip,
} from '@mui/material'
import { Refresh as RefreshIcon, Warning, Security, Psychology, Devices } from '@mui/icons-material'
import { motion } from 'framer-motion'
import { RootState, AppDispatch } from '@/store'
import { fetchDashboardData } from '@/store/slices/dashboardSlice'
import { useWebSocket } from '@/hooks/useWebSocket'
import { formatTimeAgo } from '@/utils/dateUtils'

const MetricCard = ({ title, value, change, icon: Icon, color }: any) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
    <Paper sx={{ p: 2.5, height: '100%', position: 'relative', overflow: 'hidden' }}>
      <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, bgcolor: color }} />
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="caption" color="text.secondary" gutterBottom>{title}</Typography>
          <Typography variant="h4">{value}</Typography>
        </Box>
        <Box sx={{ bgcolor: color, borderRadius: '50%', width: 40, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: 0.8 }}>
          <Icon sx={{ color: 'white', fontSize: 20 }} />
        </Box>
      </Box>
      {change !== undefined && (
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          <Typography variant="caption" color={change >= 0 ? 'success.main' : 'error.main'}>
            {change >= 0 ? '+' : ''}{change}% vs last period
          </Typography>
        </Box>
      )}
    </Paper>
  </motion.div>
)

const Dashboard: React.FC = () => {
  const theme = useTheme()
  const dispatch = useDispatch<AppDispatch>()
  const { data, isLoading, error } = useSelector((state: RootState) => state.dashboard)
  const { data: wsData, isConnected } = useWebSocket<any>('system_status')

  useEffect(() => {
    dispatch(fetchDashboardData())
  }, [dispatch])

  if (isLoading) {
    return (
      <Box>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rounded" height={140} />
            </Grid>
          ))}
        </Grid>
      </Box>
    )
  }

  if (error) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography color="error">Failed to load dashboard: {error}</Typography>
      </Paper>
    )
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>System Dashboard</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
            <Chip label={isConnected ? 'Live' : 'Reconnecting'} size="small"
              color={isConnected ? 'success' : 'warning'}
            />
            <Typography variant="caption" color="text.secondary">
              Last updated: {data?.lastUpdated ? formatTimeAgo(data.lastUpdated) : 'N/A'}
            </Typography>
          </Box>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={() => dispatch(fetchDashboardData())}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Total Threats" value={data?.metrics?.totalThreats || 0}
            change={data?.metrics?.threatChange} icon={Warning} color={theme.palette.error.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Trust Score" value={`${data?.metrics?.averageTrust || 0}%`}
            change={data?.metrics?.trustChange} icon={Security} color={theme.palette.primary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="AI Confidence" value={`${data?.metrics?.averageConfidence || 0}%`}
            change={data?.metrics?.confidenceChange} icon={Psychology} color={theme.palette.success.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Active Deceptions" value={data?.metrics?.activeDeceptions || 0}
            change={data?.metrics?.deceptionChange} icon={Devices} color={theme.palette.info.main}
          />
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, minHeight: 300 }}>
            <Typography variant="h6" gutterBottom>Recent Activity</Typography>
            {Number(data?.recentActivities?.length) > 0 ? (
              (data?.recentActivities || []).map((activity: any, i: number) => (
                <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
                  <Box>
                    <Typography variant="body2">{activity.description}</Typography>
                    <Typography variant="caption" color="text.secondary">{activity.type}</Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {formatTimeAgo(activity.timestamp)}
                  </Typography>
                </Box>
              ))
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 200 }}>
                <Typography color="text.secondary">No recent activity</Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, minHeight: 300 }}>
            <Typography variant="h6" gutterBottom>Security Status</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">System Health</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: 'success.main' }} />
                  <Typography variant="body2">Operational</Typography>
                </Box>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Active Incidents</Typography>
                <Typography variant="h5">{data?.metrics?.activeIncidents || 0}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">SSL Certificate</Typography>
                <Typography variant="body2" color="success.main">Valid</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
