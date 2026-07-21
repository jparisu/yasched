import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import { DataProvider } from './data/DataContext';
import { EditorProvider } from './data/EditorContext';
import { ElementProvider } from './data/ElementContext';
import { SettingsProvider } from './data/SettingsContext';
import { HelpProvider } from './help';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SettingsProvider>
      <DataProvider>
        <HelpProvider>
          <EditorProvider>
            <ElementProvider>
              <App />
            </ElementProvider>
          </EditorProvider>
        </HelpProvider>
      </DataProvider>
    </SettingsProvider>
  </StrictMode>
);
