import { by, device, expect, element } from 'detox';

describe('App Flow', () => {
  beforeAll(async () => {
    await device.launchApp({
      newInstance: true,
      permissions: { location: 'always' }
    });
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should display initial loading screen', async () => {
    await expect(element(by.id('loading-indicator'))).toBeVisible();
  });

  it('should navigate through main features', async () => {
    await element(by.id('location-permission-button')).tap();
    await expect(element(by.id('map-view'))).toBeVisible();
    
    await element(by.id('navigation-history-tab')).tap();
    await expect(element(by.id('location-history-list'))).toExist();
    
    await element(by.id('settings-tab')).tap();
    await element(by.id('refresh-token-button')).tap();
    await expect(element(by.text('Token refreshed'))).toBeVisible();
  });

  afterAll(async () => {
    await device.terminateApp();
  });
});