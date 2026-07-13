import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

// Mock the websocket service
jest.mock('./services/websocketService', () => ({
  connectWebSocket: jest.fn(),
  disconnectWebSocket: jest.fn(),
  subscribeToEvents: jest.fn(),
  unsubscribeFromEvents: jest.fn(),
}));

describe('App Component', () => {
  test('renders without crashing', () => {
    // App renders its own BrowserRouter, so no wrapper is needed
    render(<App />);
    expect(document.body).toBeInTheDocument();
  });
});
