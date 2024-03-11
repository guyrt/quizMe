module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'jest-environment-jsdom',
    setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
    modulePaths: ['<rootDir>/src/'],
    moduleNameMapper: {
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
    },
    testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/dist/'],
    moduleDirectories: ['node_modules']
};