import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app/App';
import { DataProvider } from './store';
import { SettingsProvider } from './settings';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SettingsProvider>
      <DataProvider>
        <App />
      </DataProvider>
    </SettingsProvider>
  </StrictMode>,
);
