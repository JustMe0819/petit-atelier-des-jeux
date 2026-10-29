import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Champ } from '../components/Divers';
import { Icone } from '../components/Icone';
import { BOUTIQUE } from '../lib/boutique';
import { useTitre } from '../lib/useTitre';
import { TEXTE_CONSENTEMENT_RETRACTATION } from '../../shared/format';

const E = BOUTIQUE.editeur;

function PageLegale({ titre, children, maj }: { titre: string; children: ReactNode; maj: string }) {
  useTitre(titre);
  return (
    <div className="conteneur max-w-3xl py-space-xl">
      <h1 className="mb-2 font-titre text-headline-lg-mobile text-marine md:text-headline-lg">{titre}</h1>
      <p className="mb-space-md font-texte text-caption text-on-surface-variant">Dernière mise à jour : {maj}</p>
      <div className="mb-space-lg flex items-start gap-2 rounded-xl border-2 border-dashed border-rose bg-rose-soft p-space-md font-texte text-body-sm text-on-rose">
        <Icone nom="edit_note" className="shrink-0 text-[22px]" />
        <p>
          <strong>Modèle à compléter et à faire valider.</strong> Les champs surlignés se remplissent dans <code>config/boutique.json</code>. Ce texte est une base de travail : faites-le relire par un professionnel du droit avant l’ouverture de la boutique.
        </p>
      </div>
      <div className="prose-legale rounded-2xl bg-surface-container-lowest p-space-md shadow-doux md:p-space-xl">{children}</div>
    </div>
  );
}

export function MentionsLegales() {
  return (
    <PageLegale titre="Mentions légales" maj="[date à compléter]">
      <h2>Éditeur du site</h2>
      <p>
        <Champ valeur={E.raison_sociale} /> — <Champ valeur={E.forme_juridique} /><br />
        Adresse : <Champ valeur={E.adresse} /><br />
        SIRET : <Champ valeur={E.siret} /> — Immatriculation : <Champ valeur={E.rcs_ou_rne} /><br />
        TVA intracommunautaire : <Champ valeur={E.tva_intracom} /><br />
        Téléphone : <Champ valeur={E.telephone} /> — E-mail : <Champ valeur={BOUTIQUE.email_contact} />
      </p>
      <p>Directeur ou directrice de la publication : <Champ valeur={E.directeur_publication} /></p>
      <h2>Hébergement</h2>
      <p><Champ valeur={BOUTIQUE.hebergeur.nom} /><br /><Champ valeur={BOUTIQUE.hebergeur.adresse} /><br /><Champ valeur={BOUTIQUE.hebergeur.contact} /></p>
      <h2>Propriété intellectuelle</h2>
      <p>Les jeux, textes, illustrations et fichiers PDF proposés sur ce site sont protégés par le droit d’auteur. Toute reproduction ou diffusion en dehors de l’usage autorisé par les conditions générales de vente est interdite.</p>
      <h2>Crédits</h2>
      <ul>
        <li>Polices Plus Jakarta Sans et Nunito Sans : licence SIL Open Font License 1.1.</li>
        <li>Icônes Material Symbols (Google) : licence Apache 2.0.</li>
        <li>Illustrations de couverture : {BOUTIQUE.illustrations}</li>
        <li>Pictogrammes et jeux à l’intérieur des PDF : créations originales générées par programme pour {BOUTIQUE.nom}.</li>
      </ul>
    </PageLegale>
  );
}

export function Cgv() {
  return (
    <PageLegale titre="Conditions générales de vente" maj="[date à compléter]">
      <h2>1. Objet</h2>
      <p>Les présentes conditions régissent la vente en ligne de contenus numériques (fichiers PDF de jeux et de cahiers d’activités à imprimer) proposés par <Champ valeur={E.raison_sociale} /> (« le vendeur ») sur le site {BOUTIQUE.nom}, à des consommateurs. Toute commande suppose leur acceptation.</p>
      <h2>2. Vendeur</h2>
      <p><Champ valeur={E.raison_sociale} />, <Champ valeur={E.adresse} />, SIRET <Champ valeur={E.siret} />. Contact : <Champ valeur={BOUTIQUE.email_contact} />.</p>
      <h2>3. Produits</h2>
      <p>Les produits sont des fichiers PDF au format A4, livrés uniquement par téléchargement. Aucun produit physique n’est expédié. Les caractéristiques essentielles (contenu, nombre de pages ou de jeux, âge conseillé, présence de corrigés) figurent sur chaque fiche produit. Un lecteur PDF et, pour l’impression, une imprimante au format A4 sont nécessaires.</p>
      <h2>4. Prix</h2>
      <p>Les prix sont indiqués en euros. <Champ valeur={BOUTIQUE.tva.mention} />. Il n’y a aucun frais de livraison. Le prix applicable est celui affiché au moment de la commande.</p>
      <h2>5. Commande</h2>
      <p>Le client ajoute des produits à son panier, indique son adresse e-mail, accepte les présentes conditions, donne son accord pour l’exécution immédiate (article 7), puis valide sa commande en cliquant sur le bouton « Commander et payer », qui implique une obligation de paiement. Le paiement s’effectue ensuite sur la page sécurisée du prestataire Stripe.</p>
      <h2>6. Paiement</h2>
      <p>Le paiement est exigible immédiatement, par les moyens proposés sur la page de paiement Stripe. Le vendeur n’a jamais accès aux données bancaires. La commande n’est confirmée qu’après la confirmation du paiement par Stripe ; en cas d’échec, aucun fichier n’est délivré.</p>
      <h2>7. Fourniture des fichiers et droit de rétractation</h2>
      <p>Les fichiers sont mis à disposition dès la confirmation du paiement, sur la page de confirmation de commande et par un lien envoyé par e-mail. Les boutons de téléchargement ont une durée de validité limitée ; le client peut à tout moment obtenir de nouveaux liens depuis la page « Mes téléchargements ».</p>
      <p>
        Conformément à l’article L221-28 13° du Code de la consommation, le droit de rétractation ne peut pas être exercé pour la fourniture d’un contenu numérique non fourni sur un support matériel dont l’exécution a commencé après accord préalable exprès du consommateur et renoncement exprès à son droit de rétractation. Avant le paiement, le client coche la mention suivante : « {TEXTE_CONSENTEMENT_RETRACTATION} ». Cet accord, sa date et son heure sont enregistrés avec la commande et confirmés au client par e-mail (support durable), conformément à l’article L221-13 du même code.
      </p>
      <h2>8. Garantie légale de conformité</h2>
      <p>Le client bénéficie de la garantie légale de conformité applicable aux contenus numériques (articles L224-25-12 et suivants du Code de la consommation). En cas de fichier défectueux (illisible, incomplet, non conforme à sa description), le client peut demander sa mise en conformité ; à défaut, il peut obtenir une réduction du prix ou la résolution du contrat. Contact : <Champ valeur={BOUTIQUE.email_contact} />.</p>
      <h2>9. Licence d’utilisation</h2>
      <p>{BOUTIQUE.licence_usage}</p>
      <h2>10. Données personnelles</h2>
      <p>Les données nécessaires à la commande sont traitées conformément à la <Link to="/confidentialite" className="lien">politique de confidentialité</Link>.</p>
      <h2>11. Réclamations et médiation</h2>
      <p>Pour toute réclamation, contactez d’abord le vendeur via la page <Link to="/contact" className="lien">Contact</Link>. En cas de litige non résolu, le client peut recourir gratuitement au médiateur de la consommation : <Champ valeur={BOUTIQUE.mediateur.nom} /> (<Champ valeur={BOUTIQUE.mediateur.site} />).</p>
      <h2>12. Droit applicable</h2>
      <p>Les présentes conditions sont soumises au droit français.</p>
    </PageLegale>
  );
}

export function Confidentialite() {
  return (
    <PageLegale titre="Politique de confidentialité" maj="[date à compléter]">
      <h2>Responsable du traitement</h2>
      <p><Champ valeur={E.raison_sociale} />, <Champ valeur={E.adresse} />. Contact : <Champ valeur={BOUTIQUE.email_contact} />.</p>
      <h2>Données collectées et finalités</h2>
      <ul>
        <li><strong>Commandes</strong> : adresse e-mail, produits achetés, montants, dates, preuve de votre accord pour l’exécution immédiate, historique des téléchargements. Finalité : exécuter la commande, vous donner accès aux fichiers et respecter nos obligations comptables. Base légale : contrat et obligation légale.</li>
        <li><strong>Paiement</strong> : vos données bancaires sont saisies directement chez Stripe et ne nous sont jamais transmises. Nous recevons seulement la confirmation du paiement et sa référence.</li>
        <li><strong>Formulaire de contact</strong> : nom, e-mail et message, transmis à notre boîte e-mail pour vous répondre. Base légale : intérêt légitime. L’assistant de la page Contact fonctionne entièrement dans votre navigateur : ce que vous y tapez n’est ni envoyé ni enregistré.</li>
        <li><strong>Journaux techniques</strong> : notre hébergeur enregistre automatiquement l’adresse IP et la date des visites, pour la sécurité du site et la limitation des abus. Base légale : intérêt légitime.</li>
      </ul>
      <h2>Durées de conservation</h2>
      <ul>
        <li>Données de commande et pièces comptables : 10 ans (obligation légale).</li>
        <li>Historique des téléchargements : conservé avec la commande, comme preuve de la livraison des fichiers.</li>
        <li>Messages de contact : le temps de traiter la demande, puis 1 an au maximum.</li>
        <li>Journaux techniques de l’hébergeur : selon la politique de Vercel (quelques jours à quelques semaines).</li>
      </ul>
      <h2>Destinataires et sous-traitants</h2>
      <p>Seuls les prestataires nécessaires au fonctionnement de la boutique traitent vos données, pour notre compte :</p>
      <ul>
        <li><strong>Stripe</strong> : paiement en ligne ;</li>
        <li><strong>{BOUTIQUE.hebergeur.nom}</strong> : hébergement du site ;</li>
        <li><strong>Turso</strong> : hébergement de la base de données des commandes ;</li>
        <li><strong>Google (Gmail)</strong> : envoi des e-mails de commande et réception des messages de contact.</li>
      </ul>
      <p>Certains de ces prestataires peuvent traiter des données hors de l’Union européenne, notamment aux États-Unis, avec des garanties appropriées (clauses contractuelles types ou décision d’adéquation, comme le cadre de protection des données UE–États-Unis). Vos données ne sont jamais vendues ni utilisées à des fins publicitaires. Le site n’envoie aucune lettre d’information.</p>
      <h2>Vos droits</h2>
      <p>Vous disposez d’un droit d’accès, de rectification, d’effacement, de limitation, d’opposition et de portabilité. Écrivez-nous à <Champ valeur={BOUTIQUE.email_contact} />. Vous pouvez aussi introduire une réclamation auprès de la CNIL (www.cnil.fr).</p>
      <h2>Mesure d’audience et cookies</h2>
      <p>Le site n’utilise ni publicité, ni outil de mesure d’audience. Voir la page <Link to="/cookies" className="lien">Cookies</Link>.</p>
    </PageLegale>
  );
}

export function Cookies() {
  return (
    <PageLegale titre="Cookies et stockage local" maj="[date à compléter]">
      <h2>Ce que le site utilise</h2>
      <ul>
        <li><strong>Panier</strong> : la liste des produits de votre panier est conservée dans le stockage local de votre navigateur (« localStorage »), uniquement pour faire fonctionner le panier.</li>
        <li><strong>Tentative de paiement</strong> : un identifiant temporaire est conservé pendant la session (« sessionStorage ») pour éviter les commandes en double.</li>
      </ul>
      <p>Ces éléments sont strictement nécessaires au service que vous demandez : ils ne nécessitent pas votre consentement et ne servent à aucun suivi.</p>
      <h2>Ce que le site n’utilise pas</h2>
      <p>Aucun cookie publicitaire, aucun pixel de réseau social, aucun outil de mesure d’audience. Les polices et icônes sont hébergées sur le site lui-même (aucune requête vers Google Fonts). C’est pourquoi aucun bandeau de consentement n’est affiché.</p>
      <h2>Page de paiement</h2>
      <p>La page de paiement est hébergée par Stripe, qui peut y déposer ses propres cookies, notamment pour la prévention de la fraude. Ils relèvent de la politique de confidentialité de Stripe.</p>
      <h2>Si cela change</h2>
      <p>Si un outil de mesure d’audience ou de publicité était ajouté un jour, un bandeau vous permettrait de l’accepter ou de le refuser avant tout dépôt, et cette page serait mise à jour.</p>
    </PageLegale>
  );
}
