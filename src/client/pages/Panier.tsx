import { useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Icone } from '../components/Icone';
import { infoContenu } from '../components/Cartes';
import { Alerte, Chargement, Champ, EtatVide } from '../components/Divers';
import { useCatalogue } from '../lib/catalogue';
import { usePanier } from '../lib/panier';
import { useTitre } from '../lib/useTitre';
import { api, ErreurApi } from '../lib/api';
import { BOUTIQUE } from '../lib/boutique';
import { formatPrix, TEXTE_CONSENTEMENT_RETRACTATION } from '../../shared/format';

/** Clé d'idempotence : la même pour un même panier, pour éviter les commandes en double (double clic, retour arrière). */
function cleTentative(signature: string, renouveler = false): string {
  const CLE = 'pad-tentative-paiement';
  try {
    const actuelle = JSON.parse(sessionStorage.getItem(CLE) ?? 'null');
    if (!renouveler && actuelle?.signature === signature) return actuelle.cle;
    const cle = crypto.randomUUID();
    sessionStorage.setItem(CLE, JSON.stringify({ signature, cle }));
    return cle;
  } catch {
    return crypto.randomUUID();
  }
}

export default function Panier() {
  useTitre('Mon panier');
  const [sp] = useSearchParams();
  const annule = sp.get('paiement') === 'annule';
  const { articles, retirer, sousTotalCentimes, retires, nombre } = usePanier();
  const { chargement, statut } = useCatalogue();
  const [email, setEmail] = useState('');
  const [cgv, setCgv] = useState(false);
  const [consentement, setConsentement] = useState(false);
  const [envoi, setEnvoi] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const paiementActif = statut && statut.paiement !== 'non_configure';
  const peutPayer = !!paiementActif && articles.length > 0 && cgv && consentement && /\S+@\S+\.\S+/.test(email) && !envoi;

  const payer = async (e: FormEvent) => {
    e.preventDefault();
    if (!peutPayer) return;
    setEnvoi(true);
    setErreur(null);
    const ids = articles.map((a) => a.id);
    const signature = [...ids].sort().join('|') + '#' + email.trim().toLowerCase();
    const envoyer = (cle: string) =>
      api<{ url: string }>('/api/commandes', { method: 'POST', json: { produits: ids, email, accepteCgv: cgv, renonceRetractation: consentement, cleIdempotence: cle } });
    try {
      let r: { url: string };
      try {
        r = await envoyer(cleTentative(signature, annule));
      } catch (err) {
        if (err instanceof ErreurApi && err.code === 'CLE_REUTILISEE') r = await envoyer(cleTentative(signature, true));
        else throw err;
      }
      window.location.assign(r.url); // Page de paiement Stripe (ou simulation en développement)
    } catch (err) {
      setErreur((err as Error).message);
      setEnvoi(false);
    }
  };

  if (chargement) return <Chargement />;

  return (
    <div className="conteneur max-w-5xl pb-28 pt-space-lg md:pb-space-xl">
      <section className="mb-space-lg space-y-space-xs">
        <h1 className="font-titre text-headline-lg-mobile text-marine md:text-headline-lg">Mon panier</h1>
        <p className="flex items-center gap-space-xs font-texte text-body-sm text-on-surface-variant">
          <Icone nom="file_download" className="text-[18px] text-secondary" />
          {nombre} PDF • <strong>aucun frais de livraison</strong> (produits numériques)
        </p>
      </section>

      <div className="mb-space-md space-y-space-sm">
        {annule && <Alerte type="info">Paiement annulé : aucun montant n’a été débité. Votre panier est conservé.</Alerte>}
        {retires.length > 0 && <Alerte type="attention">Retiré de votre panier car plus disponible : {retires.join(', ')}.</Alerte>}
      </div>

      {articles.length === 0 ? (
        <div className="rounded-2xl bg-surface-container-lowest shadow-doux">
          <EtatVide icone="shopping_bag" titre="Votre panier est vide" texte="Parcourez la boutique pour trouver des jeux à imprimer." action={<Link to="/boutique" className="btn-primaire">Découvrir les jeux</Link>} />
        </div>
      ) : (
        <div className="grid grid-cols-1 items-start gap-space-lg lg:grid-cols-5">
          <div className="space-y-space-md lg:col-span-3">
            {articles.map((p) => (
              <article key={p.id} className="flex items-start gap-space-md rounded-2xl bg-surface-container-lowest p-space-md shadow-doux">
                <Link to={`/produit/${p.slug}`} className="relative h-28 w-20 shrink-0 overflow-hidden rounded-lg bg-surface-container shadow-sm">
                  <img src={p.couverture} alt="" className="h-full w-full object-cover" />
                  <span className="absolute left-1 top-1 rounded-full bg-primary-container px-1.5 py-0.5 font-texte text-[10px] font-bold text-on-primary-container">PDF</span>
                </Link>
                <div className="min-w-0 flex-1 space-y-space-xs">
                  <div className="flex items-start justify-between gap-space-xs">
                    <h2 className="font-titre text-title-md leading-tight"><Link to={`/produit/${p.slug}`} className="hover:text-primary">{p.titre}</Link></h2>
                    <button type="button" onClick={() => retirer(p.id)} aria-label={`Retirer ${p.titre} du panier`} className="-mr-1 rounded-lg p-1 text-outline transition-colors hover:text-error">
                      <Icone nom="delete" className="text-[20px]" />
                    </button>
                  </div>
                  <p className="font-texte text-caption text-on-surface-variant">{infoContenu(p)}</p>
                  <div className="flex flex-wrap gap-1">
                    <span className="rounded-full bg-secondary-fixed px-2 py-0.5 font-texte text-[11px] font-bold text-on-secondary-fixed">{p.age}</span>
                    {p.corriges.inclus && <span className="rounded-full bg-surface-container px-2 py-0.5 font-texte text-[11px] font-bold text-on-surface-variant">Corrigés inclus</span>}
                    <span className="rounded-full bg-surface-container px-2 py-0.5 font-texte text-[11px] font-bold text-on-surface-variant">A4</span>
                  </div>
                  <div className="flex items-center justify-between pt-space-xs">
                    <span className="font-titre text-headline-sm">{formatPrix(p.prixCentimes)}</span>
                    <span className="font-texte text-caption text-on-surface-variant">1 exemplaire (impressions illimitées pour le foyer)</span>
                  </div>
                </div>
              </article>
            ))}

            <section className="space-y-space-xs rounded-2xl bg-surface-container-low p-space-md shadow-sm">
              <div className="flex items-start gap-space-sm">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-container text-on-primary-container shadow-sm"><Icone nom="info" className="text-[20px]" /></span>
                <div>
                  <h2 className="font-titre text-title-md">Produits 100 % numériques</h2>
                  <p className="font-texte text-body-sm text-on-surface-variant">Aucun colis n’est envoyé. Dès que le paiement est confirmé, vos liens de téléchargement s’affichent à l’écran et vous sont envoyés par e-mail.</p>
                </div>
              </div>
            </section>
          </div>

          <form onSubmit={payer} className="space-y-space-md rounded-2xl bg-surface-container-lowest p-space-md shadow-carte lg:sticky lg:top-48 lg:col-span-2" noValidate>
            <div className="space-y-space-xs font-texte text-body-sm text-on-surface-variant">
              <div className="flex justify-between"><span>Sous-total ({nombre} produit{nombre > 1 ? 's' : ''})</span><span className="font-bold text-on-surface">{formatPrix(sousTotalCentimes)}</span></div>
              <div className="flex items-center justify-between">
                <span>Livraison</span>
                <span className="pastille bg-secondary-container text-on-secondary-container">Aucune — 0,00 €</span>
              </div>
              <div className="flex items-baseline justify-between pt-space-sm text-on-surface">
                <div>
                  <span className="font-titre text-headline-sm">Total à payer</span>
                  <p className="font-texte text-caption text-on-surface-variant"><Champ valeur={BOUTIQUE.tva.mention} /></p>
                </div>
                <span className="font-titre text-headline-md text-primary">{formatPrix(sousTotalCentimes)}</span>
              </div>
            </div>

            <div>
              <label htmlFor="email-commande" className="etiquette">Adresse e-mail <span className="font-normal text-on-surface-variant">(pour recevoir vos fichiers)</span></label>
              <div className="relative">
                <Icone nom="mail" className="pointer-events-none absolute left-3 top-3.5 text-[20px] text-outline" />
                <input id="email-commande" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="exemple@famille.fr" className="champ pl-10" />
              </div>
            </div>

            <div className="space-y-space-sm rounded-xl bg-surface-container-low p-space-sm">
              <label className="flex cursor-pointer items-start gap-2.5">
                <input type="checkbox" checked={cgv} onChange={(e) => setCgv(e.target.checked)} className="mt-0.5 h-5 w-5 shrink-0 accent-primary" />
                <span className="font-texte text-body-sm">J’ai lu et j’accepte les <Link to="/cgv" target="_blank" className="lien">conditions générales de vente</Link>.</span>
              </label>
              <label className="flex cursor-pointer items-start gap-2.5">
                <input type="checkbox" checked={consentement} onChange={(e) => setConsentement(e.target.checked)} className="mt-0.5 h-5 w-5 shrink-0 accent-primary" />
                <span className="font-texte text-body-sm">{TEXTE_CONSENTEMENT_RETRACTATION}</span>
              </label>
              <p className="pl-8 font-texte text-caption text-on-surface-variant">Cet accord est nécessaire pour vous donner accès aux fichiers tout de suite. Il vous sera confirmé par e-mail.</p>
            </div>

            {erreur && <Alerte type="erreur">{erreur}</Alerte>}
            {!paiementActif && <Alerte type="attention">Le paiement en ligne n’est pas encore activé sur cette boutique.</Alerte>}

            <button type="submit" disabled={!peutPayer} className="btn w-full rounded-xl bg-primary-container px-space-lg py-3.5 font-titre text-headline-sm text-on-primary-container shadow-carte hover:bg-primary-fixed-dim">
              <Icone nom={envoi ? 'progress_activity' : 'lock'} className={`text-[22px] ${envoi ? 'animate-spin' : ''}`} />
              {envoi ? 'Redirection vers le paiement…' : `Commander et payer ${formatPrix(sousTotalCentimes)}`}
            </button>
            <div className="space-y-1 text-center font-texte text-caption text-on-surface-variant">
              <p>Vous allez être redirigé·e vers la page de paiement sécurisée de Stripe. Vos données bancaires ne passent pas par notre site.</p>
              <p className="flex items-center justify-center gap-1"><Icone nom="shield" className="text-[14px]" /> Nous ne collectons que votre e-mail, pour vous envoyer vos fichiers.</p>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
