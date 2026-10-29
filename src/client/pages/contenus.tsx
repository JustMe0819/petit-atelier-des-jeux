import { Link } from 'react-router-dom';
import type { ElementFaq } from '../components/Accordeon';

/** Questions fréquentes : textes factuels, sans promesse invérifiable. */
export const FAQ: (ElementFaq & { categorie: 'telechargement' | 'impression' | 'paiement' | 'droits' })[] = [
  {
    categorie: 'telechargement',
    icone: 'cloud_download',
    question: 'Comment reçoit-on les jeux après l’achat ?',
    reponse: (
      <>
        <p className="mb-2">Dès que Stripe confirme votre paiement, deux accès s’ouvrent :</p>
        <ul className="mb-2 list-disc space-y-1 pl-5">
          <li>les boutons de téléchargement sur la page de confirmation de commande ;</li>
          <li>un e-mail récapitulatif avec un lien vers cette même page.</li>
        </ul>
        <p>Aucun compte n’est nécessaire. Aucun colis n’est envoyé : ce sont des fichiers PDF.</p>
      </>
    ),
  },
  {
    categorie: 'telechargement',
    icone: 'link_off',
    question: 'Mon lien a expiré ou j’ai perdu l’e-mail : que faire ?',
    reponse: (
      <p>
        Pour protéger vos fichiers, les liens ont une durée limitée. Rendez-vous sur la page{' '}
        <Link to="/mes-telechargements" className="lien">Mes téléchargements</Link>, indiquez l’adresse e-mail utilisée lors de l’achat : vous recevrez de nouveaux liens pour toutes vos commandes payées.
      </p>
    ),
  },
  {
    categorie: 'telechargement',
    icone: 'quiz',
    question: 'Les solutions sont-elles fournies ?',
    reponse: <p>Oui. Selon le produit, les corrigés sont à la fin du PDF ou dans un fichier séparé (c’est indiqué sur chaque fiche produit). Vous pouvez ainsi imprimer les jeux sans donner les réponses.</p>,
  },
  {
    categorie: 'impression',
    icone: 'print',
    question: 'Quelle imprimante et quel papier utiliser ?',
    reponse: (
      <ul className="list-disc space-y-1 pl-5">
        <li>N’importe quelle imprimante de maison (jet d’encre ou laser) au format A4.</li>
        <li>Papier standard 80 g : parfait pour les crayons de couleur et les labyrinthes.</li>
        <li>Papier 100 à 120 g : conseillé si votre enfant utilise des feutres.</li>
        <li>Dans la fenêtre d’impression, choisissez « Taille réelle » ou « Ajuster à la page ».</li>
      </ul>
    ),
  },
  {
    categorie: 'impression',
    icone: 'eco',
    question: 'Peut-on économiser de l’encre ?',
    reponse: <p>Les pages de jeux sont en noir et blanc, avec des traits nets. Pour les grands cahiers, une version « économie d’encre » (sans couleur sur la couverture) est fournie en plus. Vous pouvez aussi n’imprimer que les pages souhaitées.</p>,
  },
  {
    categorie: 'impression',
    icone: 'replay',
    question: 'Puis-je réimprimer un jeu pour les frères et sœurs ?',
    reponse: <p>Oui : vous pouvez imprimer les fichiers autant de fois que nécessaire pour les enfants de votre foyer. En revanche, les fichiers ne doivent pas être partagés en dehors du foyer ni revendus (voir les CGV).</p>,
  },
  {
    categorie: 'paiement',
    icone: 'lock',
    question: 'Comment se passe le paiement ?',
    reponse: <p>Le paiement se fait sur la page sécurisée de Stripe, un prestataire de paiement reconnu. Vos données bancaires sont saisies chez Stripe et ne passent jamais par notre site. Les moyens proposés (carte bancaire, et selon votre appareil Apple Pay ou Google Pay) s’affichent sur la page de paiement.</p>,
  },
  {
    categorie: 'paiement',
    icone: 'local_shipping',
    question: 'Y a-t-il des frais de livraison ?',
    reponse: <p>Non. Les produits sont uniquement numériques : il n’y a ni expédition, ni frais de port.</p>,
  },
  {
    categorie: 'droits',
    icone: 'gavel',
    question: 'Puis-je me rétracter après l’achat ?',
    reponse: (
      <p>
        Pour un contenu numérique, la loi permet de renoncer au délai de rétractation de 14 jours afin d’accéder immédiatement aux fichiers. Avant de payer, nous vous demandons donc votre accord explicite pour l’accès immédiat et la reconnaissance de la perte de ce droit, et nous vous en envoyons la confirmation par e-mail. Si un fichier est défectueux (illisible, incomplet), vous restez protégé·e par la garantie légale de conformité : <Link to="/contact" className="lien">écrivez-nous</Link>. Détails dans les <Link to="/cgv" className="lien">CGV</Link>.
      </p>
    ),
  },
  {
    categorie: 'droits',
    icone: 'school',
    question: 'Je suis enseignant·e : puis-je utiliser les jeux en classe ?',
    reponse: <p>Les activités gratuites du Coin gratuit peuvent être imprimées pour votre classe. Les produits payants sont prévus pour un usage familial ; pour un usage en classe, contactez-nous afin de convenir d’une licence adaptée.</p>,
  },
];

export const FAQ_COURTE = [FAQ[0], FAQ[7], FAQ[5], FAQ[2], FAQ[3]];
