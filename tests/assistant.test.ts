import { describe, expect, it } from 'vitest';
import { chercherReponse } from '../src/client/components/AssistantFaq';

describe('Assistant de la page Contact (sans IA)', () => {
  it.each([
    ['J’ai perdu le lien de téléchargement', 'lien'],
    ['je n ai pas reçu le mail', 'lien'],
    ['Quel papier pour IMPRIMER ?', 'impression'],
    ['comment économiser de l’encre', 'encre'],
    ['Est-ce que je peux payer par carte bancaire ?', 'paiement'],
    ['je voudrais être remboursée', 'retractation'],
    ['c’est pour quel âge ?', 'age'],
    ['mon fils a 7 ans', 'age'],
    ['je suis enseignante, en classe ?', 'classe'],
    ['le fichier ne s’ouvre pas sur ma tablette', 'ouvrir'],
    ['avez-vous des fiches gratuites ?', 'gratuit'],
    ['faut-il créer un compte', 'compte'],
  ])('« %s » → %s', (question, attendu) => {
    expect(chercherReponse(question)?.id).toBe(attendu);
  });

  it('ne répond rien quand la question est hors sujet', () => {
    expect(chercherReponse('quelle est la capitale du Pérou')).toBeNull();
  });
});
