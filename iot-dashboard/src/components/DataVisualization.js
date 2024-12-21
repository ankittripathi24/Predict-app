import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Typography, Box, FormControl, InputLabel, Select, MenuItem, CircularProgress } from '@material-ui/core';
import MuiAlert from '@material-ui/lab/Alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { useInView } from 'react-intersection-observer';

const ITEMS_PER_PAGE = 1000;
const DATA_REFRESH_INTERVAL = 60000; // 1 minute
const CLIENT_CACHE_KEY = 'sensor_data_cache';
const CACHE_EXPIRY = 60000; // 1 minute

const DataVisualization = () => {
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [selectedMachine, setSelectedMachine] = useState('all');
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const { ref, inView } = useInView();
  const lastFetchTime = useRef(0);
  const fetchTimeoutRef = useRef(null);

  const checkAndUseCache = () => {
    const cachedData = localStorage.getItem(CLIENT_CACHE_KEY);
    if (cachedData) {
      try {
        const { data: storedData, timestamp } = JSON.parse(cachedData);
        const now = Date.now();
        if (now - timestamp < CACHE_EXPIRY) {
          setData(storedData);
          setMachines([...new Set(storedData.map(item => item.machine_id))]);
          return true;
        }
      } catch (err) {
        console.error('Error parsing cached data:', err);
      }
    }
    return false;
  };

  const updateCache = useCallback((newData) => {
    try {
      localStorage.setItem(CLIENT_CACHE_KEY, JSON.stringify({
        data: newData,
        timestamp: Date.now()
      }));
    } catch (err) {
      console.error('Error caching data:', err);
    }
  }, []);

  const fetchData = useCallback(async (pageNum = 0, append = false) => {
    const now = Date.now();
    if (loading || (now - lastFetchTime.current < DATA_REFRESH_INTERVAL && pageNum === 0)) {
      return;
    }

    if (pageNum === 0 && checkAndUseCache()) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get('http://0.0.0.0:8000/get-sensor-data', {
        params: {
          limit: ITEMS_PER_PAGE,
          offset: pageNum * ITEMS_PER_PAGE
        }
      });

      if (response.data && response.data.data) {
        const newData = response.data.data;
        const formattedData = newData.map(item => ({
          ...item,
          timestamp: new Date(item.timestamp).toLocaleString()
        }));

        setData(prevData => {
          const updatedData = append ? [...prevData, ...formattedData] : formattedData;
          if (pageNum === 0) {
            updateCache(updatedData);
          }
          return updatedData;
        });

        const uniqueMachines = [...new Set(formattedData.map(item => item.machine_id))];
        setMachines(uniqueMachines);
        
        setHasMore(formattedData.length === ITEMS_PER_PAGE);
        setError(null);
        lastFetchTime.current = now;
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load sensor data';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [loading, updateCache]);

  useEffect(() => {
    if (!checkAndUseCache()) {
      fetchData(0, false);
    }

    const setupPolling = () => {
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
      fetchTimeoutRef.current = setTimeout(() => {
        fetchData(0, false);
        setupPolling();
      }, DATA_REFRESH_INTERVAL);
    };

    setupPolling();

    return () => {
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
    };
  }, [fetchData]);

  useEffect(() => {
    if (inView && hasMore && !loading) {
      setPage(prevPage => {
        const nextPage = prevPage + 1;
        fetchData(nextPage, true);
        return nextPage;
      });
    }
  }, [inView, hasMore, loading, fetchData]);

  const filteredData = useMemo(() => {
    if (selectedMachine === 'all') {
      return data;
    }
    return data.filter(item => item.machine_id === selectedMachine);
  }, [data, selectedMachine]);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Sensor Data Visualization
      </Typography>

      {error && (
        <Box mb={2}>
          <MuiAlert severity="error" variant="filled">
            {error}
          </MuiAlert>
        </Box>
      )}

      {data.length > 0 && (
        <FormControl variant="outlined" style={{ minWidth: 200, marginBottom: 20 }}>
          <InputLabel>Select Machine</InputLabel>
          <Select
            value={selectedMachine}
            onChange={(e) => setSelectedMachine(e.target.value)}
            label="Select Machine"
          >
            <MenuItem value="all">All Machines</MenuItem>
            {machines.map(machine => (
              <MenuItem key={machine} value={machine}>
                Machine {machine}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      
      {data.length > 0 ? (
        <>
          <Box style={{ width: '100%', height: 400 }}>
            <ResponsiveContainer>
              <LineChart
                data={filteredData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  interval="preserveStartEnd"
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="temperature" 
                  stroke="#8884d8" 
                  name="Temperature" 
                  dot={false}
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="vibration" 
                  stroke="#82ca9d" 
                  name="Vibration" 
                  dot={false}
                  isAnimationActive={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="energy_consumption" 
                  stroke="#ffc658" 
                  name="Energy Consumption" 
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
          {hasMore && (
            <Box ref={ref} display="flex" justifyContent="center" my={2}>
              {loading && <CircularProgress />}
            </Box>
          )}
        </>
      ) : !error && (
        <Typography variant="body1" color="textSecondary">
          No data available. Please upload sensor data to visualize.
        </Typography>
      )}
    </Box>
  );
};

export default DataVisualization;
