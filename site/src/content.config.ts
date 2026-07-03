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

export const collections = { quintes };
