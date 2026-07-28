import React, { useState } from 'react'
import { Box, Paper, Typography, Grid, Chip, Tabs, Tab, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Switch, FormControlLabel, Select, MenuItem, InputLabel, FormControl, IconButton } from '@mui/material'
import { People, Settings, Storage, History, Edit, Block, Add } from '@mui/icons-material'
import { motion } from 'framer-motion'

const users = [
  { id: 'USR-001', username: 'admin', email: 'admin@blackveil.io', role: 'admin', active: true, lastLogin: '2024-01-15T10:00:00Z' },
  { id: 'USR-002', username: 'analyst1', email: 'analyst1@blackveil.io', role: 'analyst', active: true, lastLogin: '2024-01-14T15:30:00Z' },
  { id: 'USR-003', username: 'viewer1', email: 'viewer1@blackveil.io', role: 'viewer', active: true, lastLogin: '2024-01-13T09:00:00Z' },
  { id: 'USR-004', username: 'operator', email: 'operator@blackveil.io', role: 'operator', active: false, lastLogin: '2024-01-10T12:00:00Z' },
]

const AdminPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [dialogOpen, setDialogOpen] = useState(false)

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>Administration</Typography>
        <Typography variant="body2" color="text.secondary">System configuration, user management, and monitoring</Typography>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'Users', value: users.length, icon: <People />, color: 'primary.main' },
          { label: 'Active Sessions', value: 7, icon: <People />, color: 'success.main' },
          { label: 'Models', value: 8, icon: <Storage />, color: 'info.main' },
          { label: 'Config Items', value: 124, icon: <Settings />, color: 'secondary.main' },
        ].map((stat, i) => (
          <Grid item xs={6} sm={3} key={i}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ color: stat.color }}>{stat.icon}</Box>
                <Box><Typography variant="h4" sx={{ fontWeight: 700, color: stat.color }}>{stat.value}</Typography><Typography variant="caption" color="text.secondary">{stat.label}</Typography></Box>
              </Paper>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Paper>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 2, pt: 2 }}>
          <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
            <Tab label="User Management" />
            <Tab label="System Config" />
            <Tab label="Model Management" />
            <Tab label="Audit Logs" />
          </Tabs>
          {tabValue === 0 && <Button variant="contained" size="small" startIcon={<Add />} onClick={() => setDialogOpen(true)}>Add User</Button>}
        </Box>

        {tabValue === 0 && (
          <TableContainer sx={{ mt: 2 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Login</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell><Chip label={user.role} size="small" color={user.role === 'admin' ? 'primary' : user.role === 'analyst' ? 'info' : 'default'} /></TableCell>
                    <TableCell><Chip label={user.active ? 'Active' : 'Inactive'} size="small" color={user.active ? 'success' : 'default'} /></TableCell>
                    <TableCell>{new Date(user.lastLogin).toLocaleString()}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small"><Edit /></IconButton>
                      <IconButton size="small"><Block /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography color="text.secondary">System configuration panel with environment variables, feature flags, and service settings.</Typography>
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography color="text.secondary">Model registry management with version control, deployment, and rollback capabilities.</Typography>
          </Box>
        )}

        {tabValue === 3 && (
          <Box sx={{ p: 3 }}>
            <Typography color="text.secondary">Audit log viewer with search, filter, and export functionality.</Typography>
          </Box>
        )}
      </Paper>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Username" margin="normal" />
          <TextField fullWidth label="Email" type="email" margin="normal" />
          <TextField fullWidth label="Password" type="password" margin="normal" />
          <FormControl fullWidth margin="normal">
            <InputLabel>Role</InputLabel>
            <Select label="Role" defaultValue="viewer">
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="analyst">Analyst</MenuItem>
              <MenuItem value="operator">Operator</MenuItem>
              <MenuItem value="viewer">Viewer</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setDialogOpen(false)}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default AdminPage
