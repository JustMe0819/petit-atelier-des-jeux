import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Chargement } from './components/Divers';
import Accueil from './pages/Accueil';
import Boutique from './pages/Boutique';
import Produit from './pages/Produit';
import Panier from './pages/Panier';
import Commande, { PaiementSimule } from './pages/Commande';
import Gratuit from './pages/Gratuit';
import { APropos, Contact, Faq, Introuvable, MesTelechargements, TelechargementImpossible } from './pages/Infos';

const Legal = {
  MentionsLegales: lazy(() => import('./pages/Legal').then((m) => ({ default: m.MentionsLegales }))),
  Cgv: lazy(() => import('./pages/Legal').then((m) => ({ default: m.Cgv }))),
  Confidentialite: lazy(() => import('./pages/Legal').then((m) => ({ default: m.Confidentialite }))),
  Cookies: lazy(() => import('./pages/Legal').then((m) => ({ default: m.Cookies }))),
};

export default function App() {
  return (
    <Layout>
      <Suspense fallback={<Chargement />}>
        <Routes>
          <Route path="/" element={<Accueil />} />
          <Route path="/boutique" element={<Boutique />} />
          <Route path="/produit/:slug" element={<Produit />} />
          <Route path="/panier" element={<Panier />} />
          <Route path="/commande/:id" element={<Commande />} />
          <Route path="/paiement-simule/:id" element={<PaiementSimule />} />
          <Route path="/mes-telechargements" element={<MesTelechargements />} />
          <Route path="/telechargement-impossible" element={<TelechargementImpossible />} />
          <Route path="/activites-gratuites" element={<Gratuit />} />
          <Route path="/a-propos" element={<APropos />} />
          <Route path="/faq" element={<Faq />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/mentions-legales" element={<Legal.MentionsLegales />} />
          <Route path="/cgv" element={<Legal.Cgv />} />
          <Route path="/confidentialite" element={<Legal.Confidentialite />} />
          <Route path="/cookies" element={<Legal.Cookies />} />
          <Route path="*" element={<Introuvable />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}
