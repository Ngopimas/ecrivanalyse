const MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
  'août', 'septembre', 'octobre', 'novembre', 'décembre'];

type Q = {
  participant_role?: string | null;
  participant_name?: string | null;
  quintesse_num?: string | null;
  status?: string | null;
};

export function frDate(iso?: string | null): string {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  if (!y || !m || !d) return '';
  return `${d === 1 ? '1er' : d} ${MONTHS[m - 1]} ${y}`;
}

export function year(iso?: string | null): string {
  return iso ? iso.slice(0, 4) : '—';
}

/** URL-safe slug from a French collection/série name. */
export function slug(s?: string | null): string {
  return (s || '')
    .normalize('NFD').replace(/\p{Diacritic}/gu, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
    .slice(0, 80) || 'sans-titre';
}

// Ivan's orthography (used on the original pages): P(au)seur / P(au)seuse
const ROLE: Record<string, string> = {
  pauseur: 'P(au)seur', pauseuse: 'P(au)seuse', analisant: 'Analisant', analisante: 'Analisante',
};
export function roleLabel(role?: string | null): string {
  return (role && ROLE[role]) || '';
}

export function modeLabel(mode?: string | null): string {
  return mode === 'pause' ? 'séance de p(au)se'
    : mode === 'ecrivanalyse' ? 'écrivanalyse' : '';
}

/** The participant, e.g. "Analisante : anonyme" / "Pauseuse : Zingara". */
export function participant(q: Q): string {
  const r = roleLabel(q.participant_role);
  if (!r) return '';
  // narrow no-break space before the colon (French typography)
  return q.participant_name ? `${r} : ${q.participant_name}` : r;
}

/**
 * The quintesse OBJECT line, in the original sentence form. `status` holds the
 * full phrase as Ivan wrote it ("achetée par l'analisante", "suspendue pour la
 * p(au)seuse", "autorisée à la vente"), so no reconstruction is needed:
 * "Quintesse XIX achetée par l'analisante" / "Quintesse suspendue pour la p(au)seuse".
 */
export function quintesseObject(q: Q): string {
  if (!q.quintesse_num && !q.status) return '';
  return ['Quintesse', q.quintesse_num, q.status].filter(Boolean).join(' ');
}
