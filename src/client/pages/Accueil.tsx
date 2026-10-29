import { Link } from 'react-router-dom';
import { Icone } from '../components/Icone';
import { CartePlanche } from '../components/Cartes';
import { Accordeon } from '../components/Accordeon';
import { Chargement, EnTeteSection } from '../components/Divers';
import { useCatalogue } from '../lib/catalogue';
import { useTitre } from '../lib/useTitre';
import { CATEGORIES, THEMES } from '../../shared/libelles';
import { FAQ_COURTE } from './contenus';

const ATOUTS = [
  { icone: 'psychiatry', texte: 'Des activités adaptées aux 6–8 ans', fond: 'bg-[#FDF2E2]', couleur: 'text-[#4E8A5A]' },
  { icone: 'neurology', texte: 'Des thèmes variés et captivants', fond: 'bg-[#FCEEF1]', couleur: 'text-[#C85A7A]' },
  { icone: 'print', texte: 'À imprimer chez soi', fond: 'bg-[#EAF4F4]', couleur: 'text-[#3E6F82]' },
  { icone: 'download', texte: 'Téléchargement après paiement', fond: 'bg-[#EDF1F6]', couleur: 'text-[#3E6F82]' },
];

export default function Accueil() {
  useTitre('', 'Labyrinthes, jeux de logique, nonogrammes et cahiers d’activités à imprimer pour les 6-8 ans.');
  const { produits, enVente, chargement, gratuits } = useCatalogue();
  const kit = gratuits.find((g) => g.id.includes('mini-cahier')) ?? gratuits[0];
  const couvertures = produits.filter((p) => !p.composants.length).slice(0, 3);
  const compte = (filtre: (p: (typeof produits)[number]) => boolean) => enVente.filter(filtre).length;

  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden pb-space-xl">
        <div className="conteneur grid grid-cols-12 items-center gap-gutter pt-space-lg">
          <div className="col-span-12 flex flex-col items-start lg:col-span-7 lg:pr-space-md">
            <span className="pastille mb-space-md bg-secondary-container px-3.5 py-1.5 uppercase tracking-wider text-on-secondary-container shadow-sm">
              <Icone nom="verified" className="text-[18px]" /> Pour les enfants de 6 à 8 ans • PDF à imprimer
            </span>
            <h1 className="mb-space-sm font-titre text-display-hero-mobile text-marine md:text-display-hero">
              Des jeux à imprimer pour{' '}
              <span className="text-primary underline decoration-primary-container decoration-wavy decoration-2 underline-offset-8">grandir en s'amusant !</span>
            </h1>
            <p className="mb-space-lg max-w-xl font-texte text-body-md text-on-surface-variant md:text-body-lg">
              Labyrinthes, défis de logique, nonogrammes et cahiers d'activités pour les enfants de 6 à 8 ans. Téléchargez, imprimez à la maison, et place au calme et à la réflexion, loin des écrans.
            </p>
            <div className="mb-space-xl flex w-full flex-col gap-space-sm sm:w-auto sm:flex-row">
              <Link to="/boutique" className="btn-primaire px-6 py-3.5 shadow-carte">
                <Icone nom="explore" className="text-[20px]" /> Explorer le catalogue
              </Link>
              <Link to="/activites-gratuites" className="btn-secondaire px-6 py-3.5">
                <Icone nom="card_giftcard" className="text-[20px] text-secondary" /> Tester nos jeux gratuits
              </Link>
            </div>
            <div className="grid w-full grid-cols-2 gap-3 sm:grid-cols-4">
              {ATOUTS.map((a) => (
                <div key={a.texte} className={`flex items-center gap-2.5 rounded-xl p-2.5 shadow-sm ${a.fond}`}>
                  <Icone nom={a.icone} className={`shrink-0 text-[24px] ${a.couleur}`} />
                  <span className="font-texte text-caption font-bold text-on-surface">{a.texte}</span>
                </div>
              ))}
            </div>
          </div>
          {/* Composition : couvertures de la planche en éventail */}
          <div className="relative col-span-12 mt-6 lg:col-span-5 lg:mt-0">
            <div className="relative mx-auto aspect-[4/4.2] w-full max-w-md rounded-[2rem] bg-gradient-to-br from-tertiary-container/60 via-surface-container-low to-secondary-container/60 p-6 shadow-carte">
              <div className="pointer-events-none absolute -right-6 -top-6 h-32 w-32 rounded-full bg-primary-container/40 blur-2xl" />
              <div className="pointer-events-none absolute -bottom-8 -left-8 h-40 w-40 rounded-full bg-rose/40 blur-2xl" />
              <div className="relative h-full w-full">
                {couvertures.map((p, i) => (
                  <img key={p.id} src={p.couverture} alt={i === 1 ? `Couverture : ${p.titre}` : ''}
                    className={`absolute top-1/2 w-[52%] -translate-y-1/2 rounded-xl shadow-fort ${['left-0 -rotate-6', 'left-1/2 z-10 -translate-x-1/2 scale-110', 'right-0 rotate-6'][i]}`} />
                ))}
              </div>
              <div className="absolute -bottom-4 right-4 z-20 flex items-center gap-3 rounded-2xl bg-surface-container-lowest px-4 py-3 shadow-fort">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary-fixed text-on-secondary-fixed"><Icone nom="print" /></span>
                <span>
                  <span className="block font-texte text-label-md text-on-surface">Imprimante de maison</span>
                  <span className="font-texte text-caption text-on-surface-variant">A4 • noir et blanc ou couleur</span>
                </span>
              </div>
              <div className="absolute -left-3 top-4 z-20 flex items-center gap-2 rounded-2xl bg-surface-container-lowest px-4 py-2.5 shadow-carte">
                <Icone nom="task_alt" className="text-[20px] text-secondary" />
                <span className="font-texte text-label-md text-on-surface">Corrigés inclus</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CATÉGORIES */}
      <section className="bg-surface-container-low py-space-xl">
        <div className="conteneur">
          <EnTeteSection surtitre="Types d'activités" titre="Des jeux pour stimuler sans stresser" texte="Chaque activité a une consigne courte et une solution vérifiée. La difficulté monte doucement, page après page." />
          <div className="grid grid-cols-1 gap-gutter sm:grid-cols-2 lg:grid-cols-4">
            {[
              { id: 'labyrinthes', titre: 'Labyrinthes progressifs', texte: 'Repérage dans l’espace, concentration visuelle et anticipation.', fond: 'bg-primary-container text-on-primary-container', lien: 'text-primary' },
              { id: 'logique', titre: 'Jeux de logique', texte: 'Suites, intrus, éléments manquants et associations à une seule bonne réponse.', fond: 'bg-secondary-container text-on-secondary-container', lien: 'text-secondary' },
              { id: 'nonogrammes', titre: 'Nonogrammes', texte: 'Des grilles à colorier grâce aux nombres pour révéler un dessin caché.', fond: 'bg-tertiary-container text-on-tertiary-container', lien: 'text-tertiary' },
              { id: 'cahiers', titre: 'Grands cahiers', texte: 'Plusieurs types de jeux réunis, du plus facile au plus difficile.', fond: 'bg-rose text-on-rose', lien: 'text-on-rose' },
            ].map((c) => {
              const cat = CATEGORIES.find((x) => x.id === c.id)!;
              const n = compte((p) => p.categorie === c.id);
              return (
                <Link key={c.id} to={`/boutique?type=${c.id}`} className="group flex flex-col rounded-2xl bg-surface-container-lowest p-6 shadow-doux transition-all duration-300 hover:-translate-y-1 hover:shadow-carte">
                  <span className={`mb-space-md flex h-14 w-14 items-center justify-center rounded-2xl transition-transform group-hover:scale-110 ${c.fond}`}>
                    <Icone nom={cat.icone} className="text-[32px]" />
                  </span>
                  <h3 className="mb-1 font-titre text-headline-sm">{c.titre}</h3>
                  <p className="mb-space-md flex-1 font-texte text-body-sm text-on-surface-variant">{c.texte}</p>
                  <span className={`flex items-center gap-1 font-texte text-label-md ${c.lien}`}>
                    {n > 0 ? `Voir ${n > 1 ? `les ${n} produits` : 'le produit'}` : 'Bientôt disponible'}
                    <Icone nom="arrow_forward" className="text-[16px] transition-transform group-hover:translate-x-1" />
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* SÉLECTION (planche produits) */}
      <section className="py-space-xl" id="catalogue">
        <div className="conteneur">
          <EnTeteSection
            surtitre="Le catalogue en un coup d'œil"
            couleur="text-primary"
            titre="Nos jeux et cahiers à imprimer"
            action={<Link to="/boutique" className="flex items-center gap-1 font-texte text-label-lg text-primary hover:underline">Tout voir dans la boutique <Icone nom="chevron_right" /></Link>}
          />
          {chargement ? (
            <Chargement />
          ) : (
            <div className="grid grid-cols-1 gap-gutter md:grid-cols-2 xl:grid-cols-3">
              {produits.map((p, i) => <CartePlanche key={p.id} produit={p} index={i} />)}
            </div>
          )}
          <p className="mt-space-md font-texte text-caption text-on-surface-variant">
            <Icone nom="info" className="mr-1 align-[-3px] text-[16px]" />
            Les petites pages affichées sont de vrais extraits des PDF. Les produits marqués « Bientôt disponible » sont en cours de création ou de relecture.
          </p>
        </div>
      </section>

      {/* UNIVERS */}
      <section className="bg-surface-container-low py-space-xl">
        <div className="conteneur">
          <EnTeteSection centre surtitre="Imaginaires & passions" titre="Explorer par univers" texte="Chaque enfant a son monde préféré : choisissez l'aventure qui le fera voyager." />
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
            {THEMES.map((t) => {
              // Compte tous les produits annoncés (en vente ou en préparation) de l'univers.
              const n = produits.filter((p) => p.themes.includes(t.id)).length;
              return (
                <Link key={t.id} to={`/boutique?theme=${t.id}`} className="group flex flex-col items-center rounded-2xl bg-surface-container-lowest p-5 text-center shadow-doux transition-all last:col-span-2 hover:-translate-y-1.5 hover:shadow-carte md:last:col-span-1">
                  <span className={`mb-3 flex h-16 w-16 items-center justify-center rounded-2xl transition-transform group-hover:scale-110 ${t.couleur}`}>
                    <Icone nom={t.icone} className="text-[32px]" />
                  </span>
                  <span className="mb-0.5 font-titre text-title-md">{t.libelle}</span>
                  <span className="font-texte text-caption text-on-surface-variant">{n > 0 ? `${n} produit${n > 1 ? 's' : ''}` : 'Bientôt'}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* COMMENT ÇA MARCHE */}
      <section className="py-space-xl">
        <div className="conteneur">
          <EnTeteSection centre surtitre="Simple et rapide" couleur="text-primary" titre="Comment ça marche ?" texte="Aucun colis, aucun abonnement : tout se passe en ligne." />
          <div className="grid grid-cols-1 gap-gutter gap-y-10 md:grid-cols-3">
            {[
              { n: 1, icone: 'shopping_cart_checkout', titre: 'Choisissez vos jeux', texte: 'Ajoutez les PDF au panier et réglez par carte sur la page sécurisée de Stripe.', c: 'bg-primary text-on-primary', f: 'bg-primary-container text-on-primary-container' },
              { n: 2, icone: 'download_done', titre: 'Téléchargez vos PDF', texte: 'Dès que le paiement est confirmé, vos liens apparaissent à l’écran et arrivent par e-mail.', c: 'bg-secondary text-on-secondary', f: 'bg-secondary-container text-on-secondary-container' },
              { n: 3, icone: 'print', titre: 'Imprimez et jouez !', texte: 'Imprimez tout le cahier ou seulement quelques pages, autant de fois que nécessaire pour votre foyer.', c: 'bg-tertiary text-on-tertiary', f: 'bg-tertiary-container text-on-tertiary-container' },
            ].map((e) => (
              <div key={e.n} className="relative flex flex-col items-center rounded-2xl bg-surface-container-lowest p-8 text-center shadow-doux">
                <span className={`absolute -top-5 flex h-10 w-10 items-center justify-center rounded-full font-titre text-headline-sm shadow-carte ${e.c}`}>{e.n}</span>
                <span className={`my-4 flex h-16 w-16 items-center justify-center rounded-2xl ${e.f}`}><Icone nom={e.icone} className="text-[32px]" /></span>
                <h3 className="mb-2 font-titre text-headline-sm">{e.titre}</h3>
                <p className="font-texte text-body-md text-on-surface-variant">{e.texte}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* COIN GRATUIT */}
      <section className="pb-space-xl" id="gratuit">
        <div className="conteneur">
          <div className="relative overflow-hidden rounded-3xl bg-secondary-container p-8 shadow-carte md:p-12">
            <div className="pointer-events-none absolute -bottom-20 -right-20 h-80 w-80 rounded-full bg-surface-container-lowest/30 blur-3xl" />
            <div className="relative z-10 grid grid-cols-1 items-center gap-gutter lg:grid-cols-12">
              <div className="lg:col-span-8">
                <span className="pastille mb-4 bg-surface-container-lowest text-on-secondary-container shadow-sm">
                  <Icone nom="card_giftcard" className="text-[16px] text-secondary" /> Gratuit • sans inscription • sans carte bancaire
                </span>
                <h2 className="mb-3 font-titre text-headline-lg-mobile text-on-secondary-container md:text-headline-lg">Envie de tester avant de commander ?</h2>
                <p className="mb-6 max-w-2xl font-texte text-body-md text-on-secondary-container/90 md:text-body-lg">
                  {kit ? kit.description : 'Des fiches gratuites à imprimer pour découvrir nos jeux.'}
                </p>
                <div className="flex flex-wrap items-center gap-4">
                  {kit && (
                    <a href={kit.fichier} download className="btn-secondaire px-6 py-3.5 shadow-carte">
                      <Icone nom="file_download" className="text-[20px] text-secondary" /> Télécharger le PDF gratuit
                    </a>
                  )}
                  <Link to="/activites-gratuites" className="flex items-center gap-1 font-texte text-label-lg text-on-secondary-container underline underline-offset-4">
                    Voir toutes les activités gratuites
                  </Link>
                </div>
              </div>
              {kit && (
                <div className="flex justify-center lg:col-span-4 lg:justify-end">
                  <div className="w-56 -rotate-3 rounded-2xl bg-surface-container-lowest p-3 shadow-fort transition-transform duration-300 hover:rotate-0">
                    <img src={kit.apercu} alt={`Aperçu : ${kit.titre}`} loading="lazy" className="aspect-[1/1.414] w-full rounded-xl object-cover object-top" />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* VALEURS */}
      <section className="border-t border-surface-container-high py-space-xl">
        <div className="conteneur grid grid-cols-1 gap-gutter md:grid-cols-3">
          {[
            { icone: 'eco', fond: 'bg-secondary-container text-on-secondary-container', titre: 'Pensé pour l’impression', texte: 'Traits noirs nets, peu d’aplats sombres et marges confortables : les pages de jeu s’impriment très bien en noir et blanc.' },
            { icone: 'psychology_alt', fond: 'bg-primary-container text-on-primary-container', titre: 'Une progression douce', texte: 'Les activités vont du plus facile au plus difficile, pour que l’enfant gagne en confiance sans se sentir bloqué.' },
            { icone: 'task_alt', fond: 'bg-tertiary-container text-on-tertiary-container', titre: 'Des solutions vérifiées', texte: 'Chaque solution est contrôlée par un programme (labyrinthes, grilles, suites), puis relue avant publication.' },
          ].map((v) => (
            <div key={v.titre} className="flex items-start gap-4 rounded-2xl bg-surface-container-lowest p-5 shadow-doux">
              <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${v.fond}`}><Icone nom={v.icone} className="text-[26px]" /></span>
              <div>
                <h3 className="mb-1 font-titre text-title-md">{v.titre}</h3>
                <p className="font-texte text-body-sm text-on-surface-variant">{v.texte}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* FAQ COURTE */}
      <section className="py-space-xl">
        <div className="conteneur max-w-4xl">
          <EnTeteSection centre surtitre="Questions fréquentes" titre="Tout ce qu'il faut savoir" />
          <Accordeon elements={FAQ_COURTE} />
          <div className="mt-space-lg flex flex-col items-center gap-space-xs rounded-2xl bg-secondary-container/40 p-space-md text-center">
            <Icone nom="support_agent" className="text-[32px] text-secondary" />
            <h3 className="font-titre text-title-md">Une autre question ?</h3>
            <div className="flex flex-wrap justify-center gap-2">
              <Link to="/faq" className="btn-secondaire py-2">Toute la FAQ</Link>
              <Link to="/contact" className="btn-secondaire py-2">Écrire à l'atelier</Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
