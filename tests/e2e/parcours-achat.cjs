const { chromium } = require('playwright');
const fs = require('fs');
const BASE = process.env.BASE_URL || 'http://localhost:8787';
const ok = (c, m) => { if (!c) { console.error('ÉCHEC :', m); process.exitCode = 1; } else console.log('✓', m); };
const prix = (c) => (c / 100).toFixed(2).replace('.', ',');
(async () => {
  // Les valeurs attendues sont calculées à partir du catalogue servi (il évolue avec les publications).
  const cat = await (await fetch(BASE + '/api/catalogue')).json();
  const enVente = cat.produits.filter((p) => p.disponible);
  const coffret = cat.produits.find((p) => p.composants.length > 0);
  const nDino = enVente.filter((p) => p.themes.includes('dinosaures') || /dino/i.test(p.titre + p.description)).length;
  const nPlus10 = enVente.filter((p) => p.prixCentimes > 1000).length;
  const nCahiers = enVente.filter((p) => p.categorie === 'cahiers').length;
  const b = await chromium.launch();
  for (const [nom, vp] of [['mobile', { width: 390, height: 844 }], ['bureau', { width: 1366, height: 900 }]]) {
    const ctx = await b.newContext({ viewport: vp, acceptDownloads: true });
    const p = await ctx.newPage();
    const erreurs = [];
    p.on('pageerror', (e) => erreurs.push(e.message));
    p.on('console', (m) => m.type() === 'error' && !m.text().includes('404') && !m.text().includes('403') && erreurs.push(m.text()));
    console.log(`--- ${nom}`);
    await p.goto(BASE + '/boutique', { waitUntil: 'networkidle' });
    // Recherche et filtres
    const nCartes = async () => p.locator('section[aria-label="Résultats"] > div.grid > article').count(); // hors « Bientôt disponibles »
    ok(await nCartes() === enVente.length, `${enVente.length} produits listés`);
    if (nom === 'bureau') {
      await p.fill('#recherche-boutique', 'dino');
      await p.waitForTimeout(200);
      ok(await nCartes() >= nDino && nDino > 0, `recherche « dino » → au moins ${nDino} résultat(s)`);
      await p.fill('#recherche-boutique', 'zzzz');
      await p.waitForTimeout(200);
      ok(await p.getByText('Aucun jeu ne correspond').isVisible(), 'état vide affiché');
      await p.getByRole('button', { name: 'Voir tout le catalogue' }).click();
      await p.getByLabel('Plus de 10 €').click(); await p.waitForTimeout(300);
      ok(await nCartes() === nPlus10, `filtre prix > 10 € → ${nPlus10} résultat(s)`);
      await p.getByRole('button', { name: 'Réinitialiser les filtres' }).click();
      await p.selectOption('section[aria-label="Résultats"] select', 'prix-decroissant'); await p.waitForTimeout(300);
      const premier = await p.locator('section[aria-label="Résultats"] article h3').first().innerText();
      const plusCher = [...enVente].sort((x, y) => y.prixCentimes - x.prixCentimes)[0];
      ok(premier === plusCher.titre, `tri prix décroissant → « ${plusCher.titre} » en premier`);
      await p.goto(BASE + '/boutique?type=cahiers', { waitUntil: 'networkidle' });
      ok(await nCartes() === nCahiers, `catégorie cahiers → ${nCahiers}`);
    }
    // Panier
    await p.goto(BASE + '/produit/labyrinthes-petits-explorateurs', { waitUntil: 'networkidle' });
    await p.getByRole('button', { name: /Ajouter au panier/ }).first().click();
    ok(await p.getByText('Ajouté à votre panier').isVisible(), 'notification d’ajout');
    await p.goto(BASE + '/produit/grand-coffret-explorateurs', { waitUntil: 'networkidle' });
    await p.getByRole('button', { name: /Ajouter au panier/ }).first().click();
    ok(await p.getByText(/déjà inclus dans le coffret ont été retirés/).isVisible(), 'coffret retire les produits inclus');
    await p.goto(BASE + '/panier', { waitUntil: 'networkidle' });
    ok(await p.locator('article').count() === 1, 'panier : 1 article (coffret)');
    ok((await p.locator('form[novalidate]').innerText()).includes(prix(coffret.prixCentimes)), `total ${prix(coffret.prixCentimes)} €`);
    await p.getByRole('button', { name: /Retirer Le grand coffret/ }).click();
    ok(await p.getByText('Votre panier est vide').isVisible(), 'panier vide après retrait');
    await p.goto(BASE + '/produit/mes-premiers-nonogrammes', { waitUntil: 'networkidle' });
    await p.getByRole('button', { name: 'Acheter maintenant' }).click();
    await p.waitForURL('**/panier');
    const payer = p.getByRole('button', { name: /Commander et payer/ });
    ok(await payer.isDisabled(), 'bouton payer désactivé sans e-mail ni consentements');
    await p.fill('#email-commande', `parent.${nom}@exemple.fr`);
    await p.getByLabel(/conditions générales de vente/).check();
    ok(await payer.isDisabled(), 'toujours désactivé sans consentement rétractation');
    await p.getByLabel(/accès immédiat/).check();
    await p.screenshot({ path: `${process.env.DOSSIER_CAPTURES || '/tmp'}/e2e_${nom}_panier.png`, fullPage: true });
    await payer.click();
    await p.waitForURL('**/paiement-simule/**');
    ok(true, 'redirection vers la page de paiement (simulation)');
    await p.getByRole('button', { name: 'Simuler un paiement réussi' }).click();
    await p.waitForURL('**/commande/**');
    await p.getByText('Merci, votre commande est confirmée').waitFor({ timeout: 10000 });
    ok(true, 'commande confirmée après « paiement »');
    await p.screenshot({ path: `${process.env.DOSSIER_CAPTURES || '/tmp'}/e2e_${nom}_commande.png`, fullPage: true });
    const urlCommande = p.url();
    const [dl] = await Promise.all([p.waitForEvent('download'), p.getByRole('link', { name: /Fichier principal/ }).click()]);
    const chemin = await dl.path();
    const debut = fs.readFileSync(chemin).subarray(0, 5).toString();
    ok(debut === '%PDF-' && dl.suggestedFilename().endsWith('.pdf'), `téléchargement PDF réel (${dl.suggestedFilename()}, ${fs.statSync(chemin).size} octets)`);
    await p.goto(BASE + '/panier', { waitUntil: 'networkidle' });
    ok(await p.getByText('Votre panier est vide').isVisible(), 'panier vidé après achat');
    // Accès refusé sans jeton
    const id = new URL(urlCommande).pathname.split('/').pop();
    await p.goto(`${BASE}/commande/${id}?t=faux`, { waitUntil: 'networkidle' });
    ok(await p.getByText('Commande introuvable').isVisible(), 'page commande refusée avec un mauvais jeton');
    const r = await p.request.get(`${BASE}/api/telechargements/abc.def`, { maxRedirects: 0 });
    ok(r.status() === 302, 'lien de téléchargement forgé refusé');
    // Échec de paiement
    await p.goto(BASE + '/produit/defis-de-la-logique', { waitUntil: 'networkidle' });
    await p.getByRole('button', { name: 'Acheter maintenant' }).click();
    await p.fill('#email-commande', `parent.${nom}@exemple.fr`);
    await p.getByLabel(/conditions générales de vente/).check();
    await p.getByLabel(/accès immédiat/).check();
    await p.getByRole('button', { name: /Commander et payer/ }).click();
    await p.waitForURL('**/paiement-simule/**');
    await p.getByRole('button', { name: 'Simuler un échec' }).click();
    await p.getByText('Le paiement n’a pas abouti').waitFor({ timeout: 10000 });
    ok(await p.getByRole('link', { name: /Fichier principal/ }).count() === 0, 'échec : aucun lien de téléchargement');
    // Renouvellement
    await p.goto(BASE + '/mes-telechargements', { waitUntil: 'networkidle' });
    await p.fill('#email-renouvellement', `parent.${nom}@exemple.fr`);
    await p.getByRole('button', { name: 'Recevoir mes liens' }).click();
    await p.getByText(/Si une commande payée correspond/).waitFor({ timeout: 5000 }); ok(true, 'renouvellement d’accès');
    // Pages diverses
    for (const u of ['/faq', '/contact', '/a-propos', '/cgv', '/mentions-legales', '/confidentialite', '/cookies', '/activites-gratuites', '/page-inexistante']) {
      await p.goto(BASE + u, { waitUntil: 'networkidle' });
      const w = await p.evaluate(() => document.documentElement.scrollWidth);
      ok(w <= vp.width, `${u} sans défilement horizontal (${w}px)`);
    }
    ok(erreurs.length === 0, `aucune erreur console (${erreurs.join(' | ')})`);
    await ctx.close();
  }
  await b.close();
})();
