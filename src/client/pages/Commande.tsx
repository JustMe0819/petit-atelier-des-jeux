import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Icone } from '../components/Icone';
import { Alerte, Chargement } from '../components/Divers';
import { api, ErreurApi } from '../lib/api';
import { usePanier } from '../lib/panier';
import { useTitre } from '../lib/useTitre';
import { formatDate, formatPrix, formatTaille } from '../../shared/format';
import type { CommandeResume } from '../../shared/types';

const ATTENTE_MAX_MS = 90_000;

/** Page de confirmation : affiche les téléchargements UNIQUEMENT quand le serveur a reçu la confirmation de paiement. */
export default function Commande() {
  useTitre('Ma commande');
  const { id = '' } = useParams();
  const [sp] = useSearchParams();
  const jeton = sp.get('t') ?? '';
  const [commande, setCommande] = useState<CommandeResume | null>(null);
  const [erreur, setErreur] = useState<ErreurApi | null>(null);
  const [tropLong, setTropLong] = useState(false);
  const debut = useRef(Date.now());
  const { retirer } = usePanier();

  useEffect(() => {
    let actif = true;
    let minuteur: ReturnType<typeof setTimeout>;
    const charger = async () => {
      try {
        const c = await api<CommandeResume>(`/api/commandes/${encodeURIComponent(id)}?t=${encodeURIComponent(jeton)}`);
        if (!actif) return;
        setCommande(c);
        if (c.statut === 'en_attente') {
          if (Date.now() - debut.current < ATTENTE_MAX_MS) minuteur = setTimeout(charger, 2000);
          else setTropLong(true);
        }
      } catch (e) {
        if (actif) setErreur(e as ErreurApi);
      }
    };
    charger();
    return () => {
      actif = false;
      clearTimeout(minuteur);
    };
  }, [id, jeton]);

  useEffect(() => {
    if (commande?.statut === 'payee') commande.lignes.forEach((l) => retirer(l.produitId));
  }, [commande?.statut]); // eslint-disable-line react-hooks/exhaustive-deps

  if (erreur) {
    return (
      <div className="conteneur max-w-2xl py-space-xl">
        {erreur.code === 'LIEN_EXPIRE' ? (
          <>
            <h1 className="mb-space-md font-titre text-headline-lg-mobile">Ce lien a expiré</h1>
            <p className="mb-space-md font-texte text-body-md text-on-surface-variant">Pour protéger vos fichiers, les liens d’accès ont une durée limitée. Recevez-en un nouveau par e-mail :</p>
            <FormulaireRenouvellement />
          </>
        ) : (
          <>
            <h1 className="mb-space-md font-titre text-headline-lg-mobile">Commande introuvable</h1>
            <Alerte type="erreur">{erreur.message} Vérifiez que vous avez copié le lien complet reçu par e-mail.</Alerte>
            <p className="mt-space-md font-texte text-body-md"><Link to="/mes-telechargements" className="lien">Recevoir un nouveau lien par e-mail</Link></p>
          </>
        )}
      </div>
    );
  }
  if (!commande) return <Chargement texte="Chargement de votre commande…" />;

  return (
    <div className="conteneur max-w-3xl space-y-space-lg pb-28 pt-space-lg md:pb-space-xl">
      {commande.statut === 'en_attente' && (
        <section className="rounded-2xl bg-surface-container-lowest p-space-lg text-center shadow-carte" aria-live="polite">
          <Icone nom="hourglass_top" className="mb-2 animate-pulse text-[40px] text-primary" />
          <h1 className="font-titre text-headline-md">Confirmation du paiement en cours…</h1>
          <p className="mt-2 font-texte text-body-md text-on-surface-variant">
            {tropLong
              ? 'La confirmation prend plus de temps que prévu (cela arrive avec certains moyens de paiement). Vous recevrez un e-mail dès qu’elle arrivera ; vous pouvez aussi recharger cette page plus tard.'
              : 'Nous attendons la confirmation de votre banque. Cela prend en général quelques secondes, ne fermez pas cette page.'}
          </p>
        </section>
      )}

      {commande.statut === 'payee' && (
        <section className="rounded-2xl bg-secondary-fixed/40 p-space-lg shadow-doux">
          <div className="mb-space-md flex items-center gap-space-sm">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-secondary text-on-secondary shadow-sm"><Icone nom="task_alt" className="text-[28px]" /></span>
            <div>
              <h1 className="font-titre text-headline-md">Merci, votre commande est confirmée !</h1>
              <p className="font-texte text-body-sm text-on-surface-variant">Un e-mail récapitulatif a été envoyé à {commande.emailMasque}.</p>
            </div>
          </div>
          <div className="space-y-space-md">
            {commande.telechargements.map((t) => (
              <div key={t.produitId}>
                <h2 className="mb-space-xs font-titre text-title-md">{t.titre}</h2>
                <div className="space-y-space-xs">
                  {t.fichiers.map((f) => (
                    <a key={f.type} href={f.url} className={`flex w-full items-center justify-between rounded-lg px-space-md py-3 font-texte text-label-lg shadow-sm transition-colors ${f.type === 'pdf' ? 'bg-secondary text-on-secondary hover:bg-on-secondary-container' : 'bg-surface-container-lowest text-on-surface hover:bg-surface-container'}`}>
                      <span className="flex min-w-0 items-center gap-space-xs">
                        <Icone nom={f.type === 'corriges' ? 'quiz' : f.type === 'encre_eco' ? 'eco' : 'file_download'} className="shrink-0 text-[22px]" />
                        <span className="truncate">{f.libelle}</span>
                      </span>
                      <span className="shrink-0 rounded-full bg-black/10 px-2 py-0.5 font-texte text-caption">{formatTaille(f.tailleOctets)}</span>
                    </a>
                  ))}
                </div>
              </div>
            ))}
            {commande.telechargements.length === 0 && <Alerte type="attention">Les fichiers de cette commande sont momentanément indisponibles. Écrivez-nous via la page Contact en indiquant le numéro {commande.id}.</Alerte>}
          </div>
          <p className="mt-space-md font-texte text-caption text-on-surface-variant">
            <Icone nom="schedule" className="mr-1 align-[-3px] text-[16px]" />
            Ces boutons fonctionnent jusqu’au {commande.liensExpirentLe ? formatDate(commande.liensExpirentLe, true) : '—'}. Le lien de cette page reste valable jusqu’au {formatDate(commande.accesExpireLe)} ; ensuite, demandez-en un nouveau sur <Link to="/mes-telechargements" className="lien">Mes téléchargements</Link>.
          </p>
        </section>
      )}

      {(commande.statut === 'echouee' || commande.statut === 'expiree') && (
        <section className="space-y-space-md rounded-2xl bg-surface-container-lowest p-space-lg shadow-doux">
          <h1 className="font-titre text-headline-md">{commande.statut === 'echouee' ? 'Le paiement n’a pas abouti' : 'La session de paiement a expiré'}</h1>
          <p className="font-texte text-body-md text-on-surface-variant">Aucun fichier n’a été débloqué et, sauf message contraire de votre banque, aucun montant n’a été débité. Vous pouvez réessayer depuis votre panier.</p>
          <Link to="/panier" className="btn-primaire">Retourner au panier</Link>
        </section>
      )}

      {commande.statut === 'anomalie' && (
        <Alerte type="attention">Votre paiement a bien été reçu mais demande une vérification manuelle. Nous revenons vers vous rapidement par e-mail (commande {commande.id}).</Alerte>
      )}

      <section className="rounded-2xl bg-surface-container-lowest p-space-md shadow-doux">
        <h2 className="mb-space-sm font-titre text-title-md">Récapitulatif — commande {commande.id}</h2>
        <ul className="divide-y divide-surface-container-high font-texte text-body-sm">
          {commande.lignes.map((l) => (
            <li key={l.produitId} className="flex justify-between py-2"><span>{l.titre}</span><span className="font-bold">{formatPrix(l.prixCentimes)}</span></li>
          ))}
          <li className="flex justify-between py-2 font-titre text-title-md"><span>Total</span><span>{formatPrix(commande.totalCentimes)}</span></li>
        </ul>
        <p className="mt-space-sm font-texte text-caption text-on-surface-variant">
          Commande passée le {formatDate(commande.creeLe, true)}.{' '}
          {commande.consentement.executionImmediateLe && `Accord pour l’accès immédiat donné le ${formatDate(commande.consentement.executionImmediateLe, true)}.`}
          {commande.modePaiement === 'simulation' && ' (Commande de démonstration : aucun paiement réel.)'}
          {commande.modePaiement === 'stripe_test' && ' (Commande en mode test Stripe : aucun paiement réel.)'}
        </p>
      </section>

      <section className="rounded-2xl bg-surface-container-low p-space-md">
        <h2 className="mb-1 flex items-center gap-2 font-titre text-title-md"><Icone nom="print" className="text-secondary" /> Conseil d’impression</h2>
        <p className="font-texte text-body-sm text-on-surface-variant">Papier A4 standard (80 g), option « Taille réelle » ou « Ajuster à la page ». Imprimez les corrigés à part pour laisser votre enfant chercher par lui-même.</p>
      </section>
    </div>
  );
}

export function FormulaireRenouvellement() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState<{ ok: boolean; texte: string } | null>(null);
  const [envoi, setEnvoi] = useState(false);
  const envoyer = async (e: FormEvent) => {
    e.preventDefault();
    setEnvoi(true);
    try {
      const r = await api<{ message: string }>('/api/acces/renouveler', { method: 'POST', json: { email } });
      setMessage({ ok: true, texte: r.message });
    } catch (err) {
      setMessage({ ok: false, texte: (err as Error).message });
    } finally {
      setEnvoi(false);
    }
  };
  return (
    <form onSubmit={envoyer} className="space-y-space-sm rounded-2xl bg-surface-container-lowest p-space-md shadow-doux">
      <label htmlFor="email-renouvellement" className="etiquette">Adresse e-mail utilisée lors de l’achat</label>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input id="email-renouvellement" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="exemple@famille.fr" autoComplete="email" className="champ flex-1" />
        <button type="submit" disabled={envoi} className="btn-primaire">
          <Icone nom="forward_to_inbox" className="text-[20px]" /> {envoi ? 'Envoi…' : 'Recevoir mes liens'}
        </button>
      </div>
      {message && <Alerte type={message.ok ? 'succes' : 'erreur'}>{message.texte}</Alerte>}
    </form>
  );
}

export function PaiementSimule() {
  useTitre('Paiement simulé');
  const { id = '' } = useParams();
  const [sp] = useSearchParams();
  const t = sp.get('t') ?? '';
  const navigate = useNavigate();
  const [erreur, setErreur] = useState<string | null>(null);
  const simuler = async (resultat: 'succes' | 'echec') => {
    try {
      await api(`/api/simulation/${encodeURIComponent(id)}/${resultat}`, { method: 'POST', json: { t } });
      navigate(`/commande/${encodeURIComponent(id)}?t=${encodeURIComponent(t)}`);
    } catch (e) {
      setErreur((e as Error).message);
    }
  };
  return (
    <div className="conteneur max-w-xl py-space-xl">
      <div className="space-y-space-md rounded-2xl border-2 border-dashed border-outline bg-surface-container-lowest p-space-lg text-center shadow-doux">
        <span className="pastille bg-inverse-surface text-inverse-on-surface">MODE DÉMONSTRATION — AUCUN PAIEMENT RÉEL</span>
        <h1 className="font-titre text-headline-md">Simulateur de paiement</h1>
        <p className="font-texte text-body-md text-on-surface-variant">
          Cette page remplace Stripe pendant le développement. Elle déclenche exactement le même traitement que le webhook de confirmation. Elle n’existe pas en production.
        </p>
        <p className="font-texte text-label-lg">Commande {id}</p>
        <div className="flex flex-col justify-center gap-space-sm sm:flex-row">
          <button type="button" onClick={() => simuler('succes')} className="btn bg-secondary px-5 py-3 text-on-secondary">Simuler un paiement réussi</button>
          <button type="button" onClick={() => simuler('echec')} className="btn bg-error-container px-5 py-3 text-on-error-container">Simuler un échec</button>
        </div>
        <Link to="/panier?paiement=annule" className="lien inline-block font-texte text-body-sm">Annuler et revenir au panier</Link>
        {erreur && <Alerte type="erreur">{erreur}</Alerte>}
      </div>
    </div>
  );
}
