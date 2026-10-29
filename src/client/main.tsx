import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { CatalogueProvider } from './lib/catalogue';
import { PanierProvider } from './lib/panier';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <CatalogueProvider>
        <PanierProvider>
          <App />
        </PanierProvider>
      </CatalogueProvider>
    </BrowserRouter>
  </StrictMode>,
);
