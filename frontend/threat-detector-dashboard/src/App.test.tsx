import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
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
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    // Basic test to ensure the app renders
    expect(document.body).toBeInTheDocument();
  });
});
