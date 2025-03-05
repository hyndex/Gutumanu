import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import App from '../App';
import MapView from '../components/MapView';
import SettingsScreen from '../components/SettingsScreen';

describe('Component Tests', () => {
  test('App component renders correctly', () => {
    const { getByTestId } = render(<App />);
    expect(getByTestId('main-container')).toBeTruthy();
  });

  test('MapView displays initial location', () => {
    const { getByText } = render(
      <MapView initialRegion={{ latitude: 40.7128, longitude: -74.0060 }} />
    );
    expect(getByText('Current Location: 40.7128, -74.0060')).toBeTruthy();
  });

  test('SettingsScreen handles token refresh', async () => {
    const mockRefresh = jest.fn();
    const { getByTestId } = render(
      <SettingsScreen onRefreshToken={mockRefresh} />
    );
    
    fireEvent.press(getByTestId('refresh-token-button'));
    expect(mockRefresh).toHaveBeenCalled();
  });

  test('Navigation between screens', () => {
    const { getByTestId, update } = render(<App />);
    fireEvent.press(getByTestId('history-tab'));
    expect(getByTestId('history-screen')).toBeTruthy();
    
    fireEvent.press(getByTestId('settings-tab'));
    expect(getByTestId('settings-screen')).toBeTruthy();
  });

  test('Error boundary handling', () => {
    const BrokenComponent = () => {
      throw new Error('Test error');
    };
    
    const { getByText } = render(
      <ErrorBoundary>
        <BrokenComponent />
      </ErrorBoundary>
    );
    
    expect(getByText('Something went wrong')).toBeTruthy();
  });
});