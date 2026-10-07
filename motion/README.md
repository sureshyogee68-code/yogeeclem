# SSITO Production — Motion design (≈30 s, 16:9)

Vidéo de présentation de SSITO Production pour les prospects : prestations, solutions apportées et appel à l'action final pour prendre contact.

- **Vidéo finale** : `ssito-production-motion.mp4` (1920×1080, 30 i/s, 31,5 s, H.264 + AAC)
- **Source animée** : `ssito-motion.html` (s'ouvre dans un navigateur ; lecture, pause et curseur de navigation)
- **Bande-son** : `audio/make_soundtrack.py` (nappe, pulsation, transitions et impacts synthétisés, sans droits)

## Déroulé

| Temps | Scène | Message |
|---|---|---|
| 0–4 s | Logo | Anneaux dorés, SSITO PRODUCTION, Photo · Vidéo · Direction artistique |
| 4–8,5 s | Vision | « On ne fait pas des vidéos, on construit des univers. » Identité · Émotion · Histoire |
| 8,5–14,5 s | Services | Vidéo, Photographie, Mariage, Drone, Réseaux sociaux, Identité & DA, Création IA |
| 14,5–17 s | Solution | Un seul interlocuteur, de A à Z |
| 17–20,5 s | Pour qui | Restaurants, marques, artistes, entreprises, futurs mariés |
| 20,5–24,5 s | Méthode | Brief → Direction artistique → Tournage → Post-production → Livraison |
| 24,5–27,5 s | Différence | Interlocuteur unique, ancrage local, vraie DA, tournage réel + IA |
| 27,5–31,5 s | CTA | « Construisons votre univers. » Prendre contact, ssitoproduction@gmail.com, @ssitoprod |

## Choix d'animation (skill design-motion-principles)

Contexte film de marque / marketing : priorité Jakub Krehel (finition discrète), puis Jhey Tompkins.
- Entrées en opacité + translation + léger flou (≤ 6 px) avec un ease-out expo ou quart ; sorties plus discrètes (≤ 16 px).
- Pas de rebond, pas de départ à `scale(0)`, pas de pulsation en boucle : l'onde des anneaux ne se déclenche qu'une fois, au clic sur le bouton.
- Le zoom de transition reste limité (×1,35). `prefers-reduced-motion` passe l'aperçu en simples fondus.

## Re-générer

```bash
python3 audio/make_soundtrack.py   # → audio/soundtrack.wav
node render.mjs 30                 # → ssito-production-motion.mp4 (Playwright + ffmpeg)
node render.mjs stills 2.4,15.6    # captures fixes dans stills/
```
