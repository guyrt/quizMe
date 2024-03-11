import '@testing-library/jest-dom';


const createChromeStorageLocalMock = () => ({
    get: jest.fn((key: string | string[], callback: (result: any) => void) => {
      if (typeof callback === 'function') callback({});
    }),
    set: jest.fn((items: object, callback?: () => void) => {
      if (typeof callback === 'function') callback();
    }),
    remove: jest.fn((keys: string | string[], callback?: () => void) => {
      if (typeof callback === 'function') callback();
    }),
    clear: jest.fn((callback?: () => void) => {
      if (typeof callback === 'function') callback();
    }),
    // Add other methods if needed, following the same pattern
  });

// Global object to mimic chrome global variable
global.chrome = {
    storage: {
        local: createChromeStorageLocalMock(),
    },
    // Mock other chrome APIs if needed
} as any;
