import { apiClient } from '../apiClient';

jest.mock('../apiClient');

describe('apiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handles 403 forbidden errors', async () => {
    apiClient.post.mockRejectedValue({ response: { status: 403 } });
    
    await expect(apiClient.post('/update-location', {}))
      .rejects.toThrow('Authentication failed');
  });

  test('validates location data structure', async () => {
    const invalidData = { latitude: 'invalid' };
    
    await expect(apiClient.post('/update-location', invalidData))
      .rejects.toThrow('Validation error');
  });

  test('handles network errors', async () => {
    apiClient.post.mockRejectedValue(new Error('Network Error'));
    
    await expect(apiClient.post('/update-location', {}))
      .rejects.toThrow('Network Error');
  });
});