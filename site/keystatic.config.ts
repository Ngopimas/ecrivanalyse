import { config, collection, fields } from '@keystatic/core';

// Local, Git-based editing. Runs at /keystatic during `astro dev` only
// (the production build stays pure static). Manages the YAML quinte files.
export default config({
  storage: { kind: 'local' },
  ui: {
    brand: { name: 'Écrivanalyse' },
  },
  collections: {
    quintes: collection({
      label: 'Quintes',
      path: 'src/content/quintes/*',
      format: { data: 'yaml' },
      slugField: 'title',
      columns: ['title', 'date'],
      schema: {
        id: fields.integer({ label: 'ID (hérité - laisser tel quel)' }),
        title: fields.slug({
          name: { label: 'Titre', validation: { isRequired: true } },
        }),
        soustitre: fields.text({ label: 'Description (une ligne)' }),
        lines: fields.array(fields.text({ label: 'Ligne' }), {
          label: 'La quinte',
          description:
            'Cinq lignes, cinq mots, cinq ponctuations - mais libre. ' +
            'Vide si la quinte n\'a jamais été mise en ligne (quintesse achetée).',
          itemLabel: (p) => p.value || 'ligne',
        }),
        date: fields.text({ label: 'Date', description: 'AAAA-MM-JJ' }),
        mode: fields.select({
          label: 'Mode',
          options: [
            { label: '-', value: '' },
            { label: 'Séance de p(au)se', value: 'pause' },
            { label: 'Écrivanalyse', value: 'ecrivanalyse' },
          ],
          defaultValue: '',
        }),
        participant_role: fields.select({
          label: 'Rôle du·de la participant·e',
          options: [
            { label: '-', value: '' },
            { label: 'Analisante', value: 'analisante' },
            { label: 'Analisant', value: 'analisant' },
            { label: 'Pauseuse', value: 'pauseuse' },
            { label: 'Pauseur', value: 'pauseur' },
          ],
          defaultValue: '',
        }),
        participant_name: fields.text({ label: 'Nom du·de la participant·e' }),
        quintesse_num: fields.text({ label: 'Quintesse (n° romain)' }),
        status: fields.text({
          label: 'Statut de la quintesse',
          description:
            'La phrase complète, telle qu\'écrite : « achetée par l\'analisante », ' +
            '« suspendue pour la p(au)seuse », « autorisée à la vente »…',
        }),
        collection: fields.text({ label: 'Collection / série' }),
        recueil: fields.text({ label: 'Recueil (si publiée)' }),
        author: fields.text({ label: 'Auteur', defaultValue: 'Ivan Joseph' }),
        is_5x5: fields.checkbox({ label: '5×5 exact' }),
        prose: fields.text({
          label: 'Prose autour de la quinte',
          description: 'Paragraphes séparés par une ligne vide ; <i>italique</i> permis.',
          multiline: true,
        }),
      },
    }),
    textes: collection({
      label: 'Textes',
      path: 'src/content/textes/*',
      format: { data: 'yaml' },
      slugField: 'title',
      columns: ['title', 'date'],
      schema: {
        id: fields.integer({ label: 'ID (hérité - laisser tel quel)' }),
        title: fields.slug({
          name: { label: 'Titre', validation: { isRequired: true } },
        }),
        soustitre: fields.text({ label: 'Description (une ligne)' }),
        text: fields.text({
          label: 'Le texte',
          description: 'Paragraphes séparés par une ligne vide ; <i>italique</i> permis.',
          multiline: true,
          validation: { isRequired: true },
        }),
        date: fields.text({ label: 'Date', description: 'AAAA-MM-JJ' }),
        mode: fields.text({ label: 'Mode (hérité)' }),
        participant_role: fields.text({ label: 'Rôle (hérité)' }),
        participant_name: fields.text({ label: 'Participant·e (hérité)' }),
        quintesse_num: fields.text({ label: 'Quintesse (n° romain)' }),
        status: fields.text({ label: 'Statut de la quintesse' }),
        collection: fields.text({ label: 'Collection / série' }),
        recueil: fields.text({ label: 'Recueil (si publié)' }),
        author: fields.text({ label: 'Auteur', defaultValue: 'Ivan Joseph' }),
      },
    }),
  },
});
