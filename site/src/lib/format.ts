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

const ROLE: Record<string, string> = {
  pauseur: 'Pauseur', pauseuse: 'Pauseuse', analisant: 'Analisant', analisante: 'Analisante',
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

const ACQ: Record<string, string> = {
  analisante: "l'analisante", analisant: "l'analisant",
  pauseuse: 'la pauseuse', pauseur: 'le pauseur',
};
/** The quintesse OBJECT line: "Quintesse XIX · achetée par l'analisante". */
export function quintesseObject(q: Q): string {
  const parts: string[] = [];
  if (q.quintesse_num) parts.push(`Quintesse ${q.quintesse_num}`);
  const acquirer = ACQ[q.participant_role || ''] || 'le·la participant·e';
  if (q.status === 'achetée') parts.push(`achetée par ${acquirer}`);
  else if (q.status) parts.push(q.status);
  return parts.join(' · ');
}
