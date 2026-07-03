import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// One YAML file per quinte (src/content/quintes/<slug>.yaml), managed by Keystatic.
// Enum-like fields are plain strings ('' when empty) so any file validates and
// the Keystatic form never chokes on null. Route by entry id (the filename).
const quintes = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/content/quintes' }),
  schema: z.object({
    id: z.number().optional(),
    title: z.string(),
    soustitre: z.string().default(''),
    lines: z.array(z.string()).default([]),
    is_5x5: z.boolean().default(false),
    mode: z.string().default(''),
    participant_role: z.string().default(''),
    participant_name: z.string().default(''),
    quintesse_num: z.string().default(''),
    status: z.string().default(''),
    collection: z.string().default(''),
    recueil: z.string().default(''),
    date: z.string().default(''),
    author: z.string().default('Ivan Joseph'),
  }),
});

// One JSON file per comment (src/content/comments/<quinte-id>-<n>.json).
// The 10 SPIP-era comments come from scripts/import-comments.py; new ones are
// committed by the moderation endpoint (functions/api/) after Ivan approves
// them by email. JSON (not YAML) so reader-submitted text can never break parsing.
const comments = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/content/comments' }),
  schema: z.object({
    quinte: z.string(), // entry id of the quinte (numeric SPIP article id as string)
    title: z.string().default(''), // SPIP allowed a comment title; empty for new comments
    author: z.string().default(''),
    date: z.string(), // ISO 8601
    text: z.string(), // plain text; \n = line break, \n\n = paragraph break
    legacy_id: z.number().optional(), // SPIP id_forum for the archived ones
  }),
});

export const collections = { quintes, comments };
