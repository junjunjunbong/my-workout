import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import { getWeeklyVolume, getMonthlyVolume } from '../services/analyticsService';

const Analytics = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [weeklyData, setWeeklyData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [weekly, monthly] = await Promise.all([
        getWeeklyVolume(),
        getMonthlyVolume(),
      ]);
      setWeeklyData(weekly.data);
      setMonthlyData(monthly.data);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      if (error.code === 'ERR_NETWORK') {
        setError('Network Error: Unable to connect to the backend server. Please make sure the backend server is running.');
      } else {
        setError('Error fetching analytics data: ' + (error.response?.data?.detail || error.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
          <Typography color="error">{error}</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box mb={3}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 800 }}>
          운동 통계
        </Typography>
        <Paper elevation={1} sx={{ borderRadius: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            centered
          >
            <Tab label="주간 볼륨" />
            <Tab label="월간 볼륨" />
          </Tabs>
        </Paper>
      </Box>

      {activeTab === 0 && (
        <Paper elevation={0} sx={{ p: 2, borderRadius: 3, border: '1px solid #eef2f7' }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
            주간 운동 볼륨
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week_start" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="volume" name="운동 볼륨 (kg)" fill="#1e88e5" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      )}

      {activeTab === 1 && (
        <Paper elevation={0} sx={{ p: 2, borderRadius: 3, border: '1px solid #eef2f7' }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
            월간 운동 볼륨
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="volume"
                name="운동 볼륨 (kg)"
                stroke="#1e88e5"
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}
    </Container>
  );
};

export default Analytics;